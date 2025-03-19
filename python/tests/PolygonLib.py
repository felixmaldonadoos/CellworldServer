from shapely.geometry import Polygon, Point
import numpy as np
import random

class PolygonHab:
    def __init__(self):
        self.hexagon = Polygon([
            (0.0, 0.5), # Entrance
            (0.25, 0.933), 
            (0.75, 0.933), 
            (1.0, 0.5), # Exit
            (0.75, 0.067), 
            (0.25, 0.067)
        ])

    def plot(self, random_points, entrance, exit):
        import matplotlib.pyplot as plt

        x_hex, y_hex = self.hexagon.exterior.xy
        x_coords = [point.x for point in random_points]
        y_coords = [point.y for point in random_points]
        
        plt.plot(x_hex, y_hex, 'b-')  # Hexagon border
        plt.plot([entrance[0], exit[0]], [entrance[1], exit[1]], 'ro')  # Entrance and exit points
        plt.scatter(x_coords, y_coords, color='green', s=10)  # Random points

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Random Points Inside Hexagonal Arena')
        plt.show()

    def generate_path(self, origin:Point=Point(0.1,0.5), step_size:float=0.05, N:int=50):
        points = [Point(origin)]
        current_point = origin
        
        for _ in range(N - 1):
            angle = np.random.uniform(0, 2 * np.pi)

            next_point = (current_point.x + step_size * np.cos(angle), 
                          current_point.y + step_size * np.sin(angle))
            next_point = Point(next_point)
            
            if self.hexagon.contains(next_point):
                points.append(next_point)
                current_point = next_point
            else:
                # If next_point is out of bounds, try a new random angle
                while not self.hexagon.contains(next_point):
                    angle = np.random.uniform(0, 2 * np.pi)
                    next_point = (current_point.x + step_size * np.cos(angle), 
                                  current_point.y + step_size * np.sin(angle))
                    next_point = Point(next_point)
                points.append(next_point)
                current_point = next_point
        
        return points
    
    def generate_path_finish(self,origin:Point=Point(0.1,0.5), 
                             endpoint:Point=Point(1,0.5), 
                             step_size:float=0.05, 
                             N:int=50):
        points = [Point(origin)]
        current_point = origin
        
        for _ in range(N - 2):
            angle = np.random.uniform(0, 2 * np.pi)

            next_point = (current_point.x + step_size * np.cos(angle), 
                          current_point.y + step_size * np.sin(angle))
            next_point = Point(next_point)
            
            if self.hexagon.contains(next_point):
                points.append(next_point)
                current_point = next_point
            else:
                # If next_point is out of bounds, try a new random angle
                while not self.hexagon.contains(next_point):
                    angle = np.random.uniform(0, 2 * np.pi)
                    next_point = (current_point.x + step_size * np.cos(angle), 
                                  current_point.y + step_size * np.sin(angle))
                    next_point = Point(next_point)
                points.append(next_point)
                current_point = next_point
            
        points.append(Point(1.0,0.5))
        return points
    
    # Function to generate random points within the bounding box of the hexagon
    def generate_random_points_in_hexagon(self, hexagon:Polygon=None, num_points:int=1)->list:
        if hexagon is None: hexagon = self.hexagon; print("Using default Hab hexagon.")
        min_x, min_y, max_x, max_y = hexagon.bounds
        points = []
        
        while len(points) < num_points:
            random_point = Point(np.random.uniform(min_x, max_x), np.random.uniform(min_y, max_y))
            if hexagon.contains(random_point):
                points.append(random_point)
        
        return points