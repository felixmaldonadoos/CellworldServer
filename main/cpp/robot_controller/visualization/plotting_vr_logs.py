# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install cellworld
# !pip install ipywidgets == 7.0.0
# # from google.colab import drive
# # drive.mount('/content/drive')
# !pip install scikit_posthocs


import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
# import pandas as pd
import random
import math
import cellworld as cw
from cellworld import *

def plot_experiment(exp_path:str=None):
  if exp_path is None: 
    print("No file passed")
    return 
  e = Experiment.load_from_file(exp_path)
  reward_locations = e.rewards_cells
  reward_angles = e.rewards_orientations
  reward_cmap = plt.cm.tab20

  w = World.get_from_parameters_names('hexagonal',"canonical",e.occlusions)
  d = Display(w, fig_size=(10,10), padding=0, cell_edge_color="lightgrey", background_color="white", habitat_edge_color="black")
  subject_str = 'prey'
  scalar = 1.0
  mv = 1.0

  fig,ax = plt.subplots(1, 1, figsize=(7.2,6))

  for i, episode in enumerate(e.episodes[:]):
    t = episode.trajectories
    rt = t.get_agent_trajectory('prey')
    rpred = t.get_agent_trajectory('predator')

    d.add_trajectories(rt)
    d.add_trajectories(rpred)
    ax.plot(rt.get('location').get('x'),rt.get('location').get('y'))
  
    # d.add_trajectories(rt)
    # d.add_trajectories(rpred)
  fig.show()

def plot_episode(episode_path:str=None):
  if episode_path is None: 
    print("No file passed")
    return

  episode_path = '/content/alexandertest_07182024_125406.json'
  w = World.get_from_parameters_names('hexagonal',"canonical",'21_05')
  d = Display(w, fig_size=(6,6), padding=0, cell_edge_color="lightgrey", background_color="white", habitat_edge_color="black")
  scalar = 1.0
  mv = 1.0
  # d.ax.set_xlim([0,1])
  # d.ax.set_ylim([-.5,1])
  episode = Episode.load_from_file(episode_path)
  t = episode.trajectories
  agent_t = t.split_by_agent()
  m1_t = agent_t['prey']
  d.ax.plot(m1_t.get('location').get('x'),[y for y in m1_t.get('location').get('y')])
  print(t[0])
  # d.add_trajectories(t, colors = {'prey': 'darkorange'},
  #                   alphas = {'prey': 1.0}, zorder = 5)

  cw.Cell_group_builder.get_from_name("hexagonal", "20_05", "occlusions")


plot_experiment('logs/alexander_07182024_150528.json')