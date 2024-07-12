#pragma once
#include <json_cpp/json_base.h>
#include <vector>
#include <iostream>
#include <string>

namespace json_cpp {
    struct Json_buffer{
        Json_buffer();
        static Json_buffer new_buffer(void *address, size_t size, bool managed = false);
        template <class T>
        static Json_buffer new_buffer(T &o) {
            return new_buffer((void *)&o, sizeof(T));
        }
        explicit Json_buffer(bool);
        void *address;
        size_t size;
        ~Json_buffer();
        friend struct Json_base64;
    private:
        bool reserve(size_t );
        bool managed;
    };
}