from src import ExperimentService


def on_experiment_started(parameters):
    print("started a new experiment: ", parameters)


def on_episode_started(experiment_name):
    print("started a new episode: ", experiment_name)


def on_episode_finished(experiment_name):
    print("ended a new episode:", experiment_name)


def on_experiment_finished(experiment_name):
    print("ended a new experiment:", experiment_name)


def new_connection(conn):
    print("new connection!")


service = ExperimentService()
service.on_new_connection = new_connection
service.set_tracking_service_ip("127.0.0.1")
service.on_experiment_started = on_experiment_started
service.on_episode_started = on_episode_started
service.on_episode_finished = on_episode_finished
service.on_experiment_finished = on_experiment_finished
service.start()
print("service running..")
service.join()
