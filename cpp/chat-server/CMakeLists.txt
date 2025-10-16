cmake_minimum_required(VERSION 3.25)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL" CACHE STRING "MSVC runtime" FORCE)

project(chat-server VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(asio CONFIG REQUIRED)

add_library(project_options INTERFACE)
target_compile_features(project_options INTERFACE cxx_std_23)
set_target_properties(project_options PROPERTIES CXX_EXTENSIONS OFF)
target_link_libraries(project_options INTERFACE asio::asio)

target_compile_options(project_options INTERFACE
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

target_link_options(project_options INTERFACE
    $<$<CONFIG:Debug>:-fsanitize=address;-fsanitize=undefined>
)

add_subdirectory(chat-client)
add_subdirectory(chat-server)

message(STATUS "CMake Build Type: ${CMAKE_BUILD_TYPE}")
get_target_property(_CFLAGS project_options COMPILE_OPTIONS)
message(STATUS "project_options} compile options: ${_CFLAGS}")
get_target_property(_LFLAGS project_options LINK_OPTIONS)
message(STATUS "project_options} link options: ${_LFLAGS}")
