cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)
project(json-cpp
        VERSION 2019.1.0
        DESCRIPTION "Json c++ library"
        LANGUAGES CXX)

####
#### DEPENDENCIES
####

find_package (Dependencies QUIET)

if (NOT ${Dependencies_FOUND})
    if (NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/DependenciesConfig.cmake)
        file(DOWNLOAD https://raw.githubusercontent.com/germanespinosa/dependencies/main/DependenciesConfig.cmake ${CMAKE_CURRENT_BINARY_DIR}/DependenciesConfig.cmake)
    endif()
    set(Dependencies_DIR "${CMAKE_CURRENT_BINARY_DIR}")
    find_package (Dependencies REQUIRED)
endif()

####
#### END DEPENDENCIES
####

if ("${BUILD_PYTHON_MODULE_ONLY}" STREQUAL "")
    set (BUILD_PYTHON_MODULE_ONLY FALSE CACHE STRING "Builds only the python module")
endif()

set (json_cpp_core_files
        src/json_base.cpp
        src/json_base64.cpp
        src/json_buffer.cpp
        src/json_util.cpp
        src/json_builder.cpp
        src/json_object.cpp
        )

include_directories(include)

install_git_dependency( Catch
        https://github.com/cellworld/dependency_catch
        ADD_SUBDIRECTORY)

if (NOT ${BUILD_PYTHON_MODULE_ONLY})
    set (json_cpp_files
            ${json_cpp_core_files}
            src/json_date.cpp
            src/json_dictionary.cpp
            )

    install_git_dependency( Date
            https://github.com/cellworld/dependency_date
            INCLUDE_DIRECTORIES include )

    add_library(json-cpp ${json_cpp_files})

    target_include_directories(json-cpp
            SYSTEM INTERFACE
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
            $<INSTALL_INTERFACE:include>)

    set_target_properties( json-cpp
            PROPERTIES
            CXX_STANDARD 20
            CXX_STANDARD_REQUIRED On
            CXX_EXTENSIONS Off
            VERSION ${PROJECT_VERSION})

    target_compile_options(json-cpp PRIVATE -Wextra -pedantic -Wall -fPIC)

    ###
    ### TESTS
    ###

    add_catch_test( json-cpp_tests
            TEST_FILES
            catchtests/json_tests.cpp
            LINK_LIBRARIES json-cpp
            INCLUDE_DIRECTORIES
            include
            ${Date_Folder}/include)

    if (NOT ${BUILD_AS_DEPENDENCY})
        ###
        ### LIBRARY INSTALLATION
        ###

        export(TARGETS json-cpp FILE JsonCppConfig.cmake)

        include(GNUInstallDirs)

        install(TARGETS json-cpp EXPORT Json-cppConfig
                ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
                LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
                RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})

        install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

        install(EXPORT Json-cppConfig
                DESTINATION ${CMAKE_INSTALL_DATADIR}/cmake/Json-cpp
                EXPORT_LINK_INTERFACE_LIBRARIES)

        export(TARGETS json-cpp FILE Json-cppConfig.cmake)
    endif()
endif()