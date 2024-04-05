from json_cpp import *
import tcp_messages as tcp
from time import sleep
from cellworld import Location, Step, Episode, World
import cellworld_experiment_service as ces
from cellworld_tracking import TrackingClient as tc 
import time 
class TrackingServiceClient(tcp.MessageClient):
    def __init__(self):
        super().__init__()
        self.router.add_route("send_step", self.echo, JsonString)
        self.port = 4510
        self.ip = "127.0.0.1"
    def run(self):
        if self.connect("127.0.0.1", 4510):
            print("[TS] connected")
            if self.subscribe():
                print("[TS] Subscribed!")
        else:
            print("[TS] failed to connect")
    def echo(self,msg):
        print(f"[TS] Sent: {msg}")

class ExperimentServiceClient(ces.ExperimentClient):
    def __init__(self):
        super().__init__()
        self.router.add_route("predator_step",self.echo, JsonString)
        self.on_episode_started = self.on_episode_started_es
        self.port = 4540

    def send_get_experiment(self, experiment_name: str) -> ces.GetExperimentResponse:
        return self.get_experiment(experiment_name)

    def on_episode_started_es(self, msg:ces.EpisodeStartedMessage):
        print(f"[ES] Episode Started: {msg}")
      
    def pre_start(self)->None:
        res = self.connect("127.0.0.1")
        print(f"[ES] connected")
        try:
            self.response_start_experiment = self.start_experiment(suffix="test",prefix="test",world_configuration="hexagonal",world_implementation="canonical",
                        occlusions="21_05", subject_name="alexander",duration=100,
                        rewards_cells=None,rewards_orientations=None)
            print(f"[ES] Start experiment response: {self.response_start_experiment}")
        except TimeoutError:
            print("[ES] Timed out")
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
        print("stop")
        print(self.finish_episode())
        print("stop exp. getting experiment")
        get_experiment_response = self.get_experiment(self.response_start_experiment.experiment_name)
        print(get_experiment_response)
        print("after get exp resp")
        time.sleep(2)
        print(self.finish_experiment(self.response_start_experiment.experiment_name))

    def echo(self,msg)->None:
        print(f"Sent: {msg}")
    
# run tracking service
TrackingServiceClient().run()

# run experiment service 
esc = ExperimentServiceClient()
esc.run()

# finish episode and then finish experiment 
print("[LOG] Preparing to stop...")
time.sleep(0.5)
esc.stop()
