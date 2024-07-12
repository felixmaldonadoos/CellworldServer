#include <json_cpp/json_buffer.h>

namespace json_cpp{
    struct Json_base64{
        static size_t size(const std::string &);
        static void read(const std::string &, Json_buffer &);
        static void write(std::ostream &,  const Json_buffer &);
    };
}