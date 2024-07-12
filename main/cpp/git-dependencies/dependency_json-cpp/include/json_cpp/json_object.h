#pragma once
#include <json_cpp/json_builder.h>

#define Json_object_members(ADD_MEMBERS) void json_set_builder(json_cpp::Json_builder &jb) override{ADD_MEMBERS} void json_set_builder(json_cpp::Json_builder &jb) const override{ADD_MEMBERS}

#define Add_member(VARIABLE) jb.json_add_member(#VARIABLE,true,std::move(Json_wrap_object(VARIABLE).get_unique_ptr()))
#define Add_optional_member(VARIABLE) jb.json_add_member(#VARIABLE,false,std::move(Json_wrap_object(VARIABLE).get_unique_ptr()))
#define Add_member_with_name(VARIABLE, MANDATORY, NAME) jb.json_add_member(NAME,MANDATORY,std::move(Json_wrap_object(VARIABLE).get_unique_ptr()))
#define Case_insensitive() jb.case_sensitive = false;
#define Ignore_member(MEMBER_NAME) jb.json_ignore_member(MEMBER_NAME)
#define Ignore_additional_members() jb.json_ignore_additional_members()

namespace json_cpp {
    struct Json_object : Json_base{
        Json_object();
        virtual void json_set_builder(Json_builder &);
        virtual void json_set_builder(Json_builder &) const;
        virtual void after_load() {};
        virtual void after_load() const{};
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        std::string json_type() const override {
            return "object";
        }
    };
}