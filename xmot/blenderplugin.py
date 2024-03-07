import bpy
import math
import json
from mathutils import Quaternion, Vector, Matrix
import mathutils

FRAMETIME = 0.04

import json
import io
import struct
from enum import Enum

# See: https://web.archive.org/web/20230513172524/https://forum.xentax.com/viewtopic.php?t=9369

# Disassembling the Gothic 3 DLLs shows that there are things like:
# - LMA motion files
# - LMF facial motion files
#
# The beginning of every file is "GENOMFLE". After that, a 16-bit ushort and a 32-bit ulong int follow.
# The 32-bit ulong is the position of the DEADBEEF value, counted from the beginning of the file. DEADBEEF marks
#  the end of the file.
# After the 32-bit ulong directly comes the file content, and then a DEADBEEF value at the end of the file.
# The first 14 bytes (0-13) are the GENOM header
#
# The outermost structure is the eCArchiveFile content described above. Inside of that
# is the content of the Archive file. 
#
#  eCWrapper_emfx2Motion::ImportEMFX2Motion seems to be very relevant
#
# The emfx2 file format version (eCWrapper_emfx2Motion::GetVersion) seems to be hard-coded to 1.
#
# Disassembling confirmed that: (global indices) All data indices seem to be offset by one. They are already fixed here:
# - Location 0x21 (33) is checked against being 0
# - Location 0xc  (12) is used as the length of a loop
# - Location 0x14 (20) is used as a starting pointer for the loop and iterated in 4-byte steps
#
# The frames are: LP for Position (time + vec3)
#                 LR for Rotation (time + quaternion vec4)

# Important links:
#   https://github.com/o3de/o3de/tree/development/Gems/EMotionFX -> This seems to be our best source for EMotionFX
#   https://github.com/aws/lumberyard
#   https://www.gamezone.com/news/gz_interview_emotion_fx_2_gives_half_life_2_a_face_lift/
#   https://docs.o3de.org/docs/api/gems/emotionfx/class_m_core_1_1_memory_file.html
#    ^^ This seems to be very relevant too, it's the MCore::MemoryFile class used in the EMotionFX engine functions 
#
# Gothic Modding Community:
#   https://gothic-modding-community.github.io/gmc/genome/general_info/object_persistence/
#
# The EMotionFX source code gives us this gem: (SharedFileFormatStructs.h, Importer.cpp -> Importer::ProcessChunk())
#
# struct FileChunk {
#     uint32 m_chunkId;        // the chunk ID
#     uint32 m_sizeInBytes;    // the size in bytes of this chunk (excluding this chunk struct)
#     uint32 m_version;        // the version of the chunk
# }
#
# It turns out the entire file format is chunked. Every chunk has this header consisting of 4 32-bit ints, and then
#  m_sizeInBytes bytes of data. Then, the next chunk follows immediately.
#
# Every chunk is parsed by something called a ChunkProcessor, and there are a LOT of them. The ChunkID specifies
#  which ChunkProcessor to use (in Gothic 3 mainly index 1 and 2), and the version specifies the version of the
#  ChunkProcessor. So if the file format changed they just added a new ChunkProcessor with the same ID but a new version,
#  and the engine could still load old formats and write new ones. Every chunk of a file can use a different ChunkProcessor
#  and version.
#
# Disassembling and decompiling Engine.dll reveiled all Chunk Processors:
#  - AnimationChunkProcessor1               id=2    version=1
#  - ExpressionMotionPartChunkProcessor1    id=11   version=1
#  - ExpressionMotionPartChunkProcessor2    id=11   version=2
#  - FileInformationChunkProcessor1         id=16   version=1
#  - FXMaterialChunkProcessor1              id=13   version=1
#  - FXMaterialChunkProcessor2              id=13   version=2
#  - LimitChunkProcessor1                   id=8    version=1
#  - MaterialChunkProcessor1                id=6    version=1
#  - MaterialChunkProcessor2                id=6    version=2
#  - MaterialChunkProcessor3                id=6    version=3
#  - MaterialChunkProcessor4                id=6    version=4
#  - MaterialChunkProcessor5                id=6    version=5
#  - MaterialLayerChunkProcessor1           id=7    version=1
#  - MaterialLayerChunkProcessor2           id=7    version=2
#  - MaterialLayerChunkProcessor3           id=7    version=3
#  - MaterialLayerChunkProcessor4           id=7    version=4
#  - MeshChunkProcessor1                    id=3    version=1
#  - MeshChunkProcessor2                    id=3    version=2
#  - MeshChunkProcessor3                    id=3    version=3
#  - MeshExpressionPartChunkProcessor1      id=10   version=1
#  - MeshExpressionPartChunkProcessor2      id=10   version=2
#  - MeshExpressionPartChunkProcessor3      id=10   version=3
#  - MotionEventChunkProcessor1             id=15   version=1
#  - MotionEventChunkProcessor2             id=15   version=2
#  - MotionPartChunkProcessor1              id=1    version=1
#  - MotionPartChunkProcessor2              id=1    version=2
#  - NodeChunkProcessor1                    id=0    version=1
#  - NodeChunkProcessor2                    id=0    version=2
#  - NodeChunkProcessor3                    id=0    version=3
#  - PhonemeMotionDataChunkProcessor1       id=12   version=1
#  - PhonemeMotionDataChunkProcessor2       id=12   version=2
#  - PhysicsInfoChunkProcessor1             id=9    version=1
#  - RepositioningNodeChunkProcessor1       id=14   version=1
#  - RepositioningNodeChunkProcessor2       id=14   version=2
#  - SkinningInfoChunkProcessor1            id=4    version=1

GENOM_HEADER_LENGTH = 14 # This is the number of bytes before the file content starts

# Json serializer
class XMotEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):  # To array of integers
            return "0x" + obj.hex()
        elif isinstance(obj, Enum):
            return obj.name
        else:
            return json.JSONEncoder.default(self, obj)
        
# Json deserializer that converts hex to bytes again
class XMotDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=XMotDecoder.from_dict)

    @staticmethod
    def from_dict(d):
        for k, v in d.items():
            if isinstance(v, str) and v.startswith("0x"):
                d[k] = bytes.fromhex(v[2:])
        return d
    
class ChunkType(Enum):
    MotionPart = 1
    Animation = 2
    
def unpack(fmt, data):
    chunksize = struct.calcsize(fmt)
    chunk = data[:chunksize]
    data = data[chunksize:]
    return struct.unpack(fmt, chunk), data

def unpack_str(data, length):
    value = data[:length].decode("latin-1")
    data = data[length:]
    return value, data

def unpack_uint8(data):
    value, data = unpack('<B', data)
    return value[0], data

def unpack_uint16(data):
    value, data = unpack('<H', data)
    return value[0], data

def unpack_uint32(data):
    value, data = unpack('<I', data)
    return value[0], data

def unpack_bytes(data, length):
    value = data[:length]
    data = data[length:]
    return value, data

def pack(fmt, data):
    return struct.pack(fmt, *data)

def pack_str(data):
    return data.encode("latin-1")

def pack_uint8(data):
    return pack('<B', [data])

def pack_uint16(data):
    return pack('<H', [data])

def pack_uint32(data):
    return pack('<I', [data])

def pack_bytes(data):
    return data
    
def decode_MotionPartChunk_V3(content):
    output = {}

    # output["matrix"] = [{}, {}, {}]
    # output["matrix"][0] = struct.unpack('<fff', content[:12])
    # output["matrix"][1] = struct.unpack('<fff', content[12:24])
    # output["matrix"][2] = struct.unpack('<fff', content[24:36])
    # output["aftermat"] = struct.unpack('<f', content[36:40])

    output["position"] = struct.unpack('<fff', content[:12])
    output["rotation"] = struct.unpack('<ffff', content[12:28])
    output["scale"] = struct.unpack('<fff', content[28:40])

    # output["n10"] = struct.unpack('<I', content[40:44])[0]
    # output["pad1"] = content[44:48]
    # output["int1"] = struct.unpack('<I', content[48:52])[0]
    # output["pad2"] = content[52:60]
    # output["int2"] = struct.unpack('<I', content[60:64])[0]
    # output["pad3"] = content[64:80]
    output["remaining"] = content[40:80]

    label_length = struct.unpack('<I', content[80:84])[0]
    output["label"] = content[84:84+label_length].decode("latin-1")
    return output

def encode_MotionPartChunk_V3(data):
    output = b""

    # output += struct.pack('<fff', *data["matrix"][0])
    # output += struct.pack('<fff', *data["matrix"][1])
    # output += struct.pack('<fff', *data["matrix"][2])
    # output += struct.pack('<f', *data["aftermat"])

    output += struct.pack('<fff', *data["position"])
    output += struct.pack('<ffff', *data["rotation"])
    output += struct.pack('<fff', *data["scale"])

    # output += struct.pack('<I', data["n10"])
    # output += data["pad1"]
    # output += struct.pack('<I', data["int1"])
    # output += data["pad2"]
    # output += struct.pack('<I', data["int2"])
    # output += data["pad3"]
    output += data["remaining"]

    output += struct.pack('<I', len(data["label"]))
    output += data["label"].encode("latin-1")
    return output

def decode_AnimationChunk_V1(content):
    output = {}
    output["frame_count"] = struct.unpack('<I', content[:4])[0]
    output["frame_type"] = content[4:6].decode("latin-1")
    output["ll_padding"] = content[6:8]
    output["keyframes"] = []

    keyframe_source = content[8:]
    if output["frame_type"] == "LR":
        for _ in range(0, output["frame_count"]):
            output["keyframes"].append({ "rotation": {} })
            keyframe = output["keyframes"][-1]
            keyframe["time"] = struct.unpack('<f', keyframe_source[0:4])[0]
            keyframe["rotation"] = struct.unpack('<ffff', keyframe_source[4:20])
            keyframe_source = keyframe_source[20:]
    elif output["frame_type"] == "LP":
        for _ in range(0, output["frame_count"]):
            output["keyframes"].append({ "position": {} })
            keyframe = output["keyframes"][-1]
            keyframe["time"] = struct.unpack('<f', keyframe_source[0:4])[0]
            keyframe["position"] = struct.unpack('<fff', keyframe_source[4:16])
            keyframe_source = keyframe_source[16:]
    else:
        raise Exception(f"Unknown frame type {output['frame_type']}")
    
    return output

def encode_AnimationChunk_V1(data):
    output = b""
    output += struct.pack('<I', data["frame_count"])
    output += data["frame_type"].encode("latin-1")
    output += data["ll_padding"]

    if data["frame_type"] == "LR":
        for keyframe in data["keyframes"]:
            output += struct.pack('<f', keyframe["time"])
            output += struct.pack('<ffff', *keyframe["rotation"])
    elif data["frame_type"] == "LP":
        for keyframe in data["keyframes"]:
            output += struct.pack('<f', keyframe["time"])
            output += struct.pack('<fff', *keyframe["position"])
    else:
        raise Exception(f"Unknown frame type {data['frame_type']}")
    
    return output
    
def decode_chunk(content, chunk_type, chunk_version):
    if chunk_type == ChunkType.MotionPart.name and chunk_version == 3:
        return decode_MotionPartChunk_V3(content)
    elif chunk_type == ChunkType.Animation.name and chunk_version == 1:
        return decode_AnimationChunk_V1(content)
    else:
        raise Exception(f"Unknown chunk id {chunk_type} with version {chunk_version}")

def encode_chunk(content, chunk_type, chunk_version):
    if chunk_type == ChunkType.MotionPart.name and chunk_version == 3:
        return encode_MotionPartChunk_V3(content)
    elif chunk_type == ChunkType.Animation.name and chunk_version == 1:
        return encode_AnimationChunk_V1(content)
    else:
        raise Exception(f"Unknown chunk id {chunk_type} with version {chunk_version}")
    
def decode_lma(content):
    output = {}

    assert content[:4] == b"LMA "
    output["LMA_byte1"] = content[4]
    output["LMA_byte2"] = content[5]
    output["LMA_byte3"] = content[6]

    src = content[7:]
    chunks = []
    while len(src) > 0:
        chunk = {}
        chunk_id, src = unpack_uint32(src)
        chunk["chunk_type"] = ChunkType(chunk_id).name
        chunk_size, src = unpack_uint32(src)
        chunk["chunk_version"], src = unpack_uint32(src)
        chunk["chunk_content"] = decode_chunk(src[:chunk_size],
                                              chunk["chunk_type"],
                                              chunk["chunk_version"])
        chunks.append(chunk)
        src = src[chunk_size:]

    output["chunks"] = chunks

    return output

def encode_lma(data):
    output = b"LMA "
    output += struct.pack('<b', data["LMA_byte1"])
    output += struct.pack('<b', data["LMA_byte2"])
    output += struct.pack('<b', data["LMA_byte3"])

    for chunk in data["chunks"]:
        new_chunk = encode_chunk(chunk["chunk_content"],
                               chunk["chunk_type"],
                               chunk["chunk_version"])
        output += pack_uint32(ChunkType[chunk["chunk_type"]].value)
        output += pack_uint32(len(new_chunk))
        output += pack_uint32(chunk["chunk_version"])
        output += new_chunk
        
    return output

def decode_file_content(content):
    data = content
    output = {}
    output["content_int1"], data = unpack_uint32(data)
    output["content_pad2"], data = unpack_bytes(data, 2)
    output["content_string1"], data = unpack_str(data, 4)
    output["content_pad7"], data = unpack_bytes(data, 20)
    output["content_is_some_kind_of_other_format"], data = unpack_uint16(data)

    if output["content_is_some_kind_of_other_format"] != 0:
        output["content_extra_int1"], data = unpack_uint32(data)
        output["content_extra_int2"], data = unpack_uint32(data)

    lma_filesize, data = unpack_uint32(data)
    lma_content = data
    assert lma_filesize == len(lma_content)
    output["lma_file"] = decode_lma(lma_content)

    return output

def encode_file_content(content):
    output = b""
    output += pack_uint32(content["content_int1"])
    output += pack_bytes(content["content_pad2"])
    output += pack_str(content["content_string1"])
    output += pack_bytes(content["content_pad7"])
    output += pack_uint16(content["content_is_some_kind_of_other_format"])

    if content["content_is_some_kind_of_other_format"] != 0:
        output += pack_uint32(content["content_extra_int1"])
        output += pack_uint32(content["content_extra_int2"])

    lma = encode_lma(content["lma_file"])
    output += pack_uint32(len(lma))
    output += lma
    return output

def decode(original_data):
    output = {}
    header = original_data

    # First parse the Genome file format
    genomfle, header = unpack_str(header, 8)
    assert genomfle == "GENOMFLE"
    output["file_version"], header = unpack_uint16(header)
    deadbeef_index, header = unpack_uint32(header)

    # Verify the DEADBEEF value
    assert original_data[deadbeef_index:deadbeef_index+4] == b"\xef\xbe\xad\xde"

    # Now parse the file content
    output["content"] = decode_file_content(original_data[GENOM_HEADER_LENGTH:deadbeef_index])

    # Now parse the appendix after the DEADBEEF value
    appendix = original_data[deadbeef_index+4:]
    output["appendix_version"], appendix = unpack_uint8(appendix)
    output["appendix_count"], appendix = unpack_uint32(appendix)
    output["appendix_elements"] = []

    for i in range(output["appendix_count"]):
        length, appendix = unpack_uint16(appendix)
        element, appendix = unpack_str(appendix, length)
        output["appendix_elements"].append(element)

    # Now that we're done, we do a self-check
    #assert original_data == encode(output)

    return output

def encode(data):
    output = b"GENOMFLE"
    output += pack_uint16(data["file_version"])

    content = encode_file_content(data["content"])
    output += pack_uint32(len(content) + GENOM_HEADER_LENGTH)
    output += content
    output += b"\xef\xbe\xad\xde"

    output += pack_uint8(data["appendix_version"])
    output += pack_uint32(data["appendix_count"])
    for element in data["appendix_elements"]:
        output += pack_uint16(len(element))
        output += pack_str(element)
        
    return output


class GenomeBone:
    def __init__(self):
        self.name = None
        self.resting_pos = None
        self.resting_rot = None
        self.rotation_keyframes = []
        self.position_keyframes = []

GenomeBones = []
def getGenomeBone(name):
    for bone in GenomeBones:
        if bone.name == name:
            return bone
    return None

def calculate_local_matrix(bone):
    if bone is None:
        return Matrix.Identity(4)
    
    if bone.parent:
        local_resting_matrix = bone.parent.global_resting_matrix.inverted() @ bone.global_resting_matrix
        trans = local_resting_matrix.translation
        rot = local_resting_matrix.to_3x3().to_quaternion()
    else:
        local_resting_matrix = bone.global_resting_matrix
        trans = local_resting_matrix.translation
        rot = local_resting_matrix.to_3x3().to_quaternion()

    if bone.genome_quat:
        rot = Quaternion((-bone.genome_quat[3], bone.genome_quat[0], bone.genome_quat[2], bone.genome_quat[1]))
    else:
        rot = Quaternion((1, 0, 0, 0))

    if bone.genome_vec:
        trans = Vector((bone.genome_vec[0], bone.genome_vec[2], bone.genome_vec[1])) / 100
    else:
        trans = Vector((0, 0, 0))
        
    boneOrientationFix = mathutils.Matrix(((0,1,0,0),(-1,0,0,0),(0,0,1,0),(0,0,0,1)))
    local_matrix = Matrix.LocRotScale(trans, rot, None)
    local_matrix = boneOrientationFix.inverted() @ local_matrix @ boneOrientationFix
    return local_matrix

class Frame:
    def __init__(self):
        self.time = 0
        self.position = None
        self.rotation = None

class BoneNode:
    def __init__(self):
        self.children = []
        self.name = None
        self.parent = None
        self.genome_resting_vec = None
        self.genome_resting_quat = None
        self.genome_vec = None
        self.genome_quat = None
        self.genomeBone = None
        self.root_matrix = None
        self.resting_diff_inv = None
        self.global_resting_matrix = None # The global matrix from Edit mode
        self.startpose_matrix = None      # The local matrix for Pose mode
        self.local_matrix_keyframes = []  # The local matrix for Pose mode
    
    def apply(self, bones):
        posebone = bones.get(self.name)
        if self.startpose_matrix:
            posebone.matrix_basis = self.startpose_matrix
            #if self.genome_vec:
            #    posebone.location = (self.genome_vec[1] / 100, self.genome_vec[0] / 100, self.genome_vec[2] / 100)
            #if self.genome_vec:
            #    posebone.rotation_quaternion = (-self.genome_quat[3], self.genome_quat[1], self.genome_quat[0], self.genome_quat[2])
        posebone.keyframe_insert(data_path="location", frame=0)
        posebone.keyframe_insert(data_path="rotation_quaternion", frame=0)
        '''
        posebone.matrix_basis = Matrix.Identity(4)
        posebone.keyframe_insert(data_path="location", frame=0)
        posebone.keyframe_insert(data_path="rotation_quaternion", frame=0)
        if self.startpose_matrix:
            posebone.matrix_basis = self.startpose_matrix
        posebone.keyframe_insert(data_path="location", frame=500)
        posebone.keyframe_insert(data_path="rotation_quaternion", frame=500)
        bpy.context.scene.frame_end = 500
        
        '''
        if self.genomeBone:
            for f in self.genomeBone.rotation_keyframes:
                framenum = round(f.time / FRAMETIME)
                if (framenum > bpy.context.scene.frame_end):
                    bpy.context.scene.frame_end = framenum
                
                if f.rotation:
                    self.genome_quat = f.rotation
                    posebone.matrix_basis = self.resting_diff_inv @ calculate_local_matrix(self)
                    posebone.keyframe_insert(data_path="rotation_quaternion", frame=framenum)
        
        if self.genomeBone:
            for f in self.genomeBone.position_keyframes:
                framenum = round(f.time / FRAMETIME)
                if (framenum > bpy.context.scene.frame_end):
                    bpy.context.scene.frame_end = framenum
                
                if f.position:
                    self.genome_vec = f.position
                    posebone.matrix_basis = self.resting_diff_inv @ calculate_local_matrix(self)
                    posebone.keyframe_insert(data_path="location", frame=framenum)
        
        for child in self.children:
            child.apply(bones)
    
def build_bone_tree(bone, editbone, parent = None):
    bone.name = editbone.name
    bone.parent = parent
    bone.global_resting_matrix = editbone.matrix
    
    boneOrientationFix = mathutils.Matrix(((0,1,0,0),(-1,0,0,0),(0,0,1,0),(0,0,0,1)))
    genomeBone = getGenomeBone(bone.name)
    if bone.parent:
        bone.resting_diff_inv = (bone.parent.global_resting_matrix.inverted() @ bone.global_resting_matrix).inverted()
    else:
        bone.resting_diff_inv = bone.global_resting_matrix.inverted() @ boneOrientationFix
        
    #if bone.root_matrix:
    #    bone.resting_diff_inv = bone.root_matrix @ bone.resting_diff_inv
        
    if genomeBone:
        bone.genome_quat = genomeBone.resting_rot
        bone.genome_vec = genomeBone.resting_pos
        bone.genome_resting_vec = bone.genome_vec
        bone.genome_resting_rot = bone.genome_quat
        bone.genomeBone = genomeBone
        bone.startpose_matrix = bone.resting_diff_inv @ calculate_local_matrix(bone)
    else:
        bone.startpose_matrix = bone.resting_diff_inv @ calculate_local_matrix(bone)
    
    for next in editbone.children:
        bone.children.append(BoneNode())
        build_bone_tree(bone.children[-1], next, bone)

def do():
    file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.3db"
    #file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Paladin.3db"
    # Invoke the import method provided by the other plugin
    getattr(bpy.ops.import_scene, "3db")(filepath=file)
    #file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.xact"
    #bpy.ops.g3blend.io_import_xact(filepath=file)
    
    obj = bpy.context.active_object
    if not obj:
        raise Exception("No active object, something must have gone wrong")
        
    # Load the xmot animation
    #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\playerambient.xmot.json"
    #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\xmot.json"
    #xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\piercehit.json"
    
    xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot"
    #xmot_file = "C:\\Users\\zachs\\Downloads\\_compiledAnimation\\Hero_SitThrone_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    #xmot_file = "C:\\Users\\zachs\\Downloads\\_compiledAnimation\\Hero_Stand_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    with open(xmot_file, 'rb') as f:
        data = decode(f.read())

    for i in range(len(data['content']['lma_file']['chunks'])):
        chunk = data['content']['lma_file']['chunks'][i]
        if chunk["chunk_type"] == "Animation":      # This asset is a frame asset, so we merge it into the last asset, which was a MotionPart
            if chunk["chunk_content"]["frame_type"] == "LR":          # Rotation asset
                bone = GenomeBones[-1]
                for i in range(chunk["chunk_content"]["frame_count"]):
                    frame = Frame()
                    frame.time = chunk["chunk_content"]["keyframes"][i]["time"]
                    frame.rotation = chunk["chunk_content"]["keyframes"][i]["rotation"]
                    bone.rotation_keyframes.append(frame)
            elif chunk["chunk_content"]["frame_type"] == "LP":        # Position asset
                bone = GenomeBones[-1]
                for i in range(chunk["chunk_content"]["frame_count"]):
                    frame = Frame()
                    frame.time = chunk["chunk_content"]["keyframes"][i]["time"]
                    frame.position = chunk["chunk_content"]["keyframes"][i]["position"]
                    bone.position_keyframes.append(frame)
        else: # A MotionPart: Create a new bone
            bone = GenomeBone()
            bone.name = chunk["chunk_content"]["label"]
            bone.resting_pos = chunk["chunk_content"]["position"]
            bone.resting_rot = chunk["chunk_content"]["rotation"]
            GenomeBones.append(bone)
            
    
    def findTwoKeyframesToInterpolate(frames, time):
        lower = None
        upper = frames[0]       # The first keyframe is the upper one

        index = 1
        while time > upper["time"] and index < len(frames):  # Find the first keyframe that is larger than the time
            lower = upper
            upper = frames[index]
            index += 1

        if lower is None:       # If we are at the beginning of the animation, we just take the first keyframe
            lower = upper

        if time > upper["time"]:     # If we are at the end of the animation, we just take the last keyframe
            lower = upper

        return lower, upper

    def map(value, inMin, inMax, outMin, outMax):
        if value < inMin:
            return outMin
        if value > inMax:
            return outMax
        if inMin == inMax:
            return outMin
        return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
            
    #return
    bpy.ops.object.mode_set(mode='EDIT')
    
    root = BoneNode()
    root.root_matrix = Matrix.Rotation(math.radians(-90), 4, 'Y') @ Matrix.Rotation(math.radians(180), 4, 'X')
    build_bone_tree(root, obj.data.edit_bones[0])
    #root_matrix = obj.data.edit_bones[0].matrix
    #root_matrix = Matrix.Identity(4)
    
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.scene.frame_end = 0
    root.apply(obj.pose.bones)

    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Set display mode to Material Preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    break

class ImportCustomFileOperator(bpy.types.Operator):
    """Import Custom File Format"""
    bl_idname = "import_custom_file.import_file"
    bl_label = "Import Custom File"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        do()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportCustomFileOperator.bl_idname, text="Custom File (.custom)")

def register():
    bpy.utils.register_class(ImportCustomFileOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportCustomFileOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()

model_object = bpy.data.objects.get("Armature_Player")
if model_object is not None:
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    model_object.select_set(True)
    bpy.ops.object.delete()
else:
    print("Not found")

model_object = bpy.data.objects.get("G3_Hero_Body_Player")
if model_object is not None:
    bpy.ops.object.mode_set(mode='OBJECT')
    model_object.select_set(True)

    def select_children(obj):
        for child in obj.children:
            bpy.ops.object.select_hierarchy(direction='CHILD')
            select_children(child)

    select_children(model_object)
    bpy.ops.object.delete()
    model_object.select_set(True)
    bpy.ops.object.delete()
else:
    print("Not found")
    
do()