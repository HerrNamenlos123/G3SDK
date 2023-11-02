import json
import io
import struct
from enum import Enum

# See: https://web.archive.org/web/20230513172524/https://forum.xentax.com/viewtopic.php?t=9369

class AnimationType(Enum):
    ANIMATION_VECTORS = 1
    ANIMATION_FRAMES = 2
    DEADBEEF = 0xdeadbeef

class Asset:
    def __init__(self):
        pass
    
class AssetEncoder(json.JSONEncoder):
    def default(self, o):
        
        if isinstance(o, bytes): # Convert into list of bytes
            return [hex(x) for x in o]
        
        return o.__dict__

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
            self.raw_file = file.read()

        self.stream = b""

        # This object contains all parameters of the file
        self.data = Asset()
        self.data.assets = []
# def do_decode(filename):
#     obj = original.__dict__

#     # Remove all data that is not relevant for editing the file
#     del obj["deadbeef"]

#     return json.dumps(obj, indent=4, cls=AssetEncoder)

# def to_file_encodable_json(original):
#     obj = json.loads(original)

#     # Add all constant data that is only for file encoding
#     obj["deadbeef"] = 0xDEADBEEF

#     return obj


    def decode(self):
        if self.is_decoded:
            raise Exception("You can only decode a file once")
        
        self.do_decode = True
        self.operate()
        self.do_decode = False
        self.operate()
        assert self.raw_file == self.stream     # Always assert that the conversion is lossless in both directions

        # Now remove all data that is not relevant for editing
        data = self.data.__dict__
        # del data.deadbeef

        return json.dumps(data, indent=4, cls=AssetEncoder)
    
    def encode(self, data):
        if not self.is_decoded:
            raise Exception("You must decode a file at least once before encoding it")
        
        # Now load the json string and restore all data relevant for encoding
        self.data = json.loads(data)
        # self.data.deadbeef = 0xDEADBEEF

        print(self.data)
        
        self.do_decode = False
        self.operate()
        return self.stream

    def operate(self):
        if self.do_decode:
            self.stream = self.raw_file
        else:
            self.stream = b""

        # Start operating on the encoding

        self.def_string(self.data, "genom_header", 8)
        self.def_padding(self.data, "front_padding", 49)

        if self.do_decode:
            i = 1
            while True:
                self.data.assets.append(Asset())
                type = self.def_asset(self.data.assets[-1])
                if type == AnimationType.DEADBEEF:  # Check if we reached the end
                    self.data.assets.pop()
                    break
                i += 1
        else:
            for asset in self.data.assets:
                self.def_asset(asset)

        self.def_enum_int(self.data, "deadbeef", AnimationType)
        self.def_int(self.data, "deadbeef_int")
        self.def_padding(self.data, "deadbeef_end_padding", 1)

        self.def_padding(self.data, "unparsed_data", len(self.stream))
        self.is_decoded = True # If it was decoded at least once
    
    def peek_object_type(self, target):
        return self.peek_enum_int(target, "type", AnimationType)
    
    def def_object_type(self, target):
        return self.def_enum_int(target, "type", AnimationType)

    def def_label(self, target):
        self.def_int(target, "label_length")
        self.def_string(target, "label", getattr(target, "label_length"))

    def def_three_vector_asset(self, target):
        self.def_int(target, "n5")
        self.def_int(target, "n6")
        self.def_float_vector(target, "vec1", 3)
        self.def_float_vector(target, "vec2", 3)
        self.def_float_vector(target, "vec3", 4)
        self.def_int(target, "n10")
        self.def_padding(target, "pad1", 4)
        self.def_int(target, "int1")
        self.def_padding(target, "pad2", 8)
        self.def_int(target, "int2")
        self.def_padding(target, "pad3", 16)
        self.def_label(target)

    def def_frame_asset(self, target):
        self.def_int(target, "val2")
        self.def_int(target, "val3")
        self.def_int(target, "frame_count")
        self.def_string(target, "frame_type", 2)
        self.def_padding(target, "ll_padding", 2)
        if (getattr(target, "frame_type") == "LR" ):
            self.def_float_matrix(target, "frames", getattr(target, "frame_count"), 5)
        else:
            self.def_float_matrix(target, "frames", getattr(target, "frame_count"), 4)

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
            setattr(target, member_name, self.stream[:bytes])
            self.stream = self.stream[bytes:]
        else:                                           # Put them back into place
            self.stream = self.stream + getattr(target, member_name)
            
    def def_string(self, target, member_name, num_characters):
        if self.do_decode:                                 # Read the string
            setattr(target, member_name, self.stream[:num_characters].decode("utf-8"))
            self.stream = self.stream[num_characters:]
        else:                                           # Write the string
            self.stream = self.stream + getattr(target, member_name).encode("utf-8")

    def def_int(self, target, member_name):
        if self.do_decode:                                 # Read the int
            setattr(target, member_name, struct.unpack('<i', self.stream[:4])[0])
            self.stream = self.stream[4:]
        else:                                           # Write the int
            self.stream = self.stream + struct.pack('<i', getattr(target, member_name))

    def peek_enum_int(self, target, member_name, enum):
        if self.do_decode:
            int = struct.unpack('<I', self.stream[:4])[0]
            return enum(int)
        else:
            return enum[getattr(target, member_name)]

    def def_enum_int(self, target, member_name, enum):
        if self.do_decode:                                 # Read the unsigned enum int
            int = struct.unpack('<I', self.stream[:4])[0]
            setattr(target, member_name, enum(int).name)
            self.stream = self.stream[4:]
            return enum(int)
        else:                                           # Write the unsigned enum int
            string = getattr(target, member_name)
            self.stream = self.stream + struct.pack('<I', enum[string].value)
            return enum[string]

    def def_float(self, target, member_name):
        if self.do_decode:                                 # Read the float
            setattr(target, member_name, struct.unpack('<f', self.stream[:4])[0])
            self.stream = self.stream[4:]
        else:                                           # Write the float
            self.stream = self.stream + struct.pack('<f', getattr(target, member_name))

    def def_float_matrix(self, target, member_name, frames, valuesPerFrame):
        if self.do_decode:                                 # Read the float matrix
            matrix = []
            for i in range(0, frames):
                frame = []
                for j in range(0, valuesPerFrame):
                    val, self.stream = struct.unpack('<f', self.stream[:4])[0], self.stream[4:]
                    frame.append(val)
                matrix.append(frame)
            setattr(target, member_name, matrix)
        else:                                           # Write the float matrix
            for i in range(0, frames):
                for j in range(0, valuesPerFrame):
                    self.stream = self.stream + struct.pack('<f', getattr(target, member_name)[i][j])

    def def_float_vector(self, target, member_name, dimensions):
        if self.do_decode:                                 # Read the float vector
            vector = []
            for i in range(0, dimensions):
                val, self.stream = struct.unpack('<f', self.stream[:4])[0], self.stream[4:]
                vector.append(val)
            setattr(target, member_name, vector)
        else:                                           # Write the float vector
            for i in range(0, dimensions):
                self.stream = self.stream + struct.pack('<f', getattr(target, member_name)[i])

    def printMatrix(matrix):
        for frame in matrix:
            str = "[ "
            for val in frame:
                str += f"{val:.6f}, "
            str = str[:-2]
            str += " ]"
            print(str)
