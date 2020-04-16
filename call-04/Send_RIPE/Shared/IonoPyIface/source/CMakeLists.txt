# Copyright (C) 2017 Systems & Technology Research, LLC.
# http://www.stresearch.com
#
# STR Proprietary Information
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
cmake_minimum_required (VERSION 2.6)
project(IonoWrapper)

# OS detect 
#
if(APPLE)
  set(CMAKE_MACOSX_RPATH 1)
  set(libname "ionopyiface_mac")
  set(iri_bc_os_specific_name "iri2016_bc_mac")
  set(iri_pharlap_os_specific_name "iri2016_pharlap_mac")
  set(pharlap_os_specific_name "propagation_pharlap_mac")
  set(math_pharlap_os_specific_name "maths_pharlap_mac")
  set(system_libs "/usr/local/Cellar/gcc/7.1.0/lib/gcc/7/libgfortran.a" "/opt/intel/lib/libifcore.a" "/opt/intel/lib/libiomp5.a")
elseif(WIN32)
  message("NO WINDOWS YUCK!")
else()
  set(libname "ionopyiface_lin")
  set(iri_bc_os_specific_name "iri2016_bc_lin")
  set(iri_pharlap_os_specific_name "iri2016_pharlap_lin")
  set(pharlap_os_specific_name "propagation_pharlap_lin")
  set(math_pharlap_os_specific_name "maths_pharlap_lin")
  set(system_libs "/usr/lib64/libgfortran.so.3.0.0" "/opt/intel/lib/intel64/libifcore_pic.a")
endif()

# Find all the dependencies
#
find_library(iri2016_bc_lib NAMES ${iri_bc_os_specific_name} PATHS "${CMAKE_SOURCE_DIR}/../../IRI2016bc/lib")
find_library(iri2016_pharlab_lib NAMES ${iri_pharlap_os_specific_name} PATHS "${CMAKE_SOURCE_DIR}/../../Pharlap_4.2.0/lib")
find_library(pharlap_lib NAMES ${pharlap_os_specific_name} PATHS "${CMAKE_SOURCE_DIR}/../../Pharlap_4.2.0/lib")
find_library(math_pharlap_lib NAMES ${math_pharlap_os_specific_name} PATHS "${CMAKE_SOURCE_DIR}/../../Pharlap_4.2.0/lib")

# Complie Flags
#
set(CMAKE_CXX_COMPILER "/opt/intel/bin/icpc")
set(CMAKE_BUILD_TYPE RELEASE)
set(CMAKE_CXX_FLAGS "-std=c++11 -O3 -fPIC -static-intel")

# Gather up all the source files
#
set(pharlap_headers "${CMAKE_SOURCE_DIR}/../../Pharlap_4.2.0/headers/")
include_directories(pharlap_headers)
file(GLOB source_cpp "*.cpp")
file(GLOB source_h "*.h" "${pharlap_headers}/*.h")

# Build the library
#
# HNH: NOTE WE CANNOT HAVE IRIBC AND IRIPHARLAP AT THE SAME TIME
add_library(${libname} SHARED
            ${source_cpp}
            ${source_h})
target_link_libraries(${libname}
                      ${iri2016_pharlab_lib}
                      ${pharlap_lib}
                      ${math_pharlap_lib}
                      ${system_libs})

# Install
#
set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/../")
install( TARGETS ${libname}
         RUNTIME DESTINATION bin
         LIBRARY DESTINATION lib
         ARCHIVE DESTINATION lib)
