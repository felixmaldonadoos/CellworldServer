#include <json_cpp/json_date.h>
#include <json_cpp/json_util.h>
#include <string>
#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <array>

using namespace std::chrono;
using namespace std;

namespace json_cpp{

    string Json_date::time_format("%Y-%m-%d %T");

    int time_zone_diff = 0;

    void Json_date::json_parse(std::istream &i) {
        string d = Json_util::read_string(i);
        std::istringstream ss{d};
        ss >> date::parse("%Y-%m-%d %T", *this);
    }

    void Json_date::json_write(std::ostream &o) const {
        o << '"' << date::format(time_format, *this) << '"';
    }

    Json_date Json_date::now() {
        Json_date jd;
        date::sys_time<std::chrono::milliseconds> &d = jd;
        d = round<milliseconds>(system_clock::now()) + minutes(time_zone_diff);
        return jd;
    }

    void Json_date::set_format(const string &new_format) {
        Json_date::time_format = new_format;
    }

    const std::string &Json_date::get_format() {
        return Json_date::time_format;
    }

    std::string Json_date::to_string() {
        return date::format(time_format, *this);
    }

    std::string Json_date::to_string(const string &format) {
        return date::format(format, *this);
    }

    void Json_date::set_time_zone_offset(int tzo) {
        time_zone_diff = tzo;
    }

    std::string exec(const char* cmd) {
        std::string result;
        #ifdef __linux__
            //linux code goes here
            std::array<char, 128> buffer;
            std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
            if (!pipe) {
                throw std::runtime_error("popen() failed!");
            }
            while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
                result += buffer.data();
            }
            return result;
        #elif _WIN32
        #endif
    }

    void Json_date::set_local_time_zone_offset() {
        Json_date gt = Json_date::now();
        auto local_time = exec(("date +\"" + Json_date::get_format() + "\"").c_str());
        Json_date lt;
        lt.from_json("\"" + local_time + "\"");
        set_time_zone_offset(round((float)duration_cast<seconds>(lt - gt).count() / 60.0));
    }

}