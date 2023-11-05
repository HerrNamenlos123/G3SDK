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
# Then comes the file content, and then a DEADBEEF value at the end of the file.
# The first 14 bytes (0-13) are the GENOM header
#
# The outermost structure is the eCArchiveFile content described above. It is called "genom_..." here. Inside of that
# is the content of the Archive file, which is prefixed "content_..." here.
#
#  eCWrapper_emfx2Motion::ImportEMFX2Motion seems to be very relevant
#
# The emfx2 file format version (eCWrapper_emfx2Motion::GetVersion) seems to be hard-coded to 1.
#
# Disassembling confirmed that: (global indices) All data indices seem to be offset by one. They are already fixed here:
# - Location 0x21 (33) is checked against being 0
# - Location 0xc  (12) is used as the length of a loop
# - Location 0x14 (20) is used as a starting pointer for the loop and iterated in 4-byte steps

class AnimationType(Enum):
    ANIMATION_VECTORS = 1
    ANIMATION_FRAMES = 2
    DEADBEEF = 0xdeadbeef

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

# This is a very sophisticated architecture:
# The operate function defines which datatype comes when. The key is
# that this function can encode and do_decode at the same time. This means,
# you write the definitions once (which datatype, how many bytes, which variable name) (THE VARIABLE NAMES MUST NOT COLLIDE!!!!)
# And then the file is decoded, modified and re-encoded using the same function.
# Additionally, the validity of the algorithm is always checked and you should
# get an error if variable names collided, which will be noticed by the re-encoded file
# not being the same as the original file.

class XMot:
    def __init__(self, filename):

        self.do_decode = True     # True for decoding, False for encoding
        self.is_decoded = False
        
        with io.open(filename, "rb") as file:
            self.original_file_content = file.read()

        self.stream = b""
        self.data = {}

    def decode(self):
        if self.is_decoded:
            raise Exception("You can only decode a file once")
        
        self.do_decode = True
        self.operate()
        self.do_decode = False
        self.operate()
        assert self.original_file_content == self.stream     # Always assert that the conversion is lossless in both directions

        # Now remove all data that is not relevant for editing
        # del self.data["genom_header"]
        # if "deadbeef" in self.data:
        #     del self.data["deadbeef"]
        # if "deadbeef_int" in self.data:
        #     del self.data["deadbeef_int"]
        # if "deadbeef_end_padding" in self.data:
        #     del self.data["deadbeef_end_padding"]

        return json.dumps(self.data, cls=XMotEncoder, indent=4)
    
    def encode(self, data):
        if not self.is_decoded:
            raise Exception("You must decode a file at least once before encoding it")
        
        # Now load the json string and restore all data relevant for encoding
        self.data = json.loads(data, cls=XMotDecoder)
        # self.data["genom_header"] = "GENOMFLE"
        # self.data["deadbeef"] = AnimationType.DEADBEEF.name
        # self.data["deadbeef_int"] = 1
        # self.data["deadbeef_end_padding"] = b"\x00"
        
        self.do_decode = False
        self.operate()
        return self.stream

    def operate(self):
        if self.do_decode:
            self.stream = self.original_file_content
        else:
            self.stream = b""

        # Start operating on the encoding

        # Parse the GENOM wrapper
        self.def_string(self.data, "genom_header", 8)
        self.def_ushort(self.data, "genom_version")
        self.def_ulong(self.data, "genom_content_length")

        # Now parse the GENOM content which is the file wrapper
        self.def_ulong(self.data, "content_int1")                
        self.def_padding(self.data, "content_pad2", 2)                                
        self.def_string(self.data, "content_string1", 4)                              
        self.def_padding(self.data, "content_pad7", 20)             
        self.def_ushort(self.data, "content_is_some_kind_of_other_format")      

        # I HAVE NO IDEA WHYYY????
        if self.data["content_is_some_kind_of_other_format"] != 0:
            self.def_ulong(self.data, "content_extra_int1")
            self.def_ulong(self.data, "content_extra_int2")

        self.def_ulong(self.data, "content_verified_offset_from_here_to_deadbeef")
        
        # Verify deadbeef offset
        if self.do_decode:
            offset = self.data["content_verified_offset_from_here_to_deadbeef"]
            deadbeef = self.stream[offset:offset+4]
            assert deadbeef == b"\xef\xbe\xad\xde"

        # Now the LMA file content (This header is checked in CheckLMAHeader())
        self.def_string(self.data, "LMA_string", 4)         # This string is compared one by one in the source code, it must be "LMA "
        self.def_byte(self.data, "LMA_byte1")               # This byte must be 1. This byte is assigned to eCWrapper_emfx2Motion + 0x24
        self.def_byte(self.data, "LMA_byte2")               # This byte is unknown (usually 1). This byte is assigned to eCWrapper_emfx2Motion + 0x28
        self.def_byte(self.data, "LMA_byte3")               # This byte must be 0

        if self.do_decode:
            self.data["assets"] = []
            i = 1
            while True:
                self.data["assets"].append({})
                type = self.def_asset(self.data["assets"][-1])
                if type == AnimationType.DEADBEEF:  # Check if we reached the end
                    self.data["assets"].pop()
                    break
                i += 1
        else:
            for asset in self.data["assets"]:
                self.def_asset(asset)

        self.def_enum_int(self.data, "genom_deadbeef", AnimationType)

        self.def_padding(self.data, "genom_unparsed_data", len(self.stream))
        self.is_decoded = True # If it was decoded at least once
    
    def peek_object_type(self, target):
        return self.peek_enum_int(target, "type", AnimationType)
    
    def def_object_type(self, target):
        return self.def_enum_int(target, "type", AnimationType)

    def def_label(self, target):
        self.def_ulong(target, "label_length")
        self.def_string(target, "label", target["label_length"])

    def def_three_vector_asset(self, target):
        self.def_ulong(target, "n5")
        self.def_ulong(target, "n6")
        self.def_float_vector(target, "vec1", 3)
        self.def_float_vector(target, "vec2", 3)
        self.def_float_vector(target, "vec3", 4)
        self.def_ulong(target, "n10")
        self.def_padding(target, "pad1", 4)
        self.def_ulong(target, "int1")
        self.def_padding(target, "pad2", 8)
        self.def_ulong(target, "int2")
        self.def_padding(target, "pad3", 16)
        self.def_label(target)

    def def_frame_asset(self, target):
        self.def_ulong(target, "val2")
        self.def_ulong(target, "val3")
        self.def_ulong(target, "frame_count")
        self.def_string(target, "frame_type", 2)
        self.def_padding(target, "ll_padding", 2)
        if (target["frame_type"] == "LR" ):
            self.def_float_matrix(target, "frames", target["frame_count"], 5)
        else:
            self.def_float_matrix(target, "frames", target["frame_count"], 4)

    def def_asset(self, target):
        object_type = self.peek_object_type(target)
        if object_type == AnimationType.ANIMATION_VECTORS:
            self.def_object_type(target)
            self.def_three_vector_asset(target)
        elif object_type == AnimationType.ANIMATION_FRAMES:
            self.def_object_type(target)
            self.def_frame_asset(target)
        elif self.do_decode and object_type == AnimationType.DEADBEEF: # This deadbeef branch will only be encountered when decoding
            pass
        else:
            raise Exception(f"Unknown type {object_type}")
        
        return object_type

    def def_padding(self, target, member_name, bytes):
        if self.do_decode:                                 # Remove and remember said number of bytes
            target[member_name] = self.stream[:bytes]
            self.stream = self.stream[bytes:]
        else:                                           # Put them back into place
            self.stream = self.stream + target[member_name]
            
    def def_string(self, target, member_name, num_characters):
        if self.do_decode:                                 # Read the string
            binary = self.stream[:num_characters]
            try:
                target[member_name] = binary.decode("latin-1")
            except:
                raise Exception(f"Could not decode string {member_name}: {binary}")
            self.stream = self.stream[num_characters:]
        else:                                           # Write the string
            self.stream = self.stream + target[member_name].encode("latin-1")

    def def_struct(self, target, member_name, struct_format):
        if self.do_decode:                                 # Read the struct
            target[member_name] = struct.unpack(struct_format, self.stream[:struct.calcsize(struct_format)])[0]
            self.stream = self.stream[struct.calcsize(struct_format):]
        else:                                           # Write the struct
            self.stream = self.stream + struct.pack(struct_format, target[member_name])

    def def_byte(self, target, member_name):
        self.def_struct(target, member_name, '<b')

    def def_ubyte(self, target, member_name):
        self.def_struct(target, member_name, '<B')

    def def_short(self, target, member_name):
        self.def_struct(target, member_name, '<h')

    def def_ushort(self, target, member_name):
        self.def_struct(target, member_name, '<H')

    def def_long(self, target, member_name):
        self.def_struct(target, member_name, '<i')

    def def_ulong(self, target, member_name):
        self.def_struct(target, member_name, '<I')

    def def_float(self, target, member_name):
        self.def_struct(target, member_name, '<f')

    def peek_enum_int(self, target, member_name, enum):
        if self.do_decode:
            int = struct.unpack('<I', self.stream[:4])[0]
            return enum(int)
        else:
            return enum[target[member_name]]

    def def_enum_int(self, target, member_name, enum):
        if self.do_decode:                                 # Read the unsigned enum int
            int = struct.unpack('<I', self.stream[:4])[0]
            target[member_name] = enum(int).name
            self.stream = self.stream[4:]
            return enum(int)
        else:                                           # Write the unsigned enum int
            string = target[member_name]
            self.stream = self.stream + struct.pack('<I', enum[string].value)
            return enum[string]

    def def_float_matrix(self, target, member_name, frames, valuesPerFrame):
        if self.do_decode:                                 # Read the float matrix
            matrix = []
            for i in range(0, frames):
                frame = []
                for j in range(0, valuesPerFrame):
                    val, self.stream = struct.unpack('<f', self.stream[:4])[0], self.stream[4:]
                    frame.append(val)
                matrix.append(frame)
            target[member_name] = matrix
        else:                                           # Write the float matrix
            for i in range(0, frames):
                for j in range(0, valuesPerFrame):
                    self.stream = self.stream + struct.pack('<f', target[member_name][i][j])

    def def_float_vector(self, target, member_name, dimensions):
        if self.do_decode:                                 # Read the float vector
            vector = []
            for i in range(0, dimensions):
                val, self.stream = struct.unpack('<f', self.stream[:4])[0], self.stream[4:]
                vector.append(val)
            target[member_name] = vector
        else:                                           # Write the float vector
            for i in range(0, dimensions):
                self.stream += struct.pack('<f', target[member_name][i])

    def printMatrix(matrix):
        for frame in matrix:
            str = "[ "
            for val in frame:
                str += f"{val:.6f}, "
            str = str[:-2]
            str += " ]"
            print(str)
