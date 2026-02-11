from re import S
import sys, pygame, operator, bisect

from NOQA.tiles.base_tile import *
from NOQA.tiles.liquid.base_liquid import *

from NOQA.assets.base_asset import *
from NOQA.assets.trees.L_Tree import *

from NOQA.player.CC import *

from NOQA.ui.mouse.mouse import *
from NOQA.ui.buttons._base_button import *
from NOQA.ui.switch._base_switch import *
from NOQA.ui.slider._base_slider import *
from NOQA.debug404.debug import debug404

class engine():
    def __init__(self, configs, LANG):
        self.XRes:  int     =   configs[0]
        self.YRes:  int     =   configs[1]
        self.FPS:   int     =   configs[3]
        self.dt:  float     =   0
        
        self.debug:         bool    =   True
        self.show_hitboxes: bool    =   True
        self.f_cooldown:    float   =   0
    
        pygame.init()

        self.screen: pygame.Surface = pygame.display.set_mode((self.XRes, self.YRes))
        pygame.display.set_caption("ALONE: No Rescue | vDev-Kit")
        pygame.display.set_icon(pygame.image.load("gfx/icon/icon.png"))

        if configs[2] == "True":
            self.FULLSCREEN: bool = configs[2]
            pygame.display.toggle_fullscreen()

        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.cusror: mouse = mouse()

        self.tile_size: int = 32

        self.cameraX: float = 0
        self.cameraY: float = 0

        self.world:             pygame.sprite.Group     =   pygame.sprite.Group()
        self.render_items:      pygame.sprite.Group     =   pygame.sprite.Group()
        
        self.player:            pygame.sprite.Group     =   pygame.sprite.Group()
        self.floor_tiles:       pygame.sprite.Group     =   pygame.sprite.Group()

        self.assets:            pygame.sprite.Group     =   pygame.sprite.Group()
        self.resources:         pygame.sprite.Group     =   pygame.sprite.Group()
        self.scenery:           pygame.sprite.Group     =   pygame.sprite.Group()
        
        self.AI:                pygame.sprite.Group     =   pygame.sprite.Group()
        self.friendlyAI:        pygame.sprite.Group     =   pygame.sprite.Group()
        self.enemiesAI:         pygame.sprite.Group     =   pygame.sprite.Group()
        self.Static_Items:      pygame.sprite.Group     =   pygame.sprite.Group()
        self.NonStatic_Items:   pygame.sprite.Group     =   pygame.sprite.Group()
        
        ## GAME STATE ##
        self.menu_state = "start_menu"
        
        ## MENU BGs  ##
        self.Bgs = []
        directory = 'gfx/menubgs/'
        for filename in os.listdir(directory):
            if filename.endswith('.png'):
                self.Bgs.append(pygame.image.load(os.path.join(directory, filename)).convert_alpha())

        ## MENU ITEMS ##

        ## TITLE TEXT ##
        self.title_text_font       = pygame.font.Font("gfx/fonts/ui/alagard.ttf", 70)
        self.title_txt             = self.title_text_font.render("ALONE: No Rescue", True, "white")
        self.title_txt_rect        = self.title_txt.get_rect(center=(self.XRes / 2, 50))

        self.title_text_font_outline       = pygame.font.Font("gfx/fonts/ui/alagard.ttf", 70)
        self.title_txt_outline             = self.title_text_font_outline.render("ALONE: No Rescue", True, "black")
        self.title_txt_rect_outline        = self.title_txt_outline.get_rect(center=((self.XRes / 2) + 5, 50))

        self.play_button = Button((self.XRes / 2, (self.YRes / 2) - 70), 'gfx/ui/menus/button/button_bg.png', 'gfx/ui/menus/button/button_pressed.png', "Play Game", 32, (255, 255, 255), (255, 255, 0), "play_button", "Chose whether to start a new game or load a previous save.")
        
        self.newgame_button     =   Button(((self.XRes / 2) - 130, (self.YRes / 2) - 70), 'gfx/ui/menus/button/button_bg.png', 'gfx/ui/menus/button/button_pressed.png', "New Game", 32, (255, 255, 255), (255, 255, 0), "newgame_button", "Start a new game.")
        self.loadgame_button    =   Button(((self.XRes / 2) + 130, (self.YRes / 2) - 70), 'gfx/ui/menus/button/button_bg.png', 'gfx/ui/menus/button/button_pressed.png', "Load Game", 32, (255, 255, 255), (255, 255, 0), "loadgame_button", "Load a save game.")
        self.new_load           =   False
        
        self.settings_button = Button((self.XRes / 2, (self.YRes / 2)), 'gfx/ui/menus/button/button_bg.png', 'gfx/ui/menus/button/button_pressed.png', "Settings", 32, (255, 255, 255), (255, 255, 0), "settings_button", "Change game settings")

        self.exit_button = Button((self.XRes / 2, (self.YRes / 2) + 70), 'gfx/ui/menus/button/button_bg.png', 'gfx/ui/menus/button/button_pressed.png', "Exit Game", 32, (255, 255, 255), (255, 255, 0), "exit_button", "Exit the game")

        self.mm_buttons = [self.exit_button, self.settings_button, self.play_button]
        self.new_load_buttons = [self.loadgame_button, self.newgame_button]
        
        self.settings_back_button = Button((150, self.YRes - 50), 'gfx/ui/menus/button/button_bg.png', 'gfx/ui/menus/button/button_pressed.png', "Back", 32, (255, 255, 255), (255, 255, 0), "settings_back_button", "Return to the start menu.")
        
        self.settings_buttons = [self.settings_back_button]
        
        count = 0
        for i in self.Bgs:
            i = pygame.transform.scale(i, (self.XRes, self.YRes))
            self.Bgs[ count ] = i
            count += 1
        
        self.bgrect = self.Bgs[0].get_rect(topleft = (0, 0))
        self.slide_num = random.randint(0, len(self.Bgs) - 1)
        
        Tile([self.world, self.floor_tiles, self.Static_Items], (250, 300))
        Asset([self.world, self.assets, self.Static_Items, self.render_items], (175, 100), True, "scenery", False)
        Asset([self.world, self.assets, self.Static_Items, self.render_items], (125, 75), True, "scenery", False)
        Liquid([self.world, self.floor_tiles, self.Static_Items], (100, 200))
        
        LTree([self.world, self.assets, self.Static_Items, self.render_items], (300, 300))
        
        CC([self.player, self.render_items])
        
    def main_menu(self):
        self.slide_num += 0.001
        self.screen.blit(self.Bgs[int(self.slide_num) % len(self.Bgs)], self.bgrect)
        self.screen.blit(self.title_txt_outline, self.title_txt_rect_outline)
        self.screen.blit(self.title_txt, self.title_txt_rect)
        
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()
        
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in self.mm_buttons:
                    if i.check_for_update():
                        if i.type == "exit_button":
                             pygame.quit()
                             sys.exit()

                        if i.type == "play_button":
                            self.new_load = True
                            self.mm_buttons.pop(2)
                        
                        if i.type == "settings_button":
                            self.menu_state = "settings_menu"
                            
                for i in self.new_load_buttons:
                    if i.check_for_update():
                        if i.type == "newgame_button":
                            self.menu_state = "game"
                        
                        if i.type == "loadgame_button":
                            pass

        for i in self.mm_buttons:
            i.update()
            
        if self.new_load == True:
            for i in self.new_load_buttons:
                i.update()
        
        self.cusror.update()
        self.cusror.draw()

    def new_game_menu(self):
        pass

    def load_game_menu(self):
        pass
    
    def settings_menu(self):
        self.slide_num += 0.001
        self.screen.blit(self.Bgs[int(self.slide_num) % len(self.Bgs)], self.bgrect)
        self.screen.blit(self.title_txt_outline, self.title_txt_rect_outline)
        self.screen.blit(self.title_txt, self.title_txt_rect)
        
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in self.settings_buttons:
                    if i.check_for_update():
                        if i.type == "settings_back_button":
                            self.menu_state = "start_menu"
                
        for i in self.settings_buttons:
            i.update()
        
        self.cusror.update()
        self.cusror.draw()


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
                    f"Player Held Item: {self.player.sprites()[0].held_item}",
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
                
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                for i in self.world:
                    i.rect.y += 5
                
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                for i in self.world:
                    i.rect.y -= 5
                
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                for i in self.world:
                    i.rect.x += 5
                
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                for i in self.world:
                    i.rect.x -= 5
        
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
        
        self.player.update()

    def run(self):
        self.screen.fill("green")

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.game_updates()
        self.render()