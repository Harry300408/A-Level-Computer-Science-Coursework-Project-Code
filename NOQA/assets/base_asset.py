import pygame

class Asset(pygame.sprite.Sprite):                                                                              
    def __init__(self, groups, pos, _isSolid, _obj_type, _interactable = False, _asset_type = "default"):                                                                 
        super().__init__(groups)                                                                                
        self.pos = pos                          ## Position as (x, y) tuple                                                                            
        self._asset_type = _asset_type          ## Type of asset (string)     
        self._isSolid = _isSolid                ## Whether the asset is solid (boolean)
        self._obj_type = _obj_type              ## Object type (e.g., "scenery", "resouce", etc.)
        self._interacterble = _interactable     ## Whether the asset is interactable (boolean | default = False)
        self._ID = f"a{pos[0]} {pos[1]}"        ## Unique asset ID based on position
                                                
        self.set_img()                      ## References set_img method to load image and set rect 
                                            ## (will be used for sprites with multiple frames)                                                                           
        
    def set_img(self):                                                                                          
        self.image = pygame.image.load(f"gfx/assets/{self.asset_type}.png").convert_alpha()  
                ## Sets image attribute by loading image from gfx/world_assets/ folder based on asset_type
        self.rect = self.image.get_rect(topleft=self.pos)     
                ## Sets rect attribute based on image and position 
                ## (mainly used for rendereing)
    
    def update(self):   ## Update method (Empty on default, wont be on certain types)                                                                                
       pass