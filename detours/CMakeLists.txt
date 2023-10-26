
add_library(detours INTERFACE)
add_library(detours::detours ALIAS detours)

target_include_directories(detours INTERFACE "${CMAKE_CURRENT_LIST_DIR}/include")
target_link_libraries(detours INTERFACE "${CMAKE_CURRENT_LIST_DIR}/lib/detours.lib")