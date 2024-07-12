#include <fstream>
#include <string>
#include <sstream>
#include <json_cpp/json_base.h>


using namespace std;
namespace json_cpp {

    std::istream &operator>>(istream &i, Json_base &j) {
        j.json_parse(i);
        return i;
    }

    std::ostream &operator<<(ostream &o, const Json_base &j) {
        j.json_write(o);
        return o;
    }

    bool Json_base::load(const string &file_name) {
        std::ifstream file;
        file.open(file_name.c_str());
        if (!file.good()) return false;
        json_parse(file);
        return true;
    }

    bool Json_base::save(const string &file_name) const {
        std::ofstream file;
        file.open(file_name.c_str());
        if (!file.good()) return false;
        json_write(file);
        return true;
    }

    std::string &operator>>(string &i, Json_base &j) {
        std::stringstream ss(i);
        ss >> j;
        i = ss.str();
        return i;
    }

    std::string &operator<<(string &o, const Json_base &j) {
        std::stringstream ss(o);
        ss << j;
        o = ss.str();
        return o;
    }

    char *operator>>(char *s, Json_base &j) {
        string ss(s);
        ss>>j;
        return s;
    }

    const char *operator>>(const char *s, Json_base &j) {
        string ss(s);
        ss>>j;
        return s;
    }

    void Json_base::json_write(ostream &) const {

    }

    void Json_base::json_parse(istream &) {

    }

    const std::string &operator>>(const string &i, Json_base &j) {
        std::stringstream ss(i);
        ss >> j;
        return i;
    }

    std::string Json_base::to_json() const {
        string s;
        s << *(this);
        return s;
    }

    void Json_base::from_json(const string &s) {
        s >> *(this);
    }
}