from json_cpp import *
import tcp_messages as tcp
from time import sleep
from cellworld import Location, Step, Episode, World
import cellworld_experiment_service as ces
from cellworld_tracking import TrackingClient as tc 
import time 

class Client(ces.ExperimentClient):
    def __init__(self):
        super().__init__()
        # self.set_tracking_service_ip("127.0.0.1")
        self.port = 4566
    
    def run(self):
        if not self.connect(self.ip): print("Failed to connect!"); return None
        # self.set_tracking_service_ip(self.ip)
        # self.experiment.connect(self.ip)
        return True
    
    def send_start_experiment(self):
        return self.start_experiment(suffix="test",prefix="test",world_configuration="hexagonal",world_implementation="canonical",
                        occlusions="21_05", subject_name="alexander",duration=100,
                        rewards_cells=None,rewards_orientations=None)

c = Client()
if c.run():
    input("Connected. Press any button to starty experiment...")
    resp = c.send_start_experiment()

print("\nExiting...\n")