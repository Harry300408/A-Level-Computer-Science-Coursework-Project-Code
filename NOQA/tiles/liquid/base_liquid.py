import pygame, os
from NOQA.tiles.base_tile import Tile

class Liquid(Tile):
    def __init__(self, groups, pos: tuple, _tile_type: str = "default"):
        
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1  # Speed of animation

        self.load_frames(_tile_type)  ## Load frames for animation
        
        super().__init__(groups, pos, _tile_type)

        self._ID: str = f"l{pos[0]} {pos[1]}" 
        
    def set_img(self):                                                                                          
        self.image: pygame.Surface = self.frames[self.current_frame] 
                ## Sets image attribute by loading image from gfx/tiles/ folder based on tile_type

        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)
    
    
    def load_frames(self, type):
        for i in range(0,3):  ## Assuming 4 frames for each liquid type, can be adjusted as needed
            frame = pygame.image.load(f"gfx/tiles/{type}/{type}_{i}.png").convert_alpha()
            
            self.frames.append(frame)