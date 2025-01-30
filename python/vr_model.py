import cellworld_game as game
class VRModel:
    def __init__(self, 
                 model:game.BotEvade = game.BotEvade(),
                 loader:game.CellWorldLoader = game.CellWorldLoader(world_name="21_05")
                 ):
        
        self.model = model
        self.loader = loader

        # assign model callbacks
        self.on_capture = None
        pass