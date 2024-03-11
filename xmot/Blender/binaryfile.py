from typing import Optional, Tuple
import struct

Vec3 = Tuple[int,int,int]
Quat = Tuple[int,int,int,int]

class BinaryFileBuilder:
    def __init__(self, binary_stream: Optional[bytearray|bytes] = None):
        if binary_stream is None:
            self.binary_stream = bytearray()
        else:
            self.binary_stream = bytearray(binary_stream)
        self.location = 0

    def data(self):
        return self.binary_stream

    def get_bytes(self, num_of_bytes: int) -> bytes:
        if len(self.binary_stream) < num_of_bytes:
            raise ValueError("Not enough bytes in the binary stream to extract " + str(num_of_bytes) + " bytes")
        
        value = self.binary_stream[:num_of_bytes]
        self.binary_stream = self.binary_stream[num_of_bytes:]
        self.location += num_of_bytes
        return value

    def put_bytes(self, bytes: bytes) -> None:
        self.binary_stream += bytes
        self.location += len(bytes)

    def insert_uint32(self, location: int, value: int) -> None:
        type = '<I'
        size = struct.calcsize(type)
        self.binary_stream[location:location+size] = struct.pack(type, value)

    def get_uint8(self) -> int:
        type = '<B'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_uint16(self) -> int:
        type = '<H'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_uint32(self) -> int:
        type = '<I'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_uint64(self) -> int:
        type = '<Q'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_float(self) -> int:
        type = '<f'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_bool(self) -> bool:
        type = '<B'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))[0]

    def get_vec3(self) -> Vec3:
        type = '<fff'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))

    def get_quat(self) -> Quat:
        type = '<ffff'
        return struct.unpack(type, self.get_bytes(struct.calcsize(type)))
    
    def get_str(self, length: int) -> str:
        return self.get_bytes(length).decode("windows-1252")
    
    def put_str(self, value: str) -> None:
        self.put_bytes(value.encode("windows-1252"))
        
    def put_uint8(self, value: int) -> None:
        self.put_bytes(struct.pack("<B", value))
        
    def put_uint16(self, value: int) -> None:
        self.put_bytes(struct.pack("<H", value))
        
    def put_uint32(self, value: int) -> None:
        self.put_bytes(struct.pack("<I", value))
        
    def put_uint64(self, value: int) -> None:
        self.put_bytes(struct.pack("<Q", value))
        
    def put_float(self, value: float) -> None:
        self.put_bytes(struct.pack("<f", value))
        
    def put_bool(self, value: bool) -> None:
        self.put_bytes(struct.pack("<B", value))
        
    def put_vec3(self, value: Vec3) -> None:
        self.put_bytes(struct.pack("<fff", *value))
        
    def put_quat(self, value: Quat) -> None:
        self.put_bytes(struct.pack("<ffff", *value))
