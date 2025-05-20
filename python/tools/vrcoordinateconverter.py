import cellworld_game as game
import numpy as np
import math
class VRCoordinateConverter:
    def __init__(self):
        print("Initialised")
        self.origin_transform = {'direction':None, 'scale': None}
        self.origin = {'entry':None, 'exit':None}
        self.active = False
        pass
    
    def set_origin(self, originA:list=None, originB:list=None, flipY:bool=True):
        self.origin['entry'] = [originA[0], originA[1]] # flip x/y to y/-x
        self.origin['exit']  = [originB[0], originB[1]] # flip x/y to y/-x
        entry = np.array([self.origin['entry'][0], self.origin['entry'][1]])
        exit = np.array([self.origin['exit'][0], self.origin['exit'][1]])
        x_left, y_left = entry
        x_right, y_right = exit
        self.x_left = x_left
        self.y_left = y_left
        dx = x_right - x_left
        dy = y_right - y_left
        denominator = dx**2 + dy**2
        self.transform = np.array([[dx, dy], 
                                   [-dy, dx]])
        self.transform *= 1/denominator
        self.origin_transform['direction'] = game.Direction.radians(self.origin['entry'], self.origin['exit']) ##  + np.pi/2
        self.origin_transform['scale']     = game.Point.distance(self.origin['entry'] ,  self.origin['exit'])
        self.active = True
        print(f'[set origin] Active: {self.active}')
        print(f'[set origin] Origin: {self.origin}')
        print(f'[set origin] Origin Tranform: {self.origin_transform}')
    
    def vr_to_canonical_v1(self,x,y)->game.Point:
        dirp = game.Direction.radians(self.origin['entry'], (x,y)) - self.origin_transform['direction']
        distp = game.Point.distance(self.origin['entry'],(x,y)) / self.origin_transform['scale']
        return game.Point.move((0, .5), distance=distp, direction_radians=dirp)
    
    def vr_to_canon_rotation(self, x, y):
        dirp = game.Direction.radians(self.origin['entry'], (x,y)) - self.origin_transform['direction']
        return dirp

    def vr_to_canon(self, x, y)->game.Point:
        # x_prime = ((x - self.x_left) *self.dx + ( y - self.y_left)*self.dy)/self.denominator
        # y_prime = (-(x - self.x_left)*self.dy + (y - self.y_left)*self.dx)/self.denominator + 0.5
        x -= self.x_left
        y -= self.y_left
        point = np.array([x, y])
        point_prime = np.dot(self.transform, point)
        point_prime[1] *= -1
        point_prime[1] += 0.5 # y
        return [float(point_prime[0]),float(point_prime[1])]
    
    def vr_to_canonical(self,x,y)->game.Point: # german's function
        dirp = game.Direction.radians(self.origin['entry'], (x,y)) - self.origin_transform['direction']
        distp = game.Point.distance(self.origin['entry'],(x,y)) / self.origin_transform['scale'] 
        point = game.Point.move((0, .5), distance=distp, direction_radians=dirp)         
        return point

    def canonical_to_vr(self, px, py): 
        transform_inverse = np.linalg.inv(self.transform)
        point = np.array([px, py])
        point[1] -= 0.5
        point[1] *= -1
        point_prime = np.dot(transform_inverse, point)
        point_prime[0] += self.x_left
        point_prime[1] += self.y_left
        return [float(point_prime[0]), float(point_prime[1])]
        