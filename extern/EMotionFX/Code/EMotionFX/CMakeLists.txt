
include(emotionfx_files.cmake)
add_library(emotionfx STATIC ${FILES})
target_include_directories(emotionfx PUBLIC Source)

add_subdirectory(../MCore MCore)
target_link_libraries(emotionfx PUBLIC MCore)
