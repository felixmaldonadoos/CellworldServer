#Json-CPP 
A better json library.

## Installation
```
pip install json-cpp

```

## Create your first json object:
After installing the package, try the following python script:
```
from json_cpp import JsonObject
myobject = JsonObject(name="German Espinosa",age=41,weight=190.0)
print("name:", myobject.name, type(myobject.name).__name__)
print("age:", myobject.age, type(myobject.age).__name__)
print("weight:", myobject.weight, type(myobject.weight).__name__)
print(myobject)
```
output
```
name: German Espinosa str
age: 41 int
weight: 190.0 float
{"name":"German Espinosa","age":41,"weight":190.0}
```
### Loading json_data:
To quickly load json data into objects, use the load command:
```
from json_cpp import JsonObject
myobject = JsonObject.load("{\"name\":\"German Espinosa\",\"age\":41,\"weight\":190.0}")

print("name:", myobject.name, type(myobject.name).__name__)
print("age:", myobject.age, type(myobject.age).__name__)
print("weight:", myobject.weight, type(myobject.weight).__name__)

```
output
```
name: German Espinosa str
age: 41 int
weight: 190.0 float
```
### Formatting outputs:
You can easily format data, even in complex json hierarchical structures:
```
from json_cpp import JsonObject
myobject = JsonObject.load("{\"name\":\"German Espinosa\",\"age\":41,\"weight\":190.0,\"place_of_birth\":{\"country\":\"Argentina\",\"city\":\"Buenos Aires\"}}")

print(myobject.format("{name} was born in {place_of_birth.city}, {place_of_birth.country}"))

```
output
```
German Espinosa was born in Buenos Aires, Argentina
```
### Working with pre-structured data:
A powerful way to read and write json is to pre-define the structure of the data. This creates standarized data samples that are easire to be consumed by other tools.
To pre-define structure of a json object, you need to create your own custom class extending the JsonObject: 
```
from json_cpp import JsonObject

class MyJsonClass(JsonObject):
    def __init__(self, name="", age=0, weight=0.0):
        self.name = name
        self.age = age
        self.weight = weight


myobject = MyJsonClass('German Espinosa', 41, 190.0)

json_string = str(myobject)

print(json_string)

```
output
```
{"name":"German Espinosa","age":41,"weight":190.0}
```

### Loading values into an existing object:
You can also load values from a json string directly into an existing custom JsonObject:
```
from json_cpp import JsonObject

class MyJsonClass(JsonObject):
    def __init__(self, name="", age=0, weight=0.0):
        self.name = name
        self.age = age
        self.weight = weight

myobject = MyJsonClass('German Espinosa', 41, 190.0)

myobject.parse("{\"name\":\"Benjamin Franklin\",\"age\":84,\"weight\":195.5}")

json_string = str(myobject)

print(json_string)

```
output
```
{"name":"Benjamin Franklin","age":84,"weight":195.5}
```


### Object to json conversion:

All objects with type MyJsonClass will produce perfectly formed json when converted to string.
If you need to retrieve the json string representing the object:
```
from json_cpp import JsonObject

class MyJsonClass(JsonObject):
    def __init__(self, name="", age=0, weight=0.0):
        self.name = name
        self.age = age
        self.weight = weight


myobject = MyJsonClass('German Espinosa', 41, 190.0)

json_string = str(myobject)

print (json_string)

```
output
```
{"name":"German Espinosa","age":41,"weight":190.0}
```
### Json to object conversion:
You can create instances of your json objects from strings containing a correct json representation:
```
from json_cpp import JsonObject

class MyJsonClass(JsonObject):
    def __init__(self, name="", age=0, weight=0.0):
        self.name = name     # string
        self.age = age       # int
        self.weight = weight # float


json_string = "{\"name\":\"German Espinosa\",\"age\":41,\"weight\":190.0}"

myobject = MyJsonClass.parse(json_string)

print("name:", myobject.name, type(myobject.name).__name__)
print("age:", myobject.age, type(myobject.age).__name__)
print("weight:", myobject.weight, type(myobject.weight).__name__)

```
output
```
name: German Espinosa str
age: 41 int
weight: 190.0 float
```
note: all members are populated with the right values using the same data type declared in the default constructor of the class

### Nested json structures:
You can create complex structures with nested objects: 
```
from json_cpp import JsonObject

class Person(JsonObject):
    def __init__(self, name="", age=0):
        self.name = name
        self.age = age

class Transaction(JsonObject):
    def __init__(self, buyer=None, seller=None, product="", amount=0.0):
        self.buyer = buyer if buyer else Person()
        self.seller = seller if seller else Person()
        self.product = product
        self.amount = amount


mytransaction = Transaction(Person("German Espinosa", 41), Person("Benjamin Franklin", 84), "kite", 150.5)

print (mytransaction)

```
output
```
{"buyer":{"name":"German Espinosa","age":41},"seller":{"name":"Benjamin Franklin","age":84},"product":"kite","amount":150.5}
```

### Json lists:
You can load full lists with values from a json string to a JsonList:
```
from json_cpp import JsonObject, JsonList

fibonacci = JsonList(list_type=int)

json_string = "[1,1,2,3,5,8,13,21]"

fibonacci.parse(json_string)

```
You can also load a list of json objects:
```
from json_cpp import JsonObject, JsonList

class Person(JsonObject):
    def __init__(self, name="", surname=""):
        self.name = name
        self.surname = surname

person_list = JsonList(list_type=Person)

json_string = "[{\"name\":\"german\",\"surname\":\"espinosa\"},{\"name\":\"benjamin\",\"surname\":\"franklin\"}]"

person_list.parse(json_string)

```
Lists can also be used as members of other objects:
```
from json_cpp import JsonObject, JsonList

class Person(JsonObject):
    def __init__(self):
        self.name = ""
        self.surname = ""
        self.languages = JsonList(list_type=str)

person = Person.parse("{\"name\":\"German\",\"surname\":\"Espinosa\", \"languages\":[\"english\",\"spanish\",\"portuguese\"]}")

print(person)

```
output
```
{"name":"German","surname":"Espinosa","languages":["english","spanish","portuguese"]}
```