import pygame, os
from NOQA.tiles.base_tile import Tile

class Liquid(Tile):
    def __init__(self, groups, pos: tuple, _tile_type: str = "default"):
        super().__init__(groups, pos, _tile_type)
        
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1  # Speed of animation

        self._ID: str = f"l{pos[0]} {pos[1]}"  
    
    def load_frames(self):
        
        for i in os.listdir(f'gfx/tiles/{self._tile_type}'):  
            
            frame = pygame.image.load(f"gfx/tiles/{self._tile_type}_{i}").convert_alpha()
            
            self.frames.append(frame)