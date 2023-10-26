#pragma once

#define WIN32_LEAN_AND_MEAN             // Exclude rarely-used stuff from Windows headers
// Windows Header Files
#include <windows.h>
#include <detours.h>

#ifndef SPDLOG_COMPILED_LIB
#define SPDLOG_COMPILED_LIB
#endif
#include "spdlog/spdlog.h"
#include "spdlog/fmt/ranges.h"
#include "spdlog/sinks/basic_file_sink.h"

#include <iostream>
#include <unordered_map>
#include <sstream>

extern std::shared_ptr<spdlog::logger> logger;

#define G3API __declspec(dllexport)
#define LOG(...) { spdlog::info(__VA_ARGS__); logger->info(__VA_ARGS__); }
#define LOG_WARN(...) { spdlog::warn(__VA_ARGS__); logger->warn(__VA_ARGS__); }
#define LOG_ERR(...) { spdlog::error(__VA_ARGS__); logger->error(__VA_ARGS__); }
#define SILENT_TRACE(...) ScopedTimerWarner __t(__FUNCTION__);
#define TRACE(...) ScopedTimerWarner __t(__FUNCTION__); LOG(__FUNCTION__"() {}", fmt::format(__VA_ARGS__))
#define SCOPE_TRACE(...) ScopedTracePrinter __st(__FUNCTION__); TRACE(__VA_ARGS__)
#define BREAK() MessageBoxA(nullptr, __FUNCTION__, "break", MB_OK)
#define BREAK_MSG(...) MessageBoxA(nullptr, fmt::format(__FUNCTION__": {}", fmt::format(__VA_ARGS__)).c_str(), "break", MB_OK)

class ScopedTracePrinter {
public:
    ScopedTracePrinter(const std::string& func) : func(func) {
        LOG("{} Start", func);
    }

    ~ScopedTracePrinter() {
        LOG("{} End", func);
    }

private:
    std::string func;
};

class ScopedTimerWarner {
public:
    ScopedTimerWarner(const std::string& func) : func(func) {
        start = std::chrono::high_resolution_clock::now();
    }

    ~ScopedTimerWarner() {
        auto now = std::chrono::high_resolution_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start).count();
        int limit = 50;
        if (elapsed > limit) {
            LOG_ERR("WARNING: {} took more than {}ms: Took {}ms", func, limit, elapsed);
        }
    }

private:
    std::string func;
    std::chrono::steady_clock::time_point start;
};

inline std::string threadid() {
    std::stringstream ss;
    ss << std::this_thread::get_id();
    return ss.str();
}

HINSTANCE loadDll(const std::string& dll);

template <typename T>
T getDllFunc(const char* dll, const char* symbolName) {
    FARPROC raw = GetProcAddress(loadDll(dll), symbolName);
    if (raw == nullptr) {
        BREAK_MSG("{} was not found in {}", symbolName, dll);
        std::terminate();
    }
    T f;
    *(FARPROC*)&f = raw;
    return f;
}

template<typename... TArgs>
inline LONG Detour(bool detach, TArgs&&... args) {
    if (!detach) {
        return DetourAttach(std::forward<TArgs>(args)...);
    }
    else {
        return DetourDetach(std::forward<TArgs>(args)...);
    }
}

#define DETOUR_DECLARE_WINAPI(function) decltype(&function) function;
#define DETOUR_WINAPI(function) \
    f.function = function; \
    Detour(detach, reinterpret_cast<PVOID*>(&f.function), function##_detour);

//#define DETOUR_DECLARE_MEMBER(classname, function) decltype(&classname::function) classname##_##function;
//#define DETOUR_EXTERN_MEMBER(classname, function, dll, symbol) \
//    if (!detach) { \
//        f.classname##_##function = getDllFunc<decltype(&classname::function)>(dll, symbol); \
//        auto classname##_##function##_tmp = &classname::function; \
//        DetourAttach(reinterpret_cast<PVOID*>(&f.classname##_##function), *(PBYTE*)&classname##_##function##_tmp); \
//    } \
//    else { \
//        auto classname##_##function##_tmp = &classname::function; \
//        DetourDetach(reinterpret_cast<PVOID*>(&f.classname##_##function), *(PBYTE*)&classname##_##function##_tmp); \
//    }

#define DETOUR_DECLARE_MEMBER(function, dll, symbol) \
    inline static auto function##_original = getDllFunc<decltype(&function)>(dll, symbol);

#define DETOUR_EXTERN_MEMBER(classname, function) \
    auto classname##_##function##_tmp = &classname::function; \
    Detour(detach, &(PVOID&)classname::function##_original, *(PBYTE*)&classname##_##function##_tmp);