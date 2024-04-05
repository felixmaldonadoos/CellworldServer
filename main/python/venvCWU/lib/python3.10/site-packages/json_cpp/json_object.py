import json
from .util import check_type
from datetime import datetime
import requests
from os import path
from .decorators import classorinstancemethod
from .search import bin_search, SearchType, SortOrder, NotFoundBehavior
from enum import Enum
import base64


class JsonParseBehavior(Enum):
    RaiseError = 0
    IgnoreNewAttributes = 1
    IncorporateNewAttributes = 2


class JsonDate:
    """
    A utility class representing date format configurations for JSON serialization and deserialization.

    Attributes:
        date_format (str): The format string used for date-time serialization and deserialization.
    """
    date_format = '%Y-%m-%d %H:%M:%S.%f'


class JsonObject:
    """
    A generic object to represent and manipulate JSON-like data structures.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize a new instance of JsonObject.

        Parameters:
        - args (tuple): Optional argument, typically a JSON string.
        - kwargs (dict): Keyword arguments representing members of the object.

        Example:
        js = JsonObject(my_attribute1="str_value", my_attribute2=1, my_attribute3=5.2, my_attribute4=True, my_attribute2=DateTime(2023,10,30))
        print(js)           # Outputs: '{"my_attribute1":"str_value","my_attribute2":1,"my_attribute3":5.2,"my_attribute4":true,"my_attribute5":"2023-10-30 00:00:00.000000"}'

        """
        if args:
            if type(args[0]) is str:
                parsed = JsonObject.load(args[0])
                JsonObject.__init__(self, **parsed.to_dict())
        if type(self) is JsonObject:
            for key, value in kwargs.items():
                setattr(self, key, value)

        self._force_include = None

    def __str__(self):
        """
        Returns a string representation of the JsonObject in JSON format.

        Returns:
            str: JSON-formatted string.
        """
        s = ""
        for k in self.get_members():
            if s:
                s += ","
            s += "\"%s\":" % k
            i = JsonObject.__getitem__(self, k)
            if isinstance(i, Enum):
                i = i.name
            if isinstance(i, str):
                s += "%s" % json.dumps(i)
            elif isinstance(i, datetime):
                s += "\"%s\"" % i.strftime(JsonDate.date_format)
            elif isinstance(i, bytes):
                s += "\"%s\"" % base64.b64encode(i)
            elif isinstance(i, bool):
                s += "%s" % str(i).lower()
            elif i is None:
                s += "null"
            else:
                s += "%s" % str(i)
        return "{%s}" % s

    def get_numeric_values(self):
        """
        Retrieve numeric values contained within the JsonObject.

        Returns:
            JsonList: List containing numeric values from the JsonObject.
        """
        values = JsonList()
        for k in self.get_numeric_columns():
            values.append(JsonObject.__getitem__(self, k))
        return values

    def get_values(self):
        """
        Retrieve all values contained within the JsonObject.

        Returns:
            JsonList: List containing all values from the JsonObject.
        """
        values = JsonList()
        for k in self.get_columns():
            value = JsonObject.__getitem__(self, k)
            if isinstance(value, JsonList):
                values.append(value.get_values())
            else:
                values.append(value)
        return values

    def set_values(self, values: list):
        """
        Set values for the JsonObject given a list of values.

        Parameters:
            values (list): List of values to set in the JsonObject.

        Returns:
            list: The provided list of values.

        Raises:
            RuntimeError: If mismatch in expected and received values.
        """
        columns = self.get_columns()
        if len(columns) != len(values):
            if len(columns) < len(values):
                raise RuntimeError("Not enough values to populate JsonObject. Expected: %i, Received: %i" % (len(columns), len(values)))
            else:
                raise RuntimeError("Too many values to populate JsonObject. Expected: %i, Received: %i" % (len(columns), len(values)))
        for i, k in enumerate(self.get_columns()):
            if isinstance(JsonObject.__getitem__(self, k), JsonList):
                JsonObject.__getitem__(self, k).set_values(values[i])
            else:
                JsonObject.__setitem__(self, k, values[i])
        return values

    def get_numeric_columns(self):
        """
        Retrieve the names of columns containing numeric values.

        Returns:
            JsonList: List of column names with numeric values.
        """
        columns = JsonList(list_type=str)
        for v in self.get_members():
            if isinstance(JsonObject.__getitem__(self, v), JsonObject):
                columns += [v + "." + c for c in self[v].get_numeric_columns()]
            else:
                i = JsonObject.__getitem__(self, v)
                t = type(i)
                if t is float or t is int or t is bool:
                    columns.append(v)
        return columns

    def into(self, cls: type,
             behavior: JsonParseBehavior = JsonParseBehavior.RaiseError):
        """
        Convert the current JsonObject into an instance of another JsonObject-derived class.

        Parameters:
            cls (type): The target JsonObject-derived class to convert to.

        Returns:
            JsonObject-derived instance: The converted object.

        Raises:
            RuntimeError: If provided type does not derive from JsonObject.
        """
        if not issubclass(cls, JsonObject):
            raise RuntimeError("type must derive from JsonObject")
        nv = cls.parse(json_string=str(self), behavior=behavior)
        return nv

    def get_columns(self):
        """
        Retrieve the names of all columns contained within the JsonObject.

        Returns:
            JsonList: List of all column names in the JsonObject.
        """
        columns = JsonList(list_type=str)
        for v in self.get_members():
            if isinstance(JsonObject.__getitem__(self, v), JsonObject):
                columns += [v + "." + c for c in JsonObject.__getitem__(self, v).get_columns()]
            else:
                columns.append(v)
        return columns

    def __repr__(self):
        """
        Returns a string representation of the JsonObject for debugging purposes.

        Returns:
            str: String representation of the JsonObject.
        """
        return str(self)

    def __eq__(self, other):
        """
        Check equality with another JsonObject.

        Parameters:
            other (JsonObject): Another JsonObject instance to compare with.

        Returns:
            bool: True if both objects are equal, False otherwise.
        """
        if type(self) is not type(other):
            return False
        for k in self.get_members():
            if self[k] != other[k]:
                return False
        return True

    def __getitem__(self, key):
        """
        Retrieve the value associated with a given key or nested key.

        Parameters:
            key (str): The attribute name or nested key to retrieve.

        Returns:
            Any: Value associated with the key.
        """
        if "." in key:
            parts = key.split(".")
            new_key = ".".join(parts[1:])
            key = parts[0]
            return JsonObject.__getitem__(JsonObject.__getitem__(self, key), new_key)
        else:
            return getattr(self, key)

    def __setitem__(self, key, value):
        """
        Set the value associated with a given key or nested key.

        Parameters:
            key (str): The attribute name or nested key to assign a value to.
            value (Any): The value to set for the given key.
        """
        if "." in key:
            parts = key.split(".")
            new_key = ".".join(parts[1:])
            key = parts[0]
            JsonObject.__setitem__(JsonObject.__getitem__(self, key), new_key, value)
        else:
            setattr(self, key, value)

    def __iter__(self):
        """
        Return an iterator over the columns of the JsonObject.

        Returns:
            Iterator: Iterator over the JsonObject columns.
        """
        for k in self.get_members():
            yield k

    def force_include(self, member_name: str):
        """
        Adds the specified member name to list of hidden members forced during the serialization.

        This method is used to append a member name to the `_force_include` list attribute of the class.
        If `_force_include` is already initialized (i.e., not None), the `member_name` is appended to it.
        If `_force_include` is not initialized (i.e., None), it is first initialized as a list with the `member_name` as its first element.

        Parameters:
        member_name (str): The name of the member to be added to the `_force_include` list.

        Returns:
        None: This method does not return any value. It updates the `_force_include` list in place.
        """
        if self._force_include:
            self._force_include.append(member_name)
        else:
            self._force_include = [member_name]

    def get_members(self):
        """
        Retrieve all member variables of the JsonObject that don't start with an underscore.

        Returns:
            list: List of member attribute names.
        """
        members = []
        v = vars(self)
        for k in v:
            if not k:
                continue
            if k[0] == "_":
                if self._force_include:
                    if k not in self._force_include:
                        continue
                else:
                    continue
            members.append(k)
        return members

    def copy(self):
        """
        Return a deep copy of the current JsonObject.

        Returns:
            JsonObject: A deep copy of the current object.
        """
        return self.__class__.parse(str(self))

    def format(self, format_string: str):
        """
        Formats the JsonObject using a provided format string.

        Args:
            format_string (str): The format string containing placeholders that match keys in the JsonObject.

        Returns:
            str: A formatted string with placeholders replaced by their corresponding values from the JsonObject.

        Note:
            This method supports nested formatting for nested JsonObjects.
        """
        for k in self.get_members():
            if not isinstance(JsonObject.__getitem__(self, k), (JsonObject,JsonList)):
                continue
            pos = format_string.find("{"+k+":")
            if pos >= 0:
                sub_format_start = format_string.find(":", pos) + 1
                sub_format_end = sub_format_start
                bracket_count = 1
                while bracket_count and sub_format_end < len(format_string):
                    c = format_string[sub_format_end]
                    if c == '{':
                        bracket_count += 1
                    if c == '}':
                        bracket_count -= 1
                    sub_format_end += 1
                sub_format = format_string[sub_format_start:sub_format_end-1]
                sub_str = JsonObject.__getitem__(self, k).format(sub_format)
                format_string = format_string[:pos] + sub_str + format_string[sub_format_end:]
        return format_string.format(**vars(self))


    @classorinstancemethod
    def parse(cls_or_self,
              json_string: str = "",
              json_dictionary: dict = None,
              behavior: JsonParseBehavior = JsonParseBehavior.RaiseError):
        """
        Parse a JSON string or dictionary to populate a JsonObject instance.

        Args:
            json_string (str, optional): A JSON formatted string to be parsed.
            json_dictionary (dict, optional): A dictionary containing the JSON data.

        Returns:
            JsonObject: A populated JsonObject instance.

        Note:
            This method can be used both as a class method and an instance method.
        """
        if json_string:
            json_dictionary = json.loads(json_string)

        if type(cls_or_self) is type:
            new_object = cls_or_self()
        else:
            new_object = cls_or_self

        if type(json_dictionary) is list:
            new_object.set_values(json_dictionary)
        else:
            for key in json_dictionary:
                if hasattr(new_object, key):
                    member = getattr(new_object, key)
                    it = type(member)
                    if issubclass(it, JsonObject):
                        av = it.parse(json_dictionary=json_dictionary[key])
                        setattr(new_object, key, av)
                    elif issubclass(it, JsonList):
                        member.parse(json_list=json_dictionary[key])
                    elif issubclass(it, Enum):
                        av = it[json_dictionary[key]]
                        setattr(new_object, key, av)
                    elif it is datetime:
                        av = datetime.strptime(json_dictionary[key], JsonDate.date_format)
                        setattr(new_object, key, av)
                    elif it is bytes:
                        av = base64.b64decode(json_dictionary[key])
                        setattr(new_object, key, av)
                    else:
                        av = it(json_dictionary[key])
                        setattr(new_object, key, av)
                else:
                    if behavior == JsonParseBehavior.IgnoreNewAttributes:
                        continue
                    elif behavior == JsonParseBehavior.IncorporateNewAttributes:
                        if isinstance(json_dictionary[key], (dict, list)):
                            av = JsonObject.load(json_dictionary_or_list=json_dictionary[key])
                            setattr(new_object, key, av)
                        else:
                            setattr(new_object, key, json_dictionary[key])
                    else:
                        raise RuntimeError("attribute %s not found in class %s" % (key, new_object.__class__.__name__))

        return new_object

    @staticmethod
    def load(json_string: str = "", json_dictionary_or_list=None):
        """
        Load a JSON string or dictionary/list into a JsonObject or JsonList instance.

        Args:
            json_string (str, optional): A JSON formatted string to be loaded.
            json_dictionary_or_list (dict or list, optional): A dictionary or list containing the JSON data.

        Returns:
            JsonObject or JsonList: A populated JsonObject or JsonList instance.

        Raises:
            TypeError: If the provided json_dictionary_or_list is neither a dictionary nor a list.
        """
        if json_string:
            check_type(json_string, str, "wrong type for json_string")
            json_dictionary_or_list = json.loads(json_string)
        if isinstance(json_dictionary_or_list, list):
            new_list = JsonList(list_type=None)
            for item in json_dictionary_or_list:
                if isinstance(item, list) or isinstance(item, dict):
                    new_item = JsonObject.load(json_dictionary_or_list=item)
                else:
                    new_item = item
                new_list.append(new_item)
            return new_list
        elif isinstance(json_dictionary_or_list, dict):
            new_object = JsonObject()
            for key in json_dictionary_or_list.keys():
                if isinstance(json_dictionary_or_list[key], dict) or isinstance(json_dictionary_or_list[key], list):
                    setattr(new_object, key, JsonObject.load(json_dictionary_or_list=json_dictionary_or_list[key]))
                else:
                    setattr(new_object, key, json_dictionary_or_list[key])
            return new_object
        else:
            raise TypeError("wrong type for json_dictionary_or_list")

    def save(self, file_path: str):
        """
        Save the JsonObject to a file in JSON format.

        Args:
            file_path (str): Path to the file where the JsonObject should be saved.
        """
        with open(file_path, 'w') as f:
            f.write(str(self))

    @classmethod
    def load_from_file(cls, file_path: str):
        """
        Load a JsonObject from a file containing a JSON string.

        Args:
            file_path (str): Path to the file containing the JSON data.

        Returns:
            JsonObject or None: A populated JsonObject instance or None if the file doesn't exist.
        """
        if not path.exists(file_path):
            return None
        json_content = ""
        with open(file_path) as f:
            json_content = f.read()
        if cls is JsonObject:
            return cls.load(json_content)
        else:
            return cls.parse(json_content)

    @classmethod
    def load_from_url(cls, uri: str):
        """
        Load a JsonObject from a web URL containing a JSON string.

        Args:
            uri (str): The web URL pointing to the JSON data.

        Returns:
            JsonObject or None: A populated JsonObject instance or None if the request was unsuccessful.
        """
        req = requests.get(uri)
        if req.status_code == 200:
            if cls is JsonObject:
                return cls.load(req.text)
            else:
                return cls.parse(req.text)
        return None

    def __dataframe_values__(self):
        """
        Internal method to prepare data for conversion into a pandas DataFrame.
        """
        return [v.to_dataseries(recursive=True) if isinstance(v, JsonObject) else v.to_dataframe(recursive=True) if isinstance(v, JsonList) else v for v in self.get_values()]

    def to_dataseries(self, recursive: bool = False):
        """
        Convert the JsonObject into a pandas Series.

        Args:
            recursive (bool, optional): If True, converts nested JsonObjects and JsonLists as well.

        Returns:
            pandas.core.series.Series: A pandas Series representation of the JsonObject.
        """
        import pandas as pd
        columns = self.get_columns()
        if recursive:
            values = self.__dataframe_values__()
        else:
            values = self.get_values()

        return pd.core.series.Series(dict(zip(columns, values)))

    def to_dict(self):
        """
        Convert the JsonObject into a standard Python dictionary.

        Returns:
            dict: A dictionary representation of the JsonObject.
        """
        return {a: self[a] for a in self.get_members()}


class JsonList(list):
    """
    An enhanced list for JSON-like data handling with type constraints.

    Attributes:
    - list_type: The allowed type for items in the list.
    - allow_empty: Flag to allow None values in the list.

    Example:
        js = JsonList(list_type=int, iterable=[1,2,3])
        print(js)           # Outputs: [1,2,3]
        js.append(4)
        print(js)           # Outputs: [1,2,3,4]
        js.append(3.4)      # Raises TypeError
        js.append(None)      # Raises TypeError


        js = JsonList(list_type=JsonObject)
        js.append(JsonObject(x=1, y=2))
        js.append(JsonObject(x=3, y=4))
        print(js)           # Outputs: [{"x":1,"y":2},{"x":3,"y":4}]
        js.append(3.4)      # Raises TypeError
        js.append(None)      # Raises TypeError

        js = JsonList(list_type=int, iterable=[1,2,3], allow_empty=True)
        print(js)           # Outputs: [1,2,3]
        js.append(4)
        print(js)           # Outputs: [1,2,3,4]
        js.append(3.4)      # Raises TypeError
        js.append(None)
        print(js)           # Outputs: [1,2,3,4,null]
    """

    def __init__(self, list_type=None, iterable=None, allow_empty: bool = False):
        """
        Initialize the JsonList with a specific type and optionally provide an initial iterable.

        Parameters:
        - list_type (type, optional): The allowed type for items in the list.
        - iterable (iterable, optional): An initial collection of items.
        - allow_empty (bool): Flag to determine if None values are allowed. Default is False.
        """
        iterable = list() if not iterable else iterable
        iter(iterable)
        map(self._typeCheck, iterable)
        list.__init__(self, iterable)
        self.list_type = list_type
        self.allow_empty = allow_empty

    @staticmethod
    def create_type(list_item_type: type, list_type_name: str = "") -> type:
        """
        Dynamically creates a new JsonList subclass for a specific item type.

        Parameters:
        - list_item_type (type): The specific type for items in the new JsonList subclass.
        - list_type_name (str, optional): A name for the new JsonList subclass. Default is an empty string.

        Returns:
        type: A new JsonList subclass type.
        """

        def __init__(self, iterable=None):
            JsonList.__init__(self, iterable=iterable, list_type=list_item_type)
        if not list_type_name:
            list_type_name = "Json_%s_list" % list_item_type.__name__
        newclass = type(list_type_name, (JsonList,), {"__init__": __init__})
        return newclass

    def format(self, format_string: str):
        """
        Formats the JsonList using a provided format string.

        Args:
            format_string (str): The format string containing placeholders that match keys in the JsonList element.

        Returns:
            str: A formatted string with placeholders replaced by their corresponding values from the JsonList element.

        Note:
            This method supports nested formatting for nested JsonList.
        """
        formatted_string = ""
        for k in self:
            if isinstance(k, (JsonObject, JsonList)):
                formatted_string += k.format(format_string=format_string)
            else:
                formatted_string += format_string.format(k)
        return formatted_string

    def _typeCheck(self, val):
        """
        Internal method to check if a value matches the list's predefined type or valid JSON types.

        Parameters:
        - val: The value to check.

        Raises:
        ValueError: If the value does not match the allowed types.
        """
        if val is None and self.allow_empty:
            return
        if self.list_type:
            if self.list_type is float and type(val) is int: #json ints can also be floats
                val = float(val)
            check_type(val, self.list_type, "Wrong type %s, this list can hold only instances of %s" % (type(val), str(self.list_type)))
        else:
            if not isinstance(val, (str, int, float, bool, datetime, JsonList, JsonObject)):
                raise TypeError("Wrong type %s, this list can hold only str, int, float, bool, datetime, JsonObject or JsonList" % (type(val),))

    def __iadd__(self, other):
        """
        Append an iterable to the current list after type checking.

        Args:
            other (iterable): The iterable to be appended to the list.

        Raises:
            TypeError: If the provided value is not of the list type.
        """
        map(self._typeCheck, other)
        list.__iadd__(self, other)
        return self

    def __add__(self, other):
        """
        Concatenates an iterable to the current list after type checking.

        Args:
            other (iterable): The iterable to be appended to the list.

        Raises:
            TypeError: If the provided value is not of the list type.

        Returns:
            A new list with the iterable concatenated to the current list
        """
        iterable = [item for item in self] + [item for item in other]
        return JsonList(list_type=self.list_type, iterable=iterable)

    def __radd__(self, other):
        """
        Concatenates the current list to an iterable after type checking.

        Args:
            other (iterable): The iterable to be appended to the list.

        Raises:
            TypeError: If the provided value is not of the list type.

        Returns:
            A new list with the current list concatenated to the iterable
        """
        iterable = [item for item in other] + [item for item in self]
        if isinstance(other, JsonList):
            return self.__class__(list_type=other.list_type, iterable=iterable)
        return JsonList(list_type=self.list_type, iterable=iterable)

    def __setitem__(self, index, value):
        """
        Set an item of the list to a given an index after type checking.

        Args:
            key (int): The index of the item.
            iterable (iterable): The iterable whose values are to be set in the slice.

        Raises:
            TypeError: If the value type is not the same as the list type.
        """
        itervalue = (value,)
        if isinstance(index, slice):
            iter(value)
            itervalue = value
        map(self._typeCheck, itervalue)
        list.__setitem__(self, index, value)

    def __setslice__(self, i, j, iterable):
        """
        Set a slice of the list to a given iterable after type checking.

        Args:
            i (int): The starting index of the slice.
            j (int): The ending index of the slice.
            iterable (iterable): The iterable whose values are to be set in the slice.

        Raises:
            TypeError: If the iterable contains values not of the list type.
        """
        iter(iterable)
        map(self._typeCheck, iterable)
        list.__setslice__(self, i, j, iterable)

    def append(self, val):
        """
        Append a value to the list after type checking.

        Args:
            val (any): The value to be appended to the list.

        Raises:
            TypeError: If the provided value is not of the list type.
        """
        self._typeCheck(val)
        list.append(self, val)

    def extend(self, iterable):
        """
        Extend the list with values from an iterable after type checking.

        Args:
            iterable (iterable): The iterable whose values are to be added to the list.

        Raises:
            TypeError: If the iterable contains values not of the list type.
        """
        iter(iterable)
        map(self._typeCheck, iterable)
        list.extend(self, iterable)

    def insert(self, i, val):
        """
        Insert a value at a specified index in the list after type checking.

        Args:
            i (int): The index where the value is to be inserted.
            val (any): The value to be inserted into the list.

        Raises:
            TypeError: If the provided value is not of the list type.
        """
        self._typeCheck(val)
        list.insert(self, i, val)

    def __str__(self):
        """
        Provide a string representation of the list.

        Returns:
        str: A JSON-formatted string representation of the list.
        """
        return "[" + ",".join([json.dumps(x) if type(x) is str else "null" if x is None else str(x) for x in self]) + "]"

    def __repr__(self):
        """
        Official string representation of the object, used for debugging and development.

        Returns:
        str: A JSON-formatted string representation of the list.
        """
        return str(self)

    def get(self, m):
        """
        Get values associated with the specified attribute for items in the list.

        Parameters:
        - m (str): The attribute name.

        Returns:
        JsonList: A new list containing the values associated with the specified attribute.
        """
        l = JsonList()
        for i in self:
            if m in vars(i):
                l.append(vars(i)[m])
        return l

    def where(self, m: str, v, o: str = "=="):
        """
        Filter the list based on a given condition.

        Parameters:
        - m (str): The attribute name to check.
        - v (Any): The value to compare against.
        - o (str, optional): The comparison operator. Default is "==".

        Returns:
        JsonList: A new list containing items that meet the specified condition.
        """
        d = {}
        if type(v) is str:
            criteria = "def criteria(i): return i.%s %s '%s'" % (m, o, v)
        elif isinstance(v, JsonObject):
            criteria = "def criteria(i): return str(i.%s) %s '%s'" % (m, o, str(v))
        else:
            criteria = "def criteria(i): return i.%s %s %s" % (m, o, str(v))

        exec(criteria, d)
        return self.filter(d["criteria"])

    def split_by(self, m) -> dict:
        """
        Split the list into multiple lists based on the value of a specified attribute or a calculated field.

        Parameters:
        - m (str): The attribute name to split by.
        or
        - m (callable): The function to compute the calculated field, must receive an item from the list.
        Returns:
        dict: A dictionary where keys are unique attribute or calculated field values and values are lists of items.
        """
        if type(m) is str and issubclass(self.list_type, JsonObject):
            d = {}
            exec("def criteria(i): return i.%s" % m, d)
            m = d["criteria"]
        r = {}
        for i in self:
            l = m(i)
            if l not in r:
                r[l] = self.__class__()
                self.list_type = self.list_type
            r[l].append(i)
        return r

    def filter(self, key):
        """
        Filter the list based on a given function.

        Parameters:
        - key (Callable): A function that takes an item as an argument and returns a boolean.

        Returns:
        JsonList: A new list containing items for which the function returned True.
        """
        nl = self.__class__()
        for i in self:
            if key(i):
                nl.append(i)
        return nl

    def find_first(self, key, not_found_behavior=NotFoundBehavior.RaiseError):
        """
        Find the first item in the list that meets a specified condition.

        Parameters:
        - key (Any): A value or function to search for.
        - not_found_behavior (NotFoundBehavior): Determines the behavior when the item is not found.

        Returns:
        Any: The first item that meets the condition or a behavior based on the NotFoundBehavior.
        """
        i = self.find_first_index(key, not_found_behavior=not_found_behavior)
        return None if i is None else JsonList.__getitem__(self, i)

    def find_first_index(self, key, not_found_behavior=NotFoundBehavior.RaiseError):
        """
        Find the index of the first item in the list that meets a specified condition.

        Parameters:
        - key (Any): A value or function to search for.
        - not_found_behavior (NotFoundBehavior): Determines the behavior when the item is not found.

        Returns:
        int or None: The index of the first item that meets the condition or None based on the NotFoundBehavior.
        """
        if callable(key):
            for ix, i in enumerate(self):
                if key(i):
                    return ix
        else:
            for ix, i in enumerate(self):
                if key == i:
                    return ix

        if not_found_behavior == NotFoundBehavior.RaiseError:
            raise RuntimeError("Value not found")
        else:
            return None

    def find_ordered(self,
                     value,
                     key=None,
                     search_type: SearchType = SearchType.Exact,
                     order: SortOrder = SortOrder.Ascending,
                     not_found_behavior: NotFoundBehavior = NotFoundBehavior.RaiseError):
        """
        Search for an item in an ordered list.

        Parameters:
        - value (Any): The value to search for.
        - key (Callable, optional): A function that takes an item as argument and returns a value for comparison.
        - search_type (SearchType): Type of search (e.g., exact match).
        - order (SortOrder): The ordering of the list (ascending or descending).
        - not_found_behavior (NotFoundBehavior): Determines the behavior when the item is not found.

        Returns:
        Any: The found item or a behavior based on the NotFoundBehavior.
        """
        i = bin_search(self, value, key=key, search_type=search_type, order=order, not_found_behavior=not_found_behavior)
        return None if i is None else JsonList.__getitem__(self, i)

    def find_ordered_index(self,
                           value,
                           key=None,
                           search_type: SearchType = SearchType.Exact,
                           order: SortOrder = SortOrder.Ascending,
                           not_found_behavior: NotFoundBehavior = NotFoundBehavior.RaiseError):
        """
        Search for the index of an item in an ordered list.

        Parameters:
        - value (Any): The value to search for.
        - key (Callable, optional): A function that takes an item as argument and returns a value for comparison.
        - search_type (SearchType): Type of search (e.g., exact match).
        - order (SortOrder): The ordering of the list (ascending or descending).
        - not_found_behavior (NotFoundBehavior): Determines the behavior when the item is not found.

        Returns:
        int or None: The index of the found item or None based on the NotFoundBehavior.
        """
        return bin_search(self,
                          value,
                          key=key,
                          search_type=search_type,
                          order=order,
                          not_found_behavior=not_found_behavior)

    def process(self, l):
        """
        Processes each element in the list using a provided function.

        Args:
            l (callable): A function to be applied to each item in the list.

        Returns:
            JsonList: A new JsonList with items after being processed by the function `l`.
        """
        nl = JsonList()
        for i in self:
            nl.append(l(i))
        return nl

    def copy(self):
        """
        Creates a deep copy of the current JsonList.

        Returns:
            JsonList: A new JsonList that is a deep copy of the current list.
        """
        return self.__class__.parse(str(self))

    def get_values(self):
        """
        Retrieves the values from the list. If an item is an instance of JsonObject or JsonList,
        recursively gets the values from the object or list.

        Returns:
            JsonList: A new JsonList containing the values from the original list.
        """
        values = JsonList(list_type=JsonList)
        for i in self:
            if isinstance(i, (JsonObject, JsonList)):
                values.append(i.get_values())
            else:
                values.append(i)
        return values

    def set_values(self, values: list):
        """
        Sets the values in the current JsonList based on the provided values list.

        Args:
            values (list): The list of values to be set in the current JsonList.
        """
        for i in values:
            if issubclass(self.list_type, (JsonObject, JsonList)):
                ni = self.list_type()
                ni.set_values(i)
                self.append(ni)
            else:
                self.append(i)


    @classorinstancemethod
    def parse(cls_or_self, json_string="", json_list=None):
        """
        Parses a JSON string or list into a JsonList. The type of items in the resulting JsonList
        is determined based on the list_type attribute of the JsonList.

        Args:
            json_string (str, optional): A JSON-formatted string to be parsed into a JsonList.
            json_list (list, optional): A list to be converted into a JsonList.

        Returns:
            JsonList: A new or updated JsonList populated with items from the provided JSON string or list.

        Raises:
            TypeError: If provided json_string is not a string or json_list is not a list.
        """
        if json_string:
            check_type(json_string, str, "wrong type for json_string")
            json_list = json.loads(json_string)
        check_type(json_list, list, "wrong type for json_list")
        if type(cls_or_self) is type:
            new_list = cls_or_self()
        else:
            new_list = cls_or_self
            new_list.clear()
        it = new_list.list_type
        ic = it().__class__
        for i in json_list:
            if i is None:
                new_list.append(i)
            elif issubclass(ic, JsonObject):
                new_list.append(it.parse(json_dictionary=i))
            elif issubclass(ic, JsonList):
                new_list.append(it.parse(json_list=i))
            elif issubclass(ic, datetime):
                new_list.append(datetime.strptime(i, JsonDate.date_format))
            elif issubclass(ic, JsonString):
                new_list.append(JsonString(i))
            else:
                new_list.append(i)
        return new_list

    def save(self, file_path: str):
        """
        Save the list to a file in JSON format.

        Parameters:
        - file_path (str): The path to the file where the list will be saved.
        """
        with open(file_path, 'w') as f:
            f.write(str(self))

    def load_from_file(self, file_path: str):
        """
        Load the list from a file containing JSON data.

        Parameters:
        - file_path (str): The path to the file to load data from.
        """
        if not path.exists(file_path):
            return None
        json_content = ""
        with open(file_path) as f:
            json_content = f.read()
        return self.parse(json_content)

    def load_from_url(self, uri: str):
        """
        Load JSON data into the list from a URL.

        Parameters:
        - uri (str): The URL to fetch the data from.
        """
        req = requests.get(uri)
        if req.status_code == 200:
            return self.parse(req.text)
        return None

    def to_numpy_array(self):
        """
        Convert the list to a numpy array.

        Returns:
        numpy.array: The numpy array representation of the list.

        Notes:
        Only supports conversion if the list contains simple types (int, float, bool) or JsonObject instances.
        """
        from numpy import array
        if self.list_type is int or self.list_type is float or self.list_type is bool:
            return array(self)
        return array([i.get_values() for i in self if isinstance(i, JsonObject)])

    def from_numpy_array(self, a):
        """
        Populate the list from a numpy array.

        Parameters:
        - a (numpy.array): The array to load data from.

        Notes:
        Only supports loading from an array if the list's type is a JsonObject or a simple type.
        """
        self.clear()
        columns = self.list_type().get_columns()
        for row in a:
            ni = self.list_type()
            for i, c in enumerate(columns):
                ni[c] = row[i]
            self.append(ni)

    def to_dataframe(self, recursive: bool = False):
        """
        Convert the list to a pandas DataFrame.

        Parameters:
        - recursive (bool): Flag to indicate if nested objects should be recursively converted to DataFrame columns.

        Returns:
        pandas.DataFrame: The DataFrame representation of the list.
        """
        from pandas import DataFrame
        if self.list_type is JsonObject or self.list_type is None:
            if len(self) == 0:
                return DataFrame()
            if isinstance(self[0], JsonObject):
                columns = self[0].get_columns()
            else:
                raise RuntimeError("Item type cannot be loaded to dataframe")
        else:
            if issubclass(self.list_type, JsonObject):
                columns = self.list_type().get_columns()
            else:
                return DataFrame(self)

        if recursive:
            return DataFrame([i.__dataframe_values__() for i in self], columns=columns)
        else:
            return DataFrame([i.get_values() for i in self], columns=columns)

    def from_dataframe(self, df):
        """
        Populate the list from a pandas DataFrame.

        Parameters:
        - df (pandas.DataFrame): The DataFrame to load data from.
        """
        self.clear()
        columns = df.columns
        for i, row in df.iterrows():
            ni = self.list_type()
            for c in columns:
                ni[c] = row[c]
            self.append(ni)

    def into(self, cls: type):
        """
        Convert the current list into another type derived from JsonList.

        Parameters:
        - cls (type): The target JsonList derived type to convert into.

        Returns:
        JsonList: A new JsonList of the specified type with the current list's data.

        Raises:
        RuntimeError: If the provided type is not derived from JsonList.
        """
        if not issubclass(cls, JsonList):
            raise RuntimeError("type must derive from JsonList")
        nv = cls.parse(str(self))
        return nv


class JsonString(str):
    """
    A subclass of the built-in `str` class to represent JSON-formatted strings.

    This class tries to convert a given string into a JSON object upon instantiation.
    If the conversion is successful, the internal representation is a stringified version
    of the JSON object, and the original JSON object is saved as the 'value' attribute.
    If the conversion fails, the original string is preserved, and the 'value' attribute is set to None.

    Attributes:
        value (JsonObject): Parsed JSON object if successful, else None.

    Example:
        js = JsonString('{"my_attribute": "my_attribute_value"}')
        print(js)           # Outputs: {"my_attribute": "my_attribute_value"}
        print(js.value.my_attribute)     # Outputs: "my_attribute_value"


        invalid_js = JsonString('invalid_json_string')
        print(invalid_js)   # Outputs: "invalid_json_string"
        print(invalid_js.value)  # Outputs: None
    """
    def __new__(cls, string=""):
        """
        Create a new instance of the JsonString.

        Args:
            string (str, optional): The string representation of a JSON object. Defaults to an empty string.

        Returns:
            JsonString: An instance of the JsonString class.
        """
        if string:
            try:
                o = JsonObject.load(string)
                instance = super().__new__(cls, str(o))
                setattr(instance, "value", o)
            except:
                instance = super().__new__(cls, string)
                setattr(instance, "value", None)
        else:
            instance = super().__new__(cls)
        return instance
