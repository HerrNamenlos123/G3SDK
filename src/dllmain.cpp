
#ifndef GLFW_EXPOSE_NATIVE_WIN32
#define GLFW_EXPOSE_NATIVE_WIN32
#endif

#include <types.h>
#include <formatters.h>
#include "framework.h"
#include <GLFW/glfw3.h>
#include <GLFW/glfw3native.h>
#include "Script.h"

std::shared_ptr<spdlog::logger> logger;
bool _log = false;

//void eCVisualAnimation_PS::PlayMotion(eCWrapper_emfx2Actor::eEMotionType p1, eCWrapper_emfx2Motion::eSMotionDesc* p2) {
//    //TRACE("this={} p1={} p2={}", (void*)this, p1, (void*)p2);
//    //return;
//    (this->*f.eCVisualAnimation_PS_PlayMotion)(p1, p2);
//}

//bEResult eCVisualAnimationLoD::Read(bCIStream& stream) {
//    //auto size = stream.Read((void*)buffer.data(), buffer.size());
//    //TRACE("buffer[{}] = {}", size, buffer);
//    return (this->*f.eCVisualAnimationLoD_Read)(stream);
//}

GEBool eCVirtualFileHook::Open(bCString const& path, bEFileCreationMode mode, GEU8 a_u8ReadOnly) {
    SILENT_TRACE("");
    //TRACE("str = {}", path);
    ///*if (str(path).substr(str(path).size() - 5) == ".xmot") {
    //    LOG_WARN("str = {}", path);
    //}*/
    //if (str(path) == "/Data/_compiledAnimation/Hero_Stand_None_None_P0_Ambient_Loop_N_Fwd_00_%_02_P0_0.xmot") {
    //    LOG_ERR("str = {}", path);
    //    //BREAK();
    //}
    return (this->*Open_original)(path, mode, a_u8ReadOnly);
}

bEResult eCVisualAnimationLoDHook::Read(bCIStream& stream) {
    //static int i = 0;
    //TRACE("i {}", i++);
    return (this->*Read_original)(stream);
}

bEResult eCVisualAnimation_PSHook::Read(bCIStream& stream) {
    //std::string s;
    //s.resize(1024);
    //auto l = stream.Read((void*)s.data(), s.size());
    //s.resize(l);
    //static int i = 0;
    //TRACE("i {}", i++);
    auto r = (this->*Read_original)(stream);
    //LOG("path afterwards = {}", reinterpret_cast<eCVisualAnimation_PS*>(this)->GetResourceFilePath());
    //BREAK();
    //bCIStream stream2 = stream;
    /*for (int i = 0; i < 0; i++) {
        bCString str;
        stream.ReadLine(str);
        std::string s = bCStringFormat(str).str();
        std::vector<uint8_t> a = { s.begin(), s.end() };
        LOG_ERR("str: {}", str);
        LOG_ERR("str: {}", a);
    }*/
    return r;
}

void eCVisualAnimation_PSHook::PlayMotion(eCWrapper_emfx2Actor::eEMotionType type, eCWrapper_emfx2Motion::eSMotionDesc* mot) {
    SILENT_TRACE("")
    //LOG_ERR("type = {}", type);
    //return;
    (this->*PlayMotion_original)(type, mot);
}

bEResult eCVisualAnimationFactoryHook::Read(bCIStream& stream) {
    SILENT_TRACE("");

    auto r = (this->*Read_original)(stream);
    //LOG("main actor = {}", reinterpret_cast<eCVisualAnimationFactory*>(this)->GetMainActorFileName());

    return r;
}

bEResult eCWrapper_emfx2MotionHook::LoadMotion(eCArchiveFile& file) {
    TRACE("");
    LOG_ERR("LoadMotion")
    return (this->*LoadMotion_original)(file);
}

void EntityHook::DoDamage(Entity const& entity, GEU32 num, gEDamageType damageType) {
    TRACE("");
    return (this->*DoDamage_original)(entity, num, damageType);
}

bCString EntityHook::GetDisplayName() const {
    auto str = (this->*GetDisplayName_original)();
    TRACE("name = {}", str);
    return str;
}

//const bCString& __thiscall eCVisualAnimationFactory::GetMainActorFileName() const {
//    TRACE("");
//    return (this->*f.eCVisualAnimationFactory_GetMainActorFileName)();
//}
//
//void __thiscall eCVisualAnimationFactory::SetMainActorFileName(const bCString& str) {
//    TRACE("");
//    return (this->*f.eCVisualAnimationFactory_SetMainActorFileName)(str);
//}
//
//bEResult __thiscall eCVisualAnimationFactory::Read(bCIStream& stream) {
//    TRACE("");
//    return (this->*f.eCVisualAnimationFactory_Read)(stream);
//}
//
//eCApplication& __stdcall eCApplication::GetInstance() {
//    SILENT_TRACE("");
//    return (*f.eCApplication_GetInstance)();
//}
//
//eCCameraBase& __thiscall eCApplication::GetCurrentCamera() {
//    SILENT_TRACE("");
//    return (this->*f.eCApplication_GetCurrentCamera)();
//}
//
////void __thiscall eCApplication::UpdateTick() {
////    SILENT_TRACE("");
////    (this->*f.eCApplication_UpdateTick)();
////}
//
//void __thiscall eCApplication::PlayVideo(const bCString& str) {
//    TRACE("str = {}", str);
//    (this->*f.eCApplication_PlayVideo)(str);
//}
//
//bEResult __thiscall eCApplication::Run() {
//    TRACE("");
//    return (this->*f.eCApplication_Run)();
//}

//void __thiscall eCApplication::OnRun() {
//    SILENT_TRACE("");
//    (this->*f.eCApplication_OnRun)();
//}
//
//void __thiscall eCApplication::Process() {
//    SCOPE_TRACE("");
//    (this->*f.eCApplication_Process)();
//}
//
//bool __stdcall eCApplication::IsInitialised() {
//    SILENT_TRACE("");
//    return (*f.eCApplication_IsInitialised)();
//}
//
//void __thiscall eCModuleAdmin::Process() {
//    SCOPE_TRACE("");
//    (this->*f.eCModuleAdmin_Process)();
//}
//
//void __thiscall eCModuleAdmin::PostProcess() {
//    SCOPE_TRACE("");
//    (this->*f.eCModuleAdmin_PostProcess)();
//}

//void __thiscall eCEntityAdmin::Process() {
//    SCOPE_TRACE("");
//    _log = true;
//    /*this->importantFloatingValueInIfWhichIsInvalidatedTo_250 = 1000000000000000.f;
//    this->something_with_full_roi_update = false;
//    this->_EnableProcessing = false;*/
//    (this->*f.eCEntityAdmin_Process)();
//    //LOG("Processing enabled = {}, offset = {}", this->_EnableProcessing, offsetof(eCEntityAdmin, _EnableProcessing));
//    _log = false;
//    return;

    /*
    eCEntity* peVar1;
    int* piVar2;
    bCBox box;
    bCBox box_00;
    bool bVar3;
    char cVar4;
    ushort cnt;
    ulong currentTimeStamp2;
    eCApplication* applicationInstance;
    undefined4 uVar5;
    bCVector* pbVar6;
    undefined4 uVar7;
    undefined4 uVar8;
    undefined4 uVar9;
    eCPVSPrefetcher3* peVar12;
    int** ppiVar13;
    eCModuleAdmin* this_00;
    eCPVSCellItem* peVar17;
    undefined* puVar18;
    bCString bVar19;
    int iVar20;
    char* pcVar21;
    uint* puVar22;
    ulong currentTimeStamp;
    ushort uVar23;
    int** ppiVar24;
    eCEntity** someBuffer;
    ushort uVar25;
    uint cnt1;
    eCCameraBase* unaff_ESI;
    undefined4 unaff_EDI;
    uint someCount;
    uint cnt3;
    float fVar26;
    bCString* pbVar27;
    eCCameraBase* peVar30;
    void* pvVar31;
    char* pcVar32;
    undefined4* puVar33;
    undefined2 uVar34;
    undefined2 uVar35;
    uint uStack_60;
    undefined4 uStack_58;
    undefined4 uStack_50;
    void* someEntityArray[2];
    undefined4 uStack_44;
    eCPVSCellItem* auStack_40;
    float someFloat;
    undefined auStack_30[8];
    undefined auStack_28[8];
    undefined auStack_20[4];
    undefined auStack_1c[4];
    undefined auStack_18[20];
    char* string1;
    eCEntity** entity;
    bCSphere* oldCullProcessingRange;*/
    /*
    auto& currentCamera = eCApplication::GetInstance().GetCurrentCamera();
    auto& regionOfInterestSphere = this->ROI_Sphere;
    regionOfInterestSphere.SetPosition(*reinterpret_cast<bCVector*>(&currentCamera - 0x74));
    auto& cullProcessingRange = this->something_with_cull_processing_range;
    bCVector positionOfSphere2 = cullProcessingRange.GetPosition();
    bCVector vec2 = positionOfSphere2;
    positionOfSphere2 = regionOfInterestSphere.GetPosition();
    vec2 -= positionOfSphere2;
    fVar26 = vec2.GetMagnitude();
    fVar26 = 0;
    if ((this->importantFloatingValueInIfWhichIsInvalidatedTo_250 < fVar26) || (this->something_with_full_roi_update == true)) {
        BREAK_MSG("FIRST IF WAS CALLED!!! this->something_with_full_roi_update={} v={} fvar26={}", this->something_with_full_roi_update, this->importantFloatingValueInIfWhichIsInvalidatedTo_250, fVar26);
        return;
    }
    else if (this->ProbablySomeOtherEntityCount != 0) {
        someCount = (uint)(ushort)this->ProbablySomeOtherEntityCount;
        bTSmallArray<eCEntity*> a;
        bTSmallArray<eCEntity*> b;
        while (someCount != 0) {
            someCount -= 1;
            //UpdateProcessingRangeEntity(this->ProbablySomeOtherEntityArray[someCount & 0xffff], a, b);
        }
        this->ProbablySomeOtherEntityCount = 0;
    }
    cnt1 = 0;
    if (uStack_50._2_2_ != 0) {
        someCount = (uint)uStack_58 >> 0x10;
        do {
            entity = (eCEntity**)((int)someEntityArray[0] + (cnt1 & 0xffff) * 4);
            eCEntity::ExitProcessingRange(*entity, false);
            iVar20 = 0;
            if (someCount != 0) {
                do {
                    if (*entity == *(eCEntity**)(currentCamera + iVar20 * 4)) {
                        bCString::bCString((bCString*)&stack0xffffff98);
                        eCEntity::GetName(*entity);
                        bCString::Format((bCString*)&stack0xffffff98, (char*)(bCString*)&stack0xffffff98);
                        iVar20 = 0x2a0;
                        pcVar32 = ".\\components\\scene\\admin\\ge_entityadmin.cpp";
                        pcVar21 = bCString::operator_char_const * ((bCString*)&stack0xffffff9c);
                        this_01 = bCErrorAdmin::GetInstance();
                        bCErrorAdmin::CallFatalError(this_01, pcVar21, pcVar32, iVar20);
                        bCString::~bCString((bCString*)&stack0xffffff9c);
                        break;
                    }
                    iVar20 += 1;
                } while (iVar20 < (int)someCount);
            }
            cnt1 += 1;
        } while ((int)cnt1 < (int)((uint)uStack_50 >> 0x10));
    }
    someCount = (uint)uStack_58 >> 0x10;
    cnt3 = 0;
    this->field_0xc4 = 0;
    if (someCount != 0) {
        do {
            entity = (eCEntity**)(currentCamera + (cnt3 & 0xffff) * 4);
            puVar22 = (uint*)eCEntity::GetEntityFlags(*(eCEntity**)(currentCamera + (cnt3 & 0xffff) * 4));
            if ((_DAT_30aee308 & 1) == 0) {
                _DAT_30aee308 |= 1;
                DAT_30aee304 = 0x100;
            }
            if ((*puVar22 & DAT_30aee304) != 0) {
                eCEntity::EnterProcessingRange(*entity, false);
            }
            cnt3 += 1;
        } while ((int)cnt3 < (int)someCount);
    }
    if (this->EnableProcessing == true) {
        someCount = (uint)this->some_count;
        someBuffer = NULL;
        if (this->some_field7 == 0) {
            puVar18 = this->some_buffer_source;
            someBuffer = NULL;
            cnt3 = someCount;
        }
        else {
            if ((this->some_count != 0) && ((short)(someCount + 1) != 0)) {
                currentTimeStamp2 = (someCount + 1 & 0xffff) * 4;
                pvVar31 = NULL;
                memoryAdminInstance = bCMemoryAdmin::GetInstance();
                someBuffer = (eCEntity**)bCMemoryAdmin::Realloc(memoryAdminInstance, pvVar31, currentTimeStamp2);
            }
            cnt3 = (uint)this->some_count;
            puVar18 = this->some_buffer_source;
        }
        _memcpy(someBuffer, puVar18, cnt3 * 4);
        cnt3 = 0;
        if (someCount != 0) {
            do {
                (*(code*)someBuffer[cnt3 & 0xffff]->vtable->bCObjectRefBase_AddReference)();
                cnt3 += 1;
            } while ((int)cnt3 < (int)someCount);
        }
        string1 = NULL;
        if (someCount != 0) {
            do {
                entity = someBuffer + ((uint)string1 & 0xffff);
                puVar22 = (uint*)eCEntity::GetEntityFlags(*entity);
                if ((DAT_30ada2a4 & 1) == 0) {
                    DAT_30ada2a4 |= 1;
                    DAT_30ada2a0 = 0x800000;
                }
                if (((*puVar22 & DAT_30ada2a0) != 0) && (bVar3 = eCEntity::HasProcessingRangeEntered(*entity), bVar3)) {
                    peVar1 = *entity;
                    cVar4 = (*(code*)peVar1->vtable->IsKilled)();
                    if ((cVar4 != '\x01') && (bVar3 = eCEntity::IsEnabled(peVar1), bVar3)) {
                        this_02 = eCNode::GetCurrentContext((eCNode*)peVar1);
                        bVar3 = eCContextBase::IsEnabled(this_02);
                        if (bVar3) {
                            eCEntity::PreProcess(peVar1, false);
                            eCEntity::Process(peVar1, false);
                            eCEntity::PostProcess(peVar1, false);
                        }
                    }
                }
                string1 = string1 + 1;
            } while ((int)string1 < (int)someCount);
        }
        cnt3 = 0;
        if (someCount != 0) {
            do {
                (*(code*)someBuffer[cnt3 & 0xffff]->vtable->bCObjectRefBase_ReleaseReference)();
                cnt3 += 1;
            } while ((int)cnt3 < (int)someCount);
        }
        if (someBuffer != NULL) {
            memoryAdminInstance = bCMemoryAdmin::GetInstance();
            bCMemoryAdmin::Free(memoryAdminInstance, someBuffer);
        }
    }
    currentTimeStamp = bCTimer::GetTimeStamp();
    this->ElapsedTime = currentTimeStamp - this->ElapsedTime;
    bCVector::~bCVector((bCVector*)&auStack_40);
    if (someEntityArray[0] != NULL) {
        pvVar31 = someEntityArray[0];
        memoryAdminInstance = bCMemoryAdmin::GetInstance();
        bCMemoryAdmin::Free(memoryAdminInstance, pvVar31);
    }
    if (currentCamera != NULL) {
        peVar30 = currentCamera;
        memoryAdminInstance = bCMemoryAdmin::GetInstance();
        bCMemoryAdmin::Free(memoryAdminInstance, peVar30);
    }
    return;*/
//}

//void __thiscall eCEntityAdmin::EnableProcessing(bool enable) {
//    SCOPE_TRACE("enable = {}", enable);
//    BREAK();
//    (this->*f.eCEntityAdmin_EnableProcessing)(enable);
//}
//
//void __thiscall eCEntityAdmin::UpdateProcessingRangeEntity(class eCEntity* e, class bTSmallArray<class eCEntity*>& a, class bTSmallArray<class eCEntity*>& b) {
//    TRACE("");
//    (this->*f.eCEntityAdmin_UpdateProcessingRangeEntity)(e, a, b);
//}

//void __thiscall eCEntity::EnterProcessingRange(bool enter) {
//    SCOPE_TRACE("enter = {}", enter);
//    (this->*f.eCEntity_EnterProcessingRange)(enter);
//}
//
//void __thiscall eCEntity::ExitProcessingRange(bool enter) {
//    SCOPE_TRACE("enter = {}", enter);
//    (this->*f.eCEntity_ExitProcessingRange)(enter);
//}
//
//void __thiscall eCEntity::PreProcess(bool b) {
//    SCOPE_TRACE("b = {}", b);
//    BREAK();
//    (this->*f.eCEntity_PreProcess)(b);
//}
//
//void __thiscall eCEntity::Process(bool b) {
//    SCOPE_TRACE("b = {}", b);
//    BREAK();
//    (this->*f.eCEntity_Process)(b);
//}
//
//void __thiscall eCEntity::PostProcess(bool b) {
//    SCOPE_TRACE("b = {}", b);
//    BREAK();
//    (this->*f.eCEntity_PostProcess)(b);
//}
//
//bool __thiscall eCEntity::HasProcessingRangeEntered() const {
//    bool b = (this->*f.eCEntity_HasProcessingRangeEntered)();
//    TRACE("b = {}", b);
//    return b;
//}
//
//bool __thiscall eCEntity::IsEnabled() const {
//    bool b = (this->*f.eCEntity_IsEnabled)();
//    TRACE("b = {}", b);
//    return b;
//}
//
//unsigned long __stdcall bCTimer::GetTimeStamp() {
//    if (_log) {
//        TRACE("");
//        return (*f.bCTimer_GetTimeStamp)();
//    }
//    else {
//        SILENT_TRACE("");
//        return (*f.bCTimer_GetTimeStamp)();
//    }
//}
//
//eCPVSCellItem* __thiscall eCPVSPrefetcher3::GetNonDeactivationCell() {
//    SCOPE_TRACE("");
//    BREAK();
//    return (this->*f.eCPVSPrefetcher3_GetNonDeactivationCell)();
//}
//
//bCMemoryAdmin& __stdcall bCMemoryAdmin::GetInstance() {
//    if (_log) {
//        TRACE("");
//        return (*f.bCMemoryAdmin_GetInstance)();
//    }
//    else {
//        SILENT_TRACE("");
//        return (*f.bCMemoryAdmin_GetInstance)();
//    }
//}

//G3API CFFFileSystemModule& __stdcall CFFFileSystemModule::GetInstance() {
//    //TRACE("");
//    return f.CFFFileSystemModule_GetInstance();
//}

//
//void __stdcall eCApplication::ToggleFullScreen(bCObjectRefBase* p1, bCEvent p2) {
//    TRACE("");
//}
//
//bEResult __stdcall eCApplication::Create() {
//    TRACE("");
//    return (bEResult)0;
//}
//
//void Custom::Function(void) {
//    TRACE("this={}", (void*)this);
//    auto func = (decltype(&Custom::Function))f.Original_Function;
//    (this->*func)();
//}
//
//VOID WINAPI Sleep_detour(DWORD dwMilliseconds) {
//    //TRACE("{} ms", dwMilliseconds);
//    f.Sleep(dwMilliseconds);
//}
//
//HWND WINAPI CreateWindowExA_detour(DWORD dwExStyle, LPCSTR lpClassName, LPCSTR lpWindowName, DWORD dwStyle,
//    int X, int Y, int nWidth, int nHeight, HWND hWndParent, HMENU hMenu, HINSTANCE hInstance, LPVOID lpParam)
//{
//    TRACE("width={} height={} X={} Y={} windowName={} style={}", nWidth, nHeight, X, Y, lpWindowName, dwStyle);
//    return f.CreateWindowExA(dwExStyle, lpClassName, lpWindowName, dwStyle, X, Y, nWidth, nHeight, hWndParent, hMenu, hInstance, lpParam);
//    GLFWwindow* window = glfwCreateWindow(nWidth, nHeight, lpWindowName, NULL, NULL);
//    if (!window) {
//        spdlog::error("Failed to create GLFW Window!");
//        return nullptr;
//    }
//    HWND native = glfwGetWin32Window(window);
//    windows[native] = window;
//    return native;
//}
//
//HWND WINAPI GetForegroundWindow_detour() {
//    spdlog::debug("{}", (void*)GetForegroundWindow());
//    /*if (GetForegroundWindow() != hWnd) {
//        spdlog::warn("Window not focused anymore, releasing mouse capture");
//        ReleaseCapture();
//    }*/
//    return f.GetForegroundWindow();
//}
//
//HDC WINAPI BeginPaint_detour(HWND hWnd, LPPAINTSTRUCT lpPaint) {
//    //TRACE("hWnd={}", (void*)hWnd);
//    return f.BeginPaint(hWnd, lpPaint);
//}
//
//BOOL WINAPI EndPaint_detour(HWND hWnd, CONST PAINTSTRUCT* lpPaint) {
//    //TRACE("hWnd={}", (void*)hWnd);
//    return f.EndPaint(hWnd, lpPaint);
//}
//
//int WINAPI MessageBoxW_detour(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType) {
//    TRACE("type={}", uType);
//    return f.MessageBoxW(hWnd, lpText, lpCaption, uType);
//}
//
//BOOL WINAPI MoveWindow_detour(HWND hWnd, int X, int Y, int nWidth, int nHeight, BOOL bRepaint) {
//    //return true;
//    //TRACE("x={} y={} width={} height={} repaint={}", X, Y, nWidth, nHeight, (bool)bRepaint);
//    //return true;
//    return f.MoveWindow(hWnd, X, Y, nWidth, nHeight, bRepaint);
//}
//
//BOOL WINAPI GetWindowRect_detour(HWND hWnd, LPRECT lpRect) {
//    auto r = f.GetWindowRect(hWnd, lpRect);
//    //TRACE("left={} right={} bottom={} top={}", lpRect->left, lpRect->right, lpRect->bottom, lpRect->top);
//    return r;
//}
//
//int WINAPI GetSystemMetrics_detour(int nIndex) {
//    //TRACE("index={}", nIndex);
//    return f.GetSystemMetrics(nIndex);
//}
//
//BOOL WINAPI ValidateRect_detour(HWND hWnd, CONST RECT* lpRect) {
//    //TRACE("left={} right={} bottom={} top={}", lpRect->left, lpRect->right, lpRect->bottom, lpRect->top);
//    TRACE("");
//    return f.ValidateRect(hWnd, lpRect);
//}
//
//BOOL WINAPI SetWindowPos_detour(HWND hWnd, HWND hWndInsertAfter, int X, int Y, int cx, int cy, UINT uFlags) {
//    //return true;
//    //TRACE("wndInsertAfter={} x={} y={} cx={} cy={} flags={}", (void*)hWndInsertAfter, X, Y, cx, cy, uFlags);
//    //return true;
//    return f.SetWindowPos(hWnd, hWndInsertAfter, X, Y, cx, cy, uFlags);
//}
//
//int WINAPI ShowCursor_detour(BOOL bShow) {
//    //TRACE("show={}", (bool)bShow);
//    return f.ShowCursor(bShow);
//}
//
//HWND WINAPI SetFocus_detour(HWND hWnd) {
//    return f.SetFocus(hWnd);
//    return false;
//    TRACE("hWnd={}", (void*)hWnd);
//    try {
//        //HWND prev = GetFocus();
//        glfwFocusWindow(windows.at(hWnd));
//        return hWnd;
//    }
//    catch (...) {
//        return f.SetFocus(hWnd);
//    }
//}
//
//BOOL WINAPI UpdateWindow_detour(HWND hWnd) {
//    return f.UpdateWindow(hWnd);
//}
//
//BOOL WINAPI ShowWindow_detour(HWND hWnd, int nCmdShow) {
//    //return true;
//    //TRACE("cmdShow={}", nCmdShow);
//    //return true;
//    return f.ShowWindow(hWnd, nCmdShow);
//}
//
//BOOL WINAPI GetClientRect_detour(HWND hWnd, LPRECT lpRect) {
//    auto r = f.GetClientRect(hWnd, lpRect);
//    //TRACE("result: left={} right={} bottom={} top={}", lpRect->left, lpRect->right, lpRect->bottom, lpRect->top);
//    return r;
//}
//
//HCURSOR WINAPI LoadCursorA_detour(HINSTANCE hInstance, LPCSTR lpCursorName) {
//    TRACE("");  // For some reason this crashes when accessing lpCursorName (which is not null)
//    return f.LoadCursorA(hInstance, lpCursorName);
//}
////
////int WINAPI MessageBoxA_detour(HWND hWnd, LPCSTR lpText, LPCSTR lpCaption, UINT uType) {
////    TRACE("text={} caption={} type={}", lpText, lpCaption, uType);
////    return f.MessageBoxA(hWnd, lpText, lpCaption, uType);
////}
//
//LONG WINAPI SetWindowLongA_detour(HWND hWnd, int nIndex, LONG dwNewLong) {
//    //return dwNewLong;
//    //TRACE("nIndex={} value={}", nIndex, dwNewLong);
//    //return 100;
//    return f.SetWindowLongA(hWnd, nIndex, dwNewLong);
//}
//
//LONG WINAPI GetWindowLongA_detour(HWND hWnd, int nIndex) {
//    auto r = f.GetWindowLongA(hWnd, nIndex);
//    //TRACE("nIndex={} return={}", nIndex, r);
//    return r;
//}
//
//BOOL WINAPI SetRect_detour(LPRECT lprc, int xLeft, int yTop, int xRight, int yBottom) {
//    //return true;
//    //TRACE("x={} y={}", lprc->left, lprc->right, lprc->bottom, lprc->top, xLeft, yTop, xRight, yBottom);
//    //return true;
//    return f.SetRect(lprc, xLeft, yTop, xRight, yBottom);
//}
//
//BOOL WINAPI GetCursorPos_detour(LPPOINT lpPoint) {
//    //TRACE("x={} y={}", lpPoint->x, lpPoint->y);
//    return f.GetCursorPos(lpPoint);
//}

void init() {
    /*Original o;
    LOG("original object = {}", (void*)&o);
    LOG("Calling original");
    (o.*f.Original_Function)();
    LOG("Calling original 2");
    o.Function();
    LOG("Calling original done");*/
}

void attach() {
    AllocConsole();
    freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);
    std::cout << "Hello from the G3 Hacker!" << std::endl;

    logger = spdlog::basic_logger_mt("G3", "logs/last.txt", true);

    LOG("Attaching detouring");
    DetourRestoreAfterWith();
    DetourTransactionBegin();
    DetourUpdateThread(GetCurrentThread());
    detour(false);
    DetourTransactionCommit();

    LOG("Attached detouring");
    init();

    /*if (!glfwInit()) {
        MessageBoxA(nullptr, "GLFW failed to initialize!", "Failure", MB_OK);
        return;
    }*/
}

gSScriptInit& GetScriptInit() {
    static gSScriptInit s_ScriptInit;
    return s_ScriptInit;
}

extern "C" __declspec(dllexport) gSScriptInit const* GE_STDCALL ScriptInit(void) {
    attach();
    return &GetScriptInit();
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            attach();
            break;

        case DLL_PROCESS_DETACH:
            spdlog::info("Detaching detouring");
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            detour(true);
            DetourTransactionCommit();
            spdlog::info("Detached detouring");

            //glfwTerminate();
            break;
    }
    return true;
}

