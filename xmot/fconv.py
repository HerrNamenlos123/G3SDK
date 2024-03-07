import struct
from typing import Optional


        
file = BinaryFileBuilder(b'\x00\x01\x00\x00')
print(file.uint32())