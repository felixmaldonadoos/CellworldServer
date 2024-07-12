#include <json_cpp/json_builder.h>
#include <json_cpp/json_base.h>
#include <json_cpp/json_vector.h>
#include <unordered_map>

namespace json_cpp {


    struct Json_descriptor : Json_base {
        enum class Json_descriptor_type {
            Null,
            Bool,
            Int,
            Float,
            String,
            Object,
            List
        };
        virtual Json_descriptor* new_item() const {
            return new Json_descriptor();
        };
        virtual Json_descriptor_type get_type() { return Json_descriptor_type::Null; };
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        virtual ~Json_descriptor() = default;
    };

    struct Json_null_descriptor : Json_descriptor {

    };

    struct Json_descriptor_container : std::vector<Json_descriptor *> {
        ~Json_descriptor_container();
        void replace(size_t, Json_descriptor &);
        Json_descriptor_container &operator = (const Json_descriptor_container &);
    };

    struct Json_bool_descriptor :Json_descriptor {
        Json_bool_descriptor() = default;
        explicit Json_bool_descriptor(bool value) : value(value) {};
        [[nodiscard]] Json_descriptor* new_item() const override {
            auto *item = new Json_bool_descriptor();
            item->value = value;
            return item;
        };
        Json_descriptor_type get_type() override {return Json_descriptor_type::Bool;}
        bool value{};
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        ~Json_bool_descriptor() override = default;
    };

    struct Json_int_descriptor :Json_descriptor {
        Json_int_descriptor() = default;
        explicit Json_int_descriptor(int value) : value(value) {};
        [[nodiscard]] Json_descriptor* new_item() const override {
            auto *item = new Json_int_descriptor();
            item->value = value;
            return item;
        };
        Json_descriptor_type get_type() override {return Json_descriptor_type::Int;}
        int value{};
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        ~Json_int_descriptor() override = default;
    };

    struct Json_float_descriptor :Json_descriptor {
        Json_float_descriptor() = default;
        explicit Json_float_descriptor(float value) : value(value) {};
        [[nodiscard]] Json_descriptor* new_item() const override {
            auto *item = new Json_float_descriptor();
            item->value = value;
            return item;
        };
        Json_descriptor_type get_type() override {return Json_descriptor_type::Float;}
        float value{};
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        ~Json_float_descriptor() override = default;
    };

    struct Json_string_descriptor :Json_descriptor {
        Json_string_descriptor() = default;
        Json_string_descriptor(std::string value) : value(value) {};
        [[nodiscard]] Json_descriptor* new_item() const override {
            auto *item = new Json_string_descriptor();
            item->value = value;
            return item;
        };
        Json_descriptor_type get_type() override {return Json_descriptor_type::String;}
        std::string value{};
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        ~Json_string_descriptor() override = default;
    };

    struct Json_list_descriptor;

    struct Json_object_descriptor :Json_descriptor {
        [[nodiscard]] Json_descriptor* new_item() const override {
            auto *i = new Json_object_descriptor();
            *i  = *this;
            return i;
        };
        Json_descriptor_type get_type() override {return Json_descriptor_type::Object;}
        void add_member(const std::string &, Json_descriptor &, bool member_mandatory);
        Json_descriptor_container members_descriptor;
        std::vector<std::string> members_name;
        std::vector<bool> members_mandatory;
        void set(const std::string &, Json_descriptor &);
        void set(const std::string &, bool);
        void set(const std::string &, int);
        void set(const std::string &, float);
        void set(const std::string &, std::string);
        Json_descriptor &get(const std::string);
        int find(const std::string &);
        bool contains(const std::string &);
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        ~Json_object_descriptor() override = default;
    };

    struct Json_list_descriptor : Json_descriptor {
        Json_descriptor* new_item() const override {
            auto *item = new Json_list_descriptor();
            item->value = value;
            return item;
        };
        Json_descriptor_type get_type() override {return Json_descriptor_type::List;}
        Json_descriptor_container value{};
        const Json_descriptor *item_descriptor{};
        void set_item_descriptor(const Json_descriptor &item_descriptor);
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
        ~Json_list_descriptor() override;
    };

    struct Json_variant_descriptor :Json_descriptor {
        [[nodiscard]] Json_descriptor* new_item() const override {
            auto *i = new Json_variant_descriptor();
            *i  = *this;
            return i;
        };
        Json_descriptor *value{};
        Json_descriptor_type get_type() override {
            if (value) return value->get_type();
            return Json_descriptor_type::Null;
        }
        void clear();
        ~Json_variant_descriptor() override;
        Json_variant_descriptor &operator =(const Json_variant_descriptor &);
        Json_variant_descriptor &operator =(const Json_descriptor &);
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
    };

    struct Json_variant_object_descriptor :Json_descriptor {
        [[nodiscard]] Json_descriptor* new_item() const override {
            auto *i = new Json_variant_object_descriptor();
            *i  = *this;
            return i;
        };
        ~Json_variant_object_descriptor() override = default;
        Json_descriptor_container members_descriptor;
        std::vector<std::string> members_name;
        void json_parse(std::istream &) override;
        void json_write(std::ostream &) const override;
    };
}