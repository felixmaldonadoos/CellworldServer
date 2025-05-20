import pygame
from cellworld_game.agent import AgentState
from cellworld_game.navigation import Navigation
from cellworld_game.navigation_agent import NavigationAgent
from cellworld_game.resources import Resources
from cellworld_game.polygon import Polygon
from cellworld_game.points import Points
import math

class MouseVR(NavigationAgent):
    def __init__(self,
                 start_state: AgentState,
                 navigation: Navigation,
                 view_field: float = 360,
                 max_forward_speed: float = 0.5,
                 max_turning_speed: float = 20.0):
        NavigationAgent.__init__(self,
                                 navigation=navigation,
                                 max_forward_speed=max_forward_speed,
                                 max_turning_speed=max_turning_speed,
                                 view_field=view_field,
                                 size=0.04,
                                 sprite_scale=2.0,
                                 polygon_color=(20, 90, 20))
        self.start_state = start_state

    def reset(self):
        NavigationAgent.reset(self)
        return AgentState(location=self.start_state.location, direction=self.start_state.direction)

    @staticmethod
    def create_sprite() -> pygame.Surface:
        sprite = pygame.image.load(Resources.file("prey.png"))
        rotated_sprite = pygame.transform.rotate(sprite, 270)
        return rotated_sprite

    # @staticmethod
    # def create_body_polygon() -> Polygon:
    #     return Polygon([(.015, 0), (0, 0.005), (-.015, 0), (0, -0.005)])

    @staticmethod
    def create_body_polygon() -> Polygon:
        r = 0.015
        n = 32  # number of vertices
        return Polygon([
            (r * math.cos(2 * math.pi * i / n),
            r * math.sin(2 * math.pi * i / n))
            for i in range(n)
        ])
