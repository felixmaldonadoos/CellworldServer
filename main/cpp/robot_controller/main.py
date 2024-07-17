import cellworld as cw
import cellworld_game as game
import tcp_messages as tcp
import argparse 
import time

# todo:
# 1. create route for cpp server to send predator data to python server
# 2. add thread to clear data and send to cpp server for storage. if data empty, wait for data to be filled 

sample_count_prey = 0
sample_count_predator = 0


PORT = 4790 
RENDER = True
FS = 90
IP = "172.23.126.101"

parser = argparse.ArgumentParser(description='BotEvadeVR: Agent Tracking Server.')
parser.add_argument('--ip', type=str, default=IP, help=f'Server host (default: {IP})')
parser.add_argument('--port','-p', type=int, default=PORT, help=f'Server port (default: {PORT})')
parser.add_argument('--sampling_rate','-fs', type=float, default=FS, help=f'Sampling rate (default: {FS})')
parser.add_argument('--render', '-r', action='store_true', help=f'Enable rendering (default: {RENDER})')

args = parser.parse_args()

ip = args.ip
port = args.port
time_step = 1/args.sampling_rate # time step 
render = args.render

data_buffer = {"prey":[], "predator":[]}

print(f'Rendering: {render} | time step: {time_step:0.4f} ({args.sampling_rate} Hz)')
print(f"=== starting server on {ip}:{port} ===\n")

loader = game.CellWorldLoader(world_name="21_05")
model = game.BotEvade(world_name="21_05",
                      render=render,
                      time_step=time_step) 

game.save_log_output(model = model, experiment_name = "ExperimentNameTemp", 
    log_folder='logs/', save_checkpoint=True)

model.prey.dynamics.turn_speed = 10
model.prey.dynamics.forward_speed = 10
model.reset()

server = tcp.MessageServer(ip=ip) # run on localhost

def move_mouse(message):
    global server
    print(server.router.routes)
    print(message)
    step: cw.Step = message.get_body(body_type=cw.Step)
    pass
    # model.prey.state.location = (step.location.x, step.location.y)
    # global sample_count_prey
    # sample_count_prey += 1 

def get_predator_step(message):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

#todo: add function that calls reset but accepts string with experiment_name from UE
# steps: 1) add route to this server (e.g "reset_experiment") 
# 2) add function that accepts message with experiment_name 
# 3) change experiment_name for game.save_log_output to be a global variable
# 4) call original reset with experiment_name

def reset(message):
    global t0
    t0 = time.time()
    sample_count_prey = 0 
    sample_count_predator = 0
    print("New Episode Started")
    model.reset()

running = True

def _stop_(message):
    print("stopping")
    global running
    running = False

def on_connection(connection=None)->None:
    print(f"connected: {connection}")

def on_unrouted(message:tcp.Message=None)->None:
    global server
    print(server.router.routing_count.keys())
    print(f"unrouted: {message}")

def _pause_(message:tcp.Message=None)->None:
    model.pause()
    return "success"

server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
# server.router.add_route("get_predator_step", move_mouse)
server.router.add_route("stop", _stop_)
server.router.add_route("pause", _pause_)

# server.router.add_route("stop")
server.router.unrouted_message = on_unrouted
server.failed_messages = "failed"

server.allow_subscription = True
server.start(PORT)
server.on_new_connection = on_connection

# model.view.add_event_handler("mouse_move", move_mouse)
print(f"server started {server.running} (allow subscription: {server.allow_subscription})")
print(f"connections: {len(server.connections)}")

t0 = time.time()
while running:
    if (sample_count_prey != 0) and (sample_count_prey % 500 == 0):
        pass
        # t = time.time() - t0
        # print(f"fs: prey (in): {sample_count_prey/t} | predator (out): {sample_count_predator/t}")
        # print(f"connections: {len(server.connections)} | subscriptions: {len(server.subscriptions)}")

    model.step()
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    predator_step.rotation = model.predator.state.direction
    server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))
    sample_count_predator += 1
