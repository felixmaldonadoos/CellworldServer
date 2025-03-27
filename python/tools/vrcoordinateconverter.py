import cellworld_game as game
import numpy as np
import math
class VRCoordinateConverter:
    def __init__(self):
        self.origin_transform = {'direction':None, 'scale': None}
        self.origin = {'entry':None, 'exit':None}
        self.active = False
        pass
    
    def set_origin(self, originA:list=None, originB:list=None, flipY:bool=True):
        self.origin['entry'] = [originA[1], -originA[0]] # flip x/y to y/-x
        self.origin['exit']  = [originB[1], -originB[0]] # flip x/y to y/-x
        self.origin_transform['direction'] = game.Direction.radians(self.origin['entry'], self.origin['exit'])  + np.pi/2
        self.origin_transform['scale']     = game.Point.distance(self.origin['entry'] ,  self.origin['exit'])
        self.active = True
        print(f'[set origin] Active: {self.active}')
        print(f'[set origin] Origin: {self.origin}')
        print(f'[set origin] Origin Tranform: {self.origin_transform}')
    
    def vr_to_canonical_v1(self,x,y)->game.Point:
        dirp = game.Direction.radians(self.origin['entry'], (x,y)) - self.origin_transform['direction']
        distp = game.Point.distance(self.origin['entry'],(x,y)) / self.origin_transform['scale']
        return game.Point.move((0, .5), distance=distp, direction_radians= dirp)

    
    def vr_to_canonical(self,x,y)->game.Point:
        dirp = game.Direction.radians(self.origin['entry'], (x,y)) - self.origin_transform['direction']
        distp = game.Point.distance(self.origin['entry'],(x,y)) / self.origin_transform['scale'] 
        point = game.Point.move((0, .5), distance=distp, direction_radians=dirp)         
        # y = point[1]*math.sqrt(3)*0.5  + 0.5 - (math.sqrt(3)/4) 
        offset = (1-math.sqrt(3)*0.5)
        magic_num = 0.0275
        p = (point[0]+magic_num, point[1] - offset - magic_num)
        return p

    def canonical_to_vr(self, px, py) -> game.Point:
        direction = game.Direction.radians((0, 0.5), (px, py)) + self.origin_transform['direction']
        distance = game.Point.distance((0, 0.5), (px, py)) * self.origin_transform['scale']
        return game.Point.move(self.origin['entry'], distance=distance, direction_radians=direction)  
    