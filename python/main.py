import argparse 
from tools.experiment_options import ExperimentArgParse
from tools.vrcoordinateconverter import VRCoordinateConverter
import numpy as np
exp_args = ExperimentArgParse()
experiment_options = exp_args.parse_args()

print("\n=== Starting BotEvade Agent Tracking Server ===")
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import time
import math
import pygame
import torch
from cellworld_game.util import Point
import json_cpp
import cellworld as cw
import cellworld_game as game
import tcp_messages as tcp
from datetime import datetime
import threading as th 
import tests.pavtest as pavlok
import asyncio
from tools import mylog
from tools.controller_mouse import get_mouse_position
from tools.peaking import PeakingSystem
from botevadevr import BotEvadeVR
from cellworld_game.tasks import BotEvade

experiment_options.time_step = 1 / experiment_options.sampling_rate
mtx = th.RLock()
print(f'Rendering: {experiment_options.render} | time step: {experiment_options.time_step:0.4f} ({experiment_options.sampling_rate} Hz)')
print(f"*** starting server on {experiment_options.ip}:{experiment_options.port} ***\n")

## load world and model 
world = 'clump02_05'
loader = game.CellWorldLoader(world_name=world) # original: "21_05"
global model

model = BotEvadeVR(world_name=world, 
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
    # print('TODO: BROADCAST WITH MESSAGE THAT SAYS `CAPTURED` | `REACHED_GOAL`')
    mtx.release()
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_capture", body=""))
    if experiment_options.shock:
        try: 
            print('[on_capture] Sending vibe stimulus')
            pav = pavlok.PyStimTester(stims='zap', 
                         intensities=[90])
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
experiment_options.name = f'{experiment_options.name}_{world}'
print(f'Experiment name: {experiment_options.name}')

_, _, after_stop, save_step = mylog.save_log_output(model = model, experiment_name=experiment_options.name, 
    log_folder='logs/', save_checkpoint=True)

def myprint(agentstate,los):
    print(agentstate)
    print(los)

model.prey.dynamics.turn_speed = 15 # c.u./s 
model.prey.dynamics.forward_speed = 15
model.add_event_handler("puff", on_capture)
model.add_event_handler("after_stop", on_episode_stopped)
# model.add_event_handler("agents_states_update", myprint) ## new !! 

global server
server = tcp.MessageServer(ip=experiment_options.ip)

def move_mouse(message=None):
    step: cw.Step = message.get_body(body_type=cw.Step) # hold location + rotation
    if vr_coord_converter and vr_coord_converter.active:
        converted_coords = vr_coord_converter.vr_to_canon(step.location.x, step.location.y) # e-7 s
        # converted_rotation = vr_coord_converter.vr_to_canon_rotation(step.location.x, step.location.y)
        mtx.acquire() # .5- 4 sec | BAD -- FIXED -alexM 4/25/2025
        model.prey.state.location = (converted_coords[0], converted_coords[1]) # e-6 sec
        model.prey.state.direction = (180 - step.rotation) # validate
        model.time = step.time_stamp
        mtx.release() # e-6 sec 
        print(step.data)
    else:
        print(f'[move_mouse] VR coordinate converter NULL')
    save_step(step.time_stamp, step.frame, step.data)

def get_predator_step(message:tcp.Message=None):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message):
    mtx.acquire()
    model.reset()
    mtx.release()
    print(f"[New Episode Started]")
    # if experiment_options.shock:
    #     try: 
    #         print('[reset] Sending vibe stimulus')
    #         pav = pavlok.PyStimTester(stims='shock', 
    #                      intensities=[50])
    #         asyncio.run(pav.start(show_output=False))
    #     except Exception as e:
    #         print(f"[reset] Error: {e}")

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
    if message is None: return
    print(f"[UNROUTED] Header: '{message.header}'")
    print(f"[UNROUTED] Registered routes: {list(server.router.routes.keys())}")
    print(f"[UNROUTED] Body: {message.body}")

def _pause_(message:tcp.Message=None)->None:
    print(f"Pausing: {message}")
    mtx.acquire()
    model.pause()
    mtx.release()

def set_vr_origin(message=None):
    print("Set VR origin")
    try:
        origin_lst = message.body.split(',')
        if len(origin_lst) != 4:
            raise ValueError("[set_vr_origin] Expected 4 comma-separated values")
        # x,y location of entry and exit doors in UE-VR units 
        originEntry = [float(origin_lst[0]), float(origin_lst[1])] 
        originExit  = [float(origin_lst[2]), float(origin_lst[3])]
        vr_coord_converter.set_origin(originA=originEntry, originB=originExit)
    except Exception as e:
        print(f"[set_vr_origin] Exception: {e}")

def get_cell_locations(message=None):
    print("[get_cell_locations] OLD VERSION") 
    try:
        mtx.acquire()
        locations = model.loader.world.implementation.cell_locations
        for loc in locations:
            if vr_coord_converter and vr_coord_converter.active:
                loc.x, loc.y = vr_coord_converter.canonical_to_vr(loc.x, loc.y)
            else:
                print(f'vr_coord_converter not valid!')
        mtx.release()
        # print(locations)
        return locations
    except Exception as e:
        print(f"[get_cell_locations] Exception: {e}")
        mtx.release()
        return []

def get_occlusions(message:tcp.Message=None)->json_cpp.JsonList:
    print("[get_occlusions]")
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
server.router.add_route("set_vr_origin", set_vr_origin)

server.router.unrouted_message = on_unrouted
server.on_new_connection       = on_connection
server.failed_messages = "failed"

running                   = True
server.allow_subscription = True

server.start(port=experiment_options.port)
print(f"Starting server (allow subscription: {server.allow_subscription})")
print(f'Subscribers: {server.subscriptions}')
peaking_system = PeakingSystem(occluded_cells=model.loader.world.cells.occluded_cells().copy())
model.peaking_system = peaking_system
model.peaking_system.max_peak_distance = 0.075

while running:
    if not model.running: 
        time.sleep(model.time_step)
        if experiment_options.pcmouse and experiment_options.render: 
            input('Press [Enter] to start experiment...')
            model.reset()
        continue
    
    predator_step = cw.Step(agent_name="predator")
    
    mtx.acquire()
    model.step()
    # model.peaking_system.update(model.prey.state.location)
    # print(f'Is player peaking? {peaking_system.is_peaking}')
    predator_step.location = cw.Location(*model.predator.state.location)
    predator_step.rotation = model.predator.state.direction
    # print(f'fs: {model.step_count / model.time}')
    if experiment_options.pcmouse and experiment_options.render: 
        sx,sy = model.view.screen.get_size()
        mx,my = get_mouse_position(sx,sy)
        model.prey.state.location = (mx,my)
    mtx.release()

    if vr_coord_converter and vr_coord_converter.active:
        predator_location_vr = vr_coord_converter.canonical_to_vr(predator_step.location.x, predator_step.location.y)
        predator_step.rotation = (predator_step.rotation + 180)
        predator_step.location = cw.Location(x=predator_location_vr[0],y=predator_location_vr[1])
        server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))
    else:
        pass
        # print('[MAIN] NOT SENDING PREDATOR LOCATION - VRCOORDINATECONVERTER() NOT ACTIVE')
    # print(f'Frame rate: {1/(time.time()-t0):0.2f}')

print("done!")