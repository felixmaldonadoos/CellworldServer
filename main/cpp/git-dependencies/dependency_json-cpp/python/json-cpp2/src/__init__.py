#add imports here

from . import core

class JsonObject(core.JsonObject):

    def __get_descriptor__(self):
        jd = core.JsonObject()
        members = vars(self)
        for member_name in members:
            if member_name[0] == "_": #keep private members out
                continue
            member_value = members[member_name]
            member_type = type(member_value)
            if member_type is bool:
                jd.set_bool_member(member_name, member_value)
            elif member_type is int:
                jd.set_int_member(member_name, member_value)
            elif member_type is float:
                jd.set_float_member(member_name, member_value)
            elif member_type is str:
                jd.set_string_member(member_name, member_value)
            elif issubclass(member_type, JsonObject):
                jd.set_object_member(member_name, member_value.__get_descriptor__())
            else:
                raise "type not supported"
        return jd

    def __from_descriptor__(self, jd: core.JsonObject):
        members = jd.get_members_list()
        for member in members:
            if member.python_type == "bool":
                setattr(self, member.name, jd.get_bool_member(member.name))
            elif member.python_type == "int":
                setattr(self, member.name, jd.get_int_member(member.name))
            elif member.python_type == "float":
                setattr(self, member.name, jd.get_float_member(member.name))
            elif member.python_type == "string":
                setattr(self, member.name, jd.get_string_member(member.name))
            elif member.python_type == "object":
                member_value = getattr(self, member.name)
                if issubclass(type(member_value), JsonObject):
                    member_value.__from_descriptor__(jd.get_object_member(member.name))
                else:
                    raise member.name + "must inherit from JsonObject"
            else:
                raise "type not supported"

    def __str__(self):
        return str(self.__get_descriptor__())

    def from_json(self, json_string: str):
        jd = self.__get_descriptor__()
        jd.from_json(json_string)
        self.__from_descriptor__(jd)


class JsonList(list):

    def __init__(self, list_type: type):
        self.__list_type__ = list_type

    def __str__(self):
        if self.__list_type__ is bool:
            python_type = "bool"
        elif self.__list_type__ is int:
            python_type = "int"
        elif self.__list_type__ is float:
            python_type = "float"
        elif self.__list_type__ is str:
            python_type = "str"
        elif issubclass(self.__list_type__, JsonObject):
            python_type = "object"
        elif issubclass(self.__list_type__, JsonList):
            python_type = "list"
        else:
            raise "type not supported"

        jl = core.JsonList(python_type)
        jl.append



# class _Json_member:
#     def __init__(self, json_class, member_name):
#         self.member_name = member_name
#         setattr(json_class, member_name, property(fget=self._get_, fset=self._set_))
#
#     def _set_( self, o, value):
#         if type(value) is bool:
#             o.set_bool_member(self.member_name, value)
#         elif type(value) is int:
#             o.set_int_member(self.member_name, value)
#         elif type(value) is float:
#             o.set_float_member(self.member_name, value)
#         elif type(value) is str:
#             o.set_string_member(self.member_name, value)
#         elif issubclass(type(value), JsonObject):
#             o.set_object_member(self.member_name, value)
#         else:
#             raise "type not supported"
#
#     def _get_(self, o):
#         t = o.get_member_type(self.member_name)
#         if t == "bool":
#             return o.get_bool_member(self.member_name)
#         elif t == "int":
#             return o.get_int_member(self.member_name)
#         elif t == "float":
#             return o.get_float_member(self.member_name)
#         elif t == "string":
#             return o.get_string_member(self.member_name)
#         elif t == "object":
#             return o.get_object_member(self.member_name)
#         else:
#             raise "type not supported"
#
#
# class JsonObject(core.JsonObject):
#     def __init__(self):
#         core.JsonObject.__init__(self)
#         v = vars(self).copy()
#         if hasattr(self.__class__, "_getsets_"):
#             _getsets_=getattr(self.__class__, "_getsets_")
#         else:
#             _getsets_ = dict()
#         for k in v:
#             if k[0] == "_":
#                 continue
#             if not k in _getsets_:
#                 _getsets_[k] = _Json_member( self.__class__, k )
#             _getsets_[k]._set_(self, v[k])
#         setattr(self.__class__, "_getsets_" , _getsets_)
