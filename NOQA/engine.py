import os
import json
import sys
import random
import pygame
import operator

from screeninfo import get_monitors

import pygame_widgets
from pygame_widgets.dropdown import Dropdown

from NOQA.tiles.base_tile import *
from NOQA.tiles.liquid.base_liquid import *
from NOQA.tiles.terrain.grassland import *

from NOQA.assets.base_asset import *
from NOQA.assets.trees.L_Tree import *

from NOQA.player.CC import *

from NOQA.ui.mouse.mouse import *
from NOQA.ui.buttons._base_button import *
from NOQA.ui.switch._base_switch import *
from NOQA.ui.slider._base_slider import *
from NOQA.debug404.debug import debug404

from NOQA.world_generation.world_gen import generate_world_data


class engine:
    def __init__(self, configs, LANG):
        self.XRes: int = int(configs[0])
        self.YRes: int = int(configs[1])
        self.FULLSCREEN = configs[2]
        self.FPS: int = int(configs[3])
        self.dt: float = 0

        self.current_language = LANG

        self.debug: bool = True
        self.show_hitboxes: bool = True
        self.f_cooldown: float = 0

        pygame.init()

        self.screen: pygame.Surface = pygame.display.set_mode((self.XRes, self.YRes))
        pygame.display.set_caption("ALONE: No Rescue | vDev-Kit")
        pygame.display.set_icon(pygame.image.load("gfx/icon/icon.png"))

        if str(self.FULLSCREEN) == "True" or self.FULLSCREEN is True:
            self.FULLSCREEN = True
            pygame.display.toggle_fullscreen()
        else:
            self.FULLSCREEN = False

        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.cusror: mouse = mouse()

        self.tile_size: int = 32

        # Camera now controls world view instead of moving every sprite.
        self.cameraX: float = 0
        self.cameraY: float = 0

        self.screen_width = self.XRes
        self.screen_height = self.YRes

        self.world: pygame.sprite.Group = pygame.sprite.Group()
        self.render_items: pygame.sprite.Group = pygame.sprite.Group()

        self.player: pygame.sprite.Group = pygame.sprite.Group()
        self.floor_tiles: pygame.sprite.Group = pygame.sprite.Group()

        self.assets: pygame.sprite.Group = pygame.sprite.Group()
        self.resources: pygame.sprite.Group = pygame.sprite.Group()
        self.scenery: pygame.sprite.Group = pygame.sprite.Group()

        self.AI: pygame.sprite.Group = pygame.sprite.Group()
        self.friendlyAI: pygame.sprite.Group = pygame.sprite.Group()
        self.enemiesAI: pygame.sprite.Group = pygame.sprite.Group()
        self.Static_Items: pygame.sprite.Group = pygame.sprite.Group()
        self.NonStatic_Items: pygame.sprite.Group = pygame.sprite.Group()

        # Fast lookup for nearby tile collision checks
        self.tile_lookup = {}

        ## GAME STATE ##
        self.menu_state = "start_menu"

        ## MENU BGs ##
        self.Bgs = []
        directory = "gfx/menubgs/"
        for filename in os.listdir(directory):
            if filename.endswith(".png"):
                self.Bgs.append(
                    pygame.image.load(os.path.join(directory, filename)).convert_alpha()
                )

        ## TITLE TEXT ##
        self.title_text_font = pygame.font.Font("gfx/fonts/ui/alagard.ttf", 70)
        self.title_txt = self.title_text_font.render("ALONE: No Rescue", True, "white")
        self.title_txt_rect = self.title_txt.get_rect(center=(self.XRes / 2, 50))

        self.title_text_font_outline = pygame.font.Font("gfx/fonts/ui/alagard.ttf", 70)
        self.title_txt_outline = self.title_text_font_outline.render(
            "ALONE: No Rescue", True, "black"
        )
        self.title_txt_rect_outline = self.title_txt_outline.get_rect(
            center=((self.XRes / 2) + 5, 50)
        )

        self.play_button = Button(
            (self.XRes / 2, (self.YRes / 2) - 70),
            "gfx/ui/menus/button/button_bg.png",
            "gfx/ui/menus/button/button_pressed.png",
            "Play Game",
            32,
            (255, 255, 255),
            (255, 255, 0),
            "play_button",
            "Chose whether to start a new game or load a previous save.",
        )

        self.newgame_button = Button(
            ((self.XRes / 2) - 130, (self.YRes / 2) - 70),
            "gfx/ui/menus/button/button_bg.png",
            "gfx/ui/menus/button/button_pressed.png",
            "New Game",
            32,
            (255, 255, 255),
            (255, 255, 0),
            "newgame_button",
            "Start a new game.",
        )
        self.loadgame_button = Button(
            ((self.XRes / 2) + 130, (self.YRes / 2) - 70),
            "gfx/ui/menus/button/button_bg.png",
            "gfx/ui/menus/button/button_pressed.png",
            "Load Game",
            32,
            (255, 255, 255),
            (255, 255, 0),
            "loadgame_button",
            "Load a save game.",
        )
        self.new_load = False

        self.settings_button = Button(
            (self.XRes / 2, (self.YRes / 2)),
            "gfx/ui/menus/button/button_bg.png",
            "gfx/ui/menus/button/button_pressed.png",
            "Settings",
            32,
            (255, 255, 255),
            (255, 255, 0),
            "settings_button",
            "Change game settings",
        )

        self.exit_button = Button(
            (self.XRes / 2, (self.YRes / 2) + 70),
            "gfx/ui/menus/button/button_bg.png",
            "gfx/ui/menus/button/button_pressed.png",
            "Exit Game",
            32,
            (255, 255, 255),
            (255, 255, 0),
            "exit_button",
            "Exit the game",
        )

        self.mm_buttons = [self.exit_button, self.settings_button, self.play_button]
        self.new_load_buttons = [self.newgame_button, self.loadgame_button]

        self.settings_back_button = Button(
            (150, self.YRes - 50),
            "gfx/ui/menus/button/button_bg.png",
            "gfx/ui/menus/button/button_pressed.png",
            "Back & Apply Settings",
            32,
            (255, 255, 255),
            (255, 255, 0),
            "settings_back_button",
            "Return to the start menu.",
        )

        self.screens = get_monitors()
        self.primary_screen = None
        for i in self.screens:
            if i.is_primary:
                self.primary_screen = i
                break

        if self.primary_screen is None:
            self.primary_screen = self.screens[0]

        self.resolution = Dropdown(
            self.screen,
            (self.XRes / 2) - 187.5,
            (self.YRes / 2) - 200,
            250,
            50,
            name=f"Current: {self.XRes}x{self.YRes}",
            choices=[
                "1280x720",
                "1920x1080",
                "2560x1440",
                f"Screen Resolution: {self.primary_screen.width}x{self.primary_screen.height}",
            ],
            borderRadius=3,
            colour=pygame.Color("#671E1EFF"),
            values=[
                (1280, 720),
                (1920, 1080),
                (2560, 1440),
                (self.primary_screen.width, self.primary_screen.height),
            ],
            direction="down",
            textHAlign="centre",
            textColour=pygame.Color("white"),
            hoverColour=pygame.Color("#AE2424FF"),
            font=pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", 30),
        )

        self.language = Dropdown(
            self.screen,
            (self.XRes / 2) - 62.5,
            (self.YRes / 2) - 125,
            250,
            50,
            name=f"Current: {self.current_language}",
            choices=["English", "French (Français)"],
            borderRadius=3,
            colour=pygame.Color("#671E1EFF"),
            values=["en", "fr"],
            direction="down",
            textHAlign="centre",
            textColour=pygame.Color("white"),
            hoverColour=pygame.Color("#AE2424FF"),
            font=pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", 30),
        )

        self.vol_slider = Slider(
            ((self.XRes / 2) - 62.5, (self.YRes / 2) - 35),
            (250, 30),
            0.1,
            0,
            100,
        )

        self.sfx_slider = Slider(
            ((self.XRes / 2) + 62.5, (self.YRes / 2) + 20),
            (250, 30),
            0.1,
            0,
            100,
        )

        self.fullscreen_TF = switcher(
            (self.XRes - 28, self.YRes - 28),
            "gfx/ui/menus/switcher/switcher_off.png",
            "gfx/ui/menus/switcher/switcher_on.png",
            self.FULLSCREEN,
            "Toggle Fullscreen Mode",
        )

        self.settings_font = pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", 50)

        self.fullscreen_txt = self.settings_font.render("Fullscreen Mode", True, "white")
        self.fullscreen_txt_rect = self.fullscreen_txt.get_rect(
            bottomright=(self.XRes - 50, self.YRes - 2)
        )

        self.settings_buttons = [self.settings_back_button]
        self.settings_switches = [self.fullscreen_TF]
        self.settings_sliders = [self.vol_slider, self.sfx_slider]

        self.resolution.hide()
        self.language.hide()

        self.resolution_txt = self.settings_font.render("Resolution", True, "white")
        self.resolution_txt_rect = self.resolution_txt.get_rect(
            center=(self.XRes / 2 + 150, self.YRes / 2 - 175)
        )

        self.language_txt = self.settings_font.render("Language", True, "white")
        self.language_txt_rect = self.language_txt.get_rect(
            center=(self.XRes / 2 - 150, self.YRes / 2 - 105)
        )

        self.sfx_txt = self.settings_font.render("SFX", True, "white")
        self.sfx_txt_rect = self.sfx_txt.get_rect(
            center=(self.XRes / 2 + 120, self.YRes / 2 - 37)
        )

        self.music_txt = self.settings_font.render("Music", True, "white")
        self.music_txt_rect = self.music_txt.get_rect(
            center=(self.XRes / 2 - 120, self.YRes / 2 + 17)
        )

        count = 0
        for bg in self.Bgs:
            bg = pygame.transform.scale(bg, (self.XRes, self.YRes))
            self.Bgs[count] = bg
            count += 1

        self.bgrect = self.Bgs[0].get_rect(topleft=(0, 0))
        self.slide_num = random.randint(0, len(self.Bgs) - 1)

        self.create_new_world_data()

        # Create player after world
        CC([self.player, self.render_items])

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def get_player_sprite(self):
        sprites = self.player.sprites()
        return sprites[0] if sprites else None

    def get_player_world_hitbox(self):
        """
        Player is treated as screen-centred / screen-space.
        Convert its hitbox into world-space by offsetting with camera.
        """
        player = self.get_player_sprite()
        if player is None:
            return None

        if hasattr(player, "hitbox"):
            return player.hitbox.move(self.cameraX, self.cameraY)

        return player.rect.move(self.cameraX, self.cameraY)

    def get_world_view_rect(self):
        return pygame.Rect(self.cameraX, self.cameraY, self.screen_width, self.screen_height)

    def get_nearby_tiles(self, world_x, world_y, radius=2):
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)

        nearby = []
        for y in range(tile_y - radius, tile_y + radius + 1):
            for x in range(tile_x - radius, tile_x + radius + 1):
                tile = self.tile_lookup.get((x, y))
                if tile is not None:
                    nearby.append(tile)
        return nearby

    def can_move_to(self, new_camera_x, new_camera_y):
        """
        Checks solid collisions near the player only.
        """
        player = self.get_player_sprite()
        if player is None:
            return True

        if hasattr(player, "hitbox"):
            future_player_hitbox = player.hitbox.move(new_camera_x, new_camera_y)
            center_x = future_player_hitbox.centerx
            center_y = future_player_hitbox.centery
        else:
            future_player_hitbox = player.rect.move(new_camera_x, new_camera_y)
            center_x = future_player_hitbox.centerx
            center_y = future_player_hitbox.centery

        nearby_tiles = self.get_nearby_tiles(center_x, center_y, radius=2)

        for tile in nearby_tiles:
            try:
                tile_hitbox = tile.hitbox if hasattr(tile, "hitbox") else tile.rect
                if getattr(tile, "_isSolid", False) and tile_hitbox.colliderect(future_player_hitbox):
                    return False
            except:
                pass

        return True

    # --------------------------------------------------
    # MENUS
    # --------------------------------------------------

    def main_menu(self):
        self.slide_num += 0.001
        self.screen.blit(self.Bgs[int(self.slide_num) % len(self.Bgs)], self.bgrect)
        self.screen.blit(self.title_txt_outline, self.title_txt_rect_outline)
        self.screen.blit(self.title_txt, self.title_txt_rect)

        events = pygame.event.get()

        for event in events:
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
                            if self.play_button in self.mm_buttons:
                                self.mm_buttons.remove(self.play_button)

                        if i.type == "settings_button":
                            self.menu_state = "settings_menu"
                            self.resolution.show()
                            self.language.show()

                for i in self.new_load_buttons:
                    if i.check_for_update():
                        if i.type == "newgame_button":
                            self.menu_state = "game"

                        if i.type == "loadgame_button":
                            pass

        for i in self.mm_buttons:
            i.update()

        if self.new_load:
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

        self.screen.blit(self.resolution_txt, self.resolution_txt_rect)
        self.screen.blit(self.language_txt, self.language_txt_rect)
        self.screen.blit(self.sfx_txt, self.sfx_txt_rect)
        self.screen.blit(self.music_txt, self.music_txt_rect)
        self.screen.blit(self.fullscreen_txt, self.fullscreen_txt_rect)

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in self.settings_buttons:
                    if i.check_for_update():
                        if i.type == "settings_back_button":
                            self.menu_state = "start_menu"

                            if self.new_load and self.play_button not in self.mm_buttons:
                                self.mm_buttons.insert(2, self.play_button)

                            self.new_load = False
                            self.resolution.hide()
                            self.language.hide()

                for i in self.settings_switches:
                    if i.check_for_update():
                        i.state = not i.state

        for i in self.settings_buttons:
            i.update()

        for i in self.settings_switches:
            i.update()

        for i in self.settings_sliders:
            i.update(self.screen)

        pygame_widgets.update(events)

        self.cusror.update()
        self.cusror.draw()

    # --------------------------------------------------
    # WORLD
    # --------------------------------------------------

    def create_new_world_data(self):
        world_data, obj_data = generate_world_data()

        with open(
            "NOQA/world_generation/configs/world_gen_configs.json",
            "r",
            encoding="utf-8",
        ) as f:
            configs = json.load(f)

        width_offset = configs["window"]["width"] * self.tile_size / 2
        height_offset = configs["window"]["height"] * self.tile_size / 2

        self.tile_lookup.clear()

        for row in world_data:
            for j in row:
                world_x = (j["pos"][0] * self.tile_size) - width_offset
                world_y = (j["pos"][1] * self.tile_size) - height_offset

                if j["type"] == "grassland":
                    tile = Grassland(
                        [self.floor_tiles, self.world],
                        (world_x, world_y),
                    )
                    self.tile_lookup[(j["pos"][0], j["pos"][1])] = tile

        # Start camera roughly centred on world origin
        self.cameraX = -self.screen_width // 2
        self.cameraY = -self.screen_height // 2

    # --------------------------------------------------
    # RENDERING
    # --------------------------------------------------

    def render(self):
        self.screen.fill("black")

        view_rect = self.get_world_view_rect()
        cull_rect = view_rect.inflate(self.tile_size * 2, self.tile_size * 2)

        visible_sprites = []

        player = self.get_player_sprite()

        # Floor first
        for sprite in self.floor_tiles:
            if sprite.rect.colliderect(cull_rect):
                draw_pos = (
                    sprite.rect.x - self.cameraX,
                    sprite.rect.y - self.cameraY,
                )
                visible_sprites.append((sprite.image, draw_pos))

        # Only world-space render items here
        world_render_items = [s for s in self.render_items if s != player]

        sorted_render_items = sorted(
            world_render_items,
            key=lambda spr: getattr(getattr(spr, "hitbox", spr.rect), "bottom", spr.rect.bottom),
        )

        for sprite in sorted_render_items:
            if sprite.rect.colliderect(cull_rect):
                draw_pos = (
                    sprite.rect.x - self.cameraX,
                    sprite.rect.y - self.cameraY,
                )
                visible_sprites.append((sprite.image, draw_pos))

        if visible_sprites:
            self.screen.blits(visible_sprites)

        # Draw player separately in screen-space
        if player is not None:
            self.screen.blit(player.image, player.rect.topleft)

        if self.debug and player is not None:
            debug404(
                [
                    "ALONE: No Rescue | vDev-Kit 0.1 pre-Alpha",
                    f"FPS: {int(self.clock.get_fps())}",
                    f"Cursor XY: {self.cusror.location[0]} / {self.cusror.location[1]}",
                    f"Camera XY: {round(self.cameraX, 2)} / {round(self.cameraY, 2)}",
                    f"Visible Sprites: {len(visible_sprites)}",
                    f"Player State: {getattr(player, 'state', 'N/A')}",
                    f"Player Direction: {getattr(player, 'direction', 'N/A')}",
                    f"Player Held Item: {getattr(player, 'held_item', 'N/A')}",
                    f"Player Attack Cooldown: {round(getattr(player, 'attack_cooldown', 0), 2)}",
                    f"Func Cooldown: {self.f_cooldown}",
                    f"Show Hitboxes: {self.show_hitboxes}",
                ]
            )

        if self.show_hitboxes:
            for sprite in sorted_render_items:
                if sprite.rect.colliderect(cull_rect):
                    try:
                        hitbox = sprite.hitbox.move(-self.cameraX, -self.cameraY)
                        pygame.draw.rect(self.screen, (255, 0, 0), hitbox, 1)
                    except Exception:
                        pass

                    try:
                        attack_box = sprite.attack_box.move(-self.cameraX, -self.cameraY)
                        pygame.draw.rect(self.screen, (0, 0, 255), attack_box, 1)
                    except Exception:
                        pass

            if player is not None:
                try:
                    pygame.draw.rect(self.screen, (0, 255, 0), player.hitbox, 1)
                except Exception:
                    pass

        self.cusror.draw()

    # --------------------------------------------------
    # GAME LOGIC
    # --------------------------------------------------

    def game_updates(self):
        self.cusror.update()

        self.f_cooldown -= 0.05
        if self.f_cooldown < 0:
            self.f_cooldown = 0

        player = self.get_player_sprite()
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
            os.makedirs("screenshots", exist_ok=True)
            for path in os.listdir("screenshots/"):
                if os.path.isfile(os.path.join("screenshots/", path)):
                    count += 1

            pygame.image.save(self.screen, f"screenshots/screenshot{count}.png")
            self.f_cooldown = 1

        # Update dynamic entities only.
        # Do not update every floor tile; that is expensive and usually unnecessary.
        player = self.get_player_sprite()

        for sprite in self.render_items:
            if sprite != player:
                try:
                    sprite.update()
                except Exception:
                    pass

        self.player.update()

        self.player.update()

        if player is None:
            return

        ## NON DEBUG KEYS ##
        move_x = 0
        move_y = 0
        speed = 5

        player = self.get_player_sprite()

        if player and player.state not in ["hit", "death"] and player.attack_cooldown <= 0:

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                move_y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move_y += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x += 1

            # Normalize diagonal movement
            if move_x != 0 or move_y != 0:
                length = (move_x ** 2 + move_y ** 2) ** 0.5
                move_x = (move_x / length) * speed
                move_y = (move_y / length) * speed

                new_camera_x = self.cameraX + move_x
                new_camera_y = self.cameraY + move_y

                if self.can_move_to(new_camera_x, new_camera_y):
                    self.cameraX = new_camera_x
                    self.cameraY = new_camera_y

    # --------------------------------------------------
    # MAIN LOOP STEP
    # --------------------------------------------------


    def run(self):
        self.screen.fill("black")

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.game_updates()
        self.render()
