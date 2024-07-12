#include <iostream>
#include <json_cpp/json_util.h>
#include <json_cpp/json_base64.h>

#define ESCAPED_PARSE_ERROR throw logic_error("escape sequence not implemented")
#define STRING_PARSE_ERROR throw logic_error("error converting to string")
#define INT_PARSE_ERROR throw logic_error("error converting to int")
#define DOUBLE_PARSE_ERROR throw logic_error("error converting to double")

using namespace std;
namespace json_cpp {
    void Json_util::write_value(std::ostream &o, const Json_buffer &buffer) {
        Json_base64::write(o, buffer);
    }

    void Json_util::read_value(istream &i, Json_buffer &buffer) {
        Json_base64::read(read_string(i), buffer);
    }

    void Json_util::discard(istream &i) {
        char c;
        i >> c;
    }

    char Json_util::skip_blanks(istream &i, bool s) {
        i >> ws;
        char c;
        if (s) i >> c; else c = i.peek();
        return c;
    }

    char Json_util::skip_blanks(istream &i) {
        return skip_blanks(i, false);
    }

    bool Json_util::read_bool(istream &i) {
        string v;
        char c = skip_blanks(i);
        while (isdigit(c) || isalpha(c)) {
            v+=c;
            discard(i);
            c = skip_blanks(i);
        }
        if (v == "false" || v == "False" || v =="0") {
            return false;
        }
        return true;
    }

    bool Json_util::read_null(istream &i) {
        string v;
        char c = skip_blanks(i);
        while (isdigit(c) || isalpha(c)) {
            v+=c;
            discard(i);
            c = skip_blanks(i);
        }
        if (v == "null") {
            return true;
        }
        return false;
    }

    std::string Json_util::read_string(istream &i) {
        char c;
        if (skip_blanks(i) != '"') STRING_PARSE_ERROR;
        discard(i);
        i >> std::noskipws;
        string s;
        do {
            i >> c;
            if (c == '\\') {
                s += Json_util::read_escaped(i);
            } else
                if (c != '"') s += c;
        } while (c != '"');
        i >> std::skipws;
        return s;
    }

    double Json_util::read_double(istream &i) {
        char c = skip_blanks(i);
        if (!isdigit(c) && c != '.' && c != '-') DOUBLE_PARSE_ERROR;
        double r;
        i >> r;
        return r;
    }

    int Json_util::read_int(istream &i) {
        char c = skip_blanks(i);
        if (!isdigit(c) && c != '-') INT_PARSE_ERROR;
        int r;
        i >> r;
        return r;
    }

    bool Json_util::read_name(string &s, istream &i) {
        s = read_string(i);
        return skip_blanks(i, true) == ':';
    }

    void Json_util::read_value(istream &i, bool &v) {
        v = read_int(i);
    }

    void Json_util::read_value(istream &i, double &v) {
        v = read_double(i);
    }

    void Json_util::read_value(istream &i, int &v) {
        v = read_int(i);
    }

    void Json_util::read_value(istream &i, unsigned int &v) {
        v = read_int(i);
    }

    void Json_util::read_value(istream &i, string &v) {
        v = read_string(i);
    }

    void Json_util::write_value(ostream &o,const bool &v) {
        o << (v?"true":"false");
    }

    void Json_util::write_value(ostream &o,const double &v) {
        o << v;
    }

    void Json_util::write_value(ostream &o,const float &v) {
        o << v;
    }

    void Json_util::write_value(ostream &o,const int &v) {
        o << v;
    }

    void Json_util::write_value(ostream &o,const unsigned int &v) {
        o << v;
    }

    void Json_util::write_value(ostream &o,const string &v) {
        o << '"' << v << '"';
    }

    char Json_util::read_escaped(istream &i) {
        char c;
        i >> c;
        switch (c){
            case '\'':
                return '\'';
            case '\"':
                return '\"';
            case '?':
                return '?';
            case '\\':
                return '\\';
            case 'a':
                return '\a';
            case 'b':
                return '\b';
            case 'f':
                return '\f';
            case 'n':
                return '\n';
            case 'r':
                return '\r';
            case 't':
                return '\t';
            case 'v':
                return '\v';
            case 'x':
                unsigned char x0,x1;
                i>>x1;
                i>>x0;
                x0 =  x0 <= '9' ? x0 - '0' : x0 - 'A' + 10;
                if (x0>=16) ESCAPED_PARSE_ERROR;
                x1 = x1 <= '9' ? x1 - '0' : x1 - 'A' + 10;
                if (x1>=16) ESCAPED_PARSE_ERROR;
                return x1*16+x0;
            default:
                if (c>='0' && c<='9'){
                    char n1,n0;
                    i>>n1;
                    if (n1>='0' && n1<='9') {
                        i >> n0;
                        if (n0>='0' && n0<='9') {
                            return c * 64 + n1 * 8 + n0;
                        }
                    }
                }
                ESCAPED_PARSE_ERROR;
        }
        return 0;
    }

    void Json_util::write_escaped(ostream &o, const char c) {
        switch (c){
            case '\'':
                o << '\\' << '\'';
                break;
            case '\"':
                o << '\\' << '\"';
                break;
            case '?':
                o << '\\' << '?';
                break;
            case '\\':
                o << '\\' << '\\';
                break;
            case '\a':
                o << '\\' << 'a';
                break;
            case '\b':
                o <<  '\\' << 'b';
                break;
            case '\f':
                o <<  '\\' << 'f';
                break;
            case '\n':
                o << '\\' << 'n';
                break;
            case '\r':
                o << '\\' << 'r';
                break;
            case '\t':
                o << '\\' << 't';
                break;
            case '\v':
                o << '\\' << 'v';
                break;
            default:
                if (c>=32 && c<=126){
                    o << c;
                } else {
                    unsigned char cx = c, c0,c1;
                    c1 = cx >> 4;
                    c0 = cx & 31;
                    if (c1>9) c1 += -10 + 'A';
                    else c1 += '0';
                    if (c0>9) c0 += -10 + 'A';
                    else c0 += '0';
                    o << '\\' << 'x' << c1 << c0;
                }
        }
    }
}