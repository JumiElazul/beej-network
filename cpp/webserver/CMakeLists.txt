cmake_minimum_required(VERSION 3.25)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL" CACHE STRING "MSVC runtime" FORCE)

project(main VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(SOURCES
    "main.cpp"
)

add_executable(${PROJECT_NAME} ${SOURCES})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_EXTENSIONS OFF)

target_compile_options(${PROJECT_NAME} PRIVATE
    -Wall
    -Wextra
    -pedantic-errors
    -Wno-unused-parameter
    -Wshadow
    -Wconversion
    -Wno-switch-enum
    -fsigned-char

    $<$<CONFIG:Debug>:-fsanitize=address;-fsanitize=undefined>

    $<$<CONFIG:Release>:-O3>
)

target_link_options(${PROJECT_NAME} PRIVATE
    $<$<CONFIG:Debug>:-fsanitize=address;-fsanitize=undefined>
)

message(STATUS "CMake Build Type: ${CMAKE_BUILD_TYPE}")
get_target_property(_CFLAGS ${PROJECT_NAME} COMPILE_OPTIONS)
message(STATUS "${PROJECT_NAME} compile options: ${_CFLAGS}")
get_target_property(_LFLAGS ${PROJECT_NAME} LINK_OPTIONS)
message(STATUS "${PROJECT_NAME} link options: ${_LFLAGS}")
