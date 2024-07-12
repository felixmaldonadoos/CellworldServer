#include <json_cpp/python/json_descriptor.h>
#include <json_cpp/json_builder.h>
#include <json_cpp/json_object.h>


using namespace std;

namespace json_cpp {

    void Json_descriptor::json_write(std::ostream &o) const {
        o << "null";
    }

    void Json_descriptor::json_parse(std::istream &i) {
        Json_util::read_null(i);
    }

    void Json_bool_descriptor::json_write(std::ostream &o) const {
        Json_util::write_value(o, value);
    }

    void Json_bool_descriptor::json_parse(std::istream &i) {
        value = Json_util::read_bool(i);
    }

    void Json_int_descriptor::json_write(std::ostream &o) const {
        Json_util::write_value(o, value);
    }

    void Json_int_descriptor::json_parse(std::istream &i) {
        value = Json_util::read_int(i);
    }


    void Json_float_descriptor::json_write(std::ostream &o) const {
        Json_util::write_value(o, value);
    }

    void Json_float_descriptor::json_parse(std::istream &i) {
        value = (float) Json_util::read_double(i);
    }

    void Json_string_descriptor::json_write(std::ostream &o) const {
        Json_util::write_value(o, value);
    }

    void Json_string_descriptor::json_parse(std::istream &i) {
        value = Json_util::read_string(i);
    }

    void Json_object_descriptor::json_write(std::ostream &o) const {
        Json_builder jb;
        for (size_t index = 0; index < members_descriptor.size(); index++) {
            Add_member_with_name(*members_descriptor[index], members_mandatory[index], members_name[index]);
        }
        jb.json_write(o);
    }

    void Json_object_descriptor::json_parse(std::istream &i) {
        Json_builder jb;
        for (size_t index = 0; index < members_descriptor.size(); index++) {
            Add_member_with_name(*members_descriptor[index], members_mandatory[index], members_name[index]);
        }
        jb.json_parse(i);
    }

    void Json_object_descriptor::add_member(const std::string &member_name, Json_descriptor &member_descriptor,
                                            bool member_mandatory) {
        members_descriptor.emplace_back(member_descriptor.new_item());
        members_name.emplace_back(member_name);
        members_mandatory.emplace_back(member_mandatory);
    }

    void Json_object_descriptor::set(const std::string &member_name, Json_descriptor &new_descriptor) {
        int i = find(member_name);
        if (i >= 0) members_descriptor.replace(i, new_descriptor);
        else add_member(member_name, new_descriptor, true);
    }

    int Json_object_descriptor::find(const std::string &member_name) {
        for (unsigned int i = 0; i < members_descriptor.size(); i++) {
            if (members_name[i] == member_name) return (int) i;
        }
        return -1;
    }

    bool Json_object_descriptor::contains(const std::string &member_name) {
        return find(member_name) != -1;
    }

    void Json_object_descriptor::set(const std::string &member_name, bool value) {
        auto m = Json_bool_descriptor(value);
        set(member_name, m);
    }

    void Json_object_descriptor::set(const std::string &member_name, int value) {
        auto m = Json_int_descriptor(value);
        set(member_name, m);
    }

    void Json_object_descriptor::set(const std::string &member_name, float value) {
        auto m = Json_float_descriptor(value);
        set(member_name, m);
    }

    void Json_object_descriptor::set(const std::string &member_name, string value) {
        auto m = Json_string_descriptor(value);
        set(member_name, m);
    }

    Json_descriptor &Json_object_descriptor::get(const std::string member_name) {
        auto i = find(member_name);
        if (i >= 0) return *members_descriptor[i];
        throw runtime_error("member not found");
    }

    void Json_list_descriptor::json_parse(std::istream &i) {
        if (!item_descriptor) {
            item_descriptor = new Json_variant_descriptor();
        }
        if (Json_util::skip_blanks(i) != '[') throw std::logic_error("format error");
        Json_util::discard(i);
        value.clear();
        while ((Json_util::skip_blanks(i) != ']')) {
            auto item = value.emplace_back(item_descriptor->new_item());
            item->json_parse(i);
            if (Json_util::skip_blanks(i) != ',') break;
            Json_util::discard(i);
        }
        if (Json_util::skip_blanks(i, true) != ']') throw std::logic_error("format error");
    }

    void Json_list_descriptor::json_write(std::ostream &o) const {
        o << '[';
        bool first = true;
        for (auto &e: value) {
            if (!first) o << ',';
            first = false;
            e->json_write(o);
        }
        o << ']';
    }

    void Json_list_descriptor::set_item_descriptor(const Json_descriptor &id) {
        item_descriptor = &id;
    }

    Json_list_descriptor::~Json_list_descriptor() {
        if (item_descriptor) {
            delete item_descriptor;
        }
    }

    Json_descriptor_container::~Json_descriptor_container() {
        for (auto *p: *this) delete p;
    }

    Json_descriptor_container &Json_descriptor_container::operator=(const Json_descriptor_container &o) {
        clear();
        for (auto *i: o) push_back(i->new_item());
        return *this;
    }

    void Json_descriptor_container::replace(size_t index, Json_descriptor &new_descriptor) {
        if (index >= size()) throw std::runtime_error("index not found.");
        auto old_ptr = (*this)[index];
        (*this)[index] = new_descriptor.new_item();
        delete old_ptr;
    }

    Json_variant_descriptor::~Json_variant_descriptor() {
        clear();
    }

    Json_variant_descriptor &Json_variant_descriptor::operator=(const Json_variant_descriptor &jvd) {
        clear();
        if (jvd.value) {
            value = jvd.value->new_item();
        }
        return *this;
    }

    Json_variant_descriptor &Json_variant_descriptor::operator=(const Json_descriptor &jd) {
        clear();
        value = jd.new_item();
        return *this;
    }

    void Json_variant_descriptor::json_write(ostream &o) const {
        if (value) {
            value->json_write(o);
        } else {
            Json_null_descriptor().json_write(o);
        }
    }

    void Json_variant_descriptor::json_parse(istream &i) {
        clear();
        auto c = Json_util::skip_blanks(i);
        switch (c) {
            case '[':
                value = new Json_list_descriptor();
                break;
            case '{':
                value = new Json_variant_object_descriptor();
                break;
            case '"':
                value = new Json_string_descriptor();
                break;
            case 't':
            case 'f':
                value = new Json_bool_descriptor();
                break;
            case 'n':
                value = new Json_null_descriptor();
                break;
            default:
                if ((c >= '0' && c <= '9') || c == '-' || c == '.') {
                    bool is_float = c == '.';
                    string n;
                    n += c;
                    Json_util::discard(i);
                    c = i.peek();
                    while ((c >= '0' && c <= '9') || c == '.') {
                        is_float = is_float || c == '.';
                        n += c;
                        Json_util::discard(i);
                        c = i.peek();
                    }
                    if (is_float) {
                        value = new Json_float_descriptor();
                        value->from_json(n);
                    } else {
                        value = new Json_int_descriptor();
                        value->from_json(n);
                    }
                    return;
                } else {
                    throw runtime_error("error parsing json");
                }
        }
        value->json_parse(i);
    }

    void Json_variant_descriptor::clear() {
        if (value) {
            delete value;
            value = nullptr;
        }
    }

    void Json_variant_object_descriptor::json_parse(istream &i) {
        if (Json_util::skip_blanks(i) == '{') {
            Json_util::discard(i);
            string name;
            while (Json_util::skip_blanks(i) != '}') {
                if (!Json_util::read_name(name, i)) throw logic_error("format error: field name");
                Json_variant_descriptor jvd;
                jvd.json_parse(i);
                members_name.push_back(name);
                members_descriptor.emplace_back(jvd.value->new_item());
                if (Json_util::skip_blanks(i) != ',') break;
                Json_util::discard(i);
            }
            if (Json_util::skip_blanks(i) != '}') {
                throw logic_error("format error: expecting '}'");
            }
            Json_util::discard(i);
        }
    }

    void Json_variant_object_descriptor::json_write(ostream &o) const {
        o << '{';
        bool first = true;
        for (size_t i = 0; i < members_name.size(); i++) {
            if (!first) o << ',';
            first = false;
            Json_util::write_value(o,members_name[i]);
            o << ':';
            members_descriptor[i]->json_write(o);
        }
        o << '}';
    }
}