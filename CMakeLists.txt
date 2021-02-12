cmake_minimum_required(VERSION 3.2)
cmake_policy(SET CMP0054 NEW)

project (eirballoon)

# Enable C++11
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Specify lib path
set(LIBRARY_OUTPUT_PATH lib/)

# Link with the "Threads library (required to link with AFF3CT after)
set(CMAKE_THREAD_PREFER_PTHREAD ON)
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

# Link with AFF3CT
set (AFF3CT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/py_aff3ct/cmake/Modules/")
find_package(AFF3CT CONFIG 2.3.2 REQUIRED)

add_subdirectory(py_aff3ct/lib/pybind11)

file(GLOB_RECURSE SRC_FILES_CO ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/*)
file(GLOB_RECURSE PA_SRC_FILES ${CMAKE_CURRENT_SOURCE_DIR}/py_aff3ct/src/*)

# `pybind11_add_module` is a wrapper of the CMake `add_library` function
pybind11_add_module(eirballoon-lib MODULE ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp/Wrapper/wrapper.cpp ${SRC_FILES_CO})
set_target_properties(eirballoon-lib PROPERTIES
                                           OUTPUT_NAME eirballoon
                                           POSITION_INDEPENDENT_CODE ON) # set -fpic
target_link_libraries(eirballoon-lib PRIVATE aff3ct::aff3ct-static-lib)
target_include_directories(eirballoon-lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp)
target_include_directories(eirballoon-lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/py_aff3ct/src)
# Link with UHD (& boost)
option(LINK_UHD "Link with the UHD library (used in the radio USRP)" ON)
if(LINK_UHD)
    message(STATUS "UHD: on")
    target_compile_definitions(eirballoon-lib PUBLIC
                               $<BUILD_INTERFACE:LINK_UHD>
                               $<INSTALL_INTERFACE:LINK_UHD>)

    # Link UHD
    find_package (UHD REQUIRED)
    if    (UHD_FOUND)
        include_directories(${UHD_INCLUDE_DIRS})
        target_link_libraries(eirballoon-lib PRIVATE ${UHD_LIBRARIES})
    endif (UHD_FOUND)

    # Link Boost
    find_package(Boost QUIET COMPONENTS system filesystem thread REQUIRED)
    if (Boost_FOUND)
        target_link_libraries(eirballoon-lib PRIVATE ${Boost_FILESYSTEM_LIBRARY}
                                                     ${Boost_SYSTEM_LIBRARY}
                                                     ${Boost_THREAD_LIBRARY})
    endif (Boost_FOUND)
else()
    message(STATUS "UHD: off")
endif(LINK_UHD)