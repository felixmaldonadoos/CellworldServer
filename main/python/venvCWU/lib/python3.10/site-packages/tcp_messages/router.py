from threading import Thread, Lock
import types

import json_cpp

from .message import Message, Manifest, ManifestRoute, ManifestRouteParameter
from .message_event import MessageEvent
from .connection import Connection
from .util import check_type
import re
from json_cpp import JsonList, JsonObject


class Router:
    Empty = 0
    Message = 1
    Body = 2
    Parse = 3
    Complete = 4

    def __init__(self):
        self.routes = {}
        self.failed_message = None
        self.failed_route = None
        self.unrouted_message = None
        self.routing_count = 0
        self.pending_responses = dict()

    def add_message_event(self, request_id: str, event: MessageEvent):
        if request_id in self.pending_responses:
            return False
        self.pending_responses[request_id] = event
        return True

    def add_route(self, pattern: str, handler, body_type=None):
        if not callable(handler):
            raise RuntimeError ("incorrect type for handler")
        from inspect import signature
        s = signature(handler)
        if len(s.parameters) == 0:
            body_type = Router.Empty
        elif body_type is None:
            if len(s.parameters) == 1:
                body_type = Router.Message
            else:
                body_type = Router.Parse
        self.routes[pattern] = (handler, body_type)

    def get_manifest(self):
        from inspect import signature, _empty
        manifest = Manifest()
        for pattern in self.routes.keys():
            (handler, body_type) = self.routes[pattern]
            route_type = "Empty"
            manifest_route = ManifestRoute(pattern=pattern)
            if body_type == Router.Message:
                route_type = "Message"
            elif body_type == Router.Body:
                route_type = "Body"
            elif body_type == Router.Parse:
                route_type = "Parse"
                parameters = json_cpp.json_get_parameters(handler)
                for parameter in parameters:
                    manifest_route.parameters.append(ManifestRouteParameter(parameter.name,
                                                                            parameter.type))
            elif body_type == Router.Complete:
                route_type = "Complete"
            else:
                if body_type is type:
                    route_type = "Type(%s)" % body_type.__name__
            manifest_route.route_type = route_type
            manifest.append(manifest_route)
        return manifest

    def route(self, message: Message, connection: Connection):
        responses = []
        check_type(message, Message, "incorrect type for message")
        if message.id in self.pending_responses:
            self.pending_responses[message.id].trigger(message)
            return responses
        if message.header == "!manifest":
            responses.append(self.get_manifest())
        if message.header == "!ping":
            responses.append(True)
        for pattern in self.routes.keys():
            if re.search(pattern, message.header):
                (handler, body_type) = self.routes[pattern]
                try:
                    if body_type == Router.Empty:
                        responses.append(handler())
                    elif body_type == Router.Message:
                        responses.append(handler(message))
                    elif body_type == Router.Body:
                        responses.append(handler(message.body))
                    elif body_type == Router.Parse:
                        params = JsonObject.load(message.body).to_dict()
                        responses.append(handler(**params))
                    elif body_type == Router.Complete:
                        responses.append(handler(message, connection))
                    else:
                        responses.append(handler(message.get_body(body_type)))
                except:
                    if self.failed_route:
                        self.failed_route(message)
        if not responses:
            if self.unrouted_message:
                self.unrouted_message(message)
        self.routing_count += 1
        return responses

    def attend(self, connection: Connection):
        RouterProcess.attend(connection, self)


class RouterProcess:
    __handler = None
    __mutex = Lock()

    @staticmethod
    def attend(connection: Connection, router: Router):
        RouterProcess.__mutex.acquire()
        if RouterProcess.__handler is None:
            RouterProcess.__handler = RouterProcess()
        RouterProcess.__handler.connections.append((connection, router))
        RouterProcess.__mutex.release()

    def __init__(self):
        if RouterProcess.__handler:
            raise Exception("ConnectionHandler is a singleton, use ConnectionHandler.handle")
        self.connections = list()
        self.incoming_messages_threads = []
        self.running = False
        self.thread = Thread(target=self.__process__)
        self.thread.daemon = True
        self.thread.start()
        while not self.running:
            pass
        RouterProcess.__handler = self

    @staticmethod
    def __incoming_message__(connection: Connection, router: Router, message: Message):
        message._source = connection
        responses = router.route(message, connection)
        if responses:
            for response in responses:
                if isinstance(response, Message):
                    response.id = message.id
                    connection.send(response)
                elif isinstance(response, bool):
                    response_message = Message(message.header + "_response", "success" if response else "fail")
                    response_message.id = message.id
                    connection.send(response_message)
                else:
                    if response:
                        response_message = Message(message.header + "_response", str(response))
                        response_message.id = message.id
                        connection.send(response_message)

    def __process__(self):
        self.running = True
        while self.running:
            clean_up_required = []
            for index, (connection, router) in enumerate(self.connections):
                try:
                    if connection.state == Connection.State.Open:
                        message = connection.receive()
                        if message:
                            #RouterProcess.__incoming_message(connection, router, message)
                            Thread(target=RouterProcess.__incoming_message__, args=(connection, router, message)).start()
                    else:
                        clean_up_required.append(index)
                except:
                   clean_up_required.append(index)

            if clean_up_required:
                RouterProcess.__mutex.acquire()
                for failed_connection in clean_up_required:
                    try:
                        del self.connections[failed_connection]
                    except:
                        pass
                if len(self.connections) == 0:
                    RouterProcess.__handler = None
                    self.running = False
                RouterProcess.__mutex.release()

            to_remove = []
            while len(self.incoming_messages_threads) >= 10:
                for t in self.incoming_messages_threads:
                    if not t.is_alive():
                        to_remove.append(t)
                for t in to_remove:
                    self.incoming_messages_threads.remove(t)


