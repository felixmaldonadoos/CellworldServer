from tools.experiment_options import ExperimentArgParse
from tools.vrcoordinateconverter import VRCoordinateConverter

exp_args = ExperimentArgParse()
experiment_options = exp_args.parse_args()



import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import time
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
from tools.logger import Logger

global srvlog
srvlog = Logger("Server")
srvlog.success(msg="=== cellworld BotEvadeVR Server ===")

experiment_options.time_step = 1 / experiment_options.sampling_rate
mtx = th.RLock()
srvlog.log(
    f"Rendering: {experiment_options.render} | "
    f"time step: {experiment_options.time_step:0.4f} "
    f"({experiment_options.sampling_rate} Hz)",
    subheader="Config"
)
# server startup
srvlog.success(
    f"starting server on {experiment_options.ip}:{experiment_options.port}",
    subheader="Startup"
)
# print(f'Rendering: {experiment_options.render} | time step: {experiment_options.time_step:0.4f} ({experiment_options.sampling_rate} Hz)')
# print(f"*** starting server on {experiment_options.ip}:{experiment_options.port} ***\n")

world = '21_05'
loader = game.CellWorldLoader(world_name=world) 
global model

model = BotEvadeVR(world_name=world, 
                      render=experiment_options.render,
                      time_step=experiment_options.time_step, 
                      real_time=True, 
                      goal_threshold= 0.05 ,
                      puff_cool_down_time=3)

global vr_coord_converter
vr_coord_converter = VRCoordinateConverter()
if vr_coord_converter and srvlog: 
    srvlog.log(msg='Initialized',subheader='VRCoordinateConverter')

def on_capture(mdl:game.Model=None)->None:
    srvlog.log(subheader='Experiment',msg='Captured')
    mtx.acquire()
    model.stop()
    mtx.release()
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_capture", body=""))
    if experiment_options.shock:
        try: 
            print('[on_capture] Sending vibe stimulus')
            
            stim = 'zap'
            intensity = 90
            srvlog.log(subheader='Experiment',msg='Sending pavlok stimulus',stim=stim, intensity=intensity)
            pav = pavlok.PyStimTester(stims='zap', 
                         intensities=[intensity])
            asyncio.run(pav.start(show_output=False))
        except Exception as e:
            print(f"[on_capture] Error: {e}")

def on_episode_stopped(mdl:game.Model=None)->None:
    srvlog.warning(subheader='Experiment',msg='Episode Finished')
    if server: 
        server.broadcast_subscribed(message=tcp.Message("on_episode_finished", body=""))

def generate_experiment_name(basename:str = "ExperimentNameBase"):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%m%d%Y_%H%M%S")
    return f"{basename}_{formatted_time}"

experiment_options.name = generate_experiment_name(experiment_options.name)
experiment_options.name = f'{experiment_options.name}_{world}'
srvlog.warning(subheader='Status',experiment_name=experiment_options.name)

_, _, after_stop, save_step = mylog.save_log_output(model = model, experiment_name=experiment_options.name, 
    log_folder='logs/', save_checkpoint=True)

def myprint(agentstate,los):
    print(agentstate)
    print(los)

model.add_event_handler("puff", on_capture)
model.add_event_handler("after_stop", on_episode_stopped)
# model.add_event_handler("agents_states_update", myprint) ## new !! 

global server
server = tcp.MessageServer(ip=experiment_options.ip)

def move_mouse(message=None):
    step: cw.Step = message.get_body(body_type=cw.Step)
    if vr_coord_converter and vr_coord_converter.active:
        converted_coords = vr_coord_converter.vr_to_canon(step.location.x, step.location.y)
        mtx.acquire() 
        model.prey.state.location = (converted_coords[0], converted_coords[1])
        model.prey.state.direction = (180 - step.rotation) 
        model.time = step.time_stamp
        mtx.release() 
    else:
        srvlog.warning(subheader='move_mouse',msg='VR coordinate converter NULL')
    save_step(step.time_stamp, step.frame, step.data)

def get_predator_step(message:tcp.Message=None):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message):
    mtx.acquire()
    model.reset()
    mtx.release()
    srvlog.success(subheader='Experiment',msg='Episode Started')
    return 'success'

def _close_():
    print('_close_')
    srvlog.warning(subheader='_close_',msg='Closing...')
    mtx.acquire()
    model.close()
    mtx.release()

def _stop_(message:tcp.Message=None):
    srvlog.log(subheader='_stop_',msg='Episode Finished')
    mtx.acquire()
    model.stop()
    mtx.release()
    return 'success'

def on_connection(connection=None)->None:
    srvlog.success(subheader='on_connection',connection=connection)
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
    sh = 'Coordinates'
    srvlog.log(subheader=sh)
    print("Set VR origin")
    try:
        origin_lst = message.body.split(',')
        if len(origin_lst) != 4:
            raise ValueError("[set_vr_origin] Expected 4 comma-separated values")
        originEntry = [float(origin_lst[0]), float(origin_lst[1])] 
        originExit  = [float(origin_lst[2]), float(origin_lst[3])]
        vr_coord_converter.set_origin(originA=originEntry, originB=originExit)
        srvlog.log(subheader=sh,active=vr_coord_converter.active)
    except Exception as e:
        print(f"[set_vr_origin] Exception: {e}")

def get_cell_locations(message=None):
    try:
        mtx.acquire()
        locations = model.loader.world.implementation.cell_locations
        for loc in locations:
            if vr_coord_converter and vr_coord_converter.active:
                loc.x, loc.y = vr_coord_converter.canonical_to_vr(loc.x, loc.y)
            else:
                srvlog.error(subheader='Coordinates',msg='VRCoordinateConverter is NULL')
        mtx.release()
        return locations
    except Exception as e:
        print(f"[get_cell_locations] Exception: {e}")
        mtx.release()
        return []

def get_occlusions(message:tcp.Message=None)->json_cpp.JsonList:
    srvlog.log(subheader='get_occlusions')
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
srvlog.log(msg='Starting Server.',allow_subscription=server.allow_subscription, subscriptions=server.subscriptions)
# print(f"Starting server (allow subscription: {server.allow_subscription})")
# print(f'Subscribers: {server.subscriptions}')
# peaking_system = PeakingSystem(occluded_cells=model.loader.world.cells.occluded_cells().copy())
# model.peaking_system = peaking_system
# model.peaking_system.max_peak_distance = 0.075

while running:
    if not model.running: 
        time.sleep(model.time_step)
        if experiment_options.pcmouse and experiment_options.render: 
            input('Press [Enter] to start experiment...')
            reset('')
        continue
    
    predator_step = cw.Step(agent_name="predator")
    
    mtx.acquire()
    model.step()
    # model.peaking_system.update(model.prey.state.location)
    # print(f'Is player peaking? {peaking_system.is_peaking}')
    predator_step.location = cw.Location(*model.predator.state.location)
    predator_step.rotation = model.predator.state.direction
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