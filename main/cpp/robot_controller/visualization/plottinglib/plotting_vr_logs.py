# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install cellworld
# !pip install ipywidgets == 7.0.0
# # from google.colab import drive
# # drive.mount('/content/drive')
# !pip install scikit_posthocs

import matplotlib.pyplot as plt
import numpy as np 
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cellworld as cw
# from cellworld import *

class ExperimentData:
  def __init__(self, filepath:str=None, data:cw.Experiment=None)->None:
    self.filepath = filepath
    self.data = data

  
  def get_capture_list(self)->list[list]:
    """
      Get list of lists of episodes with captures:
      
      Args:
        Nothing, just self (experiment data)
        
      Returns: 

        List of list containing capture information.
      
        ret[list][0] = episode_number[int]
        ret[list][1] = frame_numbers[list]
    """
    caps = []
    for i in range(len(self.data.episodes)): 
      if len(self.data.episodes[i].captures) > 0:
        caps.append([i,self.data.episodes[i].captures])
    
    return caps
    # return [self.__get_capture_episode__(episode) for episode in self.data.episodes]

  def __get_capture_episode__(episode:cw.Episode=None):
    return 1 if episode and len(episode.captures) > 0 else 0

  def load_from_file(self, filepath:str=None):
    import os
    if filepath and os.path.exists(filepath): 
      self.filepath = filepath
      self.data = cw.Experiment.load_from_file(filepath)

class Plotter():
    def __init__(self, 
                folderpath:str = None, 
                filepath:str = None,
                occlusions:str = "21_05"):
        
      from typing import List

      self.folderpath = folderpath
      self.filepath = filepath
      self.occlusions = occlusions
      self.experiments: List[ExperimentData] = []

      if self.folderpath: 
        print(f"loading experiments from folder: {self.folderpath}")
      
      if self.filepath: 
        self.load(self.filepath)

    def load(self,filepath:str=None)->None:
      import os 
      if filepath:
        self.filepath = filepath
      else: 
        if self.filepath is None:
          raise Exception("No valid files passed, both are `None`. Pass in value to `self.load(file_path)` or `define self.file_path`")
      
      if not os.path.exists(self.filepath):
        raise FileNotFoundError("File not found!")
      
      experiment = cw.Experiment.load_from_file(self.filepath)
      if experiment is None: 
        raise BaseException("experiment is None!")
      self.experiments.append(ExperimentData(filepath = self.filepath, data=experiment))

    def is_experiment_in_list(self, experiment_idx:int=None, experiment_list:list=None)->bool:
      if experiment_list is None: 
        experiment_list = self.experiments

      if experiment_idx is None: 
        raise TypeError(f"experiment_idx is None")

      if 0 <= experiment_idx <= len(experiment_list):
        print(f"idx in range! idx= {experiment_idx}; len: {len(experiment_list)}")
        return True
      else:
        return False

    def basic_plot(self, experiment_idx:int=0, world_configuration:str='hexagonal',world_implementation_name:str='canonical',fig_size=(10,10)):
      if self.is_experiment_in_list(experiment_idx,self.experiments):
        w = cw.World.get_from_parameters_names(world_configuration,world_implementation_name,self.occlusions)
        d = cw.Display(w, fig_size=fig_size, padding=0, cell_edge_color="lightgrey", background_color="white", habitat_edge_color="black")
        for episode in self.experiments[experiment_idx].data.episodes:
          t = episode.trajectories
          prey_color = 'grey'
          if len(episode.captures) > 0:
            predt = t.get_agent_trajectory('predator')
            d.add_trajectories(predt, colors = {'predator': 'red'}, alphas = {'predator': 0.7})
            prey_color = 'blue'
          preyt = t.get_agent_trajectory('prey')
          d.add_trajectories(preyt, colors = {'prey': prey_color}, alphas = {'prey': 0.7})
      else: 
        print(f"Index not in range!")
        return
        # raise KeyError(f"Index out of range! len(self.experiment_data) = {len(self.experiment_data)}")        
        
def plot_experiment(exp_path:str=None, fs:int = 60):
  if exp_path is None: 
    print("No file passed")
    return 
  
  e = cw.Experiment.load_from_file(exp_path)
  if e is None: 
    print("No experiment found: e is NONE")
    return 
  w = cw.World.get_from_parameters_names('hexagonal',"canonical",e.occlusions)
  d = cw.Display(w, fig_size=(8,8), padding=0, cell_edge_color="lightgrey", background_color="white", habitat_edge_color="black")
  subject_str = 'prey'
  scalar = 1.0
  mv = 1.0

  frame_total = 0
  
  print(f'Episode count: {len(e.episodes)}')
  for i, episode in enumerate(e.episodes[:]):
    t = episode.trajectories
    rt = t.get_agent_trajectory('prey')
    rpred = t.get_agent_trajectory('predator')
    timestamps = t.get('time_stamp')

    # d.add_trajectories(rt)
    # d.add_trajectories(rpred)
    # d.ax.plot(rt.get('location').get('x'),rt.get('location').get('y'),'--o')
    frame_list = rt.get('frame')
    frame_total += len(frame_list)
    nv = [f/(max(frame_list)) for f in frame_list]
    d.add_trajectories(rt, colors = {'prey':[plt.cm.jet(v) for v in nv]}, alphas = {'prey':0.7})
    # d.add_trajectories(rt, colors = {'prey':'r'}, alphas = {'prey':0.7})

  print(f"Episode count: {i+1}\nTotal time (min): {(frame_total/fs)/60:0.4f}")


def plot_episode(episode_path:str=None):
  if episode_path is None: 
    print("No file passed")
    return

  w = World.get_from_parameters_names('hexagonal',"canonical",'21_05')
  d = Display(w, fig_size=(6,6), padding=0, cell_edge_color="lightgrey", background_color="white", habitat_edge_color="black")
  scalar = 1.0
  mv = 1.0
  episode = Episode.load_from_file(episode_path)
  t = episode.trajectories
  agent_t = t.split_by_agent()
  m1_t = agent_t['prey']
  d.ax.plot(m1_t.get('location').get('x'),[y for y in m1_t.get('location').get('y')])
  # d.add_trajectories(t, colors = {'prey': 'darkorange'},
  #                   alphas = {'prey': 1.0}, zorder = 5)

  cw.Cell_group_builder.get_from_name("hexagonal", "20_05", "occlusions")
  
def plot_experiment_episode_index(exp_path:str=None,idx:int=0):
  if exp_path is None: 
    print("No file passed")
    return 
  
  e = Experiment.load_from_file(exp_path)
  
  if e is None: 
    print("No experiment found: e is NONE")
    return 
  w = World.get_from_parameters_names('hexagonal',"canonical",e.occlusions)
  d = Display(w, fig_size=(6,6), padding=0, cell_edge_color="lightgrey", background_color="white", habitat_edge_color="black")
  subject_str = 'prey'
  scalar = 1.0
  mv = 1.0

  fig = plt.figure(figsize=(4,3))
    
  episode = e.episodes[idx]
  t = episode.trajectories
  rt = t.get_agent_trajectory('prey')
  rpred = t.get_agent_trajectory('predator')
  rpred = t.get_agent_trajectory('predator')
  # timestamps = t.get('time_stamp')
  # print(f'Total duration: {timestamps[-1]} | frames: {len(rt)}')

  frame_list = rt.get('frame')
  vr = rt.get('data')
  d.add_trajectories(rt, colors = {'prey':'r'}, alphas = {'prey':0.7})
  d.add_trajectories(rpred, colors={'predator':'b'})
  d.ax.set_xlim([-0.1, 1.1])


# %%

# %%
