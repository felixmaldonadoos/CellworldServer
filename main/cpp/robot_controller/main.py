
import argparse 

PORT = 4791 
RENDER = False
FS = 60
IP = "192.168.1.199"

parser = argparse.ArgumentParser(description='A server that sometimes works, sometimes does not. oh, yea its for BotEvadeVR.')
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

print("\n=== Starting BotEvade Agent Tracking Server ===")
import os
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import json_cpp
import cellworld as cw
import mylog
import cellworld_game as game
import tcp_messages as tcp
from datetime import datetime
import threading as th 

mtx = th.RLock()

sample_count_prey = 0
sample_count_predator = 0

print(f'Rendering: {render} | time step: {time_step:0.4f} ({args.sampling_rate} Hz)')
print(f"*** starting server on {ip}:{port} ***\n")

## load world and model 
loader = game.CellWorldLoader(world_name="21_05") # original: "21_05"
global model

model = game.BotEvade(world_name="21_05", 
                      render=render,
                      time_step=time_step, 
                      real_time=True, 
                      goal_threshold= -1.0,
                      puff_cool_down_time=3)

def on_capture(mdl:game.BotEvade=None)->None:
    print(f'on_puff called on_capture!')
    print("SUPRESSED TO STRESS TEST")
    return
    mtx.acquire()
    model.stop()
    mtx.release()
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_capture", body=""))

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

if experiment_name is None:
    experiment_name = get_valid_input("Enter your name (only letters, no symbols or numbers): ")

experiment_name = generate_experiment_name(experiment_name)

_, _, after_stop, save_step = mylog.save_log_output(model = model, experiment_name=experiment_name, 
    log_folder='logs/', save_checkpoint=True)

model.prey.dynamics.turn_speed = 15 # c.u./s 
model.prey.dynamics.forward_speed = 15
model.add_event_handler("puff", on_capture) ## new !! 

global server
server = tcp.MessageServer(ip=ip)

def move_mouse(message:tcp.Message=None):
    # t0 = time.time()
    step: cw.Step = message.get_body(body_type=cw.Step)
    if step is None:
        print("step is none")
        return
    mtx.acquire()
    model.prey.state.location = (step.location.x, step.location.y)
    model.prey.state.direction = step.rotation*(-1) # reverse rotation idk but it works 
    model.time = step.time_stamp
    mtx.release()
    print(f'frame: {step.frame} location: ({step.location.x:0.2f},{step.location.y:0.2f}), rotation: {step.rotation:0.2f}')
    # print(time.time() - t0)
    save_step(step.time_stamp, step.frame) 

def get_predator_step(message:tcp.Message=None):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message):
    print(f"# reset called #")
    mtx.acquire()
    model.reset()
    mtx.release()
    print(f"[ New Episode Started ]")
    return 'success'

def _close_():
    print('_close_')
    mtx.acquire()
    model.close()
    mtx.release()

def _stop_(message:tcp.Message=None):
    print(f"[ Episode Finished ] ")
    mtx.acquire()
    model.stop()
    mtx.release()
    return 'success'

def on_connection(connection=None)->None:
    print(f"connected: {connection}")

def on_unrouted(message:tcp.Message=None)->None:
    if message in None:
        print('wrong message type') 
        return
    print(f"unrouted: {message.header}")

def _pause_(message:tcp.Message=None)->None:
    print(f"Pausing: {message}")
    mtx.acquire()
    model.pause()
    mtx.release()

def get_cell_locations(message:tcp.Message=None)->json_cpp.JsonList:
    print("[ get_cell_locations ]")
    mtx.acquire()
    locations = model.loader.world.implementation.cell_locations
    mtx.release()
    return locations

def get_occlusions(message:tcp.Message=None)->json_cpp.JsonList:
    print("[ get_occlusions ]")
    mtx.acquire()
    occlusions = model.loader.world.cells.occluded_cells().get('id')
    mtx.release()
    return occlusions

## routes ##
server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
server.router.add_route("stop", _stop_)
server.router.add_route("pause", _pause_)
server.router.add_route("close", _close_)
server.router.add_route("get_cell_locations", get_cell_locations)
server.router.add_route("get_occlusions", get_occlusions)
server.router.unrouted_message = on_unrouted

server.failed_messages = "failed"
server.on_new_connection = on_connection

running = True

server.allow_subscription = True
server.start(PORT)

print(f"Starting server (allow subscription: {server.allow_subscription})")
print(f'Routes: {server.router.routes.keys()}')
print(f'Subscribers: {server.subscriptions}')
while running:
    if not model.running: 
        time.sleep(model.time_step)
        continue
    mtx.acquire()
    model.step()
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    predator_step.rotation = model.predator.state.direction
    mtx.release()
    server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))

print("done!")