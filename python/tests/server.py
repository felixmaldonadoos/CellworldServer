print("\n=== Starting BotEvade Agent Tracking Server ===")
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import time
import cellworld_game as game
import tcp_messages as tcp
import threading as th 

mtx = th.RLock()

## load world and model 
loader = game.CellWorldLoader(world_name="21_05") # original: "21_05"
global model

model = game.BotEvade(world_name="21_05", 
                      render=True,
                      time_step=0.01, 
                      real_time=True, 
                      goal_threshold= 0.05 ,
                      puff_cool_down_time=3)


global server
server = tcp.MessageServer(ip='192.168.1.2')

def move_mouse(message:tcp.Message=None):
    print(f'received step: {message}')
    mtx.release()

def on_connection(connection=None)->None:
    print(f"connected: {connection}")

def on_unrouted(message:tcp.Message=None)->None:
    print(f'unrouted | {message}')
    # print(f"unrouted: {message.header} | body: {message.body}")

## routes ##
server.router.add_route("prey_step", move_mouse)
server.router.unrouted_message = on_unrouted
server.on_new_connection       = on_connection
server.failed_messages = "failed"

running = True
server.allow_subscription = True

print(f"Starting server (allow subscription: {server.allow_subscription})")
print(f'Subscribers: {server.subscriptions}')
server.start(port=4791)
while running:
    if not model.running: 
        time.sleep(model.time_step)
    mtx.acquire()
    model.step()
    mtx.release()
    