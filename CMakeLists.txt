cmake_minimum_required(VERSION 3.16)
set(CMAKE_GENERATOR_PLATFORM Win32 CACHE STRING "" FORCE)
set(CMAKE_CONFIGURATION_TYPES Release CACHE STRING "" FORCE)
project(G3Dll)

# Gothic 3 installation folder
set(GOTHIC3_DIR "C:/Program Files (x86)/Steam/steamapps/common/Gothic 3")

# All header files (needed to be listed in Visual Studio)
set(HEADERS
	include/framework.h
	include/old.h
	include/pch.h
	include/Engine.dll.h
	include/types.h
	include/commontypes.h
	include/formatters.h
)

# All source files
set(SOURCES
	src/dllmain.cpp
	src/framework.cpp
	src/commontypes.cpp
)

# The DLL library
add_library(${PROJECT_NAME} SHARED ${SOURCES} ${HEADERS} "detours/CMakeLists.txt")
target_include_directories(${PROJECT_NAME} PUBLIC "include")

# How to group the files in the Solution Explorer
source_group(TREE "${CMAKE_CURRENT_LIST_DIR}/src" PREFIX "src" FILES ${SOURCES})
source_group(TREE "${CMAKE_CURRENT_LIST_DIR}/include" PREFIX "include" FILES ${HEADERS})
source_group(TREE "${CMAKE_CURRENT_LIST_DIR}/detours" PREFIX "detours" FILES "detours/CMakeLists.txt")

# Import the loader DLL to be also built
add_subdirectory(loader)

# Import the Microsoft Detours library (MIT License)
add_subdirectory(detours)
target_link_libraries(${PROJECT_NAME} detours)

# Import the spdlog library (MIT License)
add_subdirectory(spdlog)
target_link_libraries(${PROJECT_NAME} spdlog::spdlog)

# Import the GLFW library (Zlib License)
set(GLFW_BUILD_EXAMPLES OFF)
set(GLFW_BUILD_TESTS OFF)
set(GLFW_BUILD_DOCS OFF)
set(GLFW_INSTALL OFF)
add_subdirectory(glfw)
target_link_libraries(${PROJECT_NAME} glfw)

# Import other external dependencies like EMotionFX
#add_subdirectory(extern)

# Import the import libs of Gothic itself
target_include_directories(${PROJECT_NAME} PUBLIC ../gothic3sdk/source)
#target_link_libraries(${PROJECT_NAME} ${GOTHIC3_DIR}/Engine.lib)
#target_link_libraries(${PROJECT_NAME} ${GOTHIC3_DIR}/SharedBase.lib)
target_link_directories(${PROJECT_NAME} PUBLIC ../gothic3sdk/lib)
target_link_libraries(${PROJECT_NAME} SharedBase.lib)
target_link_libraries(${PROJECT_NAME} Engine.lib)
target_link_libraries(${PROJECT_NAME} Game.lib)
target_link_libraries(${PROJECT_NAME} Script.lib)
target_link_libraries(${PROJECT_NAME} GFC.lib)
#target_link_libraries(${PROJECT_NAME} emotionfx)

# Properties of the DLL
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)			# C++17
target_compile_options(${PROJECT_NAME} PUBLIC /Od)					# Disable optimizations to make Detours work
#target_compile_options(${PROJECT_NAME} PUBLIC /Zc:preprocessor)	    # Force the standards-compliant preprocessor
target_precompile_headers(${PROJECT_NAME} PRIVATE "include/pch.h")  # Precompiled headers to speed up compilation
add_dependencies(${PROJECT_NAME} G3Loader)							# Make it depend on the other DLL
target_link_libraries(${PROJECT_NAME} dbghelp)						# Link to dbghelp.lib

# How to handle CMake-generated targets
set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set(PREDEFINED_TARGETS_FOLDER "CMakePredefinedTargets")
set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT ${PROJECT_NAME})

# Where the DLL is written to
set_target_properties(${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE "${GOTHIC3_DIR}")

# Catch wrong compilers
if (NOT WIN32 OR NOT MSVC)
	message(FATAL_ERROR "This project can only built using Visual Studio on Windows!")
endif ()
