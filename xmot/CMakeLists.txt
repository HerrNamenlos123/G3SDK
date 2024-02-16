cmake_minimum_required(VERSION 3.16)
project(test)

add_executable(test test.cpp)
target_compile_features(test PRIVATE cxx_std_20)
