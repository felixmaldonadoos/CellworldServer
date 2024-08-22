print("=== Starting BotEvade Agent Tracking Server ===")
import cellworld as cw
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import cellworld_game as game
import tcp_messages as tcp
import argparse 
import time
from datetime import datetime

# todo:
# 1. create route for cpp server to send predator data to python server
# 2. add thread to clear data and send to cpp server for storage. if data empty, wait for data to be filled 

sample_count_prey = 0
sample_count_predator = 0

PORT = 4790 
RENDER = True
FS = 60
IP = "172.23.126.101"

parser = argparse.ArgumentParser(description='BotEvadeVR: Agent Tracking Server.')
parser.add_argument('--ip', type=str, default=IP, help=f'Server host (default: {IP})')
parser.add_argument('--name','-n', type=str, default=None, help=f'Experiment (subject) name/id (default: {None})')
parser.add_argument('--port','-p', type=int, default=PORT, help=f'Server port (default: {PORT})')
parser.add_argument('--sampling_rate','-fs', type=float, default=FS, help=f'Sampling rate (default: {FS})')
parser.add_argument('--render', '-r', action='store_true', help=f'Enable rendering (default: {RENDER})')

args = parser.parse_args()

ip = args.ip
port = args.port
time_step = 1/args.sampling_rate # time step 
render = args.render
experiment_name = args.name

print(f'Rendering: {render} | time step: {time_step:0.4f} ({args.sampling_rate} Hz)')
print(f"=== starting server on {ip}:{port} ===\n")

loader = game.CellWorldLoader(world_name="21_05") # original: "21_05"
model = game.BotEvade(world_name="21_05", # 21_05
                      render=render,
                      time_step=time_step) 

def generate_experiment_name(basename:str = "ExperimentNameBase"):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%m%d%Y_%H%M%S")
    return f"{basename}_{formatted_time}"

def get_valid_input(prompt):
    while True:
        user_input = input(prompt)
        if user_input.isalpha():
            return user_input
        else:
            print("Invalid input. Please enter only alphabetic characters.")

# Example usage
if experiment_name is None:
    experiment_name = get_valid_input("Enter your name (only letters, no symbols or numbers): ")

experiment_name = generate_experiment_name(experiment_name)

game.save_log_output(model = model, experiment_name=experiment_name, 
    log_folder='logs/', save_checkpoint=True)


model.prey.dynamics.turn_speed = 10
model.prey.dynamics.forward_speed = 10

#todo: check if this creates misalignment
# print("- Init reset")
# model.reset()

global server
server = tcp.MessageServer(ip=ip) # run on localhost

def move_mouse(message):
    step: cw.Step = message.get_body(body_type=cw.Step)
    if step is None:
        print("step is none")
        return
    
    model.prey.state.location = (step.location.x, step.location.y)
    global sample_count_prey
    global bCanUpdate
    sample_count_prey += 1
    bCanUpdate = True

def get_predator_step(message):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message):
    # if model.paused:
    #     model.pause()
    #     print(f"Paused: {model.paused}")

    global t0
    t0 = time.time()
    sample_count_prey = 0 
    sample_count_predator = 0
    model.reset()
    print("New Episode Started")
    return 'success'
    
running = True

def _close_():
    print('_close_')
    model.close()
    global running
    running = False

def _stop_(message):
    print("_stop_")
    model.stop()
    # global running
    # running = False

def on_connection(connection=None)->None:
    print(f"connected: {connection}")

def on_unrouted(message:tcp.Message=None)->None:
    print(f"unrouted: {message}")

def _pause_(message:tcp.Message=None)->None:
    print(f"Pausing: {message}")
    model.pause()

server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
server.router.add_route("stop", _stop_)
server.router.add_route("pause", _pause_)
server.router.add_route("close", _close_)

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
global bCanUpdate
bCanUpdate = False
while running:
    print('running')
    if bCanUpdate:
        print('calling: model.step()') 
        model.step()
        predator_step = cw.Step(agent_name="predator")
        predator_step.location = cw.Location(*model.predator.state.location)
        predator_step.rotation = model.predator.state.direction
        server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))
        sample_count_predator+=1
        bCanUpdate = False
    # if (sample_count_predator % 900 == 0):
    #     print(f'Subscribers: {len(server.subscriptions)} | Connections: {len(server.connections)} | Steps (prey/pred) {sample_count_prey}/{sample_count_predator}')
    # print(f"pred step: {predator_step.location}")
    # print(f"prey step: {model.prey.state.location} | {sample_count_prey}")
print("done!")