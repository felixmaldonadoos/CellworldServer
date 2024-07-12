#include <json_cpp/python/json_descriptor.h>

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

using namespace json_cpp;
using namespace std;

PYBIND11_MODULE(core, m) {

    pybind11::class_<Json_bool_descriptor>(m, "JsonBoolDescriptor")
            .def(pybind11::init<>())
            .def_readwrite("value", &Json_bool_descriptor::value)
            .def("load", &Json_bool_descriptor::load)
            .def("save", &Json_bool_descriptor::save)
            .def("__str__", &Json_bool_descriptor::to_json)
            .def("__repr__", &Json_bool_descriptor::to_json)
            .def("to_json", &Json_bool_descriptor::to_json)
            .def("from_json", &Json_bool_descriptor::from_json)
    ;

    pybind11::class_<Json_int_descriptor>(m, "JsonIntDescriptor")
            .def(pybind11::init<>())
            .def_readwrite("value", &Json_int_descriptor::value)
            .def("load", &Json_int_descriptor::load)
            .def("save", &Json_int_descriptor::save)
            .def("__str__", &Json_int_descriptor::to_json)
            .def("__repr__", &Json_int_descriptor::to_json)
            .def("to_json", &Json_int_descriptor::to_json)
            .def("from_json", &Json_int_descriptor::from_json)
    ;

    pybind11::class_<Json_float_descriptor>(m, "JsonFloatDescriptor")
            .def(pybind11::init<>())
            .def_readwrite("value", &Json_float_descriptor::value)
            .def("load", &Json_float_descriptor::load)
            .def("save", &Json_float_descriptor::save)
            .def("__str__", &Json_float_descriptor::to_json)
            .def("__repr__", &Json_float_descriptor::to_json)
            .def("to_json", &Json_float_descriptor::to_json)
            .def("from_json", &Json_float_descriptor::from_json)
    ;

    pybind11::class_<Json_string_descriptor>(m, "JsonStringDescriptor")
            .def(pybind11::init<>())
            .def_readwrite("value", &Json_string_descriptor::value)
            .def("load", &Json_string_descriptor::load)
            .def("save", &Json_string_descriptor::save)
            .def("__str__", &Json_string_descriptor::to_json)
            .def("__repr__", &Json_string_descriptor::to_json)
            .def("to_json", &Json_string_descriptor::to_json)
            .def("from_json", &Json_string_descriptor::from_json)
    ;

    pybind11::class_<Json_object_descriptor>(m, "JsonObjectDescriptor")
            .def(pybind11::init<>())
            .def("add_member",+[](Json_object_descriptor &o, const string &n, Json_bool_descriptor &d){
                o.add_member(n, d, true);
            })
            .def("add_member",+[](Json_object_descriptor &o, const string &n, Json_int_descriptor &d){
                o.add_member(n, d, true);
            })
            .def("add_member",+[](Json_object_descriptor &o, const string &n, Json_float_descriptor &d){
                o.add_member(n, d, true);
            })
            .def("add_member",+[](Json_object_descriptor &o, const string &n, Json_string_descriptor &d){
                o.add_member(n, d, true);
            })
            .def("add_member",+[](Json_object_descriptor &o, const string &n, Json_object_descriptor &d){
                o.add_member(n, d, true);
            })
            .def("add_member",+[](Json_object_descriptor &o, const string &n, Json_list_descriptor &d){
                o.add_member(n, d, true);
            })
            .def("load", &Json_object_descriptor::load)
            .def("save", &Json_object_descriptor::save)
            .def("__str__", &Json_object_descriptor::to_json)
            .def("__repr__", &Json_object_descriptor::to_json)
            .def("to_json", &Json_object_descriptor::to_json)
            .def("from_json", &Json_object_descriptor::from_json)
    ;

    pybind11::class_<Json_list_descriptor>(m, "JsonListDescriptor")
            .def(pybind11::init<>())
            .def("set_item_descriptor",+[](Json_list_descriptor &o, Json_bool_descriptor &d){
                o.set_item_descriptor(d);
            })
            .def("set_item_descriptor",+[](Json_list_descriptor &o, Json_int_descriptor &d){
                o.set_item_descriptor(d);
            })
            .def("set_item_descriptor",+[](Json_list_descriptor &o, Json_float_descriptor &d){
                o.set_item_descriptor(d);
            })
            .def("set_item_descriptor",+[](Json_list_descriptor &o, Json_string_descriptor &d){
                o.set_item_descriptor(d);
            })
            .def("set_item_descriptor",+[](Json_list_descriptor &o, Json_object_descriptor &d){
                o.set_item_descriptor(d);
            })
            .def("set_item_descriptor",+[](Json_list_descriptor &o, Json_list_descriptor &d){
                o.set_item_descriptor(d);
            })
            .def("load", &Json_list_descriptor::load)
            .def("save", &Json_list_descriptor::save)
            .def("__str__", &Json_list_descriptor::to_json)
            .def("__repr__", &Json_list_descriptor::to_json)
            .def("to_json", &Json_list_descriptor::to_json)
            .def("from_json", &Json_list_descriptor::from_json)
    ;
}
