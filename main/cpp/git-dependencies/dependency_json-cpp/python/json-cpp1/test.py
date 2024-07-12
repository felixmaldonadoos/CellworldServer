from src import *

class Coordinates(JsonObject):
    def __init__(self, x: int=0, y: int=0):
        self.x = x
        self.y = y
@json_parse
@json_parameters
@json_force_parameter_type
def sum(c1: Coordinates, c2: Coordinates):
    s = Coordinates(c1.x + c2.x, c1.y + c2.y)
    return s


# print(sum(Coordinates(10,10), Coordinates(5,7)))
# print(sum(JsonObject(x=10,y=10), Coordinates(5,7)))

print(sum(str(JsonObject(c1=JsonObject(x=1, y=2), c2=JsonObject(x=1, y=2)))))
print(json_get_parameters(sum))

print(Coordinates.parse('{"x":1, "y":2, "z":3}',behavior=JsonParseBehavior.IgnoreNewAttributes))
print(Coordinates.parse('{"x":1, "y":2, "z":3}',behavior=JsonParseBehavior.IncorporateNewAttributes))

print(Coordinates.parse('{"x":1, "y":2, "z":[{"a":2},2,3]}',behavior=JsonParseBehavior.IncorporateNewAttributes))

#print(Coordinates.parse('{"x":1, "y":2, "z":[{"a":2},2,3]}',behavior=JsonParseBehavior.RaiseError))



cl = JsonList()
for i in range(10):
    cl.append(Coordinates(i,-i))


o = JsonObject(p1="Hello", cl=cl)


o._links = JsonObject(href="https://www.google.com", text="Google")

print(o.format("{p1}\n{cl:{x},{y}\n}"))


print(o)
o.force_include("_links")
print(o)

