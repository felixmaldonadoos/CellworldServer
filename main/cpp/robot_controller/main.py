print("=== Starting BotEvade Agent Tracking Server ===")
import os
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import cellworld as cw
import mylog
import cellworld_game as game
import tcp_messages as tcp
import argparse 
from datetime import datetime
import threading as th 

mtx = th.Lock()

sample_count_prey = 0
sample_count_predator = 0

PORT = 4790 
RENDER = True
FS = 90
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
                      time_step=time_step, 
                      real_time=True, 
                      goal_threshold= -1.0,
                      max_line_of_sight_distance=1.0) 

def on_capture():
    print("[main.py] puffed!")
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_capture", body="lol"))

model.on_puff = on_capture

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

# c.u./s 
model.prey.dynamics.turn_speed = 15
model.prey.dynamics.forward_speed = 15

global server
server = tcp.MessageServer(ip=ip)

def move_mouse(message:tcp.Message=None):
    step: cw.Step = message.get_body(body_type=cw.Step)
    if step is None:
        print("step is none")
        return
    
    mtx.acquire()
    model.prey.state.location = (step.location.x, step.location.y)
    model.prey.state.direction = step.rotation
    model.time = step.time_stamp
    mtx.release()
    save_step(step.time_stamp, step.frame) # saving step 

def get_predator_step(message:tcp.Message=None):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message:tcp.Message=None):
    print("reset()")
    mtx.acquire()
    model.reset()
    mtx.release()
    print("New Episode Started")
    return 'success'
    
def _close_():
    print('_close_')
    mtx.acquire()
    model.close()
    mtx.release()

def _stop_(message:tcp.Message=None):
    print(f"_stop_: Total time elapsed: {message.body}")
    mtx.acquire()
    model.stop()
    mtx.release()

def on_connection(connection=None)->None:
    print(f"connected: {connection}")

def on_unrouted(message:tcp.Message=None)->None:
    print(f"unrouted: {message}")

def _pause_(message:tcp.Message=None)->None:
    print(f"Pausing: {message}")
    mtx.acquire()
    model.pause()
    mtx.release()

running = True

server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
server.router.add_route("stop", _stop_)
server.router.add_route("pause", _pause_)
server.router.add_route("close", _close_)

server.router.unrouted_message = on_unrouted
server.failed_messages = "failed"

server.allow_subscription = True
server.start(PORT)
server.on_new_connection = on_connection

print(f"server started {server.running} (allow subscription: {server.allow_subscription})")
print(f"connections: {len(server.connections)}")

# #todo: check if this creates misalignment
# print("- Init reset")
# model.reset()
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
    # print(len(server.subscriptions))
print("done!")