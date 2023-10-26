#pragma once

#include <iostream>

// The bCString class in the Genome Engine is very weird. It only has a single pointer 
// as member variable, but when allocating it allocates a larger buffer and sets the
// data pointer to 8 bytes after the buffer start. To achieve reference counting the
// engine looks at the data pointer and then looks 8 or 4 bytes ahead of the pointer.
// Size is 4 bytes (starting at -8) and reference count is 2 bytes (starting at -4).
// Two bytes remain unknown.
//class bCString {
//public:
//    __thiscall bCString();
//    __thiscall ~bCString();
//
//    std::string str() const;
//    uint32_t capacity() const;
//    uint16_t referenceCount() const;
//
//private:
//    char* m_data;
//};

//struct bCAnimationResourceString : public bCString {};

/*class bCIStream {
public:
    virtual uint32_t __thiscall Read(bCIStream& str);
    virtual uint32_t __thiscall Read(void* data1, uint32_t data2);
    bCIStream& __thiscall bCIStream::operator>>(unsigned short& target) {
        unsigned short temp = 0;
        LOG("T = {}", temp);

        int* cVtablePtr = (int*)((int*)this)[0];
        LOG("vtable = {}", (void*)cVtablePtr);
        void* doSomethingPtr = (void*)cVtablePtr[1];
        LOG("fptr = {}", doSomethingPtr);

        //uint32_t* pt = reinterpret_cast<uint32_t*>(this);
        unsigned short (*func)(void*, unsigned long) = reinterpret_cast<unsigned short (*)(void*, unsigned long)>(doSomethingPtr);
        auto result = func(&temp, 2);

        LOG("T = {}", temp);
        target = temp;
        return *this;
        LOG("operator>>");


        LOG("operator>> done");
        return *this;
    }
    //virtual bCIStream& __thiscall bCIStream::operator>>(class bCString&);
    //virtual bCIStream& __thiscall bCIStream::operator>>(bool&);
};*/