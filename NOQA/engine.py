import sys, pygame, operator, bisect

from NOQA.tiles.base_tile import *
from NOQA.assets.base_asset import *
from NOQA.ui.mouse.mouse import *

class engine():
    def __init__(self, configs, LANG):
        self.XRes: int      =   configs[0]
        self.YRes: int      =   configs[1]
        self.FPS: int       =   configs[3]
        self.dt: float      =   0
    
        pygame.init()

        self.screen = pygame.display.set_mode((self.XRes, self.YRes))

        if configs[2] == "True":
            self.FULLSCREEN = configs[2]
            pygame.display.toggle_fullscreen()

        self.clock = pygame.time.Clock()

        self.cusror = mouse()

        self.tile_size = 32

        self.cameraX = 0
        self.cameraY = 0

        self.player = pygame.sprite.Group()
        self.floor_tiles = pygame.sprite.Group()

        self.assets = pygame.sprite.Group()
        self.resources = pygame.sprite.Group()
        self.scenery = pygame.sprite.Group()
        
        self.AI = pygame.sprite.Group()
        self.friendlyAI = pygame.sprite.Group()
        self.enemiesAI = pygame.sprite.Group()
        self.Static_Items = pygame.sprite.Group()
        self.NonStatic_Items = pygame.sprite.Group()

        Tile([self.floor_tiles, self.Static_Items], (0, 0)) # type: ignore
        Asset([self.assets, self.Static_Items], (0, 4), True, "scenery", False)
        Asset([self.assets, self.Static_Items], (0, 3), True, "scenery", False)

    def render(self):
        world_items = self.Static_Items.copy()
        world_items.add(self.NonStatic_Items)
        world_items = sorted(world_items, key=operator.attrgetter("pos"))

        self.screen.fill((0, 0, 0))

        for i in world_items:
            self.screen.blit(i.image, (i.rect.x - self.cameraX, i.rect.y - self.cameraY))

        self.cusror.update()


    def run(self):
        self.screen.fill((0, 0, 0))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

        self.render()