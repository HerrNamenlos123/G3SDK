from binaryfile import BinaryFileBuilder, Quat, Vec3
from filetime import datetime, to_datetime, to_winfiletime
from chunks import Chunk, create_chunk_processor
from typing import Optional, Any

GENOMFLE_STR = "GENOMFLE"
GENOMFLE_VERSION = 1
DEADBEEF_BYTES = b"\xef\xbe\xad\xde"

class XAct:
    FILE_VERSION_CONSTANT = 54

    class LookAtContraint():
        def __init__(self) -> None:
            self.strtbl_index: int = 0
            self.interpolation_speed: float = 0
            self.min_constraints: Vec3 = (0, 0, 0)
            self.max_constraints: Vec3 = (0, 0, 0)

    class AmbientOcclusion():
        def __init(self) -> None:
            self.num_per_lod_vertices: int = 0
            self.per_lod_vertices: list[int] = []

    class Model():
        def __init__(self) -> None:
            self.__tmp_materials: list[Any] = []

        def build_material(self, stringtable: list[str]) -> None:
            pass

    def __init__(self) -> None:
        self.resource_size: int = 0
        self.resource_priority: float = 0
        self.native_file_time: datetime = datetime.min
        self.native_file_size: int = 0
        self.unk_file_time: Optional[datetime] = None
        self.look_at_constraints: list[XAct.LookAtContraint] = [ ]
        self.model: XAct.Model = XAct.Model()
        self.lods: list[XAct.Model] = []

    def decode(self, data: bytes) -> None:
        file = BinaryFileBuilder(data)
        assert file.get_str(8) == GENOMFLE_STR
        assert file.get_uint16() == GENOMFLE_VERSION
        tail_offset = file.get_uint32()

        file_version = file.get_uint16()
        assert file_version == self.FILE_VERSION_CONSTANT
        self.resource_size = file.get_uint32()
        self.resource_priority = file.get_float()
        self.native_file_time = to_datetime(file.get_uint64())
        self.native_file_size = file.get_uint32()

        self.boundary_min = file.get_vec3()
        self.boundary_max = file.get_vec3()
        num_constraints = file.get_uint32()
        self.look_at_constraints = []
        for i in range(num_constraints):
            c = XAct.LookAtContraint()
            c.strtbl_index = file.get_uint16()
            c.interpolation_speed = file.get_float()
            c.min_constraints = file.get_vec3()
            c.max_constraints = file.get_vec3()
            self.look_at_constraints.append(c)
            
        num_lods = file.get_uint32()
        self.lods = []
        for i in range(num_lods):
            self.look_at_constraints.append(self.__decode_model(file))

        self.model = self.__decode_model(file)
        
        deadbeef = file.get_bytes(4)
        assert deadbeef == DEADBEEF_BYTES

        strtable_present = file.get_bool()
        stringtable: list[str] = []
        for i in range(file.get_uint32()):
            stringtable.append(file.get_str(file.get_uint16()))

        for m in self.lods:
            m.build_material(stringtable)
        self.model.build_material(stringtable)

    def encode(self) -> bytes:
        file = BinaryFileBuilder()
        file.put_str(GENOMFLE_STR)
        file.put_uint16(GENOMFLE_VERSION)
        file.put_uint32(0) # tail_offset: Overwrite later

        file.put_uint16(self.FILE_VERSION_CONSTANT)
        file.put_uint32(self.resource_size)
        file.put_float(self.resource_priority)
        file.put_uint64(to_winfiletime(self.native_file_time))
        file.put_uint32(self.native_file_size)
        if self.unk_file_time:
            file.put_uint64(to_winfiletime(self.unk_file_time))
        else:
            file.put_uint64(to_winfiletime(datetime.min))

        file.put_uint16(len(self.frameeffects))
        final_stringtable: list[str] = []
        for i in range(len(self.frameeffects)):
            final_stringtable.append(self.frameeffects[i].name)
            file.put_uint16(self.frameeffects[i].framenum)
            file.put_uint16(i)

        emfx_size_location = file.location
        file.put_uint32(0) # emfx2_motion_length, overwrite later
        emfx2_motion_start = file.location
        file.put_str("LMA ")
        file.put_uint8(1)
        file.put_uint8(1)
        file.put_uint8(0)

        # Now encode chunk after chunk (Main payload)
        for i in range(len(self.chunks)):
            file.put_bytes(self.chunks[i].encode())

        file.insert_uint32(self.TAILOFFSET_INDEX, file.location)
        file.insert_uint32(emfx_size_location, file.location - emfx2_motion_start)
        file.put_bytes(DEADBEEF_BYTES)
        file.put_bool(True)
        
        file.put_uint32(len(final_stringtable))
        for s in final_stringtable:
            file.put_uint16(len(s))
            file.put_str(s)

        return file.binary_stream
    
    def __decode_model(self, file: BinaryFileBuilder) -> Model:
        m = XAct.Model()
        magic1 = file.get_uint32()
        file_version = file.get_uint16()
        size = file.get_uint32()
        magic2 = file.get_uint32()
        
        high_version = file.get_uint8()
        low_version = file.get_uint8()
        assert high_version == 1
        assert low_version == 1

        chunks = file.get_bytes(size - 6)
        # while file.location < tail_offset:
        #     processor_id = file.get_uint32()
        #     chunk_size = file.get_uint32()
        #     processor_version = file.get_uint32()
        #     chunk_content = file.get_bytes(chunk_size)
        #     processor = create_chunk_processor(processor_id, processor_version)
        #     processor.decode(chunk_content)
        #     self.chunks.append(processor)

        num_materials = file.get_uint32()
        __tmp_materials = []
        for i in range(num_materials):
            lod_index = file.get_uint16()
            mat_index = file.get_uint16()
            name_strtab_index = file.get_uint16()
            __tmp_materials.append((lod_index, mat_index, name_strtab_index))

        reserved = file.get_uint8()
        assert reserved == 1

        num_lods = file.get_uint32()
        ambient_occlusion = []
        for i in range(num_lods):
            ao = XAct.AmbientOcclusion()
            reserved = file.get_uint8()
            assert reserved == 1
            ao.num_per_lod_vertices = file.get_uint32()
            ao.per_lod_vertices = []
            for i in range(ao.num_per_lod_vertices):
                ao.per_lod_vertices.append(file.get_uint32())
            ambient_occlusion.append(ao)

        tangent_vertices = []
        for i in range(num_lods):
            raw_tangent_vertices = file.get_bytes(ambient_occlusion[i].num_per_lod_vertices * 12)
            f = BinaryFileBuilder(raw_tangent_vertices)
            while len(f.data()) > 0:
                tangent_vertices.append(f.get_vec3())

        return m

with open("../G3_Hero_Body_Player.xact", "rb") as f:
    xact = XAct()
    xact.decode(f.read())
    print(xact)