import matplotlib.pyplot as plt

from src import *
e = Experiment.load_from_file("/Users/chris/chris-lab/projects/cellworld_hackathon_01/cellworld/python/test_experiment.json")
w = World.get_from_parameters_names(e.world_configuration_name,
                                    "canonical",
                                    e.occlusions)
MDFclustering = StreamLineClusters(distance_metric=DistanceMetric.MDF)
HAUSclustering = StreamLineClusters(distance_metric=DistanceMetric.HAUS)
AMDclustering = StreamLineClusters(distance_metric=DistanceMetric.AMD)

fig, ax = plt.subplots(1, 4, figsize=(12, 3))

e.remove_episodes(e.get_incomplete_episodes() + e.get_broken_trajectory_episodes() + e.get_wrong_origin_episodes() + e.get_wrong_goal_episodes())

d = Display(w, fig_size=(3, 3), fig=fig, ax=ax[0])
for episode in e.episodes:
    split_trajectories = episode.trajectories.split_by_agent()
    if "prey" not in split_trajectories:
        continue
    prey_trajectory = split_trajectories["prey"]
    predator_trajectory = split_trajectories["predator"]
    MDFclustering.add_trajectory(prey_trajectory)
    HAUSclustering.add_trajectory(prey_trajectory)
    AMDclustering.add_trajectory(prey_trajectory)
    d.add_trajectories(prey_trajectory,
                       distance_equalization=True)
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

d = Display(w, fig_size=(3, 3), fig=fig, ax=ax[1])
d.plot_clusters(MDFclustering, colors=clrs)
print("MDFclustering:", len(MDFclustering.clusters))

d = Display(w, fig_size=(3, 3), fig=fig, ax=ax[2])
d.plot_clusters(HAUSclustering, colors=clrs)
print("HAUSclustering:", len(HAUSclustering.clusters))

d = Display(w, fig_size=(3, 3), fig=fig, ax=ax[3])
d.plot_clusters(AMDclustering, colors=clrs)
print("AMDclustering:", len(AMDclustering.clusters))
plt.show()




