set(DEPENDENCIES_IGNORE "${CMAKE_C_COMPILER}")
set(DEPENDENCIES_IGNORE "${CMAKE_CPP_COMPILER}")

function (git_dependencies_log)
    cmake_parse_arguments(LOG "ERROR;WARNING;STATUS;ACTION;RESULT" "" "" ${ARGN} )
    foreach(LOG_DATA ${LOG_UNPARSED_ARGUMENTS})
        if(NOT "${LOG_DATA}" STREQUAL "")
            if (${LOG_ERROR})
                set(LOG_TYPE "ERROR")
                message(${LOG_DATA})
            endif()
            if (${LOG_WARNING})
                set(LOG_TYPE "WARNING")
            endif()
            if (${LOG_ACTION})
                set(LOG_TYPE "ACTION")
            endif()
            if (${LOG_RESULT})
                set(LOG_TYPE "RESULT")
            endif()
            if (${LOG_STATUS})
            endif()
            string(TIMESTAMP LOG_TIME_STAMP)
            file(APPEND "${DEPENDENCIES_LOG_FILE}" "${LOG_TIME_STAMP} ${LOG_TYPE}: ${LOG_DATA}\n")
        endif()
    endforeach()
endfunction()

execute_process(COMMAND git --exec-path
        RESULT_VARIABLE GIT_TEST_RESULT
        OUTPUT_VARIABLE GIT_TEST_OUTPUT )

if (${GIT_TEST_RESULT} EQUAL 0)
    string(STRIP ${GIT_TEST_OUTPUT} GIT_TEST_OUTPUT)

    string(STRIP ${GIT_TEST_OUTPUT} GIT_LOCATION)

    execute_process(COMMAND git --version
            RESULT_VARIABLE GIT_TEST_RESULT
            OUTPUT_VARIABLE GIT_TEST_OUTPUT )

    string(STRIP ${GIT_TEST_OUTPUT} GIT_TEST_OUTPUT)
    string(REPLACE " " ";" GIT_VERSION_LIST ${GIT_TEST_OUTPUT})

    list(LENGTH GIT_VERSION_LIST GIT_VERSION_LIST_LEN)
    math(EXPR GIT_VERSION_LIST_LAST "${GIT_VERSION_LIST_LEN} - 1")
    list(GET GIT_VERSION_LIST ${GIT_VERSION_LIST_LAST} GIT_VERSION)
    file(TO_CMAKE_PATH "${GIT_LOCATION}/git" GIT_LOCATION_NATIVE)
    message(STATUS "Found GIT: ${GIT_LOCATION_NATIVE} (found version \"${GIT_VERSION}\")")
else()
    message(FATAL_ERROR "Git not found.")
endif()

set_property(GLOBAL PROPERTY source_list_property "${source_list}")
option(CONNECT_ALL_DEPENDENCIES "Leave all git dependencies connected to their repositories" OFF)
option(BUILD_AS_DEPENDENCY "Build this project as a dependency" OFF)

if (NOT "${DEPENDENCIES_FOLDER}" STREQUAL "")
    set(DEPENDENCIES_FOLDER "${DEPENDENCIES_FOLDER}" CACHE STRING "Dependencies folder")
else()
    set(DEPENDENCIES_FOLDER "${CMAKE_CURRENT_SOURCE_DIR}/git-dependencies" CACHE STRING "Dependencies folder")
endif()

if (NOT "${DEPENDENCIES_DESTINATION}" STREQUAL "")
    set(DEPENDENCIES_DESTINATION "${DEPENDENCIES_DESTINATION}" CACHE STRING "Dependencies destination folder")
else()
    set(DEPENDENCIES_DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/git-dependencies" CACHE STRING "Dependencies destination folder")
endif()

if (NOT "${DEPENDENCIES_LOG_FILE}" STREQUAL "")
    set(DEPENDENCIES_LOG_FILE "${DEPENDENCIES_LOG}" CACHE STRING "Git-Dependencies log file")
else()
    set(DEPENDENCIES_LOG_FILE "${CMAKE_CURRENT_BINARY_DIR}/git-dependencies.log" CACHE STRING "Git-Dependencies log file")
endif()

if (NOT ${BUILD_AS_DEPENDENCY} OR "${DEPENDENCIES_BUILD_NUMBER}" STREQUAL "")
    string(RANDOM LENGTH 10 DEPENDENCIES_BUILD_NUMBER)
    set(DEPENDENCIES_BUILD_NUMBER "${DEPENDENCIES_BUILD_NUMBER}" CACHE STRING "Git-Dependencies build number")
    git_dependencies_log(ACTION "Build ${DEPENDENCIES_BUILD_NUMBER} started")
else()
    set(DEPENDENCIES_BUILD_NUMBER "${DEPENDENCIES_BUILD_NUMBER}" CACHE STRING "Git-Dependencies build number")
endif()

if (NOT EXISTS ${DEPENDENCIES_FOLDER})
    git_dependencies_log(ACTION "Creating ${DEPENDENCIES_FOLDER} folder")
    make_directory(${DEPENDENCIES_FOLDER})
endif()

if (NOT EXISTS ${DEPENDENCIES_DESTINATION}/CMakeLists.txt)
    git_dependencies_log(ACTION "Creating dependency cmake wrapper")
    file(WRITE "${DEPENDENCIES_DESTINATION}/CMakeLists.txt"
"project(Dependencies)
set(DEPENDENCY_TARGETS_FOLDER \"\${CMAKE_CURRENT_BINARY_DIR}\")
add_subdirectory(\${DEPENDENCIES_FOLDER}/\${DEPENDENCY} build)
get_property(DEPENDENCY_TARGETS DIRECTORY \${DEPENDENCIES_FOLDER}/\${DEPENDENCY} PROPERTY BUILDSYSTEM_TARGETS)
get_property(DEPENDENCY_INCLUDE_DIRECTORIES DIRECTORY \${DEPENDENCIES_FOLDER}/\${DEPENDENCY} PROPERTY INCLUDE_DIRECTORIES)
set(DEPENDENCY_LIBRARY_TARGETS \"\")
if (EXISTS \"\${CMAKE_CURRENT_BINARY_DIR}/dependency-imported_targets.txt\")
    file(READ \"\${CMAKE_CURRENT_BINARY_DIR}/dependency-imported_targets.txt\" DEPENDENCY_LIBRARY_TARGETS)
endif()
foreach(DEPENDENCY_TARGET \${DEPENDENCY_TARGETS})
    get_target_property(DEPENDENCY_TARGET_TYPE \${DEPENDENCY_TARGET} TYPE)
    if (NOT \"\${DEPENDENCY_TARGET_TYPE}\" MATCHES \"LIBRARY\")
        continue()
    endif()
    if (\"\${DEPENDENCY_TARGET_TYPE}\" MATCHES \"INTERFACE_LIBRARY\")
        continue()
    endif()
    list(APPEND DEPENDENCY_LIBRARY_TARGETS \${DEPENDENCY_TARGET})
    get_target_property(DEPENDENCY_TARGET_PATH \${DEPENDENCY_TARGET} BINARY_DIR)
    get_target_property(DEPENDENCY_TARGET_INCLUDE_DIRECTORIES \${DEPENDENCY_TARGET} INCLUDE_DIRECTORIES)
    get_target_property(DEPENDENCY_TARGET_LINK_LIBRARIES \${DEPENDENCY_TARGET} LINK_LIBRARIES)
    file(WRITE \"\${CMAKE_CURRENT_BINARY_DIR}/dependency_\${DEPENDENCY_TARGET}-path.txt\" \"\${DEPENDENCY_TARGET_PATH}\")
    file(WRITE \"\${CMAKE_CURRENT_BINARY_DIR}/dependency_\${DEPENDENCY_TARGET}-include_directories.txt\" \"\${DEPENDENCY_TARGET_INCLUDE_DIRECTORIES}\")
    if (NOT \"\${DEPENDENCY_TARGET_LINK_LIBRARIES}\" MATCHES \"NOTFOUND\")
        file(WRITE \"\${CMAKE_CURRENT_BINARY_DIR}/dependency_\${DEPENDENCY_TARGET}-link_libraries.txt\" \"\${DEPENDENCY_TARGET_LINK_LIBRARIES}\")
    endif()
    file(GENERATE OUTPUT \"\${CMAKE_CURRENT_BINARY_DIR}/dependency_\${DEPENDENCY_TARGET}-bin.txt\" CONTENT \"$<TARGET_FILE:\${DEPENDENCY_TARGET}>\")
endforeach()
file(WRITE \"\${CMAKE_CURRENT_BINARY_DIR}/dependency-targets.txt\" \"\${DEPENDENCY_LIBRARY_TARGETS}\")
file(WRITE \"\${CMAKE_CURRENT_BINARY_DIR}/dependency-include_directories.txt\" \"\${DEPENDENCY_INCLUDE_DIRECTORIES}\")
")
endif()

if (NOT EXISTS ${DEPENDENCIES_DESTINATION})
    git_dependencies_log(ACTION "Creating ${DEPENDENCIES_DESTINATION} folder")
    make_directory(${DEPENDENCIES_DESTINATION})
endif()

set(DEPENDENCY_CMAKE "${CMAKE_COMMAND} '-DDEPENDENCIES_BUILD_NUMBER=${DEPENDENCIES_BUILD_NUMBER}' '-DDEPENDENCIES_LOG_FILE=${DEPENDENCIES_LOG_FILE}' '-DBUILD_AS_DEPENDENCY=TRUE' '-DDEPENDENCIES_DESTINATION=${DEPENDENCIES_DESTINATION}' '-DDEPENDENCIES_FOLDER=${DEPENDENCIES_FOLDER}' --no-warn-unused-cli -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} -Wno-dev -DCATCH_TESTS=DISABLED -DCONNECT_ALL_DEPENDENCIES=${CONNECT_ALL_DEPENDENCIES} ${DEPENDENCIES_DESTINATION}")

if (NOT "${CMAKE_CXX_COMPILER}" STREQUAL "")
    set(DEPENDENCY_CMAKE "${DEPENDENCY_CMAKE} '-DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}'")
endif()

if (NOT "${CMAKE_C_COMPILER}" STREQUAL "")
    set(DEPENDENCY_CMAKE "${DEPENDENCY_CMAKE} '-DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}'")
endif()

if(EXISTS "${DEPENDENCY_TARGETS_FOLDER}/dependency-imported_targets.txt")
    git_dependencies_log(ACTION "Removing old ${DEPENDENCY_TARGETS_FOLDER}/dependency-imported_targets.txt")
    FILE(REMOVE "${DEPENDENCY_TARGETS_FOLDER}/dependency-imported_targets.txt")
endif()

set(ADDITIONAL_CLEAN_FILES "")
list(APPEND ADDITIONAL_CLEAN_FILES ${DEPENDENCIES_FOLDER})
set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES "${ADDITIONAL_CLEAN_FILES}")

function (get_git_dependency_folder DEPENDENCY_REPOSITORY DEPENDENCY_FOLDER_NAME)
    cmake_parse_arguments(DEPENDENCY "" "BRANCH;TAG" "" ${ARGN} )
    get_filename_component(DEPENDENCY_REPOSITORY_NAME ${DEPENDENCY_REPOSITORY} NAME)

    if(NOT "${DEPENDENCY_BRANCH}${DEPENDENCY_TAG}" STREQUAL "")
        STRING(REGEX REPLACE "[^a-zA-Z0-9]" "_" DEPENDENCY_BRANCH_FOLDER "${DEPENDENCY_BRANCH}")
        STRING(REGEX REPLACE "[^a-zA-Z0-9]" "_" DEPENDENCY_TAG_FOLDER "${DEPENDENCY_TAG}")
        set(${DEPENDENCY_FOLDER_NAME} "${DEPENDENCY_REPOSITORY_NAME}_${DEPENDENCY_BRANCH_FOLDER}${DEPENDENCY_TAG_FOLDER}" PARENT_SCOPE)
    else()
        set(${DEPENDENCY_FOLDER_NAME} "${DEPENDENCY_REPOSITORY_NAME}" PARENT_SCOPE)
    endif()
endfunction()


function (import_git_dependency_target DEPENDENCY_NAME TARGET_NAME)
    if (NOT TARGET ${TARGET_NAME} AND EXISTS "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-bin.txt")
        git_dependencies_log(ACTION "Importing ${TARGET_NAME} from ${DEPENDENCY_NAME}")
        file(READ "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-bin.txt" ${TARGET_NAME}_IMPORTED_TARGET_BIN)
        set(${TARGET_NAME}_IMPORTED_TARGET_BIN ${${TARGET_NAME}_IMPORTED_TARGET_BIN} PARENT_SCOPE)
        add_library(${TARGET_NAME} STATIC IMPORTED)
        file(READ "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-include_directories.txt" ${TARGET_NAME}_IMPORTED_TARGET_INCLUDE_DIRECTORIES)
        set_target_properties(${TARGET_NAME} PROPERTIES
#                IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "CXX"
                IMPORTED_LOCATION "${${TARGET_NAME}_IMPORTED_TARGET_BIN}"
                )

        if(NOT "${${TARGET_NAME}_IMPORTED_TARGET_INCLUDE_DIRECTORIES}" STREQUAL "")
            set_target_properties(${TARGET_NAME} PROPERTIES
                    INTERFACE_INCLUDE_DIRECTORIES "${${TARGET_NAME}_IMPORTED_TARGET_INCLUDE_DIRECTORIES}"
                    )
        endif()

        file(READ "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-path.txt" ${TARGET_NAME}_IMPORTED_TARGET_PATH)
        target_link_directories(${TARGET_NAME} INTERFACE ${${TARGET_NAME}_IMPORTED_TARGET_PATH})

        if (EXISTS "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-link_libraries.txt")
            file(READ "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-link_libraries.txt" ${${TARGET_NAME}}_LINKED_LIBRARIES)
            foreach(DEPENDENCY_TARGET_LINKED_LIBRARY ${${${TARGET_NAME}}_LINKED_LIBRARIES})
                import_git_dependency_target(${DEPENDENCY_NAME} ${DEPENDENCY_TARGET_LINKED_LIBRARY})
            endforeach()
            target_link_libraries(${TARGET_NAME} INTERFACE ${${${TARGET_NAME}}_LINKED_LIBRARIES})
        endif()

        if(NOT "${${DEPENDENCY_NAME}_TARGET}" STREQUAL "")
            target_link_libraries(${${DEPENDENCY_NAME}_TARGET} ${${DEPENDENCY_NAME}_INCLUDE_SCOPE} ${TARGET_NAME})
        endif()

        if(${BUILD_AS_DEPENDENCY})

            if(EXISTS "${DEPENDENCY_TARGETS_FOLDER}/dependency-imported_targets.txt")
                file(READ "${DEPENDENCY_TARGETS_FOLDER}/dependency-imported_targets.txt" DEPENDENCY_IMPORTED_TARGETS)
                LIST(APPEND DEPENDENCY_IMPORTED_TARGETS ${TARGET_NAME})
                set(DEPENDENCY_IMPORTED_TARGETS "${DEPENDENCY_IMPORTED_TARGETS}" PARENT_SCOPE)
            else()
                set(DEPENDENCY_IMPORTED_TARGETS "${TARGET_NAME}" PARENT_SCOPE)
            endif()

            file(WRITE "${DEPENDENCY_TARGETS_FOLDER}/dependency-imported_targets.txt" "${DEPENDENCY_IMPORTED_TARGETS}")
            file(COPY
                    "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-path.txt"
                    "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-bin.txt"
                    "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-include_directories.txt"
                    DESTINATION "${DEPENDENCY_TARGETS_FOLDER}")

            if (EXISTS "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-link_libraries.txt")
                file(COPY
                        "${${DEPENDENCY_NAME}_DESTINATION}/dependency_${TARGET_NAME}-link_libraries.txt"
                        DESTINATION "${DEPENDENCY_TARGETS_FOLDER}")
            endif()

        endif()
    else()
        # Target was already added
    endif()
endfunction()

macro (update_git_dependency DEPENDENCY_REPOSITORY DEPENDENCY_FOLDER_NAME DEPENDENCY_HAS_UPDATES)
    cmake_parse_arguments(DEPENDENCY "AUTO_UPDATE;CONNECTED;VERBOSE" "BRANCH;TAG" "" ${ARGN} )

    if (${CONNECT_ALL_DEPENDENCIES})
        set(DEPENDENCY_CONNECTED "TRUE")
    endif()

    if("${DEPENDENCY_BRANCH}" STREQUAL "")
        set(DEPENDENCY_HAS_BRANCH FALSE)
    else()
        set(DEPENDENCY_HAS_BRANCH TRUE)
    endif()

    if("${DEPENDENCY_TAG}" STREQUAL "")
        set(DEPENDENCY_HAS_TAG FALSE)
    else()
        set(DEPENDENCY_HAS_TAG TRUE)
    endif()

    if (${DEPENDENCY_HAS_TAG} AND ${DEPENDENCY_HAS_BRANCH})
        message(FATAL_ERROR "BRANCH and TAG cannot be uses simultaneously" )
    endif()

    set(${DEPENDENCY_HAS_UPDATES} FALSE)

    get_git_dependency_folder(${DEPENDENCY_REPOSITORY} UPDATE_DEPENDENCY_FOLDER_NAME ${ARGN})

    set(${DEPENDENCY_FOLDER_NAME} ${UPDATE_DEPENDENCY_FOLDER_NAME})

    set(DEPENDENCY_FOLDER "${DEPENDENCIES_FOLDER}/${UPDATE_DEPENDENCY_FOLDER_NAME}")

    #locks the dependency for concurrent cmakes running
    set(DEPENDENCY_LOCK "${DEPENDENCIES_FOLDER}/${DEPENDENCY_REPOSITORY_NAME}.lock")

    file(LOCK ${DEPENDENCY_LOCK})

    # if folder doesn't exists does the cloning
    if (NOT EXISTS "${DEPENDENCY_FOLDER}")
        if (${DEPENDENCY_HAS_BRANCH} OR ${DEPENDENCY_HAS_TAG})
            if (${DEPENDENCY_CONNECTED})
                git_dependencies_log(ACTION "git clone --branch '${DEPENDENCY_BRANCH}${DEPENDENCY_TAG}' ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}")
                execute_process(COMMAND git clone --branch "${DEPENDENCY_BRANCH}${DEPENDENCY_TAG}" ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}
                        WORKING_DIRECTORY ${DEPENDENCIES_FOLDER}
                        OUTPUT_QUIET
                        RESULT_VARIABLE GIT_CLONE_RESULT
                        OUTPUT_VARIABLE GIT_CLONE_OUTPUT
                        ERROR_VARIABLE GIT_CLONE_ERROR
                        )
                git_dependencies_log(RESULT "${GIT_CLONE_RESULT}" "${GIT_CLONE_OUTPUT}")
                git_dependencies_log(ERROR ${GIT_CLONE_ERROR})
            else()
                #if it is a disconnected dependency, don't get history and remove git link
                git_dependencies_log(ACTION "git clone --depth=1 --branch \"${DEPENDENCY_BRANCH}${DEPENDENCY_TAG}\" ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}")
                execute_process(COMMAND git clone --depth=1 --branch "${DEPENDENCY_BRANCH}${DEPENDENCY_TAG}" ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}
                        WORKING_DIRECTORY ${DEPENDENCIES_FOLDER}
                        OUTPUT_QUIET
                        RESULT_VARIABLE GIT_CLONE_RESULT
                        OUTPUT_VARIABLE GIT_CLONE_OUTPUT
                        ERROR_VARIABLE GIT_CLONE_ERROR
                        )
                git_dependencies_log(RESULT "${GIT_CLONE_RESULT}" "${GIT_CLONE_OUTPUT}")
                git_dependencies_log(ERROR ${GIT_CLONE_ERROR})
                git_dependencies_log(ACTION "Removing git connection")
                file(REMOVE_RECURSE ${DEPENDENCY_FOLDER}/.git)
                file(REMOVE ${DEPENDENCY_FOLDER}/.gitmodules)
            endif()
        else()
            if (${DEPENDENCY_CONNECTED})
                git_dependencies_log(ACTION "git clone ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}")
                execute_process(COMMAND git clone ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}
                        WORKING_DIRECTORY ${DEPENDENCIES_FOLDER}
                        OUTPUT_QUIET
                        RESULT_VARIABLE GIT_CLONE_RESULT
                        OUTPUT_VARIABLE GIT_CLONE_OUTPUT
                        ERROR_VARIABLE GIT_CLONE_ERROR
                        )
                git_dependencies_log(RESULT "${GIT_CLONE_RESULT}" "${GIT_CLONE_OUTPUT}")
                git_dependencies_log(ERROR ${GIT_CLONE_ERROR})
            else()
                #if it is a disconnected dependency, don't get history and remove git link
                git_dependencies_log(ACTION "git clone --depth=1 ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}")
                execute_process(COMMAND git clone --depth=1 ${DEPENDENCY_REPOSITORY} ${DEPENDENCY_FOLDER}
                        WORKING_DIRECTORY ${DEPENDENCIES_FOLDER}
                        OUTPUT_QUIET
                        RESULT_VARIABLE GIT_CLONE_RESULT
                        OUTPUT_VARIABLE GIT_CLONE_OUTPUT
                        ERROR_VARIABLE GIT_CLONE_ERROR
                        )
                git_dependencies_log(RESULT "${GIT_CLONE_RESULT}" "${GIT_CLONE_OUTPUT}")
                git_dependencies_log(ERROR ${GIT_CLONE_ERROR})
                git_dependencies_log(ACTION "Removing git connection")
                file(REMOVE_RECURSE ${DEPENDENCY_FOLDER}/.git)
                file(REMOVE ${DEPENDENCY_FOLDER}/.gitmodules)

            endif()
        endif()
        set(${DEPENDENCY_HAS_UPDATES} TRUE)
    endif()

    #if it is a connected dependency and auto-update is set, check for changes
    if (${DEPENDENCY_CONNECTED})
        if (${DEPENDENCY_AUTO_UPDATE})
            git_dependencies_log(ACTION "git pull")
            execute_process(COMMAND git pull
                    WORKING_DIRECTORY ${DEPENDENCY_FOLDER}
                    OUTPUT_VARIABLE DEPENDENCY_PULL_OUTPUT
                    RESULT_VARIABLE DEPENDENCY_PULL_RESULT
                    ERROR_VARIABLE  DEPENDENCY_PULL_ERROR
                    OUTPUT_QUIET
                    ERROR_QUIET)
            git_dependencies_log(RESULT "${DEPENDENCY_PULL_RESULT}" "${DEPENDENCY_PULL_OUTPUT}")
            git_dependencies_log(ERROR ${DEPENDENCY_PULL_ERROR})
            if ( NOT "${DEPENDENCY_PULL_OUTPUT}" MATCHES "Already up to date.")
                set(${DEPENDENCY_HAS_UPDATES} TRUE)
            endif()
        endif()
    endif()
    file(LOCK ${DEPENDENCY_LOCK} RELEASE)
    file(REMOVE ${DEPENDENCY_LOCK})
endmacro()

macro (install_git_dependency DEPENDENCY_NAME DEPENDENCY_REPOSITORY)
    cmake_parse_arguments(${DEPENDENCY_NAME}
            "AUTO_UPDATE;LIVE;CONNECTED;NO_BUILD;VERBOSE;ADD_SUBDIRECTORY;DOWNLOAD_ONLY;CMAKE_PROJECT;PUBLIC;PRIVATE;IMPORT_ALL_TARGETS"
            "BRANCH;TAG;TARGET;CMAKE_OPTIONS"
            "PACKAGES;IMPORT_TARGETS;INCLUDE_DIRECTORIES"
            ${ARGN} )

    set(${DEPENDENCY_NAME}_INCLUDE_SCOPE "PRIVATE")
    if (${${DEPENDENCY_NAME}_PUBLIC})
        set(${DEPENDENCY_NAME}_INCLUDE_SCOPE "PUBLIC")
    endif()

    update_git_dependency(${DEPENDENCY_REPOSITORY} ${DEPENDENCY_NAME}_FOLDER_NAME ${DEPENDENCY_NAME}_HAS_UPDATES ${ARGN} )

    set(${DEPENDENCY_NAME}_FOLDER "${DEPENDENCIES_FOLDER}/${${DEPENDENCY_NAME}_FOLDER_NAME}" )
    set(${DEPENDENCY_NAME}_DESTINATION "${DEPENDENCIES_DESTINATION}/${${DEPENDENCY_NAME}_FOLDER_NAME}")

    if (${${DEPENDENCY_NAME}_ADD_SUBDIRECTORY})
        make_directory("${${DEPENDENCY_NAME}_DESTINATION}")
        add_subdirectory(${${DEPENDENCY_NAME}_FOLDER} ${${DEPENDENCY_NAME}_DESTINATION})
    elseif(${${DEPENDENCY_NAME}_CMAKE_PROJECT})
        if (NOT EXISTS "${${DEPENDENCY_NAME}_DESTINATION}/cmake-${DEPENDENCIES_BUILD_NUMBER}")

            make_directory("${${DEPENDENCY_NAME}_DESTINATION}")

            set(${DEPENDENCY_NAME}_CMAKE_COMMAND "${${DEPENDENCY_NAME}_CMAKE} '-DDEPENDENCY=${${DEPENDENCY_NAME}_FOLDER_NAME}'")

            git_dependencies_log(ACTION "${CMAKE_COMMAND}
                    ${DEPENDENCIES_DESTINATION}
                    -DDEPENDENCIES_BUILD_NUMBER=${DEPENDENCIES_BUILD_NUMBER}
                    -DDEPENDENCIES_LOG_FILE='${DEPENDENCIES_LOG_FILE}'
                    -DBUILD_AS_DEPENDENCY=TRUE
                    -DDEPENDENCIES_DESTINATION='${DEPENDENCIES_DESTINATION}'
                    -DDEPENDENCIES_FOLDER='${DEPENDENCIES_FOLDER}'
                    --no-warn-unused-cli
                    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
                    -Wno-dev
                    -DCATCH_TESTS=DISABLED
                    -DCONNECT_ALL_DEPENDENCIES=${CONNECT_ALL_DEPENDENCIES}
                    -DDEPENDENCY='${${DEPENDENCY_NAME}_FOLDER_NAME}'
                    ${${DEPENDENCY_NAME}_CMAKE_OPTIONS}")
            execute_process(COMMAND
                    ${CMAKE_COMMAND}
                    ${DEPENDENCIES_DESTINATION}
                    -DDEPENDENCIES_BUILD_NUMBER=${DEPENDENCIES_BUILD_NUMBER}
                    -DDEPENDENCIES_LOG_FILE='${DEPENDENCIES_LOG_FILE}'
                    -DBUILD_AS_DEPENDENCY=TRUE
                    -DDEPENDENCIES_DESTINATION='${DEPENDENCIES_DESTINATION}'
                    -DDEPENDENCIES_FOLDER='${DEPENDENCIES_FOLDER}'
                    --no-warn-unused-cli
                    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
                    -Wno-dev
                    -DCATCH_TESTS=DISABLED
                    -DCONNECT_ALL_DEPENDENCIES=${CONNECT_ALL_DEPENDENCIES}
                    -DDEPENDENCY='${${DEPENDENCY_NAME}_FOLDER_NAME}'
                    ${${DEPENDENCY_NAME}_CMAKE_OPTIONS}
            #execute_process(COMMAND ${DEPENDENCY_CMAKE}
                    WORKING_DIRECTORY ${${DEPENDENCY_NAME}_DESTINATION}
                    OUTPUT_VARIABLE ${DEPENDENCY_NAME}_CMAKE_OUTPUT
                    RESULT_VARIABLE ${DEPENDENCY_NAME}_CMAKE_RESULT
                    ERROR_VARIABLE ${DEPENDENCY_NAME}_CMAKE_ERROR )

            git_dependencies_log(RESULT "${${DEPENDENCY_NAME}_CMAKE_RESULT}" "${${DEPENDENCY_NAME}_CMAKE_OUTPUT}")
            git_dependencies_log(ERROR "${${DEPENDENCY_NAME}_CMAKE_ERROR}")
            if (NOT ${${DEPENDENCY_NAME}_CMAKE_RESULT} EQUAL "0")
                message(FATAL_ERROR "failed to load dependency cmake file" )
            endif()
        endif()
        file(TOUCH ${${DEPENDENCY_NAME}_DESTINATION}/cmake-${DEPENDENCIES_BUILD_NUMBER} "")
        if (NOT ${${DEPENDENCY_NAME}_NO_BUILD}) # AND ${${DEPENDENCY_NAME}_HAS_UPDATES}
            if (NOT EXISTS "${${DEPENDENCY_NAME}_DESTINATION}/make-${DEPENDENCIES_BUILD_NUMBER}")
                git_dependencies_log(ACTION "${CMAKE_COMMAND} --build ${${DEPENDENCY_NAME}_DESTINATION} --target all -j")
                execute_process(COMMAND ${CMAKE_COMMAND} --build ${${DEPENDENCY_NAME}_DESTINATION} --target all -j
                        WORKING_DIRECTORY ${${DEPENDENCY_NAME}_DESTINATION}
                        OUTPUT_VARIABLE ${DEPENDENCY_NAME}_BUILD_OUTPUT
                        RESULT_VARIABLE ${DEPENDENCY_NAME}_BUILD_RESULT
                        ERROR_VARIABLE ${DEPENDENCY_NAME}_BUILD_ERROR )

                git_dependencies_log(RESULT "${${DEPENDENCY_NAME}_BUILD_RESULT}" "${${DEPENDENCY_NAME}_BUILD_OUTPUT}")
                git_dependencies_log(ERROR "${${DEPENDENCY_NAME}_BUILD_ERROR}")
                if (NOT ${${DEPENDENCY_NAME}_BUILD_RESULT} EQUAL "0")
                    message(FATAL_ERROR "failed to build dependency cmake file" )
                endif()
            endif()
            file(TOUCH ${${DEPENDENCY_NAME}_DESTINATION}/make-${DEPENDENCIES_BUILD_NUMBER} "")
        endif()

        file(READ "${${DEPENDENCY_NAME}_DESTINATION}/dependency-include_directories.txt" ${DEPENDENCY_NAME}_GENERATED_INCLUDE_DIRECTORIES)

        if(NOT "${${DEPENDENCY_NAME}_GENERATED_INCLUDE_DIRECTORIES}" STREQUAL "")
            if("${${DEPENDENCY_NAME}_TARGET}" STREQUAL "")
                include_directories(${${DEPENDENCY_NAME}_GENERATED_INCLUDE_DIRECTORIES})
            else()
                target_include_directories(${${DEPENDENCY_NAME}_TARGET} ${${DEPENDENCY_NAME}_INCLUDE_SCOPE} ${${DEPENDENCY_NAME}_GENERATED_INCLUDE_DIRECTORIES})
            endif()
        endif()

        if(${${DEPENDENCY_NAME}_IMPORT_ALL_TARGETS})
            file(READ "${${DEPENDENCY_NAME}_DESTINATION}/dependency-targets.txt" ${DEPENDENCY_NAME}_IMPORT_TARGETS)
        endif()

        if(${${DEPENDENCY_NAME}_LIVE})
            git_dependencies_log( STATUS "${DEPENDENCY_NAME} IS LIVE")
            add_custom_target( ${DEPENDENCY_NAME}_UPDATER
                    COMMAND ${CMAKE_COMMAND} --build ${${DEPENDENCY_NAME}_DESTINATION} --target all -j
                    WORKING_DIRECTORY ${${DEPENDENCY_NAME}_DESTINATION} )
        endif()

        foreach(DEPENDENCY_IMPORTED_TARGET_NAME ${${DEPENDENCY_NAME}_IMPORT_TARGETS})
            import_git_dependency_target (${DEPENDENCY_NAME} ${DEPENDENCY_IMPORTED_TARGET_NAME})
            if(${${DEPENDENCY_NAME}_LIVE})
                add_dependencies(${DEPENDENCY_IMPORTED_TARGET_NAME} ${DEPENDENCY_NAME}_UPDATER)
            endif()
        endforeach()

        if(NOT "${${DEPENDENCY_NAME}_PACKAGES}" STREQUAL "")
            foreach(${DEPENDENCY_NAME}_PACKAGE ${${DEPENDENCY_NAME}_PACKAGES})
                set(${${DEPENDENCY_NAME}_PACKAGE}_DIR ${${DEPENDENCY_NAME}_DESTINATION}/${${DEPENDENCY_NAME}_FOLDER_NAME})
                find_package(${${DEPENDENCY_NAME}_PACKAGE})
            endforeach()
        endif()

    endif()

    if("${${DEPENDENCY_NAME}_INCLUDE_DIRECTORIES}" STREQUAL "")
        set(${DEPENDENCY_NAME}_HAS_INCLUDE_DIRECTORIES FALSE)
    else()
        set(${DEPENDENCY_NAME}_HAS_INCLUDE_DIRECTORIES TRUE)
    endif()

    if(${${DEPENDENCY_NAME}_HAS_INCLUDE_DIRECTORIES})
        foreach(${DEPENDENCY_NAME}_INCLUDE_DIRECTORY ${${DEPENDENCY_NAME}_INCLUDE_DIRECTORIES})
            include_directories(${${DEPENDENCY_NAME}_FOLDER}/${${DEPENDENCY_NAME}_INCLUDE_DIRECTORY})
        endforeach()
    endif()
endmacro()