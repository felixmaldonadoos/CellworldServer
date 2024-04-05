from .util import check_type
import json
from json_cpp import JsonObject, JsonList
from uuid import uuid1



class Message(JsonObject):

    def __init__(self, header="", body="", **kwargs):
        JsonObject.__init__(self)
        self.header = header
        if not body and kwargs:
            body = JsonObject.load(json_dictionary_or_list=kwargs)
        self.body = str(body)
        self.id = str(uuid1())
        self._source = None

    def get_body(self, body_type: type = None):
        if body_type:
            if body_type is JsonObject or body_type is JsonList:
                return JsonObject.load(self.body)
            elif issubclass(body_type, JsonObject) or issubclass(body_type, JsonList):
                return body_type.parse(self.body)
            elif body_type is str:
                return self.body
            elif body_type is bool:
                return self.body == "success" or self.body == "true" or self.body == "1"
            else:
                return body_type(json.loads(self.body))
        else:
            return self.body

    def set_body(self, v):
        self.body = str(v)

    def reply(self, message):
        check_type(message, Message, "wrong type for message")
        if self._source:
            self._source.send(message)
            return True
        else:
            return False


class MessagePart(JsonObject):

    def __init__(self, header: str = "", body: str = "", message_id: str = "", seq: int = 0, parts: int = 1):
        self.header = header
        self.body = body
        self.id = message_id
        self.seq = seq
        self.parts = parts

    def to_message(self) -> Message:
        message = Message(header=self.header, body=self.body)
        message.id = self.id
        return message


class MessageParts(JsonList):

    def __init__(self, message: Message = None):
        JsonList.__init__(self, list_type=MessagePart)
        if message:
            parts = (len(message.body) // 1024) + 1
            for i in range(parts):
                part = MessagePart(header=message.header, body=message.body[i*1024:(i+1)*1024], message_id=message.id, seq=i, parts=parts)
                self.append(part)

    def join(self) -> Message:
        if len(self) == 0:
            return Message()
        message = self[0].to_message()
        for i in range(1, len(self)):
            message.body += self[i].body
        return message

    def is_ready(self) -> bool:
        if len(self) == 0:
            return False
        return self[0].parts == len(self)


class ManifestRouteParameter(JsonObject):

    def __init__(self, parameter_name:str = "", parameter_type = ""):
        self.parameter_name = parameter_name
        self.parameter_type = parameter_type
        JsonObject.__init__(self)


class ManifestRoute(JsonObject):

    def __init__(self, pattern: str = "", route_type: str = "", parameters: JsonList = None):
        self.pattern = pattern
        self.route_type = route_type
        if parameters:
            self.parameters = parameters
        else:
            self.parameters = JsonList(list_type=ManifestRouteParameter)
        JsonObject.__init__(self)


class Manifest(JsonList):

    def __init__(self):
        JsonList.__init__(self, list_type=ManifestRoute)
