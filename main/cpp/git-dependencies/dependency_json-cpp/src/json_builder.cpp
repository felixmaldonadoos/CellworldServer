#include <json_cpp/json_builder.h>
#include <json_cpp/json_util.h>
#include <algorithm>

#define ToLower(STRING) transform(STRING.begin(), STRING.end(), STRING.begin(), ::tolower)

using namespace  std;

namespace json_cpp{

    Json_builder::Json_member::Json_member(std::string name, bool mandatory, std::unique_ptr<Json_wrapped>  ref):
        name(name), mandatory(mandatory), ref(std::move(ref)){ }

    void Json_builder::json_add_member(std::string name, bool mandatory, std::unique_ptr<Json_wrapped> ref) {
        auto case_name = name;
        if (!case_sensitive) {
            ToLower(case_name);
        }
        members.emplace_back(case_name, mandatory, std::move(ref));
    }

    void Json_builder::json_parse(istream &i) {
        vector<string> members_name;
        if (Json_util::skip_blanks(i) == '{') {
            Json_util::discard(i);
            string name;
            while (Json_util::skip_blanks(i) != '}') {
                if (!Json_util::read_name(name, i)) throw logic_error("format error: field name");
                auto member_index = _find_member(name);
                if (member_index == -1) throw logic_error("member not found '" + name + "'");
                if (member_index == -2) // ignored
                {
                    if (Json_util::skip_blanks(i) == '{' ) {
                        int bc = 0;
                        do {
                            auto c = Json_util::skip_blanks(i);
                            switch (c){
                                case '{':
                                    bc++;
                                    break;
                                case '}':
                                    bc--;
                                    break;
                                case '"':
                                    Json_util::read_string(i);
                                    continue;
                            }
                            Json_util::discard(i);
                        } while (bc);
                    }
                    if (Json_util::skip_blanks(i) == '[' ) {
                        int bc = 0;
                        do {
                            auto c = Json_util::skip_blanks(i);
                            switch (c){
                                case '[':
                                    bc++;
                                    break;
                                case ']':
                                    bc--;
                                    break;
                                case '"':
                                    Json_util::read_string(i);
                                    continue;
                            }
                            Json_util::discard(i);
                        } while (bc);
                    } else if (Json_util::skip_blanks(i) == '"' ) {
                        Json_util::read_string(i);
                    } else {
                        while (Json_util::skip_blanks(i)!=',' && Json_util::skip_blanks(i)!='}') {
                            Json_util::discard(i);
                        };
                    }
                } else {
                    members_name.push_back(name);
                    auto &member = members[member_index];
                    member.ref->json_parse(i);
                }
                if (Json_util::skip_blanks(i) != ',') break;
                Json_util::discard(i);
            }
            if (Json_util::skip_blanks(i) != '}') {
                throw logic_error("format error: expecting '}'");
            }
            Json_util::discard(i);
            _check_mandatory_members(members_name);
        } else {
            throw logic_error("format error: expecting '{'");
        }
    }

    void Json_builder::json_write(ostream &o) const {
        bool first = true;
        o << '{';
        for (auto &m:members){
            if (m.mandatory || !m.ref->empty()) {
                if (!first) o << ',';
                first = false;
                o << '"' << m.name << '"' << ':';
                m.ref->json_write(o);
            }
        }
        o << '}';
    }

    void Json_builder::_check_mandatory_members(const vector<std::string> &names) {
        for (auto &member:members){
            if (member.mandatory){
                bool found = false;
                for (auto &name:names){
                    if (name == member.name) {
                        found = true;
                        break;
                    }
                }
                if (!found) throw logic_error("member '" + member.name + "' missing and marked as mandatory");
            }
        }
    }

    void Json_builder::json_ignore_member(const std::string &member_name) {
        _ignored_members.push_back(member_name);
    }

    int Json_builder::_find_member(const string &name) {
        string cased_name = name;
        if (!case_sensitive) {
            ToLower(cased_name);
        }
        for (unsigned int i = 0; i < members.size(); i++) {
            if (members[i].name == cased_name) return i;
        }
        if (_ignore_additional_members) return -2;
        for (auto &m: _ignored_members) {
            if (m == cased_name) return -2;
        }
        return -1;
    }

    void Json_builder::json_ignore_additional_members() {
        _ignore_additional_members = true;
    }
}