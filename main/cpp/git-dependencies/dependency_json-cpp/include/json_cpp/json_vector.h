#pragma once
#include <json_cpp/json_wrapper.h>
namespace json_cpp {
    template<class T>
    struct Json_vector : Json_base, std::vector<T> {
        Json_vector () {};
        Json_vector (size_t s): std::vector<T>(s) {

        }
        Json_vector (size_t s, T e): std::vector<T>(s,e) {

        }
        std::string json_type() const override {
            return "array";
        }

        void json_parse(std::istream &i) override {
            if constexpr (std::is_default_constructible<T>::value) {
                if (Json_util::skip_blanks(i) != '[') throw std::logic_error("format error");
                Json_util::discard(i);
                Json_vector<T> &o = *this;
                o.clear();
                while ((Json_util::skip_blanks(i) != ']')) {
                    T value;
                    if constexpr (std::is_base_of<Json_base, T>::value) {
                        i >> value;
                    } else {
                        Json_object_wrapper<T> wrapped(value);
                        i >> wrapped;
                    }
                    o.push_back(value);
                    if (Json_util::skip_blanks(i) != ',') break;
                    Json_util::discard(i);
                }
                if (Json_util::skip_blanks(i, true) != ']') throw std::logic_error("format error");
            }
        }

        void json_write(std::ostream &o) const override {
            o << "[";
            bool first = true;
            for (const auto &i:*this) {
                if (!first) o << ",";
                first = false;
                if constexpr (std::is_base_of<Json_base, T>::value) {
                    o << i;
                } else {
                    Json_object_wrapper<T> wrapped(i);
                    o << wrapped;
                }
            }
            o << "]";
        }

        int index_of(const T &o) const {
            for (unsigned int i=0;i<this->size(); i++) if ((*this)[i]==o) return i;
            return -1;
        }

        template<typename FILTER>
        Json_vector<T> filter(FILTER filter) const
        {
            Json_vector<T> filtered;
            for (auto &i:*this) if (filter(i)) filtered.push_back(i);
            return filtered;
        }

        template<typename CRITERIA>
        int find_first_index(CRITERIA criteria) const
        {
            for (unsigned int i=0;i<this->size(); i++) if (criteria((*this)[i])) return (int)i;
            throw std::runtime_error("no item matches the criteria");
        }

        template<typename CRITERIA>
        T &find_first(CRITERIA criteria)
        {
            for (T &i:*this) if (criteria(i)) return i;
            throw std::runtime_error("no item matches the criteria");
        }

        template<typename CRITERIA>
        const T &find_first(CRITERIA criteria) const
        {
            for (const T &i:*this) if (criteria(i)) return i;
            throw std::runtime_error("no item matches the criteria");
        }

        template<class NEW_T, typename PROCESS>
        Json_vector<NEW_T> process(PROCESS process) const
        {
            Json_vector<NEW_T> processed;
            for (const T &i:*this) processed.push_back(process(i));
            return processed;
        }

        template<typename CRITERIA>
        size_t count(CRITERIA criteria) const
        {
            size_t c = 0;
            for (const T &i:*this) if (criteria(i)) c++;
            return c;
        }

        template<typename CRITERIA>
        float sum(CRITERIA criteria) const
        {
            float s = 0;
            for (const T &i:*this) s+= criteria(i);
            return s;
        }

        template<typename CRITERIA>
        float max(CRITERIA criteria) const
        {
            bool first = true;
            float m = 0;
            for (const T &i:*this) {
                auto s = criteria(i);
                if (first || s>m) m=s;
                first = false;
            }
            return m;
        }

        template<typename CRITERIA>
        float min(CRITERIA criteria) const
        {
            bool first = true;
            float m = 0;
            for (const T &i:*this) {
                auto s = criteria(i);
                if (first || s<m) m=s;
                first = false;
            }
            return m;
        }

        bool contains(const T &o) const {
            return index_of(o) != -1;
        }

        T get_item_at(unsigned int index) {
            return (*(this))[index];
        }

        void set_item_at(unsigned int index, T &item) {
            if (index >= this->size()) {
                throw std::runtime_error("key " + std::to_string(index) + " not found.");
            }
            (*(this))[index] = item;
        }

        Json_vector<T> reversed() const {
            Json_vector<T> r(this->size());
            size_t index = this->size();
            for(const auto &i:(*this)){
                r[--index] = i;
            }
            return r;
        }

        Json_vector<T> &operator = (const std::vector<T>&v) {
            this->clear();
            for (const auto &i:v) this->push_back(i);
            return *this;
        };
    };
}