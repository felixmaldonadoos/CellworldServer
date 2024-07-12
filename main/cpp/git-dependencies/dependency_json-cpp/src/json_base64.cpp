#include <json_cpp/json_base64.h>
#define BASE64_PARSE_ERROR throw logic_error("error converting to base64")
#define BASE64_ALLOCATION_ERROR throw logic_error("error allocating memory to parse base64")

using namespace std;
namespace json_cpp{

    static const std::string base64_chars =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789+/";

    static inline bool is_base64(char c) {
        return (isalnum(c) || (c == '+') || (c == '/'));
    }

    int find_base64_char(char c){
        if (c == '+') return 62;
        if (c == '/') return 63;
        if (c>='A' && c<='Z') return c - 'A';
        if (c>='a' && c<='z') return 26 + c - 'a';
        if (c>='0' && c<='9') return 52 + c - '0';
        return -1;
    }

    void Json_base64::read(const std::string &base64, Json_buffer &buffer) {
        size_t data_len = size(base64);
        if (buffer.managed) {
            if (!buffer.reserve(data_len)) BASE64_ALLOCATION_ERROR;
        }

        int in_len = base64.size();
        int i = 0;
        int j = 0;
        int in_ = 0;
        char char_array_4[4], char_array_3[3];

        size_t offset = 0;
        auto buf = (char *)buffer.address;
        while (in_len-- && ( base64[in_] != '=')) {
            if (!is_base64(base64[in_])) BASE64_PARSE_ERROR;
            char_array_4[i++] = base64[in_]; in_++;
            if (i ==4) {
                for (i = 0; i <4; i++)
                    char_array_4[i] = find_base64_char(char_array_4[i]);

                char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
                char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
                char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

                for (i = 0; (i < 3); i++)
                    buf[offset++] = char_array_3[i];
                i = 0;
            }
        }

        if (i) {
            for (j = i; j <4; j++)
                char_array_4[j] = 0;

            for (j = 0; j <4; j++)
                char_array_4[j] = find_base64_char(char_array_4[j]);

            char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
            char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

            for (j = 0; (j < i - 1); j++) buf[offset++] = char_array_3[j];
        }
    }

    void Json_base64::write(std::ostream &o, const Json_buffer &buffer) {
        int i = 0;
        int j = 0;
        char char_array_3[3];
        char char_array_4[4];
        auto bufLen= buffer.size;
        auto buf=(char *)buffer.address;
        while (bufLen--) {
            char_array_3[i++] = *(buf++);
            if (i == 3) {
                char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
                char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
                char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
                char_array_4[3] = char_array_3[2] & 0x3f;

                for(i = 0; (i <4) ; i++)
                    o << base64_chars[char_array_4[i]];
                i = 0;
            }
        }

        if (i)
        {
            for(j = i; j < 3; j++)
                char_array_3[j] = '\0';

            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;

            for (j = 0; (j < i + 1); j++)
                o << base64_chars[char_array_4[j]];

            while((i++ < 3))
                o << '=';
        }
    }

    size_t Json_base64::size(const std::string &base64){
        size_t len = base64.size() * 3 / 4;
        if (base64.size() > 1 && base64[base64.size()-1] == '=') {
            len --;
            if (base64.size() > 2 && base64[base64.size()-2] == '=') {
                len --;
            }
        }
        return len;
    }
}
