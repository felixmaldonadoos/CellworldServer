import tcp_messages as tm
import cellworld_experiment_service as ces
import cellworld_tracking as ct
class ExperimentTrackingService(ces.ExperimentService, ct.TrackingService):

    def __init__(self):
        ces.ExperimentService.__init__(self)
        ct.TrackingService.__init__(self)

    def start(self):
        ces.ExperimentService.start(self)


cets = ExperimentTrackingService()
cets.start()
cets.join()