
include(mcore_files.cmake)
add_library(MCore STATIC ${FILES})
target_include_directories(MCore PUBLIC Source)
target_include_directories(MCore PUBLIC ..)
