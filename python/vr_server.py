import tcp_messages as tcp
class VRServer(tcp.MessageServer):
    def __init__(self, ip: str="127.0.0.1", port:int = 4791, n:int=1):
        tcp.MessageServer.__init__(self, ip=ip)
        self.port = port
        self.model = None # maybe not, maybe
        print(self.ip)

        self.router.add_route("on_unrouted", self.on_unrouted)
        self.router.add_route("reset", self.reset)
        self.router.add_route("prey_step", self.move_mouse)
        self.router.add_route("stop", self.stop)
        self.router.add_route("pause", self.pause)
        self.router.add_route("close", self.close)
        self.router.add_route("get_cell_location", self.get_cell_location) # ret json_cpp.Jsonlist
        self.router.add_route("get_occlusions", self.get_occlusions)
        self.router.add_route("on_capture", self.on_capture)

        # callbacks/notifiers
        self.on_new_connection = self.on_new_connection_cb


    def on_unrouted(self, message: tcp.Message = None) -> None:
        if message in None:
            print('wrong message type')
            return
        print(f"unrouted: {message.header}")

    def reset(self, message:tcp.Message):
        if self.running:
            print("[Experiment] Resetting: Stopping current experiment")
            self.running = False
            self.model.stop()
        print("[Experiment] Starting a new experiment")
        self.running = True
        self.start()
        print( "Experiment started")

    def move_mouse(self, message:tcp.Message):
        print(f"receieved message: {message.header}")

    def stop(self, message:tcp.Message = None):
        print(f"stop: {message}")

    def pause(self, message:tcp.Message):
        print(f"receieved message: {message.header}")

    def close(self, message:tcp.Message):
        print(f"receieved message: {message.header}")

    def get_cell_location(self, message:tcp.Message):
        print(f"receieved message: {message}")


    def get_occlusions(self, message:tcp.Message):
        print(f"receieved message: {message}")

    # extra
    def show_routes(self): # check the routes
        return self.router.routes.keys()

    def on_capture(self, message:tcp.Message):
        print(f"receieved message: {message.header}")
        self.reset()

    def start(self):
        print('[Server] Starting ')
        self.running = True
        self.allow_subscription = True
        print(f'[Server] Running: {self.running} | Allow subs: {self.allow_subscription}')
        super().start(self.port)

    def on_new_connection_cb(self, connection):
        print(f'[Server] Connected {connection}')

    def prey_step(self, message:tcp.Message):
        print(f"receieved message: {message}")

s = VRServer()

print("server is active")
import time
s.start()
while True:
    try:
        pass  # Keeps the server running
    except KeyboardInterrupt:
        print("Server shutting down...")
        break  # Allows you to stop the server with Ctrl+C
    time.sleep(0.1)

