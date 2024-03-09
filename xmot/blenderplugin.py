import bpy
import math
import json
from mathutils import Quaternion, Vector, Matrix
from typing import Optional, Dict, Tuple, Union
from datetime import datetime, timezone
import mathutils

FRAMETIME = 0.04

from calendar import timegm

EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as filetime
HUNDREDS_OF_NS = 10000000


def to_winfiletime(dt: datetime) -> int:
	if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
		dt = dt.replace(tzinfo=timezone.utc)
	filetime = EPOCH_AS_FILETIME + (timegm(dt.timetuple()) * HUNDREDS_OF_NS)
	return filetime + (dt.microsecond * 10)


def to_datetime(filetime: int) -> datetime:
	s, ns100 = divmod(filetime - EPOCH_AS_FILETIME, HUNDREDS_OF_NS)
	return datetime.utcfromtimestamp(s).replace(microsecond=(ns100 // 10))

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
# Frame types: L for Linear
#              B for Bezier
#    and then: P for Position (time + vec3)
#              R for Rotation (time + quaternion vec4)
#
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
# Every chunk is parsed by something called a ChunkProcessor. The ChunkID specifies which ChunkProcessor to use, 
#  and the version specifies the version of the ChunkProcessor. So if the file format changed they just added a 
#  new ChunkProcessor with the same ID but a new version, and the engine could still load old and new file formats. 
#  Every chunk of a file can use a different ChunkProcessor and version.
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
GENOMFLE_STR = "GENOMFLE"
GENOMFLE_VERSION = 1
DEADBEEF_BYTES = b"\xef\xbe\xad\xde"

Vec3 = Tuple[int,int,int]
Quat = Tuple[int,int,int,int]

class BinaryFileBuilder:
    def __init__(self, binary_stream: Optional[bytearray] = None):
        self.binary_stream = binary_stream if binary_stream else bytearray()
        self.location = 0

    def get_bytes(self, num_of_bytes: int) -> bytes:
        if len(self.binary_stream) < num_of_bytes:
            raise ValueError("Not enough bytes in the binary stream to extract " + str(num_of_bytes) + " bytes")
        
        value = self.binary_stream[:num_of_bytes]
        self.binary_stream = self.binary_stream[num_of_bytes:]
        self.location += num_of_bytes
        return value

    def put_bytes(self, bytes: bytes) -> None:
        self.binary_stream += bytes
        self.location += len(bytes)

    def get_uint8(self) -> int:
        type = '<B'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_uint16(self) -> int:
        type = '<H'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_uint32(self) -> int:
        type = '<I'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_uint64(self) -> int:
        type = '<Q'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_float(self) -> int:
        type = '<f'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_bool(self) -> bool:
        type = '<B'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_vec3(self) -> Vec3:
        type = '<fff'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))

    def get_quat(self) -> Quat:
        type = '<ffff'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))
    
    def get_str(self, length: int) -> str:
        return self.get_bytes(length).decode("windows-1252")
    
    def put_str(self, value: str) -> None:
        self.put_bytes(value.encode("windows-1252"))
        
    def put_uint8(self, value: int) -> None:
        self.put_bytes(struct.pack("<B", value))
        
    def put_uint16(self, value: int) -> None:
        self.put_bytes(struct.pack("<H", value))
        
    def put_uint32(self, value: int) -> None:
        self.put_bytes(struct.pack("<I", value))
        
    def put_uint64(self, value: int) -> None:
        self.put_bytes(struct.pack("<Q", value))
        
    def put_float(self, value: float) -> None:
        self.put_bytes(struct.pack("<f", value))
        
    def put_bool(self, value: bool) -> None:
        self.put_bytes(struct.pack("<B", value))
        
    def put_vec3(self, value: Vec3) -> None:
        self.put_bytes(struct.pack("<fff", *value))
        
    def put_quat(self, value: Quat) -> None:
        self.put_bytes(struct.pack("<ffff", *value))

class XMot:

    class FrameEffect:
        def __init__(self):
            self.framenum: int = 0
            self.name: str = "" 

    class LocationKeyframe:
        def __init__(self):
            self.time: float = 0
            self.location: Vec3 = (0,0,0)

    class RotationKeyframe:
        def __init__(self):
            self.time: float = 0
            self.rotation: Quat = (0,0,0,1)

    class Chunk:
        def get_id(self) -> int:
            raise RuntimeError("Chunk base function get_id is not defined")
        
        def get_version(self) -> int:
            raise RuntimeError("Chunk base function get_version is not defined")
        
        def decode(self, file: BinaryFileBuilder):
            raise RuntimeError("Chunk base function decode is not defined")
        
        def encode(self, file: BinaryFileBuilder):
            raise RuntimeError("Chunk base function encode is not defined")

    class MotionPartChunkV3(Chunk):
        ID = 1
        def get_id(self) -> int:
            return self.ID
        
        def get_version(self) -> int:
            return 3
        
        def decode(self, file: BinaryFileBuilder):
            self.pose_location = file.get_vec3()
            self.pose_rotation = file.get_quat()
            self.pose_scale = file.get_vec3()
            self.bindpose_location = file.get_vec3()
            self.bindpose_rotation = file.get_quat()
            self.bindpose_scale = file.get_vec3()
            self.bone = file.get_str(file.get_uint32())

        def encode(self, file: BinaryFileBuilder):
            file.put_uint32(self.get_id())
            file.put_uint32(84 + len(self.bone))
            file.put_uint32(self.get_version())
            file.put_vec3(self.pose_location)
            file.put_quat(self.pose_rotation)
            file.put_vec3(self.pose_scale)
            file.put_vec3(self.bindpose_location)
            file.put_quat(self.bindpose_rotation)
            file.put_vec3(self.bindpose_scale)
            file.put_uint32(len(self.bone))
            file.put_str(self.bone)

    class AnimationChunkV1(Chunk):
        ID = 2
        RESERVED = 0xc6
        def __init__(self):
            self.interpolation_kind: str = ""
            self.frames = []

        def get_id(self) -> int:
            return self.ID
        
        def get_version(self) -> int:
            return 1
        
        def decode(self, file: BinaryFileBuilder):
            framecount = file.get_uint32()
            interpolation_mode = file.get_str(1)
            assert interpolation_mode == 'L'
            self.interpolation_kind = file.get_str(1)
            assert file.get_uint16() == self.RESERVED

            for i in range(framecount):
                match (self.interpolation_kind):
                    case 'P':
                        lframe = XMot.LocationKeyframe()
                        lframe.time = file.get_float()
                        lframe.location = file.get_vec3()
                        self.frames.append(lframe)
                    case 'R':
                        rframe = XMot.RotationKeyframe()
                        rframe.time = file.get_float()
                        rframe.rotation = file.get_quat()
                        self.frames.append(rframe)
                    case 'B':
                        raise ImportError("Failed to import Animation chunk: Bezier motion is not supported yet!")
                    case _:
                        raise ImportError(f"Failed to import Animation chunk: Unknown motion type {self.interpolation_kind}")
                    
        def encode(self, file: BinaryFileBuilder):
            file.put_uint32(self.get_id())
            file.put_uint32(8 + len(self.frames) * 4 * (4 if self.interpolation_kind == 'P' else 5))
            file.put_uint32(self.get_version())
            file.put_uint32(len(self.frames))
            file.put_str('L')
            file.put_str(self.interpolation_kind)
            file.put_uint16(self.RESERVED)
            for frame in self.frames:
                match (self.interpolation_kind):
                    case 'P':
                        file.put_float(frame.time)
                        file.put_vec3(frame.location)
                    case 'R':
                        file.put_float(frame.time)
                        file.put_quat(frame.rotation)
                    case 'B':
                        raise ImportError("Failed to export Animation chunk: Bezier motion is not supported yet!")
                    case _:
                        raise ImportError(f"Failed to export Animation chunk: Unknown motion type {self.interpolation_kind}")
        
    def __init__(self):
        self.resource_size: int = 0
        self.resource_priority: float = 0
        self.native_file_time: datetime = datetime.min
        self.native_file_size: int = 0
        self.unk_file_time: Optional[datetime] = None
        self.frameeffects: list[XMot.FrameEffect] = []
        self.chunks: list[XMot.Chunk] = []

    def decode(self, data: bytes):
        file = BinaryFileBuilder(bytearray(data))
        assert file.get_str(8) == GENOMFLE_STR
        assert file.get_uint16() == GENOMFLE_VERSION
        tail_offset = file.get_uint32()

        version = file.get_uint16()
        assert version == 5
        self.resource_size = file.get_uint32()
        self.resource_priority = file.get_float()
        self.native_file_time = to_datetime(file.get_uint64())
        self.native_file_size = file.get_uint32()

        if version >= 3:
            self.unk_file_time = to_datetime(file.get_uint64())

        frameeffects = []
        if version >= 2:
            num_frame_effects = file.get_uint16()
            for i in range(num_frame_effects):
                framenum = file.get_uint16()
                strtbl_index = file.get_uint16()
                frameeffects.append((framenum, strtbl_index))

        emfx2_motion_length = file.get_uint32()
        assert file.get_str(4) == "LMA "
        high_version = file.get_uint8()
        low_version = file.get_uint8()
        is_actor = file.get_uint8()
        assert high_version == 1
        assert low_version == 1
        assert is_actor == 0

        # Now decode chunk after chunk (Main payload)
        while file.location < tail_offset:
            processor_id = file.get_uint32()
            chunk_size = file.get_uint32()
            processor_version = file.get_uint32()
            chunk = create_chunk_processor(processor_id, processor_version)
            chunk.decode(file)
            self.chunks.append(chunk)

        assert file.get_bytes(4) == DEADBEEF_BYTES
        strtbl_present = file.get_bool()
        if len(self.frameeffects) > 0 and not strtbl_present:
            raise LookupError("Failed to look up frame effects: The file contains effects, but no string table!")
        
        stringtable: list[str] = []
        for i in range(file.get_uint32()):
            stringtable.append(file.get_str(file.get_uint16()))

        for f in frameeffects:
            effect = XMot.FrameEffect()
            effect.framenum = f[0]
            stringtable_index = f[1]
            if stringtable_index >= len(stringtable):
                raise LookupError(f"Failed to look up frame effect: Index {stringtable_index} is out of bounds of the string table!")
            effect.name = stringtable[stringtable_index]
            self.frameeffects.append(effect)

        # Now that we're done, we do a self-check
        assert data == self.encode()

        return

    def encode(self) -> bytes:
        file = BinaryFileBuilder()
        file.put_str(GENOMFLE_STR)
        file.put_uint16(GENOMFLE_VERSION)
        file.put_uint32(0) # tail_offset: Overwrite later

        file.put_uint16(5)
        file.put_uint32(self.resource_size)
        file.put_float(self.resource_priority)
        file.put_uint64(to_winfiletime(self.native_file_time))
        file.put_uint32(self.native_file_size)
        if self.unk_file_time:
            file.put_uint64(to_winfiletime(self.unk_file_time))
        else:
            file.put_uint64(to_winfiletime(datetime.min))

        file.put_uint16(len(self.frameeffects))
        final_stringtable: list[str] = []
        for i in range(len(self.frameeffects)):
            final_stringtable.append(self.frameeffects[i].name)
            file.put_uint16(self.frameeffects[i].framenum)
            file.put_uint16(i)

        emfx_size_location = file.location
        file.put_uint32(0) # emfx2_motion_length, overwrite later
        emfx2_motion_start = file.location
        file.put_str("LMA ")
        file.put_uint8(1)
        file.put_uint8(1)
        file.put_uint8(0)

        # Now encode chunk after chunk (Main payload)
        for i in range(len(self.chunks)):
            self.chunks[i].encode(file)

        file.binary_stream[10:14] = bytearray(struct.pack('<I', file.location)) # Set tail_offset
        file.binary_stream[emfx_size_location:emfx_size_location+4] = bytearray(struct.pack('<I', file.location - emfx2_motion_start)) # Set tail_offset
        file.put_bytes(DEADBEEF_BYTES)
        file.put_bool(True)
        
        file.put_uint32(len(final_stringtable))
        for s in final_stringtable:
            file.put_uint16(len(s))
            file.put_str(s)

        return file.binary_stream

def create_chunk_processor(processor_id: int, processor_version: int) -> XMot.Chunk:
    match((processor_id, processor_version)):
        case (2, 1): return XMot.AnimationChunkV1()
        case (1, 3): return XMot.MotionPartChunkV3()
        case _:
            raise KeyError(f"No chunk processor combination of {(processor_id, processor_version)} is supported")
        
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
        posebone.keyframe_insert(data_path="location", frame=0)
        posebone.keyframe_insert(data_path="rotation_quaternion", frame=0)

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
                
                if f.location:
                    self.genome_vec = f.location
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
    xmot = XMot()
    xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot"
    # xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\Hero_Stand_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    # xmot_file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\Hero_Stand_None_Tool_P0_SawLog_Ambient_N_Fwd_00_%_00_P0_0.xmot"
    # xmot_file = "C:\\Users\\zachs\\Downloads\\_compiledAnimation\\Hero_SitThrone_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    # xmot_file = "C:\\Users\\zachs\\Downloads\\_compiledAnimation\\Hero_Stand_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
    with open(xmot_file, 'rb') as f:
        xmot.decode(f.read())

    file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.3db"
    #file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Paladin.3db"
    # Invoke the import method provided by the other plugin
    getattr(bpy.ops.import_scene, "3db")(filepath=file)
    #file = "C:\\Users\\zachs\\Projects\\G3SDK\\xmot\\G3_Hero_Body_Player.xact"
    #bpy.ops.g3blend.io_import_xact(filepath=file)
    
    obj = bpy.context.active_object
    if not obj:
        raise Exception("No active object, something must have gone wrong")
    
    for i in range(len(xmot.chunks)):
        chunk = xmot.chunks[i]
        print(type(chunk))
        if chunk.get_id() == XMot.AnimationChunkV1.ID:
            if chunk.interpolation_kind == "R":
                bone = GenomeBones[-1]
                for i in range(len(chunk.frames)):
                    bone.rotation_keyframes.append(chunk.frames[i])
            elif chunk.interpolation_kind == "P":
                bone = GenomeBones[-1]
                for i in range(len(chunk.frames)):
                    bone.position_keyframes.append(chunk.frames[i])
        elif chunk.get_id() == XMot.MotionPartChunkV3.ID:
            bone = GenomeBone()
            bone.name = chunk.bone
            bone.resting_pos = chunk.pose_location
            bone.resting_rot = chunk.pose_rotation
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