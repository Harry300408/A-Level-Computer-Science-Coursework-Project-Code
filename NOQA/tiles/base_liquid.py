import pygame
from NOQA.tiles.base_tile import Tile

class BaseLiquid(Tile):
    def __init__(self, groups, pos, _tile_type="default"):
        super().__init__(groups, pos, _tile_type)
        
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1  # Speed of animation