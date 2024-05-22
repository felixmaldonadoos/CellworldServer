import tcp_messages as tm
import cellworld_experiment_service as ces
import cellworld_tracking as ct
class ExperimentTrackingService(ces.ExperimentService, ct.TrackingService):

    def __init__(self):
        ces.ExperimentService.__init__(self)
        ct.TrackingService.__init__(self)
        ct.TrackingClient.connect("127.0.0.1",4566)
        
    def start(self):
        ces.ExperimentService.start(self)


cets = ExperimentTrackingService()
cets.start()
cets.join()