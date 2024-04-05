def json_get_parameters(funct):
    if hasattr(funct, "__parameters__"):
        return funct.__parameters__
    else:
        from inspect import signature
        from .json_object import JsonObject, JsonList
        parameters = signature(funct).parameters
        __parameters__ = JsonList(list_type=JsonObject)
        for parameter_number, parameter_name in enumerate(parameters):
            if parameter_number == 0 and (parameter_name == "self" or parameter_name == "cls"):
                continue
            __parameters__.append(JsonObject(name=parameter_name,
                                             type=parameters[parameter_name].annotation.__name__))
        return __parameters__


def _use_self_or_cls(funct):
    from inspect import signature, _empty
    s = signature(funct)
    b = "self" in s.parameters and s.parameters["self"].annotation is _empty
    if b:
        return b
    b = "cls" in s.parameters and s.parameters["cls"].annotation is _empty
    if b:
        return b
    b = "self_or_cls" in s.parameters and s.parameters["self_or_cls"].annotation is _empty
    return b


def json_force_parameter_type_function(funct):
    def decorated(*args, **kwargs):
        from inspect import signature
        from .json_object import JsonObject, JsonList
        if args:
            args = list(args)
        parameters = signature(funct).parameters
        for pi, p in enumerate(parameters):
            if issubclass(parameters[p].annotation, JsonObject) and parameters[p].annotation is not JsonObject:
                if p in kwargs and isinstance(kwargs[p], JsonObject):
                    kwargs[p] = kwargs[p].into(parameters[p].annotation)
                if pi < len(args):
                    args.insert(pi, args.pop(pi).into(parameters[p].annotation))
            elif issubclass(parameters[p].annotation, JsonList) and parameters[p].annotation is not JsonList:
                if p in kwargs and isinstance(kwargs[p], JsonList):
                    kwargs[p] = kwargs[p].into(parameters[p].annotation)
                if pi < len(args):
                    args.insert(pi, args.pop(pi).into(parameters[p].annotation))
            elif p in kwargs and type(kwargs[p]) is str and parameters[p].annotation is not str:
                kwargs[p] = parameters[p].annotation(kwargs[p])
                if pi < len(args):
                    args.insert(pi, args.pop(pi).into(parameters[p].annotation))
        return funct(*args, **kwargs)
    decorated.__parameters__ = json_get_parameters(funct)
    return decorated


def json_force_parameter_type_method(funct):
    def decorated(self_or_cls, *args, **kwargs):
        from inspect import signature
        from .json_object import JsonObject, JsonList
        if args:
            args = list(args)
        parameters = signature(funct).parameters
        for pi, p in enumerate(parameters):
            if issubclass(parameters[p].annotation, JsonObject) and parameters[p].annotation is not JsonObject:
                if p in kwargs and isinstance(kwargs[p], JsonObject):
                    kwargs[p] = kwargs[p].into(parameters[p].annotation)
                if pi < len(args):
                    args.insert(pi, args.pop(pi).into(parameters[p].annotation))
            elif issubclass(parameters[p].annotation, JsonList) and parameters[p].annotation is not JsonList:
                if p in kwargs and isinstance(kwargs[p], JsonList):
                    kwargs[p] = kwargs[p].into(parameters[p].annotation)
                if pi < len(args):
                    args.insert(pi, args.pop(pi).into(parameters[p].annotation))
            elif p in kwargs and type(kwargs[p]) is str and parameters[p].annotation is not str:
                kwargs[p] = parameters[p].annotation(kwargs[p])
                if pi < len(args):
                    args.insert(pi, args.pop(pi).into(parameters[p].annotation))
        return funct(self_or_cls, *args, **kwargs)
    decorated.__parameters__ = json_get_parameters(funct)
    return decorated


def json_force_parameter_type(funct):
    if _use_self_or_cls(funct):
        return json_force_parameter_type_method(funct)
    else:
        return json_force_parameter_type_function(funct)


def json_parameters_function(funct):
    def decorated(json_object):
        from .json_object import JsonObject
        if not isinstance(json_object, JsonObject):
            raise TypeError("Parameter must be JsonObject instance")
        p = json_object.to_dict()
        return funct(**p)
    decorated.__parameters__ = json_get_parameters(funct)
    return decorated


def json_parameters_method(funct):
    from inspect import signature
    def decorated(self_or_cls, json_object):
        from .json_object import JsonObject
        if not isinstance(json_object, JsonObject):
            raise TypeError("Parameter must be JsonObject instance")
        p = json_object.to_dict()
        return funct(self_or_cls, **p)
    decorated.__parameters__ = json_get_parameters(funct)
    return decorated


def json_parameters(funct):
    if _use_self_or_cls(funct):
        return json_parameters_method(funct)
    else:
        return json_parameters_function(funct)


def json_parse(json_object_type=None):
    def decorator(funct):
        from .json_object import JsonObject
        if _use_self_or_cls(funct):
            if json_object_type:
                def decorated(self_or_cls, json_string: str):
                    return funct(self_or_cls, json_object_type.parse(json_string))
            else:
                def decorated(self_or_cls, json_string: str):
                    return funct(self_or_cls, JsonObject.load(json_string))
        else:
            if json_object_type:
                def decorated(json_string: str):
                    return funct(json_object_type.parse(json_string))
            else:
                def decorated(json_string: str):
                    return funct(JsonObject.load(json_string))
        decorated.__parameters__ = json_get_parameters(funct)
        return decorated
    if not type(json_object_type) is type:
        funct = json_object_type
        json_object_type = None
        return decorator(funct)
    return decorator


class classorinstancemethod(classmethod):

    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)
