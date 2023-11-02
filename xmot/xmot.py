import io
import os
import struct
from enum import Enum

os.system("cls")

# See: https://forum.xentax.com/viewtopic.php?t=9369

# xmot = "dragon2/Dragon_Stand_None_Cast_P0_Cast_Raise_N_Fwd_00_%_00_P0_0.xmot"
xmot = "Hero_Parade_None_1H_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
# xmot = "Hero_Parade_None_Fist_P0_Move_Walk_N_Fwd_00_%_00_P0_350.xmot"

outdir = "C:\Program Files (x86)\Steam\steamapps\common\Gothic 3\Data\_compiledAnimation"
out = [
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_00_%_02_P0_0.xmot",
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_01_%_00_P0_0.xmot",
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_02_%_00_P0_0.xmot",
]

class SomeMotionTypeEnum(Enum):
    THREE_VECTORS_TYPE_1 = 1
    FRAME_NUM_TYPE_2 = 2

class FileAttribs:
    def __init(self):
        pass

    def __str__(self):
        return '\n'.join("%s: %s" % item for item in vars(self).items())

# This is a very sophisticated architecture:
# The operate function defines which datatype comes when. The key is
# that this function can encode and decode at the same time. This means,
# you write the definitions once (which datatype, how many bytes, which variable name) (THE VARIABLE NAMES MUST NOT COLLIDE!!!!)
# And then the file is decoded, modified and re-encoded using the same function.
# Additionally, the validity of the algorithm is always checked and you should
# get an error if variable names collided, which will be noticed by the re-encoded file
# not being the same as the original file.

class FileFormat:
    def __init__(self):
        self.decode = True     # True for reading the file, False for writing
        
        self.raw_file = b""
        self.stream = b""

        # This object contains all parameters of the file
        self.attr = FileAttribs()

    def operate(self):
        if self.decode:
            self.stream = self.raw_file
        else:
            self.stream = b""

        # Start operating on the encoding

        self.def_string(8, "genom_header")

        # self.def_padding(0x1C0 - 24, "front_padding")
        # self.def_padding(0x1BC - 24, "front_padding")
        self.def_padding(49, "front_padding")

        self.def_obj("obj1")
        self.def_obj("obj2")
        self.def_obj("obj3")
        self.def_obj("obj4")
        self.def_obj("obj5")

        self.def_obj("obj6")

        self.def_obj("obj7")
        self.def_obj("obj8")
        self.def_obj("obj9")

        # self.def_obj("ik1")

        # self.def_obj("ik2")
        
        # self.def_obj("g1")
        # self.def_obj("g1_sub1")

        # self.def_float("int1")

        # self.def_int("toe_label_length")
        # self.def_string(self.attr.toe_label_length, "toe_label")
        # self.def_enum_int(SomeMotionTypeEnum, "toe_type")
        # self.def_int("toe_int2")
        # self.def_int("toe_int3")
        # self.def_float_vector(3, "toe_vector1")
        # self.def_float_vector(3, "toe_vector2")
        # self.def_float_vector(4, "toe_vector3")
        # self.def_int("tor_int4")
        # self.def_int("tor_int5")
        # self.def_int("toe_int6")
        # self.def_padding(4, "toe_2_padding")
        # self.def_int("toe_int7")
        # self.def_int("toe_int8")

        self.def_padding(len(self.stream), "back_padding")

    def __str__(self):
        return self.attr.__str__()
    
    def def_object_type(self, member_name):
        return self.def_enum_int(SomeMotionTypeEnum, f"{member_name}_type")
    
    def modify(self):
        # for i in range(len(self.attr.frame_matrix)):
        #     for j in range(len(self.attr.frame_matrix[i])):
        #         self.attr.frame_matrix[i][j] = 0.0

        # for i in range(len(self.attr.frame_matrix_b)):
        #     for j in range(len(self.attr.frame_matrix_b[i])):
        #         self.attr.frame_matrix_b[i][j] = 0.0
        pass

    def def_label(self, member_name):
        self.def_int(f"{member_name}_label_length")
        self.def_string(getattr(self.attr, f"{member_name}_label_length"), f"{member_name}_label")

    def def_three_vector_object(self, member_name):
        self.def_int(f"{member_name}_n5")
        self.def_int(f"{member_name}_n6")
        self.def_float_vector(3, f"{member_name}_vec1")
        self.def_float_vector(3, f"{member_name}_vec2")
        self.def_float_vector(4, f"{member_name}_vec3")
        self.def_int(f"{member_name}_n10")
        self.def_padding(4, f"{member_name}_pad1")
        self.def_int(f"{member_name}_int1")
        self.def_padding(8, f"{member_name}_pad2")
        self.def_int(f"{member_name}_int2")
        self.def_padding(16, f"{member_name}_pad3")
        self.def_label(member_name)

    def def_obj(self, member_name):
        setattr(self.attr, f"{member_name}_beginning", "_______________________BEGIN___________________________")
        type = self.def_object_type(member_name)
        if type == SomeMotionTypeEnum.THREE_VECTORS_TYPE_1:
            self.def_three_vector_object(member_name)
        elif type == SomeMotionTypeEnum.FRAME_NUM_TYPE_2:
            self.def_int(f"{member_name}_val2")
            self.def_int(f"{member_name}_val3")
            self.def_int(f"{member_name}_frame_count")
            self.def_string(2, f"{member_name}_ll")
            self.def_padding(2, f"{member_name}_ll_padding")
            self.def_float_matrix(getattr(self.attr, f"{member_name}_frame_count"), 4, f"{member_name}_frame_matrix")

            if (getattr(self.attr, f"{member_name}_ll") == b"LR" ):
                self.def_float_matrix(16, 4, f"{member_name}_second_matrix")
                self.def_padding(40, f"{member_name}_second_padding")
                self.def_label(member_name)

            # self.def_obj(f"{member_name}_sub1")
            # self.def_obj(f"{member_name}_sub2")
            
            #self.def_padding(292, "g1_post_padding")
            #self.def_label(member_name)
        else:
            raise Exception(f"Unknown type {type}")
        
        setattr(self.attr, f"{member_name}____ending", "_______________________END___________________________")

    def def_padding(self, bytes, member_name):
        if self.decode:                                 # Remove and remember said number of bytes
            setattr(self.attr, member_name, self.stream[:bytes])
            self.stream = self.stream[bytes:]
        else:                                           # Put them back into place
            self.stream = self.stream + getattr(self.attr, member_name)
            
    def def_string(self, num_characters, member_name):
        if self.decode:                                 # Read the string
            setattr(self.attr, member_name, self.stream[:num_characters])
            self.stream = self.stream[num_characters:]
        else:                                           # Write the string
            self.stream = self.stream + getattr(self.attr, member_name)

    def def_int(self, member_name):
        if self.decode:                                 # Read the int
            setattr(self.attr, member_name, struct.unpack('<i', self.stream[:4])[0])
            self.stream = self.stream[4:]
        else:                                           # Write the int
            self.stream = self.stream + struct.pack('<i', getattr(self.attr, member_name))

    def def_enum_int(self, enum, member_name):
        if self.decode:                                 # Read the enum int
            int = struct.unpack('<i', self.stream[:4])[0]
            setattr(self.attr, member_name, enum(int).name)
            self.stream = self.stream[4:]
            return enum(int)
        else:                                           # Write the enum int
            str = getattr(self.attr, member_name)
            self.stream = self.stream + struct.pack('<i', enum[str].value)
            return enum[str]

    def def_float(self, member_name):
        if self.decode:                                 # Read the float
            setattr(self.attr, member_name, struct.unpack('<f', self.stream[:4])[0])
            self.stream = self.stream[4:]
        else:                                           # Write the float
            self.stream = self.stream + struct.pack('<f', getattr(self.attr, member_name))

    def def_float_matrix(self, frames, valuesPerFrame, member_name):
        if self.decode:                                 # Read the float matrix
            matrix = []
            for i in range(0, frames):
                frame = []
                for j in range(0, valuesPerFrame):
                    val, self.stream = struct.unpack('<f', self.stream[:4])[0], self.stream[4:]
                    frame.append(val)
                matrix.append(frame)
            setattr(self.attr, member_name, matrix)
        else:                                           # Write the float matrix
            for i in range(0, frames):
                for j in range(0, valuesPerFrame):
                    self.stream = self.stream + struct.pack('<f', getattr(self.attr, member_name)[i][j])

    def def_float_vector(self, dimensions, member_name):
        if self.decode:                                 # Read the float vector
            vector = []
            for i in range(0, dimensions):
                val, self.stream = struct.unpack('<f', self.stream[:4])[0], self.stream[4:]
                vector.append(val)
            setattr(self.attr, member_name, vector)
        else:                                           # Write the float vector
            for i in range(0, dimensions):
                self.stream = self.stream + struct.pack('<f', getattr(self.attr, member_name)[i])

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

with io.open(xmot, "rb") as f:

    file = FileFormat()
    file.raw_file = f.read()

    file.decode = True
    file.operate()          # Decode into the class

    file.decode = False
    file.operate()          # Encode back to the file

    assert file.raw_file == file.stream     # And always assert that the conversion is lossless in both directions

    file.modify()           # Not do the real work
    
    file.operate()          # Encode back to the file

    print(file)

    for filename in out:
        file.write_file(os.path.join(outdir, filename))

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
