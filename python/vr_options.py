class Options:
    def __init__(self, **kwargs):
        self.options_dict = kwargs

    def display(self):
        print(" | ".join(f"{key}: {value}" for key, value in self.options_dict.items()))

    def set_option(self, key, value):
        self.options_dict[key] = value

    def get_option(self, key, default=None):
        return self.options_dict.get(key, default)