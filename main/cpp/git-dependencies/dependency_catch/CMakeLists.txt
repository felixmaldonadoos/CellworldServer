cmake_minimum_required(VERSION 3.10)
project(CatchTests)

get_directory_property(CATCH_TEST_HAS_PARENT_SCOPE PARENT_DIRECTORY)
if(CATCH_TEST_HAS_PARENT_SCOPE)
    set(CATCH_TEST_COUNTER 0 PARENT_SCOPE)
    set(CATCH_TEST_LOCATION ${CMAKE_CURRENT_SOURCE_DIR} PARENT_SCOPE )
else()
    set(CATCH_TEST_COUNTER 0)
    set(CATCH_TEST_LOCATION ${CMAKE_CURRENT_SOURCE_DIR})
endif()

if ("${CATCH_TESTS}" MATCHES "DISABLED")
    macro(add_catch_test)
    endmacro()
else()
    enable_testing()
    macro(add_catch_test CATCH_TEST_NAME)

        cmake_parse_arguments(CATCH_TEST
                "AUTO_RUN"
                "NAME;TESTS_FOLDER"
                "TEST_FILES;SOURCE_FILES;LINK_LIBRARIES;INCLUDE_DIRECTORIES"
                ${ARGN} )

        if (NOT "${CATCH_TEST_LINK_LIBRARIES}" STREQUAL "")
            file(GLOB CATCH_TEST_FILES "${CATCH_TEST_TESTS_FOLDER}/*.cpp")
        else()
            set(CATCH_TEST_FILES "")
        endif()

        if (NOT "${CATCH_TEST_TEST_FILES}" STREQUAL "")
            list(APPEND CATCH_TEST_FILES "${CATCH_TEST_TEST_FILES}")
        endif()

        add_executable(${CATCH_TEST_NAME} ${CATCH_TEST_LOCATION}/Resources/catchtests.cpp ${CATCH_TEST_FILES} ${CATCH_TEST_SOURCE_FILES})

        target_include_directories(${CATCH_TEST_NAME} PRIVATE ${CATCH_TEST_LOCATION}/include)

        set_target_properties(${CATCH_TEST_NAME}
                PROPERTIES
                RUNTIME_OUTPUT_DIRECTORY ".tests")

        if (NOT "${CATCH_TEST_LINK_LIBRARIES}" STREQUAL "")
            target_link_libraries(${CATCH_TEST_NAME} ${CATCH_TEST_LINK_LIBRARIES})
        endif()

        if (NOT "${CATCH_TEST_INCLUDE_DIRECTORIES}" STREQUAL "")
            target_include_directories(${CATCH_TEST_NAME} PRIVATE ${CATCH_TEST_INCLUDE_DIRECTORIES})
        endif()

        add_test(${PROJECT_NAME}_TEST .tests/${CATCH_TEST_NAME})

        if (${CATCH_TEST_AUTO_RUN})
            add_custom_command(TARGET ${CATCH_TEST_NAME}
                    POST_BUILD
                    COMMAND .tests/<TARGET_FILE_NAME:${CATCH_TEST_NAME}> )
        endif()
    endmacro()
endif()

