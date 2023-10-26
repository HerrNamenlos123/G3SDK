
#include "framework.h"

G3API void dummy() {}   // This export is necessary to make the DLL linkable

HINSTANCE loadDll(const std::string& dll) {
    static std::unordered_map<std::string, HINSTANCE> loadedDlls;
    if (loadedDlls.find(dll) != loadedDlls.end()) {
        return loadedDlls[dll];
    }

    HINSTANCE handle = LoadLibraryA(dll.c_str());
    if (!handle) {
        std::cerr << "Failed to load DLL Importer - Original.dll" << std::endl;
        abort();
        return nullptr;
    }
    loadedDlls[dll] = handle;
    return handle;
}