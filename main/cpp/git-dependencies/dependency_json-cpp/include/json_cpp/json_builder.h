#pragma once
#include <iostream>
#include <memory>
#include <json_cpp/json_util.h>
#include <json_cpp/json_base.h>
#include <json_cpp/json_wrapper.h>

namespace json_cpp {
    struct Json_builder : Json_base{
        void json_add_member(std::string, bool, std::unique_ptr<Json_wrapped>);
        void json_ignore_member(const std::string &);
        void json_ignore_additional_members();
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        struct Json_member {
            Json_member (std::string, bool, std::unique_ptr<Json_wrapped> );
            std::string name;
            bool mandatory;
            std::unique_ptr<Json_wrapped> ref;
        };
        std::vector<Json_member> members;
        bool case_sensitive = true;
    protected:
        int _find_member(const std::string &);
        void _check_mandatory_members(const std::vector<std::string> &);
        std::vector<std::string> _ignored_members;
        bool _ignore_additional_members{};
    };
}