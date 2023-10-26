#pragma once

#include "types.h"

class bCStringFormat : public bCString {
public:
    bCStringFormat() = default;
    bCStringFormat(const bCString& str) : bCString(str) {}
    virtual ~bCStringFormat() = default;
    std::string str() const {
        if (m_pcText != nullptr) {
            return m_pcText;
        }
        else {
            return "null";
        }
    }
};

template<> struct fmt::formatter<bCString> {
    constexpr auto parse(format_parse_context& ctx) -> decltype(ctx.begin()) {
        return ctx.end();
    }
    template <typename FormatContext>
    auto format(const bCString& input, FormatContext& ctx) -> decltype(ctx.out()) {
        return format_to(ctx.out(), "{}", bCStringFormat(input).str());
    }
};

template<> struct fmt::formatter<bCVector> {
    constexpr auto parse(format_parse_context& ctx) -> decltype(ctx.begin()) {
        return ctx.end();
    }
    template <typename FormatContext>
    auto format(const bCVector& vec, FormatContext& ctx) -> decltype(ctx.out()) {
        return format_to(ctx.out(), "({}, {}, {})", vec.x, vec.y, vec.z);
    }
};

inline std::string str(const bCString& str) {
    return bCStringFormat(str).str();
}
