#pragma once
#include <json_cpp/json_base.h>
#include <json_cpp/json_util.h>

namespace json_cpp {
    struct Json_dictionary : Json_base{
        struct Item : Json_base  {
            void json_parse(std::istream &) override;
            void json_write(std::ostream &) const override;
            std::string value;
            bool require_quotes;
            Json_dictionary to_dict();
        };
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        bool contains (const std::string &);
        size_t size();
        Item operator [](const std::string &);
        std::vector<Item> items;
        std::vector<std::string> keys;
    };
}