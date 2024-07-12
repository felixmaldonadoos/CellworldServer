#pragma once
#include <vector>
#include <sstream>
#include <fstream>
#include <iostream>
#include <typeinfo>

namespace requests {
    struct Response{
        std::string get_string() const;
        friend std::ostream & operator << (std::ostream & , Response &);
        std::istream &get_stream();
        void save (const std::string &);
        template <class T>
        T get() {
            T o;
            try {
                get_stream() >> o;
            } catch (...) {
                throw std::logic_error("failed to load content from " + url + " into variable of type " + typeid(o).name() );
            }
            return o;
        }
        ~Response();
    private:
        explicit Response(const std::string &, const std::string &);
        const std::string _file_path;
        const std::string url;
        std::ifstream ifs;
        friend struct Request;
    };
}