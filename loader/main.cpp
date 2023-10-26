
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <iostream>
#include <thread>
#include <atomic>
#include <unordered_map>

static std::unique_ptr<std::thread> loaderThread;
static std::atomic<bool> shouldTerminate = false;
static std::unordered_map<std::string, HINSTANCE> dlls;

bool getKey(int key) {
    return (1 << 15) & GetAsyncKeyState(key);
}

void load(const std::string& dll) {
    if (dlls.find(dll) != dlls.end()) {
        std::cout << dll << " already loaded" << std::endl;
        return;
    }

    std::cout << "Loading " << dll << "..." << std::endl;
    HINSTANCE handle = LoadLibraryA(dll.c_str());
    if (!handle) {
        std::cerr << "Failed to load DLL " << dll << std::endl;
        system("Pause");
        return;
    }
    dlls[dll] = handle;
    std::cout << dll << " loaded successfully" << std::endl;
}

void unload(const std::string& dll) {
    try {
        std::cout << "Freeing " << dll << "..." << std::endl;
        FreeLibrary(dlls.at(dll));
        dlls.erase(dlls.find(dll));
        std::cout << dll << " freed successfully" << std::endl;
    }
    catch (...) {
        std::cout << dll << " was not loaded" << std::endl;
    }
}

void G3Loader() {
    std::cout << "Hello from the G3 Loader thread! I will hot-reload your DLLs! \nPress F2 to load, F3 to unload, or F11 to immediately terminate." << std::endl;

    while (!shouldTerminate) {
        if (getKey(VK_F2)) {
            std::cout << "F2: Loading G3Dll.dll" << std::endl;
            load("G3Dll.dll");
            while (getKey(VK_F2));
        }

        if (getKey(VK_F3)) {
            std::cout << "F3: Unloading G3Dll.dll" << std::endl;
            unload("G3Dll.dll");
            while (getKey(VK_F3));
        }

        if (getKey(VK_F11)) {
            std::cout << "F11: Terminating application" << std::endl;
            std::terminate();
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

void attach() {
    AllocConsole();
    freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);
    
    shouldTerminate = false;
    loaderThread = std::make_unique<std::thread>(G3Loader);
}

void detach() {
    shouldTerminate = true;
    loaderThread.reset();
}

__declspec(dllexport) void dummy() {} // Necessary to make the DLL linkable

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        attach();
        break;

    case DLL_THREAD_ATTACH:
        break;

    case DLL_THREAD_DETACH:
        break;

    case DLL_PROCESS_DETACH:
        detach();
        break;
    }
    return true;
}

