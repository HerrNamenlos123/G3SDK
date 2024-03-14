from abc import ABC, abstractmethod
from .binaryfile import BinaryFileBuilder, Quat, Vec3
from typing import List, Any

class Chunk(ABC):
    @abstractmethod
    def get_id(self) -> int:
        raise NotImplementedError()
    
    @abstractmethod
    def get_version(self) -> int:
        raise NotImplementedError()
    
    @abstractmethod
    def decode(self, data: bytes):
        raise NotImplementedError()
    
    @abstractmethod
    def encode(self) -> bytes:
        raise NotImplementedError()
    
class MotionPartChunkV3(Chunk):
    ID = 1
    CORE_CHUNK_SIZE = 84
    def get_id(self) -> int:
        return self.ID

    def get_version(self) -> int:
        return 3

    def decode(self, data: bytes):
        file = BinaryFileBuilder(data)
        self.pose_location = file.get_vec3()
        self.pose_rotation = file.get_quat()
        self.pose_scale = file.get_vec3()
        self.bindpose_location = file.get_vec3()
        self.bindpose_rotation = file.get_quat()
        self.bindpose_scale = file.get_vec3()
        self.bone = file.get_str(file.get_uint32())

    def encode(self) -> bytes:
        file = BinaryFileBuilder()
        file.put_uint32(self.get_id())
        file.put_uint32(self.CORE_CHUNK_SIZE + len(self.bone))
        file.put_uint32(self.get_version())
        file.put_vec3(self.pose_location)
        file.put_quat(self.pose_rotation)
        file.put_vec3(self.pose_scale)
        file.put_vec3(self.bindpose_location)
        file.put_quat(self.bindpose_rotation)
        file.put_vec3(self.bindpose_scale)
        file.put_uint32(len(self.bone))
        file.put_str(self.bone)
        return file.data()

class AnimationChunkV1(Chunk):
    ID = 2
    CORE_CHUNK_SIZE = 8

    class LocationKeyframe:
        def __init__(self) -> None:
            self.time: float = 0
            self.location: Vec3 = (0,0,0)

    class RotationKeyframe:
        def __init__(self) -> None:
            self.time: float = 0
            self.rotation: Quat = (0,0,0,1)

    def __init__(self) -> None:
        self.motion: str = ""
        self.reserved: int = 0
        self.keyframes: List[Any] = []

    def get_id(self) -> int:
        return self.ID

    def get_version(self) -> int:
        return 1

    def decode(self, data: bytes):
        file = BinaryFileBuilder(data)
        framecount = file.get_uint32()
        interpolation = file.get_str(1)
        assert interpolation == 'L'
        self.motion = file.get_str(1)
        self.reserved = file.get_uint16()
        for i in range(framecount):
            match (self.motion):
                case 'P':
                    lframe = self.LocationKeyframe()
                    lframe.time = file.get_float()
                    lframe.location = file.get_vec3()
                    self.keyframes.append(lframe)
                case 'R':
                    rframe = self.RotationKeyframe()
                    rframe.time = file.get_float()
                    rframe.rotation = file.get_quat()
                    self.keyframes.append(rframe)
                case 'B':
                    raise ImportError("Failed to import Animation chunk: Bezier motion is not supported yet!")
                case _:
                    raise ImportError(f"Failed to import Animation chunk: Unknown motion type {self.motion}")
                
    def encode(self) -> bytes:
        file = BinaryFileBuilder()
        file.put_uint32(self.get_id())
        file.put_uint32(self.CORE_CHUNK_SIZE + len(self.keyframes) * 4 * (4 if self.motion == 'P' else 5))
        file.put_uint32(self.get_version())
        file.put_uint32(len(self.keyframes))
        file.put_str('L')
        file.put_str(self.motion)
        file.put_uint16(self.reserved)
        for frame in self.keyframes:
            match (self.motion):
                case 'P':
                    file.put_float(frame.time)
                    file.put_vec3(frame.location)
                case 'R':
                    file.put_float(frame.time)
                    file.put_quat(frame.rotation)
                case 'B':
                    raise ImportError("Failed to export Animation chunk: Bezier motion is not supported yet!")
                case _:
                    raise ImportError(f"Failed to export Animation chunk: Unknown motion type {self.motion}")
        return file.data()
    
def create_chunk_processor(processor_id: int, processor_version: int) -> Chunk:
    match((processor_id, processor_version)):
        case (2, 1): return AnimationChunkV1()
        case (1, 3): return MotionPartChunkV3()
        case _:
            raise KeyError(f"No chunk processor combination of {(processor_id, processor_version)} is supported")