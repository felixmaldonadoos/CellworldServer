import sys

import tcp_messages as tcp
import threading as th
import cellworld_game as game
import cellworld as cw
mtx = th.RLock()

class VRServer(tcp.MessageServer):
    def __init__(self, ip: str= "127.0.0.1", port: int = 4791, n: int = 1, model: game.Model = game.BotEvade):
        tcp.MessageServer.__init__(self, ip=ip)
        self.port = port
        self.model = model
        print(self.ip)

        self.router.add_route("on_unrouted", self.on_unrouted)
        self.router.add_route("reset_model", self.reset)
        self.router.add_route("prey_step", self.move_mouse)
        self.router.add_route("stop_model", self.stop_model) # stop model
        self.router.add_route("pause_model", self.pause)
        self.router.add_route("close", self.close)
        self.router.add_route("get_cell_location", self.get_cell_location) # ret json_cpp.Jsonlist
        self.router.add_route("get_occlusions", self.get_occlusions)

        # callbacks/notifiers
        self.on_new_connection = self.on_new_connection_cb


    def on_unrouted(self, message: tcp.Message = None) -> None:
        if message in None:
            print('wrong message type')
            return
        print(f"unrouted: {message.header}")

    def reset(self, message:tcp.Message=None):
        print("[Experiment] Starting a new experiment")
        mtx.acquire()
        self.model.reset()
        mtx.release()
        return 'success'

    def move_mouse(self, message: tcp.Message):
        print(f"receieved message: {message.header}")

    def stop_model(self, message: tcp.Message):
        print(f"[stop]")
        mtx.acquire()
        self.model.stop()
        mtx.release()
        return 'success'

    def pause(self, message:tcp.Message):
        print(f"receieved message: {message.header}")
        mtx.acquire()
        self.model.stop()
        mtx.release()

    def close(self, message:tcp.Message):
        print(f"receieved message: {message.header}")
        mtx.acquire()
        self.model.stop()
        mtx.release()

    def get_cell_location(self, message:tcp.Message):
        print(f"receieved message: {message}")
        mtx.acquire()
        locations = self.model.loader.world.implementation.cell_locations
        mtx.release()
        return locations

    def get_occlusions(self, message:tcp.Message):
        print(f"received message: {message.header}")
        mtx.acquire()
        occlusions = self.model.loader.world.cells.occluded_cells().get('id')
        mtx.release()
        return occlusions

    # extra
    def show_routes(self): # check the routes
        return self.router.routes.keys()

    def on_capture(self, mdl:game.Model)->None:
        print(f"[on_capture]")
        mtx.acquire()
        self.model.stop()
        mtx.release()
        self.broadcast_subscribed(message=tcp.Message("on_capture", body=""))

    def start(self):
        print('[Server] Starting ')
        super().start(self.port)
        self.allow_subscription = True
        print(f'[Server] Allow subs: {self.allow_subscription}')

    def on_new_connection_cb(self, connection):
        print(f'[Server] Connected {connection}')

    def prey_step(self, message:tcp.Message):
        print(f"receieved message: {message}")


s = VRServer()
fs = 60
s.model = game.BotEvade(world_name="21_05",
                        time_step=1/fs, # 60 hz
                        real_time=True,
                        render=True)

s.model.add_event_handler("puff", s.on_capture)

print("server is active")
import time
import os
s.start()
while True:
    if not s.model.running:
        time.sleep(s.model.time_step)
        continue
    try:
        mtx.acquire()
        s.model.step()
        mtx.release()
    except Exception as e:
        print(f"Server shutting down...error: {e}")
        continue  # Allows you to stop the server with Ctrl+C




print('I SHOULD NOT GET HERE UNLESS CTRL+C')