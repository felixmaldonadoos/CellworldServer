#include <json_cpp/json_object.h>
using namespace std;

namespace json_cpp {

    void Json_object::json_parse(istream &i) {
        Json_builder jb;
        json_set_builder(jb);
        i >> jb;
        after_load();
    }

    void Json_object::json_write(ostream &o) const {
        Json_builder jb;
        json_set_builder(jb);
        o << jb;
    }

    void Json_object::json_set_builder(Json_builder &) const {

    }

    void Json_object::json_set_builder(Json_builder &jb) {
        const auto &current = *this;
        current.json_set_builder(jb);
    }

    Json_object::Json_object() {

    }
}
