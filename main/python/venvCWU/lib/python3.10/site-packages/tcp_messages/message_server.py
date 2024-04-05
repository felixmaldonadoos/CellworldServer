import socket
from threading import Thread
from .connection import Connection
from .router import Router
from .message import Message
from .message_list import MessageList
from json_cpp import JsonObject



class MessageServer:

    def __init__(self, ip: str = "0.0.0.0"):
        self.failed_messages = None
        self.messages = MessageList()
        self.router = Router()
        self.router.unrouted_message = self.__unrouted__
        self.connections = []
        self.thread = None
        self.server = socket.socket()
        self.ip = ip
        self.running = False
        self.thread = Thread(target=self.__proc__)
        self.thread.daemon = True
        self.allow_subscription = False
        self.subscriptions = []
        self.on_new_connection = None

    def broadcast(self, message: Message):
        to_remove = []
        for connection in self.connections:
            try:
                connection.send(message)
            except:
                to_remove.append(connection)
        for connection in to_remove:
            self.connections.remove(connection)

    def broadcast_subscribed(self, message: Message):
        to_remove = []
        for connection in self.subscriptions:
            try:
                connection.send(message)
            except:
                to_remove.append(connection)
        for connection in to_remove:
            self.subscriptions.remove(connection)

    def __unrouted__(self, message: Message):
        self.messages.append(message)

    def __subscribe_connection_fail__(self, message: Message):
        return False

    def __unsubscribe_connection_fail__(self, message: Message):
        return False

    def __subscribe_connection__(self, message: Message):
        if message._source in self.subscriptions:
            return False
        self.subscriptions.append(message._source)
        return True

    def __unsubscribe_connection__(self, message: Message):
        if message._source not in self.subscriptions:
            return False
        self.subscriptions.remove(message._source)
        return True

    def start(self, port: int):
        self.server.bind((self.ip, port))
        try:
            self.server.listen()
        except socket.error as err:
            return False
        self.server.settimeout(0.001)
        if self.allow_subscription:
            self.router.add_route("!subscribe", self.__subscribe_connection__)
            self.router.add_route("!unsubscribe", self.__unsubscribe_connection__)
        else:
            self.router.add_route("!subscribe", self.__subscribe_connection_fail__)
            self.router.add_route("!unsubscribe", self.__unsubscribe_connection_fail__)
        self.thread.start()
        while not self.running:
            pass
        return True

    def stop(self):
        if self.running:
            self.running = False
            for c in self.connections:
                c.close()
            self.thread.join()
            self.server.close()

    def __proc__(self):
        self.running = True
        while self.running:
            try:
                client, address = self.server.accept()
                if client:
                    client_connection = Connection(client, self.failed_messages)
                    self.connections.append(client_connection)
                    self.router.attend(client_connection)
                    if self.on_new_connection:
                        self.on_new_connection(client_connection)

            except socket.timeout:
                pass  # no pending connecttions
            except Exception as e:
                print("Server: socked closed unexpectedly")
                self.running = False

    def join(self):
        if self.running:
            self.thread.join()

    def __del__(self):
        self.stop()

    def __bool__(self):
        if self.running:
            return True
        else:
            try:
                self.thread.join()
            finally:
                return False


class MessageServiceServer(MessageServer):

    def __init__(self, service_class: type, enable_sessions: bool = False, ip: str = "0.0.0.0"):
        MessageServer.__init__(self, ip=ip)
        self.service_class = service_class

        self.sessions_enabled = enable_sessions
        methods = [c for c in dir(service_class) if c[0] != "_"]
        if not self.sessions_enabled:
            self.service_object = service_class()
            for method in methods:
                candidate = getattr(self.service_object, method)
                if type(candidate) is type(self.join):
                    self.router.add_route(method, candidate, Router.Parse)
        else:
            self.on_new_connection = self.__new_session__
            for method in methods:
                self.router.add_route(method, MessageServiceServer.__handler__, Router.Complete)

    def __new_session__(self, client_connection):
        client_connection.service_object = self.service_class()
        client_connection.service_object.server = self

    @staticmethod
    def __handler__(message, client_connection):
        method = getattr(client_connection.service_object, message.header)
        if message.body:
            o = JsonObject.load(message.body)
            d = o.to_dict()
            return method(**d)
        else:
            return method()
