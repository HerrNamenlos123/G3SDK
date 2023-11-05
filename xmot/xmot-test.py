import xmot
import os
import io

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
# xmot_file = "Hero_Parade_1H_1H_P1_PierceAttack_Hit_N_Fwd_00_%_00_P1_50_F.xmot"
# xmot_file = "Hero_Parade_1H_1H_P0_PierceAttack_Raise_N_Fwd_00_%_00_P0_0_F.xmot"
# xmot_file = "Hero_Stand_None_Tool_P0_SawLog_Ambient_N_Fwd_00_%_00_P0_0.xmot"
xmot_file = "Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot"

x = xmot.XMot(xmot_file)
data = x.decode()

# print(f"{byte_at(x.original_file_content, 0x21)} == 0: Do mallocs")
# print(f"{byte_at(x.original_file_content, 0x1f)} != 0: Print stuff")
# print(f"{byte_at(x.original_file_content, 0x0c)} = loop length")
# print(f"{x.original_file_content[0x14:0x18]} = first int")


# print(x.original_file_content)
print(data)

result = x.encode(data)

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

output("Hero_Stand_None_Tool_P0_SawLog_Loop_N_Fwd_00_%_00_P0_0.xmot")
# output("")
