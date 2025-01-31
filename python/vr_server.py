import tcp_messages as tcp
class VRServer(tcp.MessageServer):
    def __init__(self, ip:str="127.0.0.1", n:int=1):
        tcp.MessageServer.__init__(self, ip=ip)
        self.model = None # maybe not, maybe
        print(self.ip)

    # extra
    def show_routes(self): # check the routes
        return self.router.routes.keys()

s = VRServer()