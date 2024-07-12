cmake_minimum_required(VERSION 3.10)

set(CMAKE_CXX_STANDARD 20)

project(experiment_service
        VERSION 2019.1.0
        DESCRIPTION "experiment services"
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

string(APPEND CMAKE_CXX_FLAGS " -fno-strict-aliasing -pthread ")

include_directories(include)

set(experiment_service_files
        src/experiment_client.cpp
        src/experiment_service.cpp
        )

install_git_dependency(Cellworld
        https://github.com/cellworld/cellworld
        CMAKE_PROJECT
        IMPORT_TARGETS cellworld requests json-cpp)

install_git_dependency(Agent_tracking https://github.com/cellworld/cellworld_agent_tracking
        CMAKE_PROJECT
        IMPORT_TARGETS agent_tracking
        INCLUDE_DIRECTORIES include)

add_library(experiment_service ${experiment_service_files})

install_git_dependency( Perf-analysis
        https://github.com/cellworld/dependency_perf-analysis
        CMAKE_PROJECT
        IMPORT_TARGETS perf-analysis
        INCLUDE_DIRECTORIES include)

target_link_libraries( experiment_service perf-analysis )
#
#add_executable(experiment_server src/tools/server.cpp)
#
#target_link_libraries(experiment_server
#        PUBLIC
#        experiment_service
#        params-cpp
#        json-cpp )

###
### TESTS
###
#install_dependency(https://github.com/cellworld/dependency_catch CatchTests)
#test_library(experiment_service catchtests/client_test.cpp)



###
### LIBRARY INSTALLATION
###

include(GNUInstallDirs)

install(TARGETS experiment_service EXPORT Experiment_serviceConfig
        ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(EXPORT Experiment_serviceConfig
        DESTINATION ${CMAKE_INSTALL_DATADIR}/cmake/Experiment_service
        EXPORT_LINK_INTERFACE_LIBRARIES)

export(TARGETS experiment_service FILE Experiment_serviceConfig.cmake)
