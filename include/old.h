#pragma once

/*
    [278] ? ? 0bCString@@QAE@XZ ==> public: __thiscall bCString::bCString(void)"
    [430] ? ? 1bCString@@QAE@XZ ==> public: __thiscall bCString::~bCString(void)"

    [271] ? ? 0bCString@@QAE@ABV0@@Z ==> public: __thiscall bCString::bCString(class bCString const&)"



    [272] ? ? 0bCString@@QAE@ABV0@H@Z ==> public: __thiscall bCString::bCString(class bCString const&, int)"
    [273] ? ? 0bCString@@QAE@ABVbCUnicodeString@@@Z ==> public: __thiscall bCString::bCString(class bCUnicodeString const&)"
    [274] ? ? 0bCString@@QAE@DH@Z ==> public: __thiscall bCString::bCString(char, int)"
    [275] ? ? 0bCString@@QAE@MH@Z ==> public: __thiscall bCString::bCString(float, int)"
    [276] ? ? 0bCString@@QAE@PBD@Z ==> public: __thiscall bCString::bCString(char const*)"
    [277] ? ? 0bCString@@QAE@PBDH@Z ==> public: __thiscall bCString::bCString(char const*, int)"
    [546] ? ? 4bCString@@QAEAAV0@ABV0@@Z ==> public: class bCString& __thiscall bCString::operator=(class bCString const&)"
    [547] ? ? 4bCString@@QAEAAV0@D@Z ==> public: class bCString& __thiscall bCString::operator=(char)"
    [548] ? ? 4bCString@@QAEAAV0@PBD@Z ==> public: class bCString& __thiscall bCString::operator=(char const*)"
    [804] ? ? 8bCString@@QBE_NABV0@@Z ==> public: bool __thiscall bCString::operator==(class bCString const&)const "
    [805] ? ? 8bCString@@QBE_NPBD@Z ==> public: bool __thiscall bCString::operator==(char const*)const "
    [841] ? ? 9bCString@@QBE_NABV0@@Z ==> public: bool __thiscall bCString::operator!=(class bCString const&)const "
    [842] ? ? 9bCString@@QBE_NPBD@Z ==> public: bool __thiscall bCString::operator!=(char const*)const "
    [864] ? ? AbCString@@QAEAADH@Z ==> public: char& __thiscall bCString::operator[](int)"
    [865] ? ? AbCString@@QBEDH@Z ==> public: char __thiscall bCString::operator[](int)const "
    [894] ? ? BbCString@@QBEPBDXZ ==> public: __thiscall bCString::operator char const* (void)const "
    [1053] ? ? HbCString@@QBE ? AV0@ABV0@@Z ==> public: class bCString __thiscall bCString::operator+(class bCString const&)const "
    [1054] ? ? HbCString@@QBE ? AV0@D@Z ==> public: class bCString __thiscall bCString::operator+(char)const "
    [1055] ? ? HbCString@@QBE ? AV0@PBD@Z ==> public: class bCString __thiscall bCString::operator+(char const*)const "
    [1107] ? ? MbCString@@QBE_NABV0@@Z ==> public: bool __thiscall bCString::operator<(class bCString const&)const "
    [1108] ? ? MbCString@@QBE_NPBD@Z ==> public: bool __thiscall bCString::operator<(char const*)const "
    [1115] ? ? NbCString@@QBE_NABV0@@Z ==> public: bool __thiscall bCString::operator<=(class bCString const&)const "
    [1116] ? ? NbCString@@QBE_NPBD@Z ==> public: bool __thiscall bCString::operator<=(char const*)const "
    [1123] ? ? ObCString@@QBE_NABV0@@Z ==> public: bool __thiscall bCString::operator>(class bCString const&)const "
    [1124] ? ? ObCString@@QBE_NPBD@Z ==> public: bool __thiscall bCString::operator>(char const*)const "
    [1131] ? ? PbCString@@QBE_NABV0@@Z ==> public: bool __thiscall bCString::operator>=(class bCString const&)const "
    [1132] ? ? PbCString@@QBE_NPBD@Z ==> public: bool __thiscall bCString::operator>=(char const*)const "
    [1243] ? ? YbCString@@QAEAAV0@ABV0@@Z ==> public: class bCString& __thiscall bCString::operator+=(class bCString const&)"
    [1244] ? ? YbCString@@QAEAAV0@D@Z ==> public: class bCString& __thiscall bCString::operator+=(char)"
    [1245] ? ? YbCString@@QAEAAV0@PBD@Z ==> public: class bCString& __thiscall bCString::operator+=(char const*)"
    [1566] ? Alloc@bCString@@IAEXH@Z ==> protected: void __thiscall bCString::Alloc(int)"
    [1627] ? Clear@bCString@@QAEXXZ ==> public: void __thiscall bCString::Clear(void)"
    [1648] ? Compare@bCString@@QBEHABV1@@Z ==> public: int __thiscall bCString::Compare(class bCString const&)const "
    [1649] ? Compare@bCString@@QBEHPBD@Z ==> public: int __thiscall bCString::Compare(char const*)const "
    [1652] ? CompareFast@bCString@@QBE_NABV1@@Z ==> public: bool __thiscall bCString::CompareFast(class bCString const&)const "
    [1654] ? CompareNoCase@bCString@@QBEHABV1@@Z ==> public: int __thiscall bCString::CompareNoCase(class bCString const&)const "
    [1655] ? CompareNoCase@bCString@@QBEHPBD@Z ==> public: int __thiscall bCString::CompareNoCase(char const*)const "
    [1658] ? CompareNoCaseFast@bCString@@QBE_NABV1@@Z ==> public: bool __thiscall bCString::CompareNoCaseFast(class bCString const&)const "
    [1660] ? ConcatCopy@bCString@@IAEXPBDH0H@Z ==> protected: void __thiscall bCString::ConcatCopy(char const*, int, char const*, int)"
    [1662] ? ConcatInPlace@bCString@@IAEXPBDH@Z ==> protected: void __thiscall bCString::ConcatInPlace(char const*, int)"
    [1716] ? Contains@bCString@@QBE_NDH@Z ==> public: bool __thiscall bCString::Contains(char, int)const "
    [1717] ? Contains@bCString@@QBE_NPBDH@Z ==> public: bool __thiscall bCString::Contains(char const*, int)const "
    [1722] ? ContainsOneOf@bCString@@QBE_NPBDH@Z ==> public: bool __thiscall bCString::ContainsOneOf(char const*, int)const "
    [1729] ? CopyBeforeWrite@bCString@@IAEXXZ ==> protected: void __thiscall bCString::CopyBeforeWrite(void)"
    [1794] ? CopyUnicode@bCString@@IAEXPB_WH@Z ==> protected: void __thiscall bCString::CopyUnicode(wchar_t const*, int)"
    [1795] ? CountWords@bCString@@QBEHABV1@@Z ==> public: int __thiscall bCString::CountWords(class bCString const&)const "
    [1916] ? Decrement@bCString@@IAEXXZ ==> protected: void __thiscall bCString::Decrement(void)"
    [1917] ? Decrement@bCString@@KGHPAUbSStringData@1@@Z ==> protected: static int __stdcall bCString::Decrement(struct bCString::bSStringData*)"
    [1921] ? Delete@bCString@@QAEHHH@Z ==> public: int __thiscall bCString::Delete(int, int)"
    [2032] ? Find@bCString@@QBEHDH_N@Z ==> public: int __thiscall bCString::Find(char, int, bool)const "
    [2033] ? Find@bCString@@QBEHPBDH_N@Z ==> public: int __thiscall bCString::Find(char const*, int, bool)const "
    [2038] ? FindNoCase@bCString@@QBEHPBDH@Z ==> public: int __thiscall bCString::FindNoCase(char const*, int)const "
    [2039] ? FindNoiseChar@bCString@@QBEHH_N@Z ==> public: int __thiscall bCString::FindNoiseChar(int, bool)const "
    [2040] ? FindNumericalChar@bCString@@QBEHH_N@Z ==> public: int __thiscall bCString::FindNumericalChar(int, bool)const "
    [2041] ? FindOneOf@bCString@@QBEHPBDH@Z ==> public: int __thiscall bCString::FindOneOf(char const*, int)const "
    [2049] ? Format@bCString@@QAA_NPBDZZ ==> public: bool __cdecl bCString::Format(char const*, ...)"
    [2053] ? FreeData@bCString@@IAEXXZ ==> protected: void __thiscall bCString::FreeData(void)"
    [2054] ? FreeData@bCString@@KGXPAUbSStringData@1@@Z ==> protected: static void __stdcall bCString::FreeData(struct bCString::bSStringData*)"
    [2056] ? FreeExtra@bCString@@QAEXXZ ==> public: void __thiscall bCString::FreeExtra(void)"
    [2072] ? GetAllocLength@bCString@@QBEHXZ ==> public: int __thiscall bCString::GetAllocLength(void)const "
    [2089] ? GetAt@bCString@@QBEDH_N@Z ==> public: char __thiscall bCString::GetAt(int, bool)const "
    [2111] ? GetBool@bCString@@QBE_NXZ ==> public: bool __thiscall bCString::GetBool(void)const "
    [2123] ? GetBuffer@bCString@@QAEPADH@Z ==> public: char* __thiscall bCString::GetBuffer(int)"
    [2125] ? GetBufferSetLength@bCString@@QAEPADH@Z ==> public: char* __thiscall bCString::GetBufferSetLength(int)"
    [2236] ? GetData@bCString@@IBEPAUbSStringData@1@XZ ==> protected: struct bCString::bSStringData * __thiscall bCString::GetData(void)const "
    [2311] ? GetDouble@bCString@@QBENH@Z ==> public: double __thiscall bCString::GetDouble(int)const "
    [2354] ? GetFloat@bCString@@QBEMH@Z ==> public: float __thiscall bCString::GetFloat(int)const "
    [2361] ? GetFormattedString@bCString@@SA ? AV1@PBDZZ ==> public: static class bCString __cdecl bCString::GetFormattedString(char const*, ...)"
    [2395] ? GetI64@bCString@@QBE_JH@Z ==> public: __int64 __thiscall bCString::GetI64(int)const "
    [2416] ? GetInteger@bCString@@QBEHH_N@Z ==> public: int __thiscall bCString::GetInteger(int, bool)const "
    [2584] ? GetLength@bCString@@QBEHXZ ==> public: int __thiscall bCString::GetLength(void)const "
    [2876] ? GetRefCount@bCString@@IBEHXZ ==> protected: int __thiscall bCString::GetRefCount(void)const "
    [3066] ? GetText@bCString@@QBEPBDXZ ==> public: char const* __thiscall bCString::GetText(void)const "
    [3193] ? GetUnicodeText@bCString@@QBE ? AVbCUnicodeString@@XZ ==> public: class bCUnicodeString __thiscall bCString::GetUnicodeText(void)const "
    [3243] ? GetWord@bCString@@QBEHHABV1@AAV1@_N2@Z ==> public: int __thiscall bCString::GetWord(int, class bCString const&, class bCString&, bool, bool)const "
    [3324] ? Increment@bCString@@KGXPAUbSStringData@1@@Z ==> protected: static void __stdcall bCString::Increment(struct bCString::bSStringData*)"
    [3334] ? Insert@bCString@@QAEHHABV1@@Z ==> public: int __thiscall bCString::Insert(int, class bCString const&)"
    [3335] ? Insert@bCString@@QAEHHD@Z ==> public: int __thiscall bCString::Insert(int, char)"
    [3336] ? Insert@bCString@@QAEHHPBD@Z ==> public: int __thiscall bCString::Insert(int, char const*)"
    [3608] ? IsEmpty@bCString@@QBE_NXZ ==> public: bool __thiscall bCString::IsEmpty(void)const "
    [3693] ? Left@bCString@@QBE ? AV1@H@Z ==> public: class bCString __thiscall bCString::Left(int)const "
    [3696] ? LockBuffer@bCString@@QAEPADXZ ==> public: char* __thiscall bCString::LockBuffer(void)"
    [3709] ? MakeLower@bCString@@QAEAAV1@XZ ==> public: class bCString& __thiscall bCString::MakeLower(void)"
    [3714] ? MakeReverse@bCString@@QAEXXZ ==> public: void __thiscall bCString::MakeReverse(void)"
    [3716] ? MakeUpper@bCString@@QAEAAV1@XZ ==> public: class bCString& __thiscall bCString::MakeUpper(void)"
    [3734] ? Mid@bCString@@QBE ? AV1@H@Z ==> public: class bCString __thiscall bCString::Mid(int)const "
    [3735] ? Mid@bCString@@QBE ? AV1@HH@Z ==> public: class bCString __thiscall bCString::Mid(int, int)const "
    [3900] ? Realloc@bCString@@IAEXH@Z ==> protected: void __thiscall bCString::Realloc(int)"
    [3911] ? Release@bCString@@IAEXXZ ==> protected: void __thiscall bCString::Release(void)"
    [3912] ? Release@bCString@@KGXPAUbSStringData@1@@Z ==> protected: static void __stdcall bCString::Release(struct bCString::bSStringData*)"
    [3915] ? ReleaseBuffer@bCString@@QAEXH@Z ==> public: void __thiscall bCString::ReleaseBuffer(int)"
    [3924] ? Remove@bCString@@QAEHABV1@@Z ==> public: int __thiscall bCString::Remove(class bCString const&)"
    [3925] ? Remove@bCString@@QAEHD@Z ==> public: int __thiscall bCString::Remove(char)"
    [3926] ? Remove@bCString@@QAEHPBD@Z ==> public: int __thiscall bCString::Remove(char const*)"
    [3934] ? Replace@bCString@@QAEHDD@Z ==> public: int __thiscall bCString::Replace(char, char)"
    [3935] ? Replace@bCString@@QAEHPBD0@Z ==> public: int __thiscall bCString::Replace(char const*, char const*)"
    [3949] ? ReverseFind@bCString@@QBEHD@Z ==> public: int __thiscall bCString::ReverseFind(char)const "
    [3950] ? ReverseFind@bCString@@QBEHDH@Z ==> public: int __thiscall bCString::ReverseFind(char, int)const "
    [3951] ? ReverseFind@bCString@@QBEHPBD@Z ==> public: int __thiscall bCString::ReverseFind(char const*)const "
    [3952] ? ReverseFind@bCString@@QBEHPBDH@Z ==> public: int __thiscall bCString::ReverseFind(char const*, int)const "
    [3957] ? ReverseFindOneOf@bCString@@QBEHPBD@Z ==> public: int __thiscall bCString::ReverseFindOneOf(char const*)const "
    [3958] ? ReverseFindOneOf@bCString@@QBEHPBDH@Z ==> public: int __thiscall bCString::ReverseFindOneOf(char const*, int)const "
    [3966] ? Right@bCString@@QBE ? AV1@H@Z ==> public: class bCString __thiscall bCString::Right(int)const "
    [4063] ? SetAt@bCString@@QAEXHD@Z ==> public: void __thiscall bCString::SetAt(int, char)"
    [4344] ? SetText@bCString@@QAEXABV1@@Z ==> public: void __thiscall bCString::SetText(class bCString const&)"
    [4345] ? SetText@bCString@@QAEXABV1@H@Z ==> public: void __thiscall bCString::SetText(class bCString const&, int)"
    [4346] ? SetText@bCString@@QAEXDH@Z ==> public: void __thiscall bCString::SetText(char, int)"
    [4347] ? SetText@bCString@@QAEXPBD@Z ==> public: void __thiscall bCString::SetText(char const*)"
    [4348] ? SetText@bCString@@QAEXPBDH@Z ==> public: void __thiscall bCString::SetText(char const*, int)"
    [4408] ? SetUnicodeText@bCString@@QAEXABVbCUnicodeString@@@Z ==> public: void __thiscall bCString::SetUnicodeText(class bCUnicodeString const&)"
    [4409] ? SetUnicodeText@bCString@@QAEXABVbCUnicodeString@@H@Z ==> public: void __thiscall bCString::SetUnicodeText(class bCUnicodeString const&, int)"
    [4410] ? SetUnicodeText@bCString@@QAEXPB_W@Z ==> public: void __thiscall bCString::SetUnicodeText(wchar_t const*)"
    [4411] ? SetUnicodeText@bCString@@QAEXPB_WH@Z ==> public: void __thiscall bCString::SetUnicodeText(wchar_t const*, int)"
    [4478] ? SpanExcluding@bCString@@QBE ? AV1@PBD@Z ==> public: class bCString __thiscall bCString::SpanExcluding(char const*)const "
    [4480] ? SpanIncluding@bCString@@QBE ? AV1@PBD@Z ==> public: class bCString __thiscall bCString::SpanIncluding(char const*)const "
    [4508] ? ToLower@bCString@@QAEXXZ ==> public: void __thiscall bCString::ToLower(void)"
    [4510] ? ToUpper@bCString@@QAEXXZ ==> public: void __thiscall bCString::ToUpper(void)"
    [4584] ? Trim@bCString@@QAEXD@Z ==> public: void __thiscall bCString::Trim(char)"
    [4585] ? Trim@bCString@@QAEXPBD@Z ==> public: void __thiscall bCString::Trim(char const*)"
    [4586] ? Trim@bCString@@QAEXXZ ==> public: void __thiscall bCString::Trim(void)"
    [4587] ? Trim@bCString@@QAEX_N0@Z ==> public: void __thiscall bCString::Trim(bool, bool)"
    [4592] ? TrimLeft@bCString@@QAEXD@Z ==> public: void __thiscall bCString::TrimLeft(char)"
    [4593] ? TrimLeft@bCString@@QAEXPBD@Z ==> public: void __thiscall bCString::TrimLeft(char const*)"
    [4594] ? TrimLeft@bCString@@QAEXXZ ==> public: void __thiscall bCString::TrimLeft(void)"
    [4598] ? TrimRight@bCString@@QAEXD@Z ==> public: void __thiscall bCString::TrimRight(char)"
    [4599] ? TrimRight@bCString@@QAEXPBD@Z ==> public: void __thiscall bCString::TrimRight(char const*)"
    [4600] ? TrimRight@bCString@@QAEXXZ ==> public: void __thiscall bCString::TrimRight(void)"
    [4609] ? UnlockBuffer@bCString@@QAEXXZ ==> public: void __thiscall bCString::UnlockBuffer(void)"
    */
    //
#define PRINT(x) std::cout << #x ": " << x << std::endl;
//
//class bCString {
//public:
//    G3API bCString() { std::cout << __FUNCTION__ << std::endl; }
//    G3API ~bCString() { std::cout << __FUNCTION__ << std::endl; }
//
//private:
//    const char* ptr;
//};
//
//class gCGeometryLayer {
//public:
//    G3API gCGeometryLayer() { std::cout << __FUNCTION__ << std::endl; }
//    G3API ~gCGeometryLayer() { std::cout << __FUNCTION__ << std::endl; }
//};
//
//class gCWorld {
//public:
//    G3API gCWorld() { std::cout << __FUNCTION__ << std::endl; }
//    G3API ~gCWorld() { std::cout << __FUNCTION__ << std::endl; }
//};
//
//class bCCommandLine {
//public:
//    G3API bCCommandLine() { std::cout << __FUNCTION__ << std::endl; }
//    G3API ~bCCommandLine() { std::cout << __FUNCTION__ << std::endl; }
//
//    void print() const {
//        std::cout << "Buf: [ ";
//        for (int i = 0; i < 16; i++) {
//            std::cout << (int)buf[i] << ", ";
//        }
//        std::cout << "]" << std::endl;
//        PRINT(val1);
//        PRINT(val2);
//        PRINT(val3);
//    }
//
//private:
//    uint8_t buf[16];
//    uint32_t val1;
//    uint32_t val2;
//    uint32_t val3;
//};
//
////class bCCommandLine {
////public:
////    G3API bCCommandLine();
////    G3API ~bCCommandLine();
////};
//
////class iCResourceCompiler {
////public:
////    G3API iCResourceCompiler() { std::cout << __FUNCTION__ << std::endl; }
////    virtual G3API ~iCResourceCompiler() { std::cout << __FUNCTION__ << std::endl; }
////
////    //bool G3API ParseCommandLine(class bCCommandLine const& c) {
////    //    std::cout << __FUNCTION__ << std::endl;
////    //    //c.print();
////    //    return true;
////    //}
////    bool G3API ParseCommandLine(class bCCommandLine const& c);
////};
//
//class iCSceneCompiler {
//public:
//    G3API iCSceneCompiler() { std::cout << __FUNCTION__ << std::endl; }
//    virtual G3API ~iCSceneCompiler() { std::cout << __FUNCTION__ << std::endl; }
//
//    bool G3API ParseCommandLine(class bCCommandLine const& c) {
//        std::cout << __FUNCTION__ << std::endl;
//        //c.print();
//        return true;
//    }
//};
//
//class iCDemoCompiler {
//public:
//    G3API iCDemoCompiler() { std::cout << __FUNCTION__ << std::endl; }
//    virtual G3API ~iCDemoCompiler() { std::cout << __FUNCTION__ << std::endl; }
//
//    bool G3API  ParseCommandLine(class bCCommandLine const& c) {
//        std::cout << __FUNCTION__ << std::endl;
//        std::cout << sizeof(c) << std::endl;
//        //c.print();
//        return true;
//    }
//};
//
//class iCMeshImporter {
//public:
//    G3API iCMeshImporter() { std::cout << __FUNCTION__ << std::endl; }
//    virtual G3API ~iCMeshImporter() { std::cout << __FUNCTION__ << std::endl; }
//};
//
//class iCImporterAdmin {
//public:
//    G3API iCImporterAdmin() { std::cout << __FUNCTION__ << std::endl; }
//    virtual G3API ~iCImporterAdmin() { std::cout << __FUNCTION__ << std::endl; }
//
//    virtual bool G3API Create() {
//        std::cout << __FUNCTION__ << std::endl;
//        return true;
//    }
//
//    void G3API SetMeshPath(bCString str) { std::cout << __FUNCTION__ << std::endl; }
//    void G3API SetMaterialPath(bCString str) { std::cout << __FUNCTION__ << std::endl; }
//    void G3API SetImagePath(bCString str) { std::cout << __FUNCTION__ << std::endl; }
//    void G3API SetSpatialLayer(gCGeometryLayer* layer) { std::cout << __FUNCTION__ << std::endl; }
//    void G3API SetWorld(gCWorld* world) { std::cout << __FUNCTION__ << std::endl; }
//    void G3API SetScaleFactor(float) { std::cout << __FUNCTION__ << std::endl; }
//    bool G3API ImportFile(bCString str) {
//        std::cout << __FUNCTION__ << std::endl;
//        return false;
//    }
//};
//
////void WINAPI CImporterAdmin() {
////    std::cout << "Hello guys" << std::endl;
////}
//
//class iCResourceCompiler {
//public:
//    G3API iCResourceCompiler();
//    virtual G3API ~iCResourceCompiler();
//    bool G3API ParseCommandLine(const bCCommandLine& c);
//
//private:
//    char g[100];
//};
//
//typedef int(__stdcall iCResourceCompiler::*iCResourceCompilerConstr)();
//typedef int(__stdcall iCResourceCompiler::*iCResourceCompilerDestr)();
//typedef int(__stdcall iCResourceCompiler::*ParseCommandLineOriginal)(const bCCommandLine&);
//
//G3API iCResourceCompiler::iCResourceCompiler() {/*
//    static auto x = getDllFunc<iCResourceCompilerConstr>("Importer.dll", "??0iCResourceCompiler@@QAE@XZ");
//    std::cout << this << " " << __FUNCTION__ << std::endl;
//    (this->*x)();*/
//    std::cout << this << " " << __FUNCTION__ << std::endl;
//}
//
//G3API iCResourceCompiler::~iCResourceCompiler() {
//    static auto x = getDllFunc<iCResourceCompilerConstr>("Importer.dll", "??1iCResourceCompiler@@UAE@XZ");
//    //std::cout << this << " " << __FUNCTION__ << std::endl;
//    //(this->*x)();
//}
//
//bool G3API iCResourceCompiler::ParseCommandLine(const bCCommandLine& c) {
//    static auto x = getDllFunc<ParseCommandLineOriginal>("Importer.dll", "?ParseCommandLine@iCResourceCompiler@@QAE_NABVbCCommandLine@@@Z");
//    //std::cout << this << " " << __FUNCTION__ << std::endl;
//    return (this->*x)(c);
//}



















struct F {
    //DETOUR_DECLARE_MEMBER(eCVisualAnimation_PS, PlayMotion);
    //DETOUR_DECLARE_MEMBER(eCVisualAnimation_PS, Read);
    //DETOUR_DECLARE_MEMBER(eCVisualAnimationLoD, Read);
    //DETOUR_DECLARE_MEMBER(bCFile, Open);
    //DETOUR_DECLARE_MEMBER(eCVisualAnimationFactory, GetMainActorFileName);
    //DETOUR_DECLARE_MEMBER(eCVisualAnimationFactory, SetMainActorFileName);
    //DETOUR_DECLARE_MEMBER(eCVisualAnimationFactory, Read);
    //DETOUR_DECLARE_MEMBER(eCApplication, GetInstance);
    //DETOUR_DECLARE_MEMBER(eCApplication, GetCurrentCamera);
    ////DETOUR_DECLARE_MEMBER(eCApplication, UpdateTick);
    //DETOUR_DECLARE_MEMBER(eCApplication, PlayVideo);
    //DETOUR_DECLARE_MEMBER(eCApplication, Run);
    //DETOUR_DECLARE_MEMBER(eCApplication, Process);
    //DETOUR_DECLARE_MEMBER(eCApplication, IsInitialised);
    ////DETOUR_DECLARE_MEMBER(eCApplication, OnRun);
    //DETOUR_DECLARE_MEMBER(eCModuleAdmin, Process);
    //DETOUR_DECLARE_MEMBER(eCModuleAdmin, PostProcess);
    //DETOUR_DECLARE_MEMBER(eCEntityAdmin, Process);
    //DETOUR_DECLARE_MEMBER(eCEntityAdmin, EnableProcessing);
    //DETOUR_DECLARE_MEMBER(eCEntityAdmin, UpdateProcessingRangeEntity);
    ////DETOUR_DECLARE_MEMBER(eCEntity, EnterProcessingRange);
    ////DETOUR_DECLARE_MEMBER(eCEntity, ExitProcessingRange);
    //DETOUR_DECLARE_MEMBER(eCEntity, PreProcess);
    //DETOUR_DECLARE_MEMBER(eCEntity, Process);
    //DETOUR_DECLARE_MEMBER(eCEntity, PostProcess);
    //DETOUR_DECLARE_MEMBER(eCEntity, HasProcessingRangeEntered);
    //DETOUR_DECLARE_MEMBER(eCEntity, IsEnabled);
    //DETOUR_DECLARE_MEMBER(eCPVSPrefetcher3, GetNonDeactivationCell);
    //DETOUR_DECLARE_MEMBER(bCTimer, GetTimeStamp);
    //DETOUR_DECLARE_MEMBER(bCMemoryAdmin, GetInstance);
} f;