from src import ExperimentClient
from time import sleep


def on_experiment_started(parameters):
    print("started a new experiment: ", parameters)


def on_episode_started(experiment_name):
    print("started a new episode: ", experiment_name)


def on_episode_finished(experiment_name):
    print("ended a new episode:", experiment_name )


def on_experiment_finished(experiment_name):
    print("ended a new experiment:", experiment_name)


def print_step(step):
    print(step)


client = ExperimentClient()
client.on_experiment_started = on_experiment_started
client.on_episode_started = on_episode_started
client.on_episode_finished = on_episode_finished
client.on_experiment_finished = on_experiment_finished
client.connect()
client.set_tracking_service_ip("127.0.0.1")
client.subscribe()

client2 = ExperimentClient()
client2.connect()
print("start_experiment")
response = client2.start_experiment("PREFIX", "SUFFIX", "hexagonal", "mice", "10_05", "test_subject", 60)
experiment_name = response.experiment_name
while client2.is_active(experiment_name):
    print("start_episode")
    if not client2.start_episode(experiment_name):
        print("failed to start episode")
    sleep(10)
    print("finish_episode")
    if not client2.finish_episode():
        print("failed to finish episode")

print("finish_experiment")
if not client2.finish_experiment(experiment_name):
    print("failed to finish experiment")
