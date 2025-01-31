import cellworld_game as game
from vr_options import Options

class VRModel(game.BotEvade):
    def __init__(self, 
                 loader:game.CellWorldLoader = game.CellWorldLoader(world_name="21_05"),
                 world_name:str = "21_05",
                 render:bool = True, 
                 time_step:float = 60,
                 goal_threshold= 0.01,
                 puff_cool_down_time=3
                 ):
        game.BotEvade.__init__(self, 
                               world_name=world_name, 
                               render=render,
                               time_step=time_step, 
                               real_time=True, 
                               goal_threshold=goal_threshold,
                               puff_cool_down_time=puff_cool_down_time)
        
        # assign model callbacks
        self.on_capture = None
        pass