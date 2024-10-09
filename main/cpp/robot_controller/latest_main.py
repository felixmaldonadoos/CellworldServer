import cellworld as cw
import cellworld_game as game
import tcp_messages as tcp
import argparse 
# import time

# todo:
# 1. create route for cpp server to send predator data to python server
# 2. add thread to clear data and send to cpp server for storage. if data empty, wait for data to be filled 

class ArgParser:
    print("ArgParser")
    import argparse
    
    def __init__(self):
        print("ArgParser init")
        self.ip = ""
        self.parser = None
        self.PORT = 4790 
        self.RENDER = True
        self.FS = 90
        self.IP = "0.0.0.0"
    
    def start(self):
        self.parser = argparse.ArgumentParser(description='BotEvadeVR: Agent Tracking Server.')
        self.parser.add_argument('--ip', type=str, default=self.IP, help=f'Server host (default: {self.IP})')
        self.parser.add_argument('--port','-p', type=int, default=self.PORT, help=f'Server port (default: {self.PORT})')
        self.parser.add_argument('--sampling_rate','-fs', type=float, default=self.FS, help=f'Sampling rate (default: {self.FS})')
        self.parser.add_argument('--render', '-r', action='store_true', help=f'Enable rendering (default: {self.RENDER})')
        return self.parser.parse_args()
    
    def test(self):
        args = self.start()
        print(f"TEST: ArgParser", args)
        return args
        
class BotEvadeServer:
    def __init__(self, ip:str="0.0.0.0", port:int=4790, fs:int=90, render:bool=False) -> None:
        print("BotEvadeServer init")
        self.ip = ip
        self.port = port
        self.fs = fs
        self.time_step = 1/self.fs
        self.render = render
        
        self.server = tcp.MessageServer(ip=self.ip) # run on localhost
        self.server.router.add_route("reset", self.reset)
        self.server.router.add_route("prey_step", self.move_mouse)
        self.server.router.add_route("predator_step", self.myprint)
        self.server.router.add_route("stop", self._stop_)
        self.server.router.add_route("pause", self._pause_)
        self.server.router.unrouted_message = self.on_unrouted
        self.server.allow_subscription = True
        self.server.on_new_connection = self.on_new_connection
        self.server.failed_messages = "failed"
        
        self.game_model = None
        self.game_models = []
        self.running = True
        
        print(f"=== Preparing server on {self.ip}:{self.port} ===\n")
        print(f'Rendering: {render} | time step: {self.time_step:0.4f} ({self.fs} Hz)')
    
    def myprint(msg):
        print(msg)
        
    def _stop_(self, message):
        print('_stop_()')
        self.running = False
        
        if len(self.game_models) > 0:
            print("stopping")
            self.running = False
            self.game_models[0].stop()
            return None
        else:
            print("no game_model found")
        
    def _pause_(self, message):
        print("pausing")
        self.model.pause()
        # return "success"
        
    def start(self)->None:
        print("BotEvadeServer: start")
        self.server.allow_subscription = True
        
        if self.server.start(self.port) == False:
            self.running = False
            print("BotEvadeServer: failed to start")
        
        print(f"server started {self.server.running} (allow subscription: {self.server.allow_subscription})")
        print(f"connections: {len(self.server.connections)}")
    
    def on_unrouted(self, message:tcp.Message=None)->None:
        print(f"BotEvadeServer: unrouted: {message}")
        
    def on_new_connection(self, connection=None)->None:
        print(f"BotEvadeServer: connected: {connection}")

    def reset(self, message)->None:
        if (len(self.game_models) > 0):
            print("BotEvadeServer: reset")
            self.game_models[0].reset()
        
    # todo: accept jsonstring with info
    # todo: add this to structure or list 
    def start_new_experiment(self, experiment_name:str="start_new_experiment", world_name:str="21_05") -> None:
        game_model = BotEvadeGame(experiment_name=experiment_name, 
                                  render=self.render, 
                                  time_step=self.time_step, 
                                  world_name=world_name)
        
        new_experiment = game_model.new_game()
        self.game_models.append(new_experiment)
        print(f"BotEvadeServer: start_new_experiment | {experiment_name} | {world_name} | {len(self.game_models)}")
     
    def reset(self, message):
        if len(self.game_models) > 0: 
            print("BotEvadeServer: reset")
            self.game_models[0].reset()
            return
        print("BotEvadeServer: reset | no game_model found")
                
    def move_mouse(self, message):
        print("BotEvadeServer: inside move_mouse()")
        # print(f"BotEvadeServer: move_mouse | {message} | {self.sample_count_predator}")

        # todo: add a check to find the correct game_model when more than 1 is running
        if len(self.game_models) > 0:
            if self.game_models[0] is None:
                print('game_models[0] is None')
                return
            
            # self.game_models[0].move_mouse(message)
            print("after self.game_models[0].move_mouse(message) ")            
            print(f"subscriptions: {self.server.subscriptions}")
            # predator_step = self.game_models[0].get_predator_step()
            # self.server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))
            
            self.sample_count_predator += 1
        else:
            print(f"BotEvadeServer: move_mouse | no game_model found | {len(self.game_models)}")

    def move_predator(self, message=None):
        print("inside move_predator()")
        # if len(self.game_models) > 0:
        #     if self.game_models[0] is None:
        #         print('game_models[0] is None')
        #         return None
            
        #     print(f"BotEvadeServer: move_predator | {message}")
        #     # self.game_models[0]
        #     predator_step = cw.Step(agent_name="predator")
        #     predator_step.location = cw.Location(*self.game_models[0].model.predator.state.location)
        #     predator_step.rotation = self.game_models[0].model.predator.state.direction
        #     print("before broadcast_subscribed")
        #     self.server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))
        #     print("after broadcast_subscribed")
        # else:
        #     print(f"BotEvadeServer: move_predator | no game_model found | {len(self.game_models)}")

class BotEvadeGame:
    def __init__(self, experiment_name:str="ExperimentNameTemp",
                 render:bool=False, 
                 time_step:float=1/90, 
                 turn_speed:int = 10, 
                 forward_speed:int=10,
                 world_name:str='21_05') -> None:
        
        self.experiment_name = experiment_name
        self.time_step = time_step
        self.world_name = world_name
        
        self.render = render
        self.turn_speed = turn_speed
        self.forward_speed = forward_speed
        
        self.sample_count_prey = 0
        self.sample_count_predator = 0
        
        self.loader = None
        self.model = None
        
        self.running = True
        
        pass
    
    def get_predator_step(self):
        self.model.step()
        predator_step = cw.Step(agent_name="predator")
        predator_step.location = cw.Location(*self.model.predator.state.location)
        predator_step.rotation = self.model.predator.state.direction
        return predator_step
    
    def new_game(self):
        print("BotEvadeGame: prepare")
        
        self.loader = game.CellWorldLoader(world_name=self.world_name)
        self.model = game.BotEvade(world_name=self.world_name,
                            render=self.render,
                            time_step=self.time_step) 

        game.save_log_output(model = self.model, experiment_name = self.experiment_name, 
            log_folder='logs/', save_checkpoint=True)

        self.model.prey.dynamics.turn_speed = self.turn_speed
        self.model.prey.dynamics.forward_speed = self.forward_speed 
        self.model.reset()
        return self

    def reset(self):
        print("BotEvadeGame: reset")
        if self.model:
            self.model.reset()
        else: 
            print("BotEvadeGame: reset | no model found")
    
    def move_mouse(self, message):
        print(f"BotEvadeGame: move_mouse | {message}")
        return
        step: cw.Step = message.get_body(body_type=cw.Step)
    
        if self.model:
            print("inside if self.model")
            self.model.prey.state.location = (step.location.x, step.location.y)
            self.sample_count_prey += 1 
            print("after self.model.prey.state.location")
        else:
            print("BotEvadeGame: move_mouse | no model found")
    
def main():
    args = ArgParser().start() # works 

    time_step = 1/args.sampling_rate # time step 

    print(f'Rendering: {args.render} | time step: {time_step:0.4f} ({args.sampling_rate} Hz)')
    print(f"=== starting server on {args.ip}:{args.port} ===\n")
    
    server = BotEvadeServer(ip='172.30.127.68', port=args.port, fs=args.sampling_rate)
    server.start()
    
    if server.running: 
        print("starting new experiment")
        server.start_new_experiment(experiment_name="start_new_experiment", world_name="21_05")
        
    while server.running:
        pass
    
if __name__ == '__main__':
    main()