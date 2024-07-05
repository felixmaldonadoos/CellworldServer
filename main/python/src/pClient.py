from json_cpp import *
import tcp_messages as tcp
# from cellworld import Location, Step, Episode, World
import cellworld_experiment_service as ces
import time 

class ExperimentServiceClient(ces.ExperimentClient):

    def __init__(self):
        super().__init__()
        self.router.add_route("predator_step", self.echo_predator_response, JsonString)
        self.on_episode_started = self.on_episode_started_es
        self.response_start_experiment = None

    def send_get_experiment(self, experiment_name: str) -> ces.GetExperimentResponse:
        return self.get_experiment(experiment_name)

    def on_episode_started_es(self, msg:ces.EpisodeStartedMessage):
        print(f"[ES] Episode Started: {msg}")
    
    def init_connect(self, port)->bool:
        return tcp.MessageClient.connect(self, "127.0.0.1", 4970) # alt 
    
    def pre_start(self)->None:
        
        # input("Press Enter to connect to Experiment Service server...")
        
        if not self.init_connect(4566):
            print("[ES] Connection failed")
            return None
        
        print("[ES] Connected to Experiment Service server")
        
        try:
            self.response_start_experiment = self.start_experiment(suffix="suffix",prefix="prefix",world_configuration="hexagonal", world_implementation="canonical",
                        occlusions="21_05", subject_name="alexander",duration=100,
                        rewards_cells = ces.Cell_group_builder(), rewards_orientations=JsonList())
            print(f"[ES] Start experiment response: {self.response_start_experiment}")
        except TimeoutError:
            print(f"[ES] Timed out! unrouted/pending requests: {self.router.pending_responses}; count: {self.router.routing_count};")
            return None
        try:
            self.response_start_episode = self.start_episode(experiment_name=self.response_start_experiment.experiment_name,
                                        rewards_sequence=None)
            print(f"[ES] Start episode response: {self.response_start_episode}")
        except TimeoutError:
            print("[ES] Start episode timed out")
            return None

    def send_broadcast_prey(self, step):
        print(f"Sending prey_step {step.location}")
        self.send_message(message=tcp.Message(header="prey_step", 
                                body=step))
    
    def run(self)->None:
        self.pre_start()
            
    def stop(self)->None:
        if self.response_start_experiment is None:
            print("[ES] @ stop:  response_start_experiment NONE")
            return
        r = self.finish_episode()
        print(f"[ES] finish_episode: {r}")
        response = self.finish_experiment(self.response_start_experiment.experiment_name)
        print(f"[ES] finish_experiment: {response}")
        return None
    
    def echo_predator_response(self,msg)->None:
        print(f"[echo_predator_response]: {msg}")
        
    def echo(self,msg)->None:
        print(f"Sent: {msg}")
    
client = ExperimentServiceClient()
client.run()

# finish episode and then finish experiment 
print("[LOG] Preparing to stop...")
time.sleep(0.5)

try:
    for i in range(0,10):
        step = ces.Step(0.5,1.0)
        step.agent_name = "prey"
        step.frame = i 
        client.send_broadcast_prey(step)
except: 
    print("ERROR SENDING MESSAGE")

client.stop()

print("[LOG] Exiting...")