#include <json_cpp/json_wrapper.h>
#define Json_id(ID_MEMBER) virtual void json_write(std::ostream &o) const { o << Json_wrap_object(_json_reference.get().ID_MEMBER); }

namespace json_cpp {
    template <class T>
    struct Json_reference : Json_base{
        Json_reference(T &o) : _json_reference(o) {}
    protected:
        std::reference_wrapper<T> _json_reference;
    };
}