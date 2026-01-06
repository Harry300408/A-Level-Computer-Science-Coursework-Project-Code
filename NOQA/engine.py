import sys, pygame, operator, bisect

from NOQA.tiles.base_tile import *
from NOQA.tiles.liquid.base_liquid import *

from NOQA.assets.base_asset import *
from NOQA.player.CC import *

from NOQA.ui.mouse.mouse import *
from NOQA.debug404.debug import debug404

class engine():
    def __init__(self, configs, LANG):
        self.XRes:  int     =   configs[0]
        self.YRes:  int     =   configs[1]
        self.FPS:   int     =   configs[3]
        self.dt:  float     =   0
        
        self.debug: bool    =   True
    
        pygame.init()

        self.screen: pygame.Surface = pygame.display.set_mode((self.XRes, self.YRes))
        pygame.display.set_caption("ALONE:No Rescue | vDev-Kit")

        if configs[2] == "True":
            self.FULLSCREEN: bool = configs[2]
            pygame.display.toggle_fullscreen()

        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.cusror: mouse = mouse()

        self.tile_size: int = 32

        self.cameraX: float = 0
        self.cameraY: float = 0

        self.player:        pygame.sprite.Group     =   pygame.sprite.Group()
        self.floor_tiles:   pygame.sprite.Group     =   pygame.sprite.Group()

        self.assets:    pygame.sprite.Group     =   pygame.sprite.Group()
        self.resources: pygame.sprite.Group     =   pygame.sprite.Group()
        self.scenery:   pygame.sprite.Group     =   pygame.sprite.Group()
        
        self.AI:                pygame.sprite.Group     =   pygame.sprite.Group()
        self.friendlyAI:        pygame.sprite.Group     =   pygame.sprite.Group()
        self.enemiesAI:         pygame.sprite.Group     =   pygame.sprite.Group()
        self.Static_Items:      pygame.sprite.Group     =   pygame.sprite.Group()
        self.NonStatic_Items:   pygame.sprite.Group     =   pygame.sprite.Group()

        Tile([self.floor_tiles, self.Static_Items], (250, 300))
        Asset([self.assets, self.Static_Items], (175, 100), True, "scenery", False)
        Asset([self.assets, self.Static_Items], (125, 75), True, "scenery", False)
        Liquid([self.floor_tiles, self.Static_Items], (100, 200))
        
        #CC([self.player, self.NonStatic_Items], 0, 0)
        
        

    def render(self):
            
            
        world_items = self.Static_Items.copy()
        world_items.add(self.NonStatic_Items)
        
        world_items = sorted(world_items, key=operator.attrgetter("pos"))

        self.screen.fill((0, 0, 0))

        for i in world_items:
            self.screen.blit(i.image, (i.rect.x - self.cameraX, i.rect.y - self.cameraY))
        
        if self.debug == True:
            debug404(

                [
                    f"ALONE: No Rescue | vDev-Kit 0.1 pre-Alpha", 
                    f"FPS: {int(self.clock.get_fps())}", 
                    f"Delta Time (Δt): {self.dt}", 
                    f"Cursor XY: {self.cusror.location[0]} / {self.cusror.location[1]}"
                ]
                
                )
            
        self.cusror.update()


    def run(self):
        self.screen.fill((0, 0, 0))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

        self.render()