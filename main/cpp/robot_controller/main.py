import cellworld as cw
import cellworld_game as game
import tcp_messages as tcp
# import sys
# import time

# todo:
# 1. create route for cpp server to send predator data to python server
# 2. add thread to clear data and send to cpp server for storage. if data empty, wait for data to be filled 

# sample_count_prey = 0
# sample_count_predator = 0

data_buffer = {"prey":[], "predator":[]}

PORT = 4790 
IP = "127.0.0.1"
print(f"starting server on {IP}:{PORT}")

loader = game.CellWorldLoader(world_name="21_05")
model = game.BotEvade(world_name="21_05",
                      render=True,
                      time_step=.011) # 90 hz 

model.prey.dynamics.turn_speed = 0
model.prey.dynamics.forward_speed = 0
model.reset()

server = tcp.MessageServer() # run on localhost

def move_mouse(message):
    # print("received step")
    step: cw.Step = message.get_body(body_type=cw.Step)
    model.prey.state.location = (step.location.x, step.location.y)
    # global sample_count_prey
    # sample_count_prey += 1 

def get_predator_step(message):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message):
    print("resetting")
    model.reset()

running = True

def stop(message):
    print("stopping")
    global running
    running = False

def on_connection(connection=None)->None:
    print(f"connected: {connection}")
    
def on_unrouted(message:tcp.Message=None)->None:
    print(f"unrouted: {message.header}")

server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
server.router.add_route("get_predator_step", move_mouse)
server.router.add_route("stop", stop)
server.router.unrouted_message = on_unrouted
server.failed_messages = "failed"

server.allow_subscription = True
server.start(PORT)
server.on_new_connection = on_connection

# t0 = time.time()

# model.view.add_event_handler("mouse_move", move_mouse)
print(f"server started {server.running} (allow subscription: {server.allow_subscription})")
print(f"connections: {len(server.connections)}")
while running:
    # if (sample_count_prey+1) % 100 == 0:
    #     t = time.time() - t0
    #     print(f"fs: prey (in): {sample_count_prey/t} | predator (out): {sample_count_predator/t}")
    
    model.step()
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    predator_step.rotation = model.predator.state.direction
    server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))
    # sample_count_predator += 1