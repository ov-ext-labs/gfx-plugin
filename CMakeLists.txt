cmake_minimum_required(VERSION 3.20)
project(ovx_gfx_plugin LANGUAGES CXX)

option(OVX_ENABLE_TESTS "Build ovx-gfx-plugin tests" ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(ovx_gfx_plugin SHARED
    src/plugin.cpp
)

target_include_directories(ovx_gfx_plugin
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

install(TARGETS ovx_gfx_plugin DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)

if(OVX_ENABLE_TESTS)
    enable_testing()
    add_executable(ovx_gfx_plugin_unit_tests tests/unit/plugin_unit_test.cpp)
    target_link_libraries(ovx_gfx_plugin_unit_tests PRIVATE ovx_gfx_plugin)
    add_test(NAME ovx_gfx_plugin_unit_tests COMMAND ovx_gfx_plugin_unit_tests)
endif()
