cmake_minimum_required(VERSION 3.5.2)
enable_language(Fortran)

add_subdirectory(Driver)

# Specific project settings
project(ESMX VERSION 0.1.0)
add_executable(esmx_app ESMX_App.F90)
target_include_directories(esmx_app PUBLIC ${PROJECT_BINARY_DIR})
target_link_libraries(esmx_app PUBLIC esmx_driver)

