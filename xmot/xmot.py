import io
import os
import json
import struct
from enum import Enum

os.system("cls")

# See: https://forum.xentax.com/viewtopic.php?t=9369

# xmot_file = "dragon2/Dragon_Stand_None_Cast_P0_Cast_Raise_N_Fwd_00_%_00_P0_0.xmot"
# xmot_file = "Hero_Parade_None_1H_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
xmot_file = "Hero_Parade_None_Fist_P0_Move_Walk_N_Fwd_00_%_00_P0_350.xmot"

outdir = "C:\Program Files (x86)\Steam\steamapps\common\Gothic 3\Data\_compiledAnimation"
out = [
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_00_%_02_P0_0.xmot",
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_01_%_00_P0_0.xmot",
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_02_%_00_P0_0.xmot",
]

class SomeMotionTypeEnum(Enum):
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
# that this function can encode and decode at the same time. This means,
# you write the definitions once (which datatype, how many bytes, which variable name) (THE VARIABLE NAMES MUST NOT COLLIDE!!!!)
# And then the file is decoded, modified and re-encoded using the same function.
# Additionally, the validity of the algorithm is always checked and you should
# get an error if variable names collided, which will be noticed by the re-encoded file
# not being the same as the original file.

class XMot:
    def __init__(self):
        self.decode = True     # True for reading the file, False for writing
        
        self.raw_file = b""
        self.stream = b""

        # This object contains all parameters of the file
        self.root = Asset()
        self.root.assets = []

    def operate(self):
        if self.decode:
            self.stream = self.raw_file
        else:
            self.stream = b""

        # Start operating on the encoding

        self.def_string(self.root, "genom_header", 8)
        self.def_padding(self.root, "front_padding", 49)

        if self.decode:
            i = 1
            while True:
                self.root.assets.append(Asset())
                type = self.def_asset(self.root.assets[-1])
                if type == SomeMotionTypeEnum.DEADBEEF:  # Check if we reached the end
                    self.root.assets.pop()
                    break
                i += 1
        else:
            for asset in self.root.assets:
                self.def_asset(asset)

        self.def_enum_int(self.root, "deadbeef", SomeMotionTypeEnum)
        self.def_int(self.root, "deadbeef_int")
        self.def_padding(self.root, "deadbeef_end_padding", 1)

        self.def_padding(self.root, "unparsed_data", len(self.stream))
    
    def modify(self):
        # Modify the file here
        print(self)
        pass

    def __str__(self):
        return json.dumps(self.root, indent=4, cls=AssetEncoder)
    
    def peek_object_type(self, target):
        return self.peek_enum_int(target, "type", SomeMotionTypeEnum)
    
    def def_object_type(self, target):
        return self.def_enum_int(target, "type", SomeMotionTypeEnum)

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
        if object_type == SomeMotionTypeEnum.ANIMATION_VECTORS:
            self.def_object_type(target)
            self.def_three_vector_asset(target)
        elif object_type == SomeMotionTypeEnum.ANIMATION_FRAMES:
            self.def_object_type(target)
            self.def_frame_asset(target)
        elif self.decode and object_type == SomeMotionTypeEnum.DEADBEEF: # This deadbeef branch will only be encountered when decoding
            pass
        else:
            raise Exception(f"Unknown type {object_type}")
        
        return object_type

    def def_padding(self, target, member_name, bytes):
        if self.decode:                                 # Remove and remember said number of bytes
            setattr(target, member_name, self.stream[:bytes])
            self.stream = self.stream[bytes:]
        else:                                           # Put them back into place
            self.stream = self.stream + getattr(target, member_name)
            
    def def_string(self, target, member_name, num_characters):
        if self.decode:                                 # Read the string
            setattr(target, member_name, self.stream[:num_characters].decode("utf-8"))
            self.stream = self.stream[num_characters:]
        else:                                           # Write the string
            self.stream = self.stream + getattr(target, member_name).encode("utf-8")

    def def_int(self, target, member_name):
        if self.decode:                                 # Read the int
            setattr(target, member_name, struct.unpack('<i', self.stream[:4])[0])
            self.stream = self.stream[4:]
        else:                                           # Write the int
            self.stream = self.stream + struct.pack('<i', getattr(target, member_name))

    def peek_enum_int(self, target, member_name, enum):
        if self.decode:
            int = struct.unpack('<I', self.stream[:4])[0]
            return enum(int)
        else:
            return enum[getattr(target, member_name)]

    def def_enum_int(self, target, member_name, enum):
        if self.decode:                                 # Read the unsigned enum int
            int = struct.unpack('<I', self.stream[:4])[0]
            setattr(target, member_name, enum(int).name)
            self.stream = self.stream[4:]
            return enum(int)
        else:                                           # Write the unsigned enum int
            string = getattr(target, member_name)
            self.stream = self.stream + struct.pack('<I', enum[string].value)
            return enum[string]

    def def_float(self, target, member_name):
        if self.decode:                                 # Read the float
            setattr(target, member_name, struct.unpack('<f', self.stream[:4])[0])
            self.stream = self.stream[4:]
        else:                                           # Write the float
            self.stream = self.stream + struct.pack('<f', getattr(target, member_name))

    def def_float_matrix(self, target, member_name, frames, valuesPerFrame):
        if self.decode:                                 # Read the float matrix
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
        if self.decode:                                 # Read the float vector
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

    def write_file(self, filename):
        with io.open(filename, "wb") as f:
            f.write(self.stream)

with io.open(xmot_file, "rb") as f:

    xmot = XMot()
    xmot.raw_file = f.read()

    xmot.decode = True
    xmot.operate()          # Decode into the class

    xmot.decode = False
    xmot.operate()          # Encode back to the file

    assert xmot.raw_file == xmot.stream     # And always assert that the conversion is lossless in both directions

    xmot.modify()           # Now do the real work
    
    xmot.operate()          # Encode back to the file

    for filename in out:
        xmot.write_file(os.path.join(outdir, filename))

# dir = "_compiledAnimation"
# for file in os.listdir(dir):
#     # Open file
#     with io.open(os.path.join(dir, file), "rb") as f:
#         data = f.read()

#         # if (data.find(b'!FH_Dragon_Right_Leg_Leg_1_New Layer_NEWIKGoalHelper') == -1):
#         #     continue

#         # if (data.find(b'!FH_Dragon_Left_Leg_Leg_1_New Layer_NEWIKGoalHelper') == -1):
#         #     continue

#         # if (data.find(b'!FH_Dragon_Spine_Spine_1_New Layer_GradientRotation') == -1):
#         #     continue

#         # if (data.find(b'\xAE\x47\xE1\x3E') == -1):
#         #     continue

#         # if (data.find(b'\x8F\xC2\xF5\x3E') == -1):
#         #     continue

#         # if (data.find(b'\xFD\xBE\xC5\xC1') == -1):
#         #     continue

#         # if (data.find(b'\x11\xFD\xC8\xC1') == -1):
#         #     continue

#         # if (data.find(b'\x0A\xD7\x23\x3D') == -1):
#         #     continue

#         if (data.find(b"Layer_GradientRotation") == -1):
#             continue

#         print(f"{file}")
