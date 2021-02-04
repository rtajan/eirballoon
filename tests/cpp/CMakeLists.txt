cmake_minimum_required(VERSION 3.2)
cmake_policy(SET CMP0054 NEW)

project (test_cpp)

# Enable C++11
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Specify lib path
set (EXECUTABLE_OUTPUT_PATH bin/)

# Link with the "Threads library (required to link with AFF3CT after)
set(CMAKE_THREAD_PREFER_PTHREAD ON)
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

# Link with AFF3CT
set (AFF3CT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../py_aff3ct/cmake/Modules/")
find_package(AFF3CT CONFIG 2.3.2 REQUIRED)

file(GLOB_RECURSE SRC_FILES_CO ${CMAKE_CURRENT_SOURCE_DIR}/../../src/Module/*)
#file(GLOB_RECURSE PA_SRC_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../py_aff3ct/src/*)

add_library               (common STATIC ${SRC_FILES_CO}   )
target_link_libraries     (common PRIVATE aff3ct::aff3ct-static-lib)
target_include_directories(common PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../src)

# `pybind11_add_module` is a wrapper of the CMake `add_library` function
add_executable(test_cpp ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp)
target_link_libraries(test_cpp PRIVATE aff3ct::aff3ct-static-lib)
target_link_libraries(test_cpp PRIVATE common)
target_include_directories(test_cpp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../../src)
#target_include_directories(test_cpp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../../py_aff3ct/src)
