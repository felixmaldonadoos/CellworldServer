from vr_options import *

opts = Options(ip='127.0.0.1', port=4791, render=False, fs=60, name='name')

opts.set_option('new_opt', 123)  # Dynamically add new options
print(opts.get_option('dsd'))  # Retrieve an existing option
