import argparse 
from tools.experiment_options import ExperimentArgParse

exp_args = ExperimentArgParse()
experiment_options = exp_args.parse_args()

# ip = experiment_options.ip
# port = experiment_options.port
# time_step = 1 / experiment_options.sampling_rate  # Time step
# render = experiment_options.render
# experiment_name = experiment_options.name
# use_shock = experiment_options.shock

print("\n=== Starting BotEvade Agent Tracking Server ===")
import os
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import torch
import json_cpp
import cellworld as cw
from tools import mylog
import cellworld_game as game
import tcp_messages as tcp
from datetime import datetime
import threading as th 
import pavtest as pavlok
import asyncio
from tools.controller_mouse import get_mouse_position
from tools.peaking import Peak

experiment_options.time_step = 1 / experiment_options.sampling_rate

mtx = th.RLock()
print(f'Rendering: {experiment_options.render} | time step: {experiment_options.time_step:0.4f} ({experiment_options.sampling_rate} Hz)')
print(f"*** starting server on {experiment_options.ip}:{experiment_options.port} ***\n")

## load world and model 
loader = game.CellWorldLoader(world_name="21_05") # original: "21_05"
global model

model = game.BotEvade(world_name="21_05", 
                      render=experiment_options.render,
                      time_step=experiment_options.time_step, 
                      real_time=True, 
                      goal_threshold= 0.05 ,
                      puff_cool_down_time=3,)

def on_capture(mdl:game.BotEvade=None)->None:
    print(f'[on capture] suppressed')
    mtx.acquire()
    model.stop()
    print('[on capture] Called model.stop()')
    print('TODO: BROADCAST WITH MESSAGE THAT SAYS `CAPTURED` | `REACHED_GOAL`')
    mtx.release()

    if experiment_options.shock:
        try: 
            print('[on_capture] Sending vibe stimulus')
            pav = pavlok.PyStimTester(stims='vibe', 
                         intensities=[100])
            asyncio.run(pav.start(show_output=False))
        except Exception as e:
            print(f"[on_capture] Error: {e}")
        if server: 
            server.broadcast_subscribed(message=tcp.Message("on_capture", body=""))

def on_episode_stopped(mdl:game.BotEvade=None)->None:
    print('[on_episode_stopped] Sending `on_capture` message (temporary)')
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_capture", body=""))

print(experiment_options.name)
_, _, after_stop, save_step = mylog.save_log_output(model = model, experiment_name=experiment_options.name, 
    log_folder='logs/', save_checkpoint=True)

model.prey.dynamics.turn_speed = 15 # c.u./s 
model.prey.dynamics.forward_speed = 15
model.add_event_handler("puff", on_capture) ## new !! 
model.add_event_handler("after_stop", on_episode_stopped) ## new !! 

global server
server = tcp.MessageServer(ip=experiment_options.ip)

def move_mouse(message:tcp.Message=None):
    step: cw.Step = message.get_body(body_type=cw.Step)
    if step is None:
        return
    mtx.acquire()
    model.prey.state.location = (step.location.x, step.location.y) 
    model.prey.state.direction = step.rotation*(-1) # reverse rotation idk but it works 
    model.time = step.time_stamp
    mtx.release()
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
    if experiment_options.shock:
        try: 
            print('[reset] Sending vibe stimulus')
            pav = pavlok.PyStimTester(stims='vibe', 
                         intensities=[100])
            asyncio.run(pav.start(show_output=False))
        except Exception as e:
            print(f"[reset] Error: {e}")

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

    if experiment_options.shock:
        pav = pavlok.PyStimTester(stims='vibe',
                        intensities=[100])
        asyncio.run(pav.start(show_output=False))

def on_unrouted(message:tcp.Message=None)->None:
    if message is None:
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
    print("[get_occlusions ]")
    mtx.acquire()
    occlusions = model.loader.world.cells.occluded_cells().get('id')
    mtx.release()
    return occlusions

def use_float16_list(p1:list=None, p2:list=None):
    # Convert to float16
    p1 = torch.tensor(p1, dtype=torch.float16, device='cuda')
    p2 = torch.tensor(p2, dtype=torch.float16, device='cuda')
    
    # Compute Euclidean distance
    return torch.sqrt(torch.sum((p2 - p1) ** 2))

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
server.start(experiment_options.port)
print(f"Starting server (allow subscription: {server.allow_subscription})")
print(f'Subscribers: {server.subscriptions}')
import sys

max_peak_time = 2
max_peak_distance = 0.01
detected = False
max_peak_cooldown = 3

occluded_cells = model.loader.world.cells.occluded_cells().copy()
for cell in occluded_cells: 
    cell.peaking = False
    cell.distance = 1
    cell.peak_time_start    = 0
    cell.peak_time_elapsed  = 0
    cell.max_peak_cooldown_time = 3
    cell.in_peak_cooldown   = False
    cell.peak_cooldown_time_elapsed = 0
    cell.peak_cooldown_time_start = 0

while running:
    if not model.running: 
        time.sleep(model.time_step)
        if not model.running:
            t = 2
            print(f'Starting episode in {t} seconds...')
            model.reset()
        continue
    mtx.acquire()
    if experiment_options.pcmouse and experiment_options.render: 
        sx,sy = model.view.screen.get_size()
        mx,my = get_mouse_position(sx,sy)
        mouse_step = tcp.Message(header="", body=cw.Step(location=cw.Location(mx,my),time_stamp=0, frame=0))
        move_mouse(mouse_step)

    model.step()
    # print(sys.getsizeof(model.loader.world.cells.occluded_cells())) # 392
    # print(sys.getsizeof(model.loader.world.cells.occluded_cells()[0])) #48
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)

    ### START NEW FUNCTION ###
    for cell in occluded_cells:
        # print(cell.peaking)
        cell.distance = use_float16_list([model.prey.state.location[0], model.prey.state.location[1]],
                                    [cell.location.x, cell.location.y])
        
        if cell.distance <= abs(max_peak_distance):
            if not cell.in_peak_cooldown:
                # print(f'in peak area, distance: {cell.distance} | peaking: {cell.peaking} | cell: {cell['id']}')
                
                if not cell.peaking: # start peak counters 
                    cell.peak_time_start = time.time()
                    cell.peaking = True
                    print(f'STARTED peaking! cell {cell.id} | distance: {cell.distance}')
                
                elif cell.peaking: # tick thru active peak
                    cell.peak_time_elapsed = time.time() - cell.peak_time_start
                    if cell.peak_time_elapsed >= max_peak_time: 
                        print(f'peak time elapsed! Starting cooldown. | {cell.id}')
                        cell.peaking = False
                        cell.in_peak_cooldown = True
                        cell.peak_cooldown_time_start = time.time()
                    else: # in active peak
                        print(f'In an active peak! {cell.id} | {cell.peak_time_elapsed:0.2f}')
                        continue
            else: # in peak cooldown 
                cell.peak_cooldown_time_elapsed = time.time() - cell.peak_cooldown_time_start
                # print(f'In peak cooldown: peak cooldown time elapsed {cell.peak_cooldown_time_elapsed:0.2f} (reset time: {cell.max_peak_cooldown_time:0.2f})')
                if cell.peak_cooldown_time_elapsed >= cell.max_peak_cooldown_time:
                    cell.in_peak_cooldown           = False
                    cell.peak_cooldown_time_elapsed = 0
                    cell.peak_cooldown_time_start   = 0
                    print(f'ending peak cooldown: {cell.in_peak_cooldown} | {cell.id}')
        else: 
            cell.peak_time_elapsed = 0
            cell.peaking = False
            if cell.in_peak_cooldown:
                print(f'left active peak during cooldown period! cooldown time elapsed: {cell.peak_cooldown_time_elapsed:0.2f} | {cell.id} ')
                cell.in_peak_cooldown = False
                cell.peak_cooldown_time_elapsed = 0
                cell.peak_cooldown_time_start   = 0

    ### END NEW FUNCTION ###

    predator_step.rotation = model.predator.state.direction
    mtx.release()
    predator_step.rotation = (predator_step.rotation +180) * -1
    server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))

print("done!")