# Library for cpp and python servers for BotEvade VR Experiment 


## Setup



### Agent Tracking (main/cpp/robot_controller/main.py)

#### Make sure to add a 'CELLWORLD_CACHE' variable in your system's environment variable

You want to clone `git@github.com:germanespinosa/cellworld_data.git` into your system and add 
that path to `$CELLWORLD_CACHE`.

Steps: 

```
# assume saving into current working directory (outside of this repo's folder is preferred)
git clone --depth 1 git@github.com:germanespinosa/cellworld_data.git

echo "export CELLWORLD_CACHE="path/to/dir/cellworld_data""

```

#### Todo: 

- Check `model.is_valid_state()` to investigate how to implement collision detection

