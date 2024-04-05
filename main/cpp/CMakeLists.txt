cmake_minimum_required(VERSION 3.10)

set(CMAKE_CXX_STANDARD 20)

project(cellworld_vr_server
        VERSION 2019.1.0
        DESCRIPTION "A server for the cellworld vr Experiment"
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

install_git_dependency( Cellworld-Experiment-Service
        https://github.com/cellworld/cellworld_experiment_service
        PRIVATE
        CMAKE_PROJECT
        IMPORT_TARGETS
        json-cpp cellworld experiment_service tcp_messages)


install_git_dependency( Cellworld-Tracking-Service
        https://github.com/cellworld/cellworld_agent_tracking
        PRIVATE
        CMAKE_PROJECT
        IMPORT_TARGETS
        agent_tracking  )


####
#### MAIN LIBRARY SETUP
####


set (cellworld_vr_server_files
        src/vr_server.cpp)

include_directories(include)

add_library(vr_server
${cellworld_vr_server_files})

target_link_libraries(vr_server
        LINK_PUBLIC
        experiment_service
        agent_tracking
        cellworld
        json-cpp
        tcp_messages )


add_executable(server
        src/main.cpp )

target_link_libraries(server
        vr_server)