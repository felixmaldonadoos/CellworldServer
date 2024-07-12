#pragma once
#include <json_cpp/json_base.h>
#include <json_cpp/json_buffer.h>
#include <vector>
#include <iostream>
#include <string>

namespace json_cpp {
    struct Json_binary : Json_base {
        virtual Json_buffer get_write_buffer() const = 0;
        virtual Json_buffer get_parse_buffer() {
            buffer = Json_buffer(true);
            return buffer;
        };
        virtual void set_value(const Json_buffer &) = 0;
        virtual void json_parse(std::istream &i) override {
            Json_buffer jb = get_parse_buffer();
            Json_util::read_value(i, jb);
            set_value (jb);
        }
        virtual void json_write(std::ostream &o) const override{
            Json_buffer jb = get_write_buffer();
            Json_util::write_value(o, jb);
        }
        std::string json_type() const override {
            return "string";
        }
    private:
        Json_buffer buffer;
    };
}