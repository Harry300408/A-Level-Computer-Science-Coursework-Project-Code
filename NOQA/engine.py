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
        self.show_hitboxes: bool = False
        self.f_cooldown: float = 0
    
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

        self.world:        pygame.sprite.Group     =   pygame.sprite.Group()
        self.render_items: pygame.sprite.Group     =   pygame.sprite.Group()
        
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

        Tile([self.world, self.floor_tiles, self.Static_Items], (250, 300))
        Asset([self.world, self.assets, self.Static_Items, self.render_items], (175, 100), True, "scenery", False)
        Asset([self.world, self.assets, self.Static_Items, self.render_items], (125, 75), True, "scenery", False)
        Liquid([self.world, self.floor_tiles, self.Static_Items], (100, 200))
        
        CC([self.player, self.render_items])
        
        

    def render(self):
        self.render_items = sorted(self.render_items, key=operator.attrgetter("hitbox.bottom"))
   
        for i in self.floor_tiles:
            self.screen.blit(i.image, (i.rect.x, i.rect.y))

        for i in self.render_items:
            self.screen.blit(i.image, (i.rect.x, i.rect.y))
        
        
        if self.debug == True:
            debug404(

                [
                    f"ALONE: No Rescue | vDev-Kit 0.1 pre-Alpha", 
                    f"FPS: {int(self.clock.get_fps())}", 
                    f"Cursor XY: {self.cusror.location[0]} / {self.cusror.location[1]}",
                    f"Player State: {self.player.sprites()[0].state}", 
                    f"Player Direction: {self.player.sprites()[0].direction}", 
                    f"Player Attack Cooldown: {round(self.player.sprites()[0].attack_cooldown, 2)}",
                    f"Func Cooldown: {self.f_cooldown}",
                    f"Show Hitboxes: {self.show_hitboxes}"
                ]
                
                )
        
        if self.show_hitboxes == True:
            for i in self.render_items:
                try:
                    pygame.draw.rect(self.screen, (255, 0, 0), i.hitbox, 1)
                    pygame.draw.rect(self.screen, (0, 0, 255), i.attack_box, 1)
                except:
                    pass
        
        self.cusror.draw()
            
        
    def game_updates(self):
        self.cusror.update()
        
        self.f_cooldown -= 0.05
        if self.f_cooldown < 0:
            self.f_cooldown = 0
        
        keys = pygame.key.get_pressed()
        
        ## DEBUG KEYS ##
        if keys[pygame.K_F1] and self.f_cooldown <= 0:
            self.debug = not self.debug
            self.f_cooldown = 1
        
        if keys[pygame.K_F2] and self.f_cooldown <= 0:
            self.show_hitboxes = not self.show_hitboxes
            self.f_cooldown = 1
        
        if keys[pygame.K_F3] and self.f_cooldown <= 0:
            count = 0
            
            for path in os.listdir("screenshots/"):
                if os.path.isfile(os.path.join("screenshots/", path)):
                    count += 1
                    
            pygame.image.save(self.screen, f"screenshots/screenshot{count}.png")
            self.f_cooldown = 1
        
        
        
        ## NON DEBUG KEYS ##
        if not self.player.sprites()[0].state in ["hit", "death"] and \
            not self.player.sprites()[0].attack_cooldown > 0:
                
            if keys[pygame.K_w]:
                for i in self.world:
                    i.rect.y += 5
                
            elif keys[pygame.K_s]:
                for i in self.world:
                    i.rect.y -= 5
                
            elif keys[pygame.K_a]:
                for i in self.world:
                    i.rect.x += 5
                
            elif keys[pygame.K_d]:
                for i in self.world:
                    i.rect.x -= 5
        
        self.player.update()
        
        for i in self.world:
            try:
                if i.hitbox.colliderect(self.player.sprites()[0].hitbox) and i._isSolid == True:
                    if self.player.sprites()[0].direction == "up":
                        for j in self.world:
                            j.rect.y -= 5
                    elif self.player.sprites()[0].direction == "down":
                        for j in self.world:
                            j.rect.y += 5
                    elif self.player.sprites()[0].direction == "left":
                        for j in self.world:
                            j.rect.x -= 5
                    elif self.player.sprites()[0].direction == "right":
                        for j in self.world:
                            j.rect.x += 5
            except:
                pass
            
            i.update()

    def run(self):
        self.screen.fill("green")

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

        self.render()
        
        self.game_updates()