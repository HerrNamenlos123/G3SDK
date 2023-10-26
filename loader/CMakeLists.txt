
# All source files
set(SOURCES
	main.cpp
)

# The DLL library
add_library(G3Loader SHARED ${SOURCES} "CMakeLists.txt")

# How to group the files in the Solution Explorer
source_group(TREE "${CMAKE_CURRENT_LIST_DIR}/" PREFIX "" FILES ${SOURCES})

# Properties of the DLL
target_compile_features(G3Loader PUBLIC cxx_std_14)			# C++14
target_compile_options(G3Loader PUBLIC /Od)					# Disable optimizations to make Detours work
target_compile_options(G3Loader PUBLIC /Zc:preprocessor)    # Force the standards-compliant preprocessor

# Where the DLL is written to
set_target_properties(G3Loader PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE "${GOTHIC3_DIR}")