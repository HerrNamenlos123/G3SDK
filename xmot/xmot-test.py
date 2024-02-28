import xmot
import os
import io
import json
import random

# Every animation must contain at least one MotionPart Chunk and one Animation Chunk
# with at least two animation keyframes, one of which not being at time 0.
# The Appendix at the end of the file (e.g. ["EFF_Ani_Saw_Pull_01", "EFF_Ani_Saw_Push_01"])
# is for EFFects such as particles and sound effects. It is not tied to the animation itself. 
# For example the particles when sawing a log only appear when this label is added. Otherwise,
# the animation plays without particles and sound. The particles appear roughly half a second
# after the animation started. If the animation is longer, the particles appear after that time
# and only reappear after the animation restarts. If the animation is shorter, they don't appear
# at all.
#
# So: A minimal animation must contain at least one MotionPart for defining "Hero_ROOT" (or the hero will fly off into space ???)
# and one MotionPart and Animation Chunk for one bone with at least two animation frames.
# The longest animation frame defines the total length of the animation.

os.system("cls")

# def write_file(self, filename):
#     with io.open(filename, "wb") as f:
#         f.write(self.stream)

# def int_at(data, offset):
#     return int.from_bytes(data[offset:offset+4], byteorder='little')

# def byte_at(data, offset):
#     return int.from_bytes(data[offset:offset+1], byteorder='little')

# xmot_file = "dragon2/Dragon_Stand_None_Cast_P0_Cast_Raise_N_Fwd_00_%_00_P0_0.xmot"
# xmot_file = "Hero_Parade_None_1H_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
# xmot_file = "Hero_Parade_None_Fist_P0_Move_Walk_N_Fwd_00_%_00_P0_350.xmot"
#xmot_file = "Hero_Parade_1H_1H_P1_PierceAttack_Hit_N_Fwd_00_%_00_P1_50_F.xmot"
# xmot_file = "Hero_Parade_1H_1H_P0_PierceAttack_Raise_N_Fwd_00_%_00_P0_0_F.xmot"
# xmot_file = "Hero_Stand_None_Tool_P0_SawLog_Ambient_N_Fwd_00_%_00_P0_0.xmot"

# xmot_file = "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_02_%_00_P0_0.xmot"
#xmot_file = "Hero_Stand_None_Smoke_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"

xmot_file = "Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot" # < This one works

with io.open(xmot_file, "rb") as f:
    data = xmot.decode(f.read())

# os.system("notepad xmot.json")

# with io.open("xmot.json", "r") as f:
#     data = json.loads(f.read(), cls=xmot.XMotDecoder)

# print(f"{byte_at(x.original_file_content, 0x21)} == 0: Do mallocs")
# print(f"{byte_at(x.original_file_content, 0x1f)} != 0: Print stuff")
# print(f"{byte_at(x.original_file_content, 0x0c)} = loop length")
# print(f"{x.original_file_content[0x14:0x18]} = first int")

# for i in range(len(data["assets"])):
#     if data["assets"][i]["type"] == "ANIMATION_FRAMES":
#         for frame in range(len(data["assets"][i]["frames"])):
#             if data["assets"][i]["frame_type"] == "LR":
#                 data["assets"][i]["frames"][frame] = [ random.random(), random.random(), random.random(), random.random(), random.random() ]
#             else:
#                 data["assets"][i]["frames"][frame] = [ random.random(), random.random(), random.random(), random.random() ]
#             pass

# print(x.original_file_content)
#print(json.dumps(data, indent=4, cls=xmot.XMotEncoder))
# print(x.data["assets"][4])
# x.data["assets"][4]["vec1"] = [ 1, 2, 3 ]
# x.data["assets"][4]["vec2"] = [ 4, 5, 6 ]
# x.data["assets"][4]["vec3"] = [ 7, 8, 9, 10 ]

rem = data["content"]["lma_file"]["chunks"][0]["chunk_content"]["remaining"]
pad = data["content"]["lma_file"]["chunks"][6]["chunk_content"]["ll_padding"]

# for i in range(len(data["content"]["lma_file"]["chunks"])):
#     del data["content"]["lma_file"]["chunks"][-1]

# for chunk in data["content"]["lma_file"]["chunks"]:
#     if chunk["chunk_type"] == "MotionPart":
#         if chunk["chunk_content"]["label"] == "Hero_Spine_Spine_1":
#             chunk["chunk_content"]["position"] = [ 0, 0, 0 ]

# for i in range(len(data["content"]["lma_file"]["chunks"])):
#     if data["content"]["lma_file"]["chunks"][i]["chunk_type"] == "MotionPart":
#         if data["content"]["lma_file"]["chunks"][i]["chunk_content"]["label"] == "Hero_Right_Arm_Arm_1":
#             del data["content"]["lma_file"]["chunks"][i]
#             del data["content"]["lma_file"]["chunks"][i+1]
#             break

# for i in range(len(data["content"]["lma_file"]["chunks"])):
#     if data["content"]["lma_file"]["chunks"][i]["chunk_type"] == "MotionPart":
#         if data["content"]["lma_file"]["chunks"][i]["chunk_content"]["label"] == "Hero_Right_Arm_Arm_2":
#             del data["content"]["lma_file"]["chunks"][i]
#             del data["content"]["lma_file"]["chunks"][i+1]
#             break

# for i in range(len(data["content"]["lma_file"]["chunks"])):
#     chunk = data["content"]["lma_file"]["chunks"][i]
#     if chunk["chunk_type"] == "MotionPart":
#         if chunk["chunk_content"]["label"] == "Hero":
#             chunk["chunk_content"]["position"] = [ 5, 0, 0 ]

# for i in range(len(data["content"]["lma_file"]["chunks"])):
#     chunk = data["content"]["lma_file"]["chunks"][i]
#     if chunk["chunk_type"] == "MotionPart":
#         if chunk["chunk_content"]["label"] == "Hero_ROOT":
#             chunk["chunk_content"]["position"] = [ 5, 0, 0 ]

# for y in range(1, 10):
#     for i in range(len(data["content"]["lma_file"]["chunks"])):
#         chunk = data["content"]["lma_file"]["chunks"][i]
#         if chunk["chunk_type"] == "MotionPart":
#             if "Layer_" in chunk["chunk_content"]["label"]:
#                 del data["content"]["lma_file"]["chunks"][i]
#                 break
    
# Remove all animation frames except the first
# for i in range(len(data["content"]["lma_file"]["chunks"])):
#     chunk = data["content"]["lma_file"]["chunks"][i]
#     if chunk["chunk_type"] == "Animation":
#         while len(chunk["chunk_content"]["keyframes"]) > 2:
#             chunk["chunk_content"]["keyframes"].pop()
#         chunk["chunk_content"]["frame_count"] = 2
#         chunk["chunk_content"]["keyframes"][0]["time"] = 0
#         chunk["chunk_content"]["keyframes"][1]["time"] = 2

# for i in range(len(data["content"]["lma_file"]["chunks"])):
#     if data["content"]["lma_file"]["chunks"][i]["chunk_type"] == "MotionPart":
#         if data["content"]["lma_file"]["chunks"][i]["chunk_content"]["label"] == "Hero_Right_Leg_Leg_1":
#             for f in data["content"]["lma_file"]["chunks"][i+1]["chunk_content"]["keyframes"]:
#                 f["rotation"] = [ 0.914, 0.38, 0.052, -0.13 ]

# for i in range(8):
#     data["content"]["lma_file"]["chunks"].pop(0)

# for y in range(1, 500):
#     for i in range(len(data["content"]["lma_file"]["chunks"])):
#         chunk = data["content"]["lma_file"]["chunks"][i]
#         if chunk["chunk_type"] == "MotionPart":
#             if "Right" in chunk["chunk_content"]["label"] or "Left" in chunk["chunk_content"]["label"]:
#                 if data["content"]["lma_file"]["chunks"][i+2]["chunk_type"] == "Animation":
#                     data["content"]["lma_file"]["chunks"].pop(i+2)
#                 if data["content"]["lma_file"]["chunks"][i+1]["chunk_type"] == "Animation":
#                     data["content"]["lma_file"]["chunks"].pop(i+1)
#                 data["content"]["lma_file"]["chunks"].pop(i)
#                 break

# for i in range(18):
#     data["content"]["lma_file"]["chunks"].pop(0)

# data["content"]["lma_file"]["chunks"].pop(2)
# data["content"]["lma_file"]["chunks"].pop(3)
# data["content"]["lma_file"]["chunks"].pop(2)
    
data["content"]["lma_file"]["chunks"] = []

def appendMotionPart(position, rotation, scale, label):
    data["content"]["lma_file"]["chunks"].append({
                    "chunk_type": "MotionPart",
                    "chunk_version": 3,
                    "chunk_content": {
                        "position": [
                            position[0],
                            position[1],
                            position[2]
                        ],
                        "rotation": [
                            rotation[0],
                            rotation[1],
                            rotation[2],
                            rotation[3],
                        ],
                        "scale": [
                            scale[0],
                            scale[1],
                            scale[2]
                        ],
                        "remaining": rem,
                        "label": label
                    }
                })

appendMotionPart((0, 0, 0), (0, 1, 0, 0), (1, 1, 1), "Hero_ROOT")
# appendMotionPart((0, 1000, 0), (1, 0, 0, 0), (1, 1, 1), "Hero_Spine_Spine_ROOT")
appendMotionPart((0, 0, 0), (0, 1, 0, 0), (1, 1, 1), "Hero_Spine_Spine_1")
#appendMotionPart((0, 0, 0), (0, 0, 0, 1), (1, 1, 1), "Hero_Spine_Spine_1")
appendMotionPart((0, 0, 0), (0, 0, 0, 1), (1, 1, 1), "Hero_Head_Neck_ROOT")
# data["content"]["lma_file"]["chunks"].append({
#     "chunk_type": "Animation",
#     "chunk_version": 1,
#     "chunk_content": {
#         "frame_type": "LP",
#         "frame_count": 2,
#         "ll_padding": pad,
#         "keyframes": [
#             {
#                 "time": 0,
#                 "position": [ 0, 0, 0 ]
#             },
#             {
#                 "time": 5,
#                 "position": [ 100, 100, 100 ]
#             }
#         ]
#     }
# })
data["content"]["lma_file"]["chunks"].append({
    "chunk_type": "Animation",
    "chunk_version": 1,
    "chunk_content": {
        "frame_type": "LR",
        "frame_count": 2,
        "ll_padding": pad,
        "keyframes": [
            {
                "time": 0,
                "rotation": [ 0, 0, 0, 1 ]
            },
            {
                "time": 2,
                "rotation": [ 0, 1, 0, 0 ]
            },
            {
                "time": 4,
                "rotation": [ 0, 0, 0, 1 ]
            },
        ]
    }
})

with io.open("xmot-edit.json", "w") as f:
    f.write(json.dumps(data, indent=4, cls=xmot.XMotEncoder))


result = xmot.encode(data)

def p(file):
    with io.open(file, "rb") as f:
        content = f.read()[:70]
        # Print all bytes with spaces
        print(" ".join([f"{b:02x}" for b in content]))
        # Print all bytes as characters if possible
        print(" ".join([f" {chr(b)}" if b >= 32 and b <= 126 else ".." for b in content]))

# p("dragon2/Dragon_Stand_None_Cast_P0_Cast_Raise_N_Fwd_00_%_00_P0_0.xmot")
# p("Hero_Parade_None_Fist_P0_Move_Walk_N_Fwd_00_%_00_P0_350.xmot")
# p("Hero_Parade_1H_1H_P0_PierceAttack_Raise_N_Fwd_00_%_00_P0_0_F.xmot")
# p("Hero_Parade_1H_1H_P1_PierceAttack_Hit_N_Fwd_00_%_00_P1_50_F.xmot")
# p("Hero_Parade_None_1H_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot")
# p("Hero_Stand_None_Tool_P0_SawLog_Ambient_N_Fwd_00_%_00_P0_0.xmot")
# p("Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot")


outdir = "C:/Program Files (x86)/Steam/steamapps/common/Gothic 3/Data/_compiledAnimation"
# out_files = [
    # "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_00_%_02_P0_0.xmot",
    # "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_01_%_00_P0_0.xmot",
    # "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_02_%_00_P0_0.xmot",
    # "Hero_Parade_1H_1H_P1_PierceAttack_Hit_N_Fwd_00_%_00_P1_50_F.xmot"
# ]

# for file in out_files:
    # with io.open(os.path.join(outdir, file), "wb") as f:
        # f.write(result)

def output(file):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    with io.open(os.path.join(outdir, file), "wb") as f:
        f.write(result)

output("C:/Program Files (x86)/Steam/steamapps/common/Gothic 3/Data/_compiledAnimation/Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot")
# output("Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot")
# output("")
