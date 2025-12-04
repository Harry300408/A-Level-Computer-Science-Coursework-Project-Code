import pygame

class Tile(pygame.sprite.Sprite):                                                                              
    def __init__(self, groups, pos: tuple, _tile_type: str = "default"):                                                                 
        super().__init__(groups)                                                                                
        self.pos: tuple = pos                      ## Position as (x, y) tuple                                                                            
        self._tile_type: str = _tile_type          ## Type of tile (string)     
        self._ID: str = f"t{pos[0]} {pos[1]}"     ## Unique tile ID based on position
                                                
        self.set_img()                      ## References set_img method to load image and set rect 
                                            ## (will be used for sprites with multiple frames)                                                                           
        
    def set_img(self):                                                                                          
        self.image: pygame.Surface = pygame.image.load(f"gfx/tiles/{self._tile_type}.png").convert_alpha()  
                ## Sets image attribute by loading image from gfx/tiles/ folder based on tile_type

        self.rect: pygame.Rect = self.image.get_rect(topleft=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)
    
    def update(self):   ## Update method (Empty on default, wont be on certain types)                                                                                
       pass                                                                                                     