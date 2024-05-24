from json_cpp import *
import tcp_messages as tcp
from time import sleep
from cellworld import Location, Step, Episode, World
import cellworld_experiment_service as ces
from cellworld_tracking import TrackingClient as tc 
import time 

class ExperimentServiceClient(ces.ExperimentClient):
    def __init__(self):
        super().__init__()
        self.router.add_route("predator_step",self.echo, JsonString)
        self.on_episode_started = self.on_episode_started_es
        self.port = 4566
        self.response_start_experiment = None
        
    def send_get_experiment(self, experiment_name: str) -> ces.GetExperimentResponse:
        return self.get_experiment(experiment_name)

    def on_episode_started_es(self, msg:ces.EpisodeStartedMessage):
        print(f"[ES] Episode Started: {msg}")
    
    def pre_start(self)->None:
        input("Press Enter to connect to Experiment Service server...")
        res = tcp.MessageClient.connect(self, "127.0.0.1", 4566)
        print(f"[ES] connected")
        try:
            # r = self.send_request(tcp.Message("!subscribe"), 5000)
            # print("[DBG-RQST] !subscribe: ", r.body)
            # r = self.send_request(tcp.Message("!ping"), 5000)
            # print("[DBG-RQST] !ping: ", r.body)
            # r = self.send_request(tcp.Message("start_experiment", ), 5000)
            # print("[DBG-RQST] start_experiment: ", r.body)
            self.response_start_experiment = self.start_experiment(suffix="test",prefix="test",world_configuration="hexagonal",world_implementation="canonical",
                        occlusions="21_05", subject_name="alexander",duration=100,
                        rewards_cells= ces.Cell_group_builder(), rewards_orientations=JsonList())
            print(f"[ES] Start experiment response: {self.response_start_experiment}")
        except TimeoutError:
            print("[ES] Timed out")
            print(f"[ES] unrouted: pending {self.router.pending_responses}; count: {self.router.routing_count};")
            return
        try:
            self.response_start_episode = self.start_episode(experiment_name=self.response_start_experiment.experiment_name,
                                        rewards_sequence=None)
            print(f"[ES] Start episode response: {self.response_start_episode}")
        except TimeoutError:
            print("[ES] Start episode timed out")
            return
    
    def run(self)->None:
        self.pre_start()

    def stop(self)->None:
        if self.response_start_experiment:
            get_experiment_response = self.get_experiment(self.response_start_experiment.experiment_name)
            if get_experiment_response:
                print(f"[ES] get_experiment_response: {get_experiment_response}")
                time.sleep(1)
                print(self.finish_experiment(self.response_start_experiment.experiment_name))
            else:
                print("[ES] get_experiment_response NONE")
        else: 
            print("[ES] response_start_experiment NONE")
    def echo(self,msg)->None:
        print(f"Sent: {msg}")
    
# run tracking service
# TrackingServiceClient().run()

# run experiment service 
esc = ExperimentServiceClient()
esc.run()

# finish episode and then finish experiment 
print("[LOG] Preparing to stop...")
time.sleep(0.5)
esc.stop()

print("[LOG] Exiting...")
