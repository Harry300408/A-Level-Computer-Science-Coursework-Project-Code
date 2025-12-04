import sys, pygame, operator, bisect

from NOQA.tiles.base_tile import *
from NOQA.tiles.liquid.base_liquid import *

from NOQA.assets.base_asset import *

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

        Tile([self.floor_tiles, self.Static_Items], (50, 0))
        Asset([self.assets, self.Static_Items], (75, 4), True, "scenery", False)
        Asset([self.assets, self.Static_Items], (125, 3), True, "scenery", False)
        Liquid([self.floor_tiles, self.Static_Items], (100, 100))
        
        

    def render(self):
        if self.debug == True:
            pygame.display.set_caption(f"NOQA | FPS: {int(self.clock.get_fps())} | DT: {self.dt}")
            
            
        world_items = self.Static_Items.copy()
        world_items.add(self.NonStatic_Items)
        
        world_items = sorted(world_items, key=operator.attrgetter("pos"))

        self.screen.fill((0, 0, 0))

        for i in world_items:
            self.screen.blit(i.image, (i.rect.x - self.cameraX, i.rect.y - self.cameraY))

        debug404([f"FPS: {int(self.clock.get_fps())}", f"DT: {self.dt}"])

        self.cusror.update()


    def run(self):
        self.screen.fill((0, 0, 0))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

        self.render()