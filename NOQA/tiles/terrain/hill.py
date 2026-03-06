import pygame
import random
from NOQA.tiles.base_tile import Tile

class Hill(Tile):
    def __init__(self, groups, pos: tuple):
        super().__init__(groups, pos, "hill")
        
    def set_img(self):        
        self.image: pygame.Surface = pygame.image.load(f"gfx/tiles/{self._tile_type}/{self._tile_type}_{0}.png").convert_alpha()  
                ## Sets image attribute by loading image from gfx/tiles/ folder based on tile_type

        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)