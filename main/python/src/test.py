import tcp_messages as tm
import time
import cellworld_experiment_service as ces
import cellworld_tracking as ct
class ExperimentTrackingService(ces.ExperimentService, ct.TrackingService):

    def __init__(self):
        ces.ExperimentService.__init__(self)
        ct.TrackingService.__init__(self)
        ct.TrackingClient.connect(self,"127.0.0.1",port=4566)
        
    def start(self):
        ces.ExperimentService.start(self)


cets = ExperimentTrackingService()

while True:
    try:
        print("Starting cets")
        cets.start()
        break
    except OSError as e:
        print(f"{e}\nRetrying...")
        cets.stop()
        time.sleep(1)
        # cets.start()

cets.join()