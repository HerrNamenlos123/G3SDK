
#include <iostream>
#include <inttypes.h>
#include <assert.h>
#include <bit>

using int8 = int8_t;
using int16 = int16_t;
using int32 = int32_t;
using int64 = int64_t;
using uint8 = uint8_t;
using uint16 = uint16_t;
using uint32 = uint32_t;
using uint64 = uint64_t;
#define MCORE_UNUSED(x) static_cast<void>(x)
#define MCORE_ASSERT(x) assert(x)

enum
{
    MCORE_DEFAULT_ALIGNMENT = 4, /**< The default memory address alignment of objects, in bytes. */
    MCORE_SIMD_ALIGNMENT = 16
};

enum
{
    MCORE_MEMCATEGORY_UNKNOWN = 0,
    MCORE_MEMCATEGORY_ARRAY = 1,
    MCORE_MEMCATEGORY_STRING = 2,
    MCORE_MEMCATEGORY_DISKFILE = 3,
    MCORE_MEMCATEGORY_MEMORYFILE = 4,
    MCORE_MEMCATEGORY_MATRIX = 5,
    MCORE_MEMCATEGORY_HASHTABLE = 6,
    MCORE_MEMCATEGORY_TRILISTOPTIMIZER = 7,
    MCORE_MEMCATEGORY_LOGMANAGER = 9,
    MCORE_MEMCATEGORY_COMMANDLINE = 10,
    MCORE_MEMCATEGORY_LOGFILECALLBACK = 13,
    MCORE_MEMCATEGORY_HALTONSEQ = 14,
    MCORE_MEMCATEGORY_SMALLARRAY = 15,
    MCORE_MEMCATEGORY_COORDSYSTEM = 16,
    MCORE_MEMCATEGORY_MCORESYSTEM = 17,
    MCORE_MEMCATEGORY_COMMANDSYSTEM = 18,
    MCORE_MEMCATEGORY_ATTRIBUTES = 20,
    MCORE_MEMCATEGORY_IDGENERATOR = 21,
    MCORE_MEMCATEGORY_WAVELETS = 22,
    MCORE_MEMCATEGORY_HUFFMAN = 23,
    MCORE_MEMCATEGORY_ABSTRACTDATA = 26,
    MCORE_MEMCATEGORY_SYSTEM = 27,
    MCORE_MEMCATEGORY_THREADING = 29,
    MCORE_MEMCATEGORY_ATTRIBUTEPOOL = 32,
    MCORE_MEMCATEGORY_ATTRIBUTEFACTORY = 33,
    MCORE_MEMCATEGORY_RANDOM = 34,
    MCORE_MEMCATEGORY_STRINGOPS = 35,
    MCORE_MEMCATEGORY_FRUSTUM = 36,
    MCORE_MEMCATEGORY_STREAM = 37,
    MCORE_MEMCATEGORY_MULTITHREADMANAGER = 38,
    MCORE_MEMCATEGORY_TRIANGULATOR = 39,
    // insert new categories here
    MCORE_MEMCATEGORY_MISC = 99
};

#define MCORE_MEMORYOBJECTCATEGORY(CLASSNAME, ALIGNMENT, CATEGORY)                                   \
public:                                                                                              \
    static uint16 GetMemoryCategory() { return CATEGORY; }                                           \
    static uint16 GetMemoryAlignment()                                                               \
    {                                                                                                \
        return 0;                                                                                    \
        /*return AZ::GetMax<uint16>(ALIGNMENT, AZStd::alignment_of<CLASSNAME>::value);*/             \
    }                                                                                                \
                                                                                                     \
    void *operator new(size_t numBytes)                                                              \
    {                                                                                                \
        const uint16 category = GetMemoryCategory();                                                 \
        const uint16 alignment = GetMemoryAlignment();                                               \
        return 0;                                                                                    \
        /*return MCore::AlignedAllocate(numBytes, alignment, category, 0, MCORE_FILE, MCORE_LINE);*/ \
    }                                                                                                \
                                                                                                     \
    void *operator new(size_t numBytes, void *location)                                              \
    {                                                                                                \
        static_cast<void>(numBytes);                                                                 \
        return location;                                                                             \
    }                                                                                                \
                                                                                                     \
    void operator delete(void *memLocation)                                                          \
    {                                                                                                \
        /*MCore::AlignedFree(memLocation);*/                                                         \
    }                                                                                                \
                                                                                                     \
    void operator delete(void *memLocation, void *placement)                                         \
    {                                                                                                \
        static_cast<void>(memLocation);                                                              \
        static_cast<void>(placement);                                                                \
    }                                                                                                \
                                                                                                     \
    void *operator new[](size_t numBytes)                                                            \
    {                                                                                                \
        const uint16 category = GetMemoryCategory();                                                 \
        const uint16 alignment = GetMemoryAlignment();                                               \
        return 0;                                                                                    \
        /*return MCore::AlignedAllocate(numBytes, alignment, category, 0, MCORE_FILE, MCORE_LINE);*/ \
    }                                                                                                \
                                                                                                     \
    void *operator new[](size_t numBytes, void *place)                                               \
    {                                                                                                \
        static_cast<void>(numBytes);                                                                 \
        return place;                                                                                \
    }                                                                                                \
                                                                                                     \
    void operator delete[](void *memLocation)                                                        \
    {                                                                                                \
        /*MCore::AlignedFree(memLocation);*/                                                         \
    }

class Stream
{
    MCORE_MEMORYOBJECTCATEGORY(Stream, MCORE_DEFAULT_ALIGNMENT, MCORE_MEMCATEGORY_STREAM)

public:
    /**
     * The constructor.
     */
    Stream() {}

    /**
     * The destructor.
     */
    virtual ~Stream() {}

    /**
     * Get the unique type ID.
     * @result The type identification number.
     */
    virtual uint32 GetType() const { return -1; }

    /**
     * Read a given amount of data from the stream.
     * @param data The pointer where to store the read data.
     * @param length The size in bytes of the data to read.
     * @result Returns the number of bytes read.
     */
    virtual size_t Read(void *data, size_t length)
    {
        MCORE_UNUSED(data);
        MCORE_UNUSED(length);
        MCORE_ASSERT(false);
        return true;
    } // should never be called, since this method should be overloaded somewhere else

    /**
     * Writes a given amount of data to the stream.
     * @param data The pointer to the data to write.
     * @param length The size in bytes of the data to write.
     * @result Returns the number of written bytes.
     */
    virtual size_t Write(const void *data, size_t length)
    {
        MCORE_UNUSED(data);
        MCORE_UNUSED(length);
        MCORE_ASSERT(false);
        return true;
    } // should never be called, since this method should be overloaded somewhere else

    // write operators
    virtual Stream &operator<<(bool b)
    {
        Write(&b, sizeof(bool));
        return *this;
    }
    virtual Stream &operator<<(char ch)
    {
        Write(&ch, sizeof(char));
        return *this;
    }
    virtual Stream &operator<<(uint8 ch)
    {
        Write(&ch, sizeof(uint8));
        return *this;
    }
    virtual Stream &operator<<(int16 number)
    {
        Write(&number, sizeof(int16));
        return *this;
    }
    virtual Stream &operator<<(uint16 number)
    {
        Write(&number, sizeof(uint16));
        return *this;
    }
    virtual Stream &operator<<(int32 number)
    {
        Write(&number, sizeof(int32));
        return *this;
    }
    virtual Stream &operator<<(uint32 number)
    {
        Write(&number, sizeof(uint32));
        return *this;
    }
    virtual Stream &operator<<(uint64 number)
    {
        Write(&number, sizeof(uint64));
        return *this;
    }
    virtual Stream &operator<<(int64 number)
    {
        Write(&number, sizeof(int64));
        return *this;
    }
    virtual Stream &operator<<(float number)
    {
        Write(&number, sizeof(float));
        return *this;
    }
    virtual Stream &operator<<(double number)
    {
        Write(&number, sizeof(double));
        return *this;
    }
    virtual Stream &operator<<(std::string &text)
    {
        Write((void *)text.c_str(), text.size() + 1);
        return *this;
    } // +1 to include the '\0'
    virtual Stream &operator<<(const char *text)
    {
        Write((void *)text, (int32)strlen(text));
        char c = '\0';
        Write(&c, 1);
        return *this;
    }

    // read operators
    virtual Stream &operator>>(bool &b)
    {
        Read(&b, sizeof(bool));
        return *this;
    }
    virtual Stream &operator>>(char &ch)
    {
        Read(&ch, sizeof(char));
        return *this;
    }
    virtual Stream &operator>>(uint8 &ch)
    {
        Read(&ch, sizeof(uint8));
        return *this;
    }
    virtual Stream &operator>>(int16 &number)
    {
        Read(&number, sizeof(int16));
        return *this;
    }
    virtual Stream &operator>>(uint16 &number)
    {
        Read(&number, sizeof(uint16));
        return *this;
    }
    virtual Stream &operator>>(int32 &number)
    {
        Read(&number, sizeof(int32));
        return *this;
    }
    virtual Stream &operator>>(uint32 &number)
    {
        Read(&number, sizeof(uint32));
        return *this;
    }
    virtual Stream &operator>>(int64 &number)
    {
        Read(&number, sizeof(int64));
        return *this;
    }
    virtual Stream &operator>>(uint64 &number)
    {
        Read(&number, sizeof(uint64));
        return *this;
    }
    virtual Stream &operator>>(float &number)
    {
        Read(&number, sizeof(float));
        return *this;
    }
    virtual Stream &operator>>(double &number)
    {
        Read(&number, sizeof(double));
        return *this;
    }
    virtual Stream &operator>>(std::string &text)
    {
        char c;
        for (;;)
        {
            // check if we can read the character
            if (!Read(&c, 1))
            {
                return *this;
            }

            // add the character or quit
            if (c != '\0')
            {
                text += c;
            }
            else
            {
                break;
            }
        }

        return *this;
    }
};

class File
    : public Stream
{
public:
    /**
     * The constructor.
     */
    File()
        : Stream() {}

    /**
     * The destructor.
     */
    virtual ~File() {}

    /**
     * Close the file.
     */
    virtual void Close() = 0;

    /**
     * Flush the file. All cached (not yet written) data will be forced to written when calling this method.
     */
    virtual void Flush() = 0;

    /**
     * Check if we reached the end of the file or not.
     * @result Returns true when we have returned the end of the file. Otherwise false is returned.
     */
    virtual bool GetIsEOF() const = 0;

    /**
     * Reads and returns the next byte/character in the file. So this will increase the position in the file with one.
     * @result The character or byte read.
     */
    virtual uint8 GetNextByte() = 0;

    /**
     * Returns the position in the file.
     * @result The offset in the file in bytes.
     */
    virtual size_t GetPos() const = 0;

    /**
     * Returns the size of this file in bytes.
     * @result The filesize in bytes.
     */
    virtual size_t GetFileSize() const = 0;

    /**
     * Write a character or byte in the file.
     * @param value The character or byte to write.
     * @result Returns true when successfully written, otherwise false is returned.
     */
    virtual bool WriteByte(uint8 value) = 0;

    /**
     * Seek ahead a given number of bytes. This can be used to skip a given number of upcoming bytes in the file.
     * @param numBytes The number of bytes to seek ahead.
     * @result Returns true when succeeded or false when an error occured (for example when we where trying to read past the end of the file).
     */
    virtual bool Forward(size_t numBytes) = 0;

    /**
     * Seek to a given byte position in the file, where 0 would be the beginning of the file.
     * So we're talking about the absolute position in the file. After successfully executing this method
     * the method GetPos will return the given offset.
     * @param offset The offset in bytes (the position) in the file to seek to.
     * @result Returns true when successfully moved to the given position in the file, otherwise false.
     */
    virtual bool Seek(size_t offset) = 0;

    /**
     * Read a given amount of data from the file.
     * @param data The pointer where to store the read data.
     * @param length The size in bytes of the data to read.
     * @result Returns the number of read bytes.
     */
    virtual size_t Read(void *data, size_t length) = 0;

    /**
     * Writes a given amount of data to the file.
     * @param data The pointer to the data to write.
     * @param length The size in bytes of the data to write.
     * @result Returns the number of written bytes.
     */
    virtual size_t Write(const void *data, size_t length) = 0;

    /**
     * Check if the file has been opened already.
     * @result Returns true when the file has been opened, otherwise false.
     */
    virtual bool GetIsOpen() const = 0;
};

class MemoryFile
    : public File
{
    MCORE_MEMORYOBJECTCATEGORY(MemoryFile, MCORE_DEFAULT_ALIGNMENT, MCORE_MEMCATEGORY_MEMORYFILE)

public:
    // the type returned by GetType()
    enum
    {
        TYPE_ID = 0x0000002
    };

    /**
     * Constructor.
     */
    MemoryFile()
        : File(), mMemoryStart(nullptr), mCurrentPos(nullptr), mLength(0), mUsedLength(0), mPreAllocSize(1024), mAllocate(false) {}

    /**
     * Destructor. Automatically closes the file.
     */
    ~MemoryFile() { Close(); }

    /**
     * Get the unique type ID.
     * @result The type identification number.
     */
    uint32 GetType() const override { return 0; }

    /**
     * Open the file from a given memory location, with a given length in bytes.
     * If you want to create a new block of memory that can grow, like creating a new file on disk, you
     * can pass nullptr as memory start address, and as length the initial memory block size you want to be allocated, or 0 if it should start empty.
     * @param memoryStart The memory position of the first byte in the file, or nullptr when you want to automatically allocate memory.
     * @param length The length in bytes of the file. So the size in bytes of the memory block.
     * @result Returns true when the file could be opened, otherwise false.
     */
    bool Open(uint8 *memoryStart = nullptr, size_t length = 0);

    /**
     * Close the file.
     */
    void Close() override { return; }

    /**
     * Flush the file. All cached (not yet written) data will be forced to written when calling this method.
     */
    void Flush() override { return; }

    /**
     * Check if we reached the end of the file or not.
     * @result Returns true when we have returned the end of the file. Otherwise false is returned.
     */
    bool GetIsEOF() const override { return 0; }

    /**
     * Reads and returns the next byte/character in the file. So this will increase the position in the file with one.
     * @result The character or byte read.
     */
    uint8 GetNextByte() override { return 0; }

    /**
     * Returns the position in the file.
     * @result The offset in the file in bytes.
     */
    size_t GetPos() const override { return 0; }

    /**
     * Write a character or byte in the file.
     * @param value The character or byte to write.
     * @result Returns true when successfully written, otherwise false is returned.
     */
    bool WriteByte(uint8 value) override { return 0; }

    /**
     * Seek ahead a given number of bytes. This can be used to skip a given number of upcoming bytes in the file.
     * @param numBytes The number of bytes to seek ahead.
     * @result Returns true when succeeded or false when an error occured (for example when we where trying to read past the end of the file).
     */
    bool Forward(size_t numBytes) override { return 0; }

    /**
     * Seek to a given byte position in the file, where 0 would be the beginning of the file.
     * So we're talking about the absolute position in the file. After successfully executing this method
     * the method GetPos will return the given offset.
     * @param offset The offset in bytes (the position) in the file to seek to.
     * @result Returns true when successfully moved to the given position in the file, otherwise false.
     */
    bool Seek(size_t offset) override { return 0; }

    /**
     * Writes a given amount of data to the file.
     * @param data The pointer to the data to write.
     * @param length The size in bytes of the data to write.
     * @result Returns the number of written bytes.
     */
    size_t Write(const void *data, size_t length) override { return 0; }

    /**
     * Read a given amount of data from the file.
     * @param data The pointer where to store the read data.
     * @param length The size in bytes of the data to read.
     * @result The number of bytes read.
     */
    size_t Read(void *data, size_t length) override { return 0; }

    /**
     * Check if the file has been opened already.
     * @result Returns true when the file has been opened, otherwise false.
     */
    bool GetIsOpen() const override { return 0; }

    /**
     * Returns the size of this file in bytes.
     * @result The filesize in bytes.
     */
    size_t GetFileSize() const override { return 0; }

    /**
     * Get the memory start address, where the data is stored.
     * @result The memory start address that points to the start of the file.
     */
    uint8 *GetMemoryStart() const;

    /**
     * Get the pre-allocation size, which is the number of bytes that are allocated extra when
     * writing to the file and the data wouldn't fit in the file anymore. On default this value is 1024.
     * This can reduce the number of reallocations being performed significantly.
     * @result The pre-allocation size, in bytes.
     */
    size_t GetPreAllocSize() const;

    /**
     * Set the pre-allocation size, which is the number of bytes that are allocated extra when
     * writing to the file and the data wouldn't fit in the file anymore. On default this value is 1024.
     * This can reduce the number of reallocations being performed significantly.
     * @param newSizeInBytes The size in bytes to allocate on top of the required allocation size.
     */
    void SetPreAllocSize(size_t newSizeInBytes);

    /**
     * Load memory file from disk.
     * The memory file object should be newly created or not containing any data yet when calling this function. Also please make sure
     * that the memory file is opened.
     * @param fileName The full or relative path/file name of the disk file to load into this memory file.
     * @return True when loading worked fine, false if any error occurred. All errors that happen will be logged.
     */
    bool LoadFromDiskFile(const char *fileName);

    /**
     * Save the memory file to disk.
     * The memory file object should contain data yet when calling this function else the resulting disk file will be empty. Also please make sure
     * that the memory file is opened.
     * @param fileName The full or relative path/file name of the disk file to be created.
     * @return True when saving worked fine, false if any error occurred. All errors that happen will be logged.
     */
    bool SaveToDiskFile(const char *fileName);

private:
    uint8 *mMemoryStart;  /**< The location of the file */
    uint8 *mCurrentPos;   /**< The current location */
    size_t mLength;       /**< The total length of the file. */
    size_t mUsedLength;   /**< The actual used length of the memory file. */
    size_t mPreAllocSize; /**< The pre-allocation size (in bytes) when we have to reallocate memory. This prevents many allocations. The default=1024, which is 1kb.*/
    bool mAllocate;       /**< Can we reallocate or not? */
};

#define FIND_OFFSET(type, func) findOffset<type>(&type::func, #func)

template <typename T, typename Tfunc>
void findOffset(Tfunc &&func, std::string name)
{
    T obj;
    void **vtablePtr = *std::bit_cast<void ***>(&obj);
    void **funcPtr = *std::bit_cast<void ***>(&func);
    std::cout << "vtablePtr: " << vtablePtr << std::endl;
    std::cout << "First vtablePtr: " << *vtablePtr << std::endl;
    std::cout << "First vtablePtr: " << vtablePtr[0] << std::endl;
    std::cout << "First vtablePtr: " << vtablePtr[9] << std::endl;
    std::cout << "funcPtr: " << funcPtr << std::endl;

    int idx = 0;
    for (int i = 0; i < 100; i++)
    {
        if (vtablePtr[i] == funcPtr)
        {
            std::cout << typeid(T).name() << "::" << name << " is at index " << idx << std::endl;
            return;
        }
    }
    std::cout << typeid(T).name() << "::" << name << " not found" << std::endl;
}

class Test {
public:
    Test() {}

    virtual void foo1() {}
    virtual void foo2() {}
    virtual void foo3() {}

    int a = -1;
};

class Test2 : public Test {
public:
    Test2() {}

    void foo2() override {};

    virtual void foo4() {};
    virtual void foo5() {};
};

int main()
{
    Stream stream;
    //File file;
    MemoryFile mem;

    Test t1;
    Test2 t2;

    t2.foo5();

    Test obj;
    void ***vtablePtr = std::bit_cast<void ***>(&obj);
    void **vtable = *vtablePtr;
    /*for (int i = 0; i < 5; i++)
    {
        std::cout << i << ": " << vtable[i] << std::endl;
    }*/
    void **func = std::bit_cast<void **>(&Test::foo1);

    std::cout << "vtablePtr: " << vtablePtr << std::endl;
    //std::cout << "vtable[0]: " << *vtable << std::endl;
    std::cout << "func: " << func << std::endl;

    // FIND_OFFSET(MemoryFile, GetType);
    // FIND_OFFSET(MemoryFile, GetMemoryCategory);
    // FIND_OFFSET(MemoryFile, GetMemoryAlignment);
    // FIND_OFFSET(MemoryFile, GetIsEOF);
}
