import pygame
import random
from NOQA.tiles.base_tile import Tile

class Beach(Tile):
    def __init__(self, groups, pos: tuple):
        super().__init__(groups, pos, "beach")
        
    def set_img(self):        
        img_num = random.randint(1, 40)  
        if img_num == 40:  ## Randomly selects a number between 1 and 5 to choose a beach tile variation, with a higher chance of selecting the first three variations                                                                   
            self.image: pygame.Surface = pygame.image.load(f"gfx/tiles/{self._tile_type}/{self._tile_type}_{1}.png").convert_alpha()  
                ## Sets image attribute by loading image from gfx/tiles/ folder based on tile_type
        else:
            self.image: pygame.Surface = pygame.image.load(f"gfx/tiles/{self._tile_type}/{self._tile_type}_{0}.png").convert_alpha()  
                ## Sets image attribute by loading image from gfx/tiles/ folder based on tile_type

        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)