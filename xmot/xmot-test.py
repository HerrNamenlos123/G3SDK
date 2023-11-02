import xmot
import os
import io

os.system("cls")

# def write_file(self, filename):
#     with io.open(filename, "wb") as f:
#         f.write(self.stream)

# xmot_file = "dragon2/Dragon_Stand_None_Cast_P0_Cast_Raise_N_Fwd_00_%_00_P0_0.xmot"
xmot_file = "Hero_Parade_None_1H_P0_Ambient_Loop_N_Fwd_00_%_00_P0_0.xmot"
# xmot_file = "Hero_Parade_None_Fist_P0_Move_Walk_N_Fwd_00_%_00_P0_350.xmot"

x = xmot.XMot(xmot_file)
data = x.decode()

print(data)

result = x.encode(data)





outdir = "C:\Program Files (x86)\Steam\steamapps\common\Gothic 3\Data\_compiledAnimation"
out_files = [
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_00_%_02_P0_0.xmot",
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_01_%_00_P0_0.xmot",
    "Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_02_%_00_P0_0.xmot",
]

for file in out_files:
    with io.open(os.path.join(outdir, file), "wb") as f:
        f.write(result)
