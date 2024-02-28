import json
import io
import struct
from enum import Enum

GENOM_HEADER_LENGTH = 14 # This is the number of bytes before the file content starts

# Json serializer
class XActEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):  # To array of integers
            return "0x" + obj.hex()
        elif isinstance(obj, Enum):
            return obj.name
        else:
            return json.JSONEncoder.default(self, obj)
        
# Json deserializer that converts hex to bytes again
class XActDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=XActDecoder.from_dict)

    @staticmethod
    def from_dict(d):
        for k, v in d.items():
            if isinstance(v, str) and v.startswith("0x"):
                d[k] = bytes.fromhex(v[2:])
        return d
    
class ChunkType(Enum):
    Node = 0
    MotionPart = 1
    Animation = 2
    Mesh = 3
    SkinningInfo = 4
    Material = 6
    MaterialLayer = 7
    
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
    
def decode_NodeChunk_V3(content):
    output = {}

    output["position"] = struct.unpack('<fff', content[:12])
    output["rotation"] = struct.unpack('<ffff', content[12:28])
    output["scale"] = struct.unpack('<fff', content[28:40])
    output["scale_orient"] = struct.unpack('<fff', content[40:52])
    output["scale_shear"] = struct.unpack('<ffff', content[52:68])

    label_length = struct.unpack('<I', content[68:72])[0]
    output["label"] = content[72:72+label_length].decode("latin-1")
    parent_label_length = struct.unpack('<I', content[72+label_length:76+label_length])[0]
    output["parent_label"] = content[76+label_length:76+label_length+parent_label_length].decode("latin-1")
    return output

def encode_NodeChunk_V3(data):
    output = b""

    output += struct.pack('<fff', *data["position"])
    output += struct.pack('<ffff', *data["rotation"])
    output += struct.pack('<fff', *data["scale"])
    output += struct.pack('<fff', *data["scale_orient"])
    output += struct.pack('<ffff', *data["scale_shear"])

    output += struct.pack('<I', len(data["label"]))
    output += data["label"].encode("latin-1")
    return output
    
def decode_MaterialChunk_V5(content):
    output = {}
    output["materialchunk"] = content
    return output

def encode_MaterialChunk_V5(data):
    output = b""
    output += data["materialchunk"]
    return output
    
def decode_MaterialLayerChunk_V4(content):
    output = {}
    output["materiallayerchunk"] = content
    return output

def encode_MaterialLayerChunk_V4(data):
    output = b""
    output += data["materiallayerchunk"]
    return output
    
def decode_MeshChunk_V3(content):
    output = {}
    output["mesh"] = content
    return output

def encode_MeshChunk_V3(data):
    output = b""
    output += data["mesh"]
    return output
    
def decode_SkinningInfoChunk_V1(content):
    output = {}
    output["skinninginfo"] = content
    return output

def encode_SkinningInfoChunk_V1(data):
    output = b""
    output += data["skinninginfo"]
    return output
    
def decode_chunk(content, chunk_type, chunk_version):
    if chunk_type == ChunkType.MotionPart.name and chunk_version == 3:
        return decode_MotionPartChunk_V3(content)
    elif chunk_type == ChunkType.Animation.name and chunk_version == 1:
        return decode_AnimationChunk_V1(content)
    elif chunk_type == ChunkType.Node.name and chunk_version == 3:
        return decode_NodeChunk_V3(content)
    elif chunk_type == ChunkType.Material.name and chunk_version == 5:
        return decode_MaterialChunk_V5(content)
    elif chunk_type == ChunkType.MaterialLayer.name and chunk_version == 4:
        return decode_MaterialLayerChunk_V4(content)
    elif chunk_type == ChunkType.Mesh.name and chunk_version == 3:
        return decode_MeshChunk_V3(content)
    elif chunk_type == ChunkType.SkinningInfo.name and chunk_version == 1:
        return decode_SkinningInfoChunk_V1(content)
    else:
        raise Exception(f"Unknown chunk id {chunk_type} with version {chunk_version}")

def encode_chunk(content, chunk_type, chunk_version):
    if chunk_type == ChunkType.MotionPart.name and chunk_version == 3:
        return encode_MotionPartChunk_V3(content)
    elif chunk_type == ChunkType.Animation.name and chunk_version == 1:
        return encode_AnimationChunk_V1(content)
    elif chunk_type == ChunkType.Node.name and chunk_version == 3:
        return encode_NodeChunk_V3(content)
    elif chunk_type == ChunkType.Material.name and chunk_version == 5:
        return encode_MaterialChunk_V5(content)
    elif chunk_type == ChunkType.MaterialLayer.name and chunk_version == 4:
        return encode_MaterialLayerChunk_V4(content)
    elif chunk_type == ChunkType.Mesh.name and chunk_version == 3:
        return encode_MeshChunk_V3(content)
    elif chunk_type == ChunkType.SkinningInfo.name and chunk_version == 1:
        return encode_SkinningInfoChunk_V1(content)
    else:
        raise Exception(f"Unknown chunk id {chunk_type} with version {chunk_version}")
    
def decode_fxa(content):
    output = {}

    assert content[:4] == b"FXA "
    output["FXA_bytes"] = content[4:26]
    d = content[26:]

    strlen, d = unpack_uint32(d)
    output["fxa_str1"], d = unpack_str(d, strlen)
    strlen, d = unpack_uint32(d)
    output["fxa_str2"], d = unpack_str(d, strlen)
    strlen, d = unpack_uint32(d)
    output["fxa_str3"], d = unpack_str(d, strlen)

    src = d
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

def encode_fxa(data):
    output = b"FXA "
    output += struct.pack('<b', data["FXA_byte1"])
    output += struct.pack('<b', data["FXA_byte2"])
    output += struct.pack('<b', data["FXA_byte3"])

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
    # output["content_int1"], data = unpack_uint32(data)
    # output["content_pad2"], data = unpack_bytes(data, 2)
    # output["content_string1"], data = unpack_str(data, 4)
    # output["content_pad7"], data = unpack_bytes(data, 20)
    # output["content_is_some_kind_of_other_format"], data = unpack_uint16(data)

    # if output["content_is_some_kind_of_other_format"] != 0:
    #     output["content_extra_int1"], data = unpack_uint32(data)
    #     output["content_extra_int2"], data = unpack_uint32(data)

    output["content_pad_front"], data = unpack_bytes(data, 60)

    fxa_filesize, data = unpack_uint32(data)
    fxa_content = data[:fxa_filesize]

    output["content_unparsed_rest"] = data[fxa_filesize:]

    assert fxa_filesize == len(fxa_content)
    output["fxa_file"] = decode_fxa(fxa_content)

    return output

def encode_file_content(content):
    output = b""

    output += pack_bytes(content["content_pad_front"])
    # output += pack_uint32(content["content_int1"])
    # output += pack_bytes(content["content_pad2"])
    # output += pack_str(content["content_string1"])
    # output += pack_bytes(content["content_pad7"])
    # output += pack_uint16(content["content_is_some_kind_of_other_format"])

    # if content["content_is_some_kind_of_other_format"] != 0:
    #     output += pack_uint32(content["content_extra_int1"])
    #     output += pack_uint32(content["content_extra_int2"])

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
