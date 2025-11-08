# CMakeLists.txt for VALORAIPLUS System
cmake_minimum_required(VERSION 3.10)

# Project Name and Version
project(VALORAIPLUS VERSION 6.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- valoraiplus_newt25 Library ---
# This library encapsulates the NEWT25 EMP/EMI defensive simulation module.
# It is built as a static library so it can be easily linked into other
# components of the VALORAIPLUS system.

add_library(valoraiplus_newt25 STATIC
    src/newt25.cpp
)

# Add the include directory for the library and for downstream targets
target_include_directories(valoraiplus_newt25 PUBLIC
    "${PROJECT_SOURCE_DIR}/include"
)

# --- Optional Executable for Testing ---
# This executable provides a simple way to test the newt25 library.
# It is not required for the final integration but is good practice.
enable_testing()

add_executable(run_newt25_tests tests/run_tests.cpp)
target_link_libraries(run_newt25_tests valoraiplus_newt25)

# Add a simple test
add_test(NAME Newt25Test COMMAND run_newt25_tests)
