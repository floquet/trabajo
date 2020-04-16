# Copyright (C) 2017 Boston College and Systems & Technology Research, LLC.
# http://www.stresearch.com
# http://bc.edu
#
# STR & BC Proprietary Information
#
# US Government retains Unlimited Rights
# Non-Government Users – restricted usage as defined through
# licensing with STR or via arrangement with Government.
#
# In no event shall the initial developers or copyright holders be
# liable for any damages whatsoever, including - but not restricted
# to - lost revenue or profits or other direct, indirect, special,
# incidental or consequential damages, even if they have been
# advised of the possibility of such damages, except to the extent
# invariable law, if any, provides otherwise.
#
# The Software is provided AS IS with NO
# WARRANTY OF ANY KIND, INCLUDING THE WARRANTY OF DESIGN,
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

# Project
#
cmake_minimum_required (VERSION 3.0)
project(IonoFit)

if(APPLE)
  set(CMAKE_MACOSX_RPATH 1)
  set(libname "saopy_mac")
  set(sao_os_specific_name "sao_mac")
elseif(WIN32)
  message("NO WINDOWS YUCK!")
else()
  set(libname "saopy_lin")
  set(sao_os_specific_name "sao_lin")
endif()

# Find all the dependencies
#
find_library(saolib NAMES ${sao_os_specific_name} PATHS "${CMAKE_SOURCE_DIR}/../lib")

# Complie Flags
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
                      ${saolib})

# Install
#
set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/../")
install( TARGETS ${libname}
         RUNTIME DESTINATION bin
         LIBRARY DESTINATION lib
         ARCHIVE DESTINATION lib)