import argparse
class ExperimentOptions:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __repr__(self):
        return f"ExperimentOptions({self.__dict__})"

    def get(self, key, default=None):
        """Retrieve an option with a default value."""
        return self.__dict__.get(key, default)

class ExperimentArgParse:
    def __init__(self):
        """Initialize the argument parser."""
        
        DEFAULTS = {
            "ip": "127.0.0.1",
            "port": 4791,
            "name": 'default',
            "sampling_rate": 60,
            "render": False,
            "shock": False,
            "pcmouse": False
        }
        
        self.parser = argparse.ArgumentParser(description="Experiment Argument Parser")

        # Define common experiment arguments (can be extended dynamically)
        self.parser.add_argument('--ip', type=str, default=DEFAULTS['ip'],
                                 help=f'Server host (default: {DEFAULTS['ip']})')
        
        self.parser.add_argument('--name','-n', type=str, default=DEFAULTS['name'], 
                                 help=f'Experiment (subject) name/id (default: {DEFAULTS['name']})')
        
        self.parser.add_argument('--port','-p', type=int, default=DEFAULTS['port'], 
                                 help=f'Server port (default: {DEFAULTS['port']})')
        
        self.parser.add_argument('--sampling_rate','-fs', type=float, default=DEFAULTS['sampling_rate'], 
                                 help=f'Sampling rate (default: {DEFAULTS['sampling_rate']})')
        
        self.parser.add_argument('--render', '-r', action='store_true', 
                                 help=f'Enable rendering (default: {DEFAULTS['render']})')
        
        self.parser.add_argument('--shock','-s', action='store_true', 
                                 help=f'Toggle shock on capture (default: {DEFAULTS['shock']})')
        
        self.parser.add_argument('--pcmouse','-pcm', action='store_true', 
                                help=f'Use PC mouse to emulate mouse position (default: {DEFAULTS['pcmouse']})')

    def parse_args(self):
        """Parse command-line arguments and return an ExperimentOptions instance."""
        args = self.parser.parse_args()
        return ExperimentOptions(**vars(args))
    

if __name__ == "__main__":
    import argparse

    arg_parser = ExperimentArgParse()
    experiment_options = arg_parser.parse_args()
    print(experiment_options)