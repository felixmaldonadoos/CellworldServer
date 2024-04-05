import cellworld_experiment_service as ces
import cellworld_tracking as ct
import tcp_messages as tcp
import cellworld as cw
import sys
import json
import errno
import os

class Server:
    def __init__(self) -> None:
        print("=== BotEvade Server ===")
        self.logs_folder = "../logs/"
        self.tracking_service   = ServerTrackingService()
        self.experiment_service = ServerExperimentService()
        self.experiment_service.get_trajectory = self.tracking_service.get_trajectory
        self.tracking_service.__process_step__ = self.experiment_service.__process_step__

    def start(self)->bool:
        if self.verify_logs_folder() is not True: 
            self.create_logs_folder()

        # check again to make sure 
        if self.verify_logs_folder() is not True: 
            self.log("Failed to create and find logs folder found.")

        if not self.tracking_service.run():
            self.log("ERROR! Failed to start Tracking Service.")
            return False
        
        if not self.experiment_service.run():
            self.log("ERROR! Failed to start Experiment Service.")
            return False
        return True
    
    def stop(self)->None:
        self.experiment_service.stop()
        self.tracking_service.stop()
        self.exit()
        return
    
    def exit(self)->None:
        self.log("Exiting program")
        sys.exit()

    def create_logs_folder(self)->None:
        self.log("Creating logs directory.")
        os.mkdir(self.logs_folder)

    def verify_logs_folder(self)->bool: 
        if os.path.exists(self.logs_folder) and os.path.isdir(self.logs_folder):
            self.log("Successfully found logs directory.")
            return True
        self.log("Failed to find logs directory.")
        return False

    def log(self, msg, *args):
        additional_info = ', '.join(str(arg) for arg in args)
        if additional_info:
            print(f"[Server] {msg}. Info: {additional_info}")
        else:
            print(f"[Server] {msg}.")

class ServerTrackingService(ct.TrackingService):
    def __init__(self) -> None:
        ct.TrackingService.__init__(self)
        # super().__init__(self)
        self.ip                  = "127.0.0.1"
        self.on_new_connection   = self.on_connection_ts
        self.router.add_route("send_step",self.send_step_ts,ces.Step)
        self.current_trajectory = None
        self.__process_step__   = None
        
    def run(self)->bool:
        # print('here')
        res = False
        try:
            res = self.start(port=4510)
            self.log("Started service.",res)
        except OSError:
            self.log("lol server is still refreshing")
        return res

    def get_trajectory(self)->ces.Trajectories:
        self.log("get trajectory")
        trajectory = self.current_trajectory
        self.current_trajectory = None
        # self.log(trajectory)
        return trajectory

    def on_connection_ts(self,msg)->None:
        self.log("New connection.",msg)
    
    def process_to_json_list(self,step:ces.Step = None)->None:
        if step is None: 
            return
        self.trajectories
        return None
    
    def process_step(self, step:ces.Step)->ces.Step: # not being called but i get a message back? 
        # print(step)
        if self.current_trajectory is None:
            self.current_trajectory = ces.Trajectories()
        if step is not None: self.current_trajectory.append(step)
        else: self.log("step none")
        
        if self.current_trajectory is None: self.log("current trajectory is none")
        self.__process_step__(step)
        step = ces.Step()
        step.agent_name = "predator"
        return step

    def send_step_ts(self,step:ces.Step = None):
        step = self.process_step(step)
        self.ts.broadcast_subscribed(ces.Message(step.agent_name + "_step", step))
        return
    
    def log(self, msg, *args):
        additional_info = ', '.join(str(arg) for arg in args)
        if additional_info:
            print(f"[TS] {msg}. Info: {additional_info}")
        else:
            print(f"[TS] {msg}.")
    
    def echo(self,msg):
        self.log("message received:",msg)
        
class ServerExperimentService(ces.ExperimentService):
    def __init__(self):
        super().__init__()
        self.world = cw.World.get_from_parameters_names("hexagonal", "canonical")
        self.on_new_connection      = self.on_new_connection_es
        self.on_experiment_started  = self.on_experiment_started_es
        self.on_experiment_finished = self.on_experiment_finished_es
        self.on_episode_started     = self.on_episode_started_es
        self.on_episode_finished    = self.on_episode_finished_es
        self.on_experiment_resumed  = self.on_experiment_resumed_es  
        self.router.add_route("get_cells_locations", self.get_cells_locations)
        self.router.add_route("get_occlusions", self.get_occlusions, str) 
        # self.on_step                = self.on_step_ts 
        self.set_tracking_service_ip("127.0.0.1")
        self.current_trajectory = None
        self.get_trajectory = None # tell TS to send us trajectory for this episode 
        pass

    def get_cells_locations(self, m=None) -> cw.Location_list:
        return cw.Location_list([c.location for c in self.world.cells])
    
    def get_occlusions(self, occlusions_name) -> cw.Cell_group_builder:
        self.log("received get_occlusions:", occlusions_name)
        return cw.Cell_group_builder.get_from_name("hexagonal", occlusions_name, "occlusions")

    def run(self)->bool:
        res = self.start()
        self.log(f"Started server", res)
        self.join()
        return res
    
    def _call_tracking_service_(self):
        return

    def save_trajectories_to_log(self,trajectories:ces.Trajectories=None)->bool:
        if self.episode_in_progress:
            return False
        return True
    
    def on_new_connection_es(self,msg:tcp.Connection = None)->None:
        self.log("New connection", msg.state)

    def on_episode_started_es(self,msg:ces.StartEpisodeRequest = None)->None:
        self.log("episode started",msg)
      
    def on_episode_finished_es(self,msg:bool = None)->None:
        self.log("Episode finished.", msg)
        if self.get_trajectory is not None: 
            self.active_episode.trajectories = self.get_trajectory() 
            self.log(self.active_episode)

    def on_experiment_started_es(self,msg:ces.StartExperimentResponse = None)->None:
        self.log("Experiment started.",f"experiment name: {msg.experiment_name}")
    
    def on_experiment_resumed_es(self,msg:ces.ResumeExperimentRequest = None)->None:
        self.log("Experiment resumed",
                 f"experiment name: {msg.experiment_name}", 
                 f"duration extension: {msg.duration_extension}")

    def on_experiment_finished_es(self,msg:bool = None)->None:
        self.log("Experiment finished.",msg)
  
    def log(self, msg, *args):
        additional_info = ', '.join(str(arg) for arg in args)
        if additional_info:
            print(f"[ES] {msg}. Info: {additional_info}")
        else:
            print(f"[ES] {msg}.")

# as steps come in, append to traj JsonList and then save as trejectory into episode file. 
# output: 1 trajlist, Experiment(Json):Episode_N:Trajectory
# go to experiment.py -> line 28
            

def main():
    s = Server()
    s.start()
if __name__ == "__main__":
    main()