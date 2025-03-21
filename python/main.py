import argparse 
from tools.experiment_options import ExperimentArgParse
from tools.vrcoordinateconverter import VRCoordinateConverter

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
import math
import pygame
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
from tools.peaking import PeakingSystem

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
                      puff_cool_down_time=3)

global vr_coord_converter
vr_coord_converter = VRCoordinateConverter()

def on_capture(mdl:game.BotEvade=None)->None:
    mtx.acquire()
    model.stop()
    print('TODO: BROADCAST WITH MESSAGE THAT SAYS `CAPTURED` | `REACHED_GOAL`')
    mtx.release()
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_capture", body=""))
    if experiment_options.shock:
        try: 
            print('[on_capture] Sending vibe stimulus')
            pav = pavlok.PyStimTester(stims='vibe', 
                         intensities=[100])
            asyncio.run(pav.start(show_output=False))
        except Exception as e:
            print(f"[on_capture] Error: {e}")

def on_episode_stopped(mdl:game.BotEvade=None)->None:
    print('[on_episode_stopped] Sending `on_capture` message (temporary)')
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_capture", body=""))

def generate_experiment_name(basename:str = "ExperimentNameBase"):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%m%d%Y_%H%M%S")
    return f"{basename}_{formatted_time}"

experiment_options.name = generate_experiment_name(experiment_options.name)
_, _, after_stop, save_step = mylog.save_log_output(model = model, experiment_name=experiment_options.name, 
    log_folder='logs/', save_checkpoint=True)

def myprint(agentstate,los):
    print(agentstate)
    print(los)

model.prey.dynamics.turn_speed = 15 # c.u./s 
model.prey.dynamics.forward_speed = 15
model.add_event_handler("puff", on_capture)
# model.add_event_handler("agents_states_update", myprint) ## new !! 
model.add_event_handler("after_stop", on_episode_stopped)

global server
server = tcp.MessageServer(ip=experiment_options.ip)
# used to convert legacy canonical data before sending out for canonical-VR conversion
def inverse_scale_legacy_y(scaled_y):
    return (scaled_y - 0.5 + math.sqrt(3) / 4) / (0.5 * math.sqrt(3))

def scale_legacy_y(y):
    return y * 0.5 * math.sqrt(3) + 0.5 - math.sqrt(3) / 4

def move_mouse(message:tcp.Message=None):
    mtx.acquire()
    if message is None: return
    step: cw.Step = message.get_body(body_type=cw.Step)
    if step is None: return

    if vr_coord_converter:
        converted_coords = vr_coord_converter.vr_to_canonical(step.location.x, step.location.y)
        model.prey.state.location = (converted_coords[0],converted_coords[1])
        print(model.prey.state.location)

    model.prey.state.direction = step.rotation*(-1) # reverse rotation idk but it works 
    model.time = step.time_stamp

    mtx.release()
    save_step(step.time_stamp, step.frame) 

def get_predator_step(message:tcp.Message=None):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message):
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
    print(f"unrouted: {message.header} | body: {message.body}")

def _pause_(message:tcp.Message=None)->None:
    print(f"Pausing: {message}")
    mtx.acquire()
    model.pause()
    mtx.release()

def set_vr_origin(message:tcp.Message=None)->None:
    # print(f'Setting VR origin (UE units): {message.header} | {message.body}')
    mtx.acquire()
    origin_lst = message.body.split(',')
    originA = [int(origin_lst[0]), int(origin_lst[1])]
    originB = [int(origin_lst[2]), int(origin_lst[3])]
    vr_coord_converter.set_origin(originA=originA, originB=originB)
    print(f'Set origin: Direction = {vr_coord_converter.origin_transform['direction']}')
    print(f'Set origin: Scale     = {vr_coord_converter.origin_transform['scale']}')
    print('here')
    mtx.release()

def get_cell_locations(message:tcp.Message=None)->json_cpp.JsonList:
    print("[get_cell_locations]")
    mtx.acquire()
    locations = model.loader.world.implementation.cell_locations
    for loc in locations: # correct for legacy camera system  
        loc.y = inverse_scale_legacy_y(loc.y)
    mtx.release()
    return locations

def get_occlusions(message:tcp.Message=None)->json_cpp.JsonList:
    print("[get_occlusions ]")
    mtx.acquire()
    occlusions = model.loader.world.cells.occluded_cells().get('id')
    mtx.release()
    return occlusions

def use_float16_list(p1:list=None, p2:list=None):
    p1 = torch.tensor(p1, dtype=torch.float16, device='cuda')
    p2 = torch.tensor(p2, dtype=torch.float16, device='cuda')
    return torch.sqrt(torch.sum((p2 - p1) ** 2))

## routes ##
server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
server.router.add_route("stop", _stop_)
server.router.add_route("pause", _pause_)
server.router.add_route("close", _close_)
server.router.add_route("get_cell_locations", get_cell_locations)
server.router.add_route("get_occlusions", get_occlusions)
# server.router.add_route("set_vr_origin", set_vr_origin)
server.router.unrouted_message = on_unrouted

server.failed_messages = "failed"

server.router.unrouted_message = on_unrouted
server.on_new_connection       = on_connection

running = True
server.allow_subscription = True

server.start(experiment_options.port)
print(f"Starting server (allow subscription: {server.allow_subscription})")
print(f'Subscribers: {server.subscriptions}')

coordinate_converter = game.CoordinateConverter(screen_size=model.view.screen.get_size())
peaking_system = PeakingSystem(occluded_cells=model.loader.world.cells.occluded_cells().copy())
model.peaking_system = peaking_system
model.peaking_system.max_peak_distance = 0.075

while running:
    if not model.running: 
        time.sleep(model.time_step)
        if experiment_options.pcmouse and experiment_options.render:
            print(f'Press any key to start new episode...')
            input()
            model.reset()
        continue
    t0 = time.time()
    mtx.acquire()
    if experiment_options.pcmouse and experiment_options.render: 
        x,y = pygame.mouse.get_pos()
        mouse_step = tcp.Message(header="", body=cw.Step(location=cw.Location(x,y),
                                                        time_stamp=0, 
                                                        frame=0))
        move_mouse(mouse_step)

    model.step()
    model.peaking_system.update(model.prey.state.location)
    print(f'Is player peaking? {peaking_system.is_peaking}')

    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    predator_step_vr = vr_coord_converter.canonical_to_vr(predator_step.location.x, predator_step.location.y)
    predator_step.rotation = model.predator.state.direction

    if vr_coord_converter:
        predator_step.rotation = (predator_step.rotation +180) * -1
        server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step_vr))

    mtx.release()
    
print("done!")