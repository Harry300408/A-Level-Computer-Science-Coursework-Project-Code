import pygame, random
from NOQA.assets.base_asset import Asset

class LTree(Asset):                                                                              
    def __init__(self, groups, pos):    
        self.rand = random.randint(0, 5)
                                                                         
        super().__init__(groups, pos, True, "L_Tree", False, "tree")
    
        if self._isSolid == True:
            self.hitbox = self.rect
        
    def set_img(self):                                                                                          
        self.image = pygame.image.load(f"gfx/assets/trees/tree{self.rand}.png").convert_alpha()  
                ## Sets image attribute by loading image from gfx/world_assets/ folder based on asset_type
        self.rect = self.image.get_rect(bottomleft=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)
    
    def update(self):   ## Update method (Empty on default, wont be on certain types)                                                                                
       self.hitbox = self.rect.inflate(-125, -125)
       self.hitbox = self.hitbox.move(0, 63)