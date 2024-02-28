import xact
import os
import io
import json
import random

os.system("cls")

xmot_file = "G3_Hero_Body_Player.xact"

with io.open(xmot_file, "rb") as f:
    data = xact.decode(f.read())

with io.open("xact.json", "w") as f:
    f.write(json.dumps(data, indent=4, cls=xact.XActEncoder))
