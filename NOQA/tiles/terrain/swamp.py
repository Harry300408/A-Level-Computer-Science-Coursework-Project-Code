import pygame
import random
from NOQA.tiles.base_tile import Tile

class Swamp(Tile):
    def __init__(self, groups, pos: tuple):
        super().__init__(groups, pos, "swamp")
        
    def set_img(self):        
        img_num = random.randint(1, 7)  
        if img_num == 7: 
            self.image: pygame.Surface = pygame.image.load(f"gfx/tiles/{self._tile_type}/{self._tile_type}_{img_num - 4}.png").convert_alpha()  
        else:
            self.image: pygame.Surface = pygame.image.load(f"gfx/tiles/{self._tile_type}/{self._tile_type}_{img_num}.png").convert_alpha()  
                

        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)