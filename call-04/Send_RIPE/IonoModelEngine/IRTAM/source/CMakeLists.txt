# Project
#
cmake_minimum_required (VERSION 2.8)
project(IrtamWrapper)

if(APPLE)
  set(CMAKE_MACOSX_RPATH 1)
  set(libname "irtampy_mac")
  set(irtam_os_specific_name "irtam_mac")
elseif(WIN32)
  message("NO WINDOWS YUCK!")
else()
  set(libname "irtampy_lin")
  set(irtam_os_specific_name "irtam_lin")
endif()

# Find all the dependencies
#
find_library(irtamlib NAMES ${irtam_os_specific_name} PATHS "${CMAKE_SOURCE_DIR}/../lib")

# Flags
#
set(CMAKE_BUILD_TYPE RELEASE)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -fPIC")

# Gather the sources
#
file(GLOB source_cpp "*.cpp")
file(GLOB source_h "*.h")

# Build the library
#
add_library(${libname} SHARED
            ${source_cpp}
            ${source_h})
target_link_libraries(${libname}
                      ${irtamlib})

# Install
#
set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/../")
install( TARGETS ${libname}
         RUNTIME DESTINATION bin
         LIBRARY DESTINATION lib
         ARCHIVE DESTINATION lib)
