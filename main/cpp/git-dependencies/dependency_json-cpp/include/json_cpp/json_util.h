#pragma once
#include <json_cpp/json_base.h>
#include <json_cpp/json_buffer.h>

namespace json_cpp {
    struct Json_util {
        static void discard(std::istream &);
        static char skip_blanks(std::istream &, bool);
        static char skip_blanks(std::istream &);
        static char read_escaped(std::istream &);
        static bool read_bool(std::istream &);
        static bool read_null(std::istream &);
        static std::string read_string(std::istream &);
        static double read_double(std::istream &);
        static int read_int(std::istream &);
        static bool read_name(std::string &, std::istream &);
        static void read_value(std::istream &, bool &);
        static void read_value(std::istream &, double &);
        static void read_value(std::istream &, int &);
        static void read_value(std::istream &, unsigned int&);
        static void read_value(std::istream &, std::string &);
        static void read_value(std::istream &, Json_buffer &);
        static void write_value(std::ostream &, const bool &);
        static void write_value(std::ostream &, const double &);
        static void write_value(std::ostream &, const float &);
        static void write_value(std::ostream &, const int &);
        static void write_value(std::ostream &, const unsigned int&);
        static void write_value(std::ostream &, const std::string &);
        static void write_value(std::ostream &, const Json_buffer &);
        static void write_escaped(std::ostream &, const char);
    };
}