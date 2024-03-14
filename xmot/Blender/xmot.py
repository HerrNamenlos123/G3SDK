# See: https://web.archive.org/web/20230513172524/https://forum.xentax.com/viewtopic.php?t=9369

# Disassembling the Gothic 3 DLLs shows that there are things like:
# - LMA motion files
# - LMF facial motion files
#
# The beginning of every file is "GENOMFLE". After that, a 16-bit ushort and a 32-bit ulong int follow.
# The 32-bit ulong is the position of the DEADBEEF value, counted from the beginning of the file. DEADBEEF marks
#  the end of the file.
# After the 32-bit ulong directly comes the file content, and then a DEADBEEF value at the end of the file.
# The first 14 bytes (0-13) are the GENOM header
#
# The outermost structure is the eCArchiveFile content described above. Inside of that
# is the content of the Archive file. 
#
#  eCWrapper_emfx2Motion::ImportEMFX2Motion seems to be very relevant
#
# The emfx2 file format version (eCWrapper_emfx2Motion::GetVersion) seems to be hard-coded to 1.
#
# Disassembling confirmed that: (global indices) All data indices seem to be offset by one. They are already fixed here:
# - Location 0x21 (33) is checked against being 0
# - Location 0xc  (12) is used as the length of a loop
# - Location 0x14 (20) is used as a starting pointer for the loop and iterated in 4-byte steps
#
# Frame types: L for Linear
#              B for Bezier
#    and then: P for Position (time + vec3)
#              R for Rotation (time + quaternion vec4)
#
# Important links:
#   https://github.com/o3de/o3de/tree/development/Gems/EMotionFX -> This seems to be our best source for EMotionFX
#   https://github.com/aws/lumberyard
#   https://www.gamezone.com/news/gz_interview_emotion_fx_2_gives_half_life_2_a_face_lift/
#   https://docs.o3de.org/docs/api/gems/emotionfx/class_m_core_1_1_memory_file.html
#    ^^ This seems to be very relevant too, it's the MCore::MemoryFile class used in the EMotionFX engine functions 
#
# Gothic Modding Community:
#   https://gothic-modding-community.github.io/gmc/genome/general_info/object_persistence/
#
# The EMotionFX source code gives us this gem: (SharedFileFormatStructs.h, Importer.cpp -> Importer::ProcessChunk())
#
# struct FileChunk {
#     uint32 m_chunkId;        // the chunk ID
#     uint32 m_sizeInBytes;    // the size in bytes of this chunk (excluding this chunk struct)
#     uint32 m_version;        // the version of the chunk
# }
#
# Every chunk is parsed by something called a ChunkProcessor. The ChunkID specifies which ChunkProcessor to use, 
#  and the version specifies the version of the ChunkProcessor. So if the file format changed they just added a 
#  new ChunkProcessor with the same ID but a new version, and the engine could still load old and new file formats. 
#  Every chunk of a file can use a different ChunkProcessor and version.
#
# Disassembling and decompiling Engine.dll reveiled all Chunk Processors:
#  - AnimationChunkProcessor1               id=2    version=1
#  - ExpressionMotionPartChunkProcessor1    id=11   version=1
#  - ExpressionMotionPartChunkProcessor2    id=11   version=2
#  - FileInformationChunkProcessor1         id=16   version=1
#  - FXMaterialChunkProcessor1              id=13   version=1
#  - FXMaterialChunkProcessor2              id=13   version=2
#  - LimitChunkProcessor1                   id=8    version=1
#  - MaterialChunkProcessor1                id=6    version=1
#  - MaterialChunkProcessor2                id=6    version=2
#  - MaterialChunkProcessor3                id=6    version=3
#  - MaterialChunkProcessor4                id=6    version=4
#  - MaterialChunkProcessor5                id=6    version=5
#  - MaterialLayerChunkProcessor1           id=7    version=1
#  - MaterialLayerChunkProcessor2           id=7    version=2
#  - MaterialLayerChunkProcessor3           id=7    version=3
#  - MaterialLayerChunkProcessor4           id=7    version=4
#  - MeshChunkProcessor1                    id=3    version=1
#  - MeshChunkProcessor2                    id=3    version=2
#  - MeshChunkProcessor3                    id=3    version=3
#  - MeshExpressionPartChunkProcessor1      id=10   version=1
#  - MeshExpressionPartChunkProcessor2      id=10   version=2
#  - MeshExpressionPartChunkProcessor3      id=10   version=3
#  - MotionEventChunkProcessor1             id=15   version=1
#  - MotionEventChunkProcessor2             id=15   version=2
#  - MotionPartChunkProcessor1              id=1    version=1
#  - MotionPartChunkProcessor2              id=1    version=2
#  - NodeChunkProcessor1                    id=0    version=1
#  - NodeChunkProcessor2                    id=0    version=2
#  - NodeChunkProcessor3                    id=0    version=3
#  - PhonemeMotionDataChunkProcessor1       id=12   version=1
#  - PhonemeMotionDataChunkProcessor2       id=12   version=2
#  - PhysicsInfoChunkProcessor1             id=9    version=1
#  - RepositioningNodeChunkProcessor1       id=14   version=1
#  - RepositioningNodeChunkProcessor2       id=14   version=2
#  - SkinningInfoChunkProcessor1            id=4    version=1

from .binaryfile import BinaryFileBuilder, Quat, Vec3
from .filetime import datetime, to_datetime, to_winfiletime
from .chunks import Chunk, create_chunk_processor
from typing import Optional

GENOMFLE_STR = "GENOMFLE"
GENOMFLE_VERSION = 1
DEADBEEF_BYTES = b"\xef\xbe\xad\xde"

class XMot:
    TAILOFFSET_INDEX = 10
    FILE_VERSION_CONSTANT = 5
    class FrameEffect:
        def __init__(self) -> None:
            self.framenum: int = 0
            self.name: str = "" 

    def __init__(self) -> None:
        self.resource_size: int = 0
        self.resource_priority: float = 0
        self.native_file_time: datetime = datetime.min
        self.native_file_size: int = 0
        self.unk_file_time: Optional[datetime] = None
        self.frameeffects: list[XMot.FrameEffect] = []
        self.chunks: list[Chunk] = []

    def decode(self, data: bytes):
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

        if file_version >= 3:
            self.unk_file_time = to_datetime(file.get_uint64())

        frameeffects = []
        if file_version >= 2:
            num_frame_effects = file.get_uint16()
            for i in range(num_frame_effects):
                framenum = file.get_uint16()
                strtbl_index = file.get_uint16()
                frameeffects.append((framenum, strtbl_index))

        emfx2_motion_length = file.get_uint32()
        assert file.get_str(4) == "LMA "
        high_version = file.get_uint8()
        low_version = file.get_uint8()
        is_actor = file.get_uint8()
        assert high_version == 1
        assert low_version == 1
        assert is_actor == 0

        # Now decode chunk after chunk (Main payload)
        while file.location < tail_offset:
            processor_id = file.get_uint32()
            chunk_size = file.get_uint32()
            processor_version = file.get_uint32()
            chunk_content = file.get_bytes(chunk_size)
            processor = create_chunk_processor(processor_id, processor_version)
            processor.decode(chunk_content)
            self.chunks.append(processor)

        assert file.get_bytes(4) == DEADBEEF_BYTES
        strtbl_present = file.get_bool()
        if len(self.frameeffects) > 0 and not strtbl_present:
            raise LookupError("Failed to look up frame effects: The file contains effects, but no string table!")
        
        stringtable: list[str] = []
        for i in range(file.get_uint32()):
            stringtable.append(file.get_str(file.get_uint16()))

        for f in frameeffects:
            effect = XMot.FrameEffect()
            effect.framenum = f[0]
            stringtable_index = f[1]
            if stringtable_index >= len(stringtable):
                raise LookupError(f"Failed to look up frame effect: Index {stringtable_index} is out of bounds of the string table!")
            effect.name = stringtable[stringtable_index]
            self.frameeffects.append(effect)

        assert self.encode() == data # Self-check

        return

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
