import sys, pygame
from NOQA.tiles.base_tile import *

class engine():
    def __init__(self, configs, LANG):
        self.XRes   =   configs[0]
        self.YRes   =   configs[1]
        self.FPS    =   configs[3]
        self.dt     =   0
    
        pygame.init()

        self.screen = pygame.display.set_mode((self.XRes, self.YRes))

        if configs[2] == "True":
            self.FULLSCREEN = configs[2]
            pygame.display.toggle_fullscreen()

        self.clock = pygame.time.Clock()

        self.tile_size = 32

        self.cameraX = 0
        self.cameraY = 0

        self.world_sprites = []

        self.player         =   pygame.sprite.Group()
        self.floor_tiles    =   pygame.sprite.Group()

        self.assets         =   pygame.sprite.Group()
        self.resources      =   pygame.sprite.Group()
        self.scenery        =   pygame.sprite.Group()
        
        self.ai             =   pygame.sprite.Group()
        self.friendlyAi     =   pygame.sprite.Group()
        self.enemiesAi      =   pygame.sprite.Group()

    def render(self):
        ## Boundries for 'visible'
        left_bound      =   self.cameraX            
        right_bound     =   self.cameraX + self.XRes
        top_bound       =   self.cameraY            
        bottom_bound    =   self.cameraY + self.YRes
        
        self.visible_sprites = []
        sprites = self.world_sprites.copy()
        
        for sprite in sprites:                                                                                        ## Loops through sprites in group
            sprite_x, sprite_y = sprite.rect.topleft                                                                            ## Gets sprite position

            # Check if tile is within the visible area
            if left_bound - self.tile_size < sprite_x < right_bound and top_bound - self.tile_size < sprite_y < bottom_bound:   ## Fancy calculation to see if it's in view
                self.visible_sprites.append((sprite.image, (sprite_x - self.cameraX, sprite_y - self.cameraY)))                              ## If it's in view it will draw to screen
        

    def run(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()