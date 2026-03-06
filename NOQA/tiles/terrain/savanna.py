import pygame
import random
from NOQA.tiles.base_tile import Tile

class Savanna(Tile):
    def __init__(self, groups, pos: tuple):
        super().__init__(groups, pos, "savanna")
        
    def set_img(self):        
        img_num = random.randint(1, 2)  
        self.image: pygame.Surface = pygame.image.load(f"gfx/tiles/{self._tile_type}/{self._tile_type}_{img_num}.png").convert_alpha()  

        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)