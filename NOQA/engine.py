import os
import json
from re import I
import sys
import random
import pygame
import operator

import heapq

from NOQA.entities.friendly.base_friendly import FriendlyAI
from NOQA.entities.enemy.base_enemy import EnemyAI

from screeninfo import get_monitors

import pygame_widgets
from pygame_widgets.dropdown import Dropdown

from NOQA.tiles.base_tile import *
from NOQA.tiles.terrain.grassland import Grassland
from NOQA.tiles.terrain.beach import Beach
from NOQA.tiles.terrain.forest import Forest
from NOQA.tiles.terrain.swamp import Swamp
from NOQA.tiles.terrain.savanna import Savanna
from NOQA.tiles.terrain.desert import Desert
from NOQA.tiles.terrain.hill import Hill
from NOQA.tiles.terrain.mountain import Mountain
from NOQA.tiles.terrain.snow import Snow

from NOQA.tiles.liquid.base_liquid import *
from NOQA.tiles.liquid.deep_water import Deep_Water
from NOQA.tiles.liquid.shallow_water import Shallow_Water

from NOQA.assets.base_asset import *
from NOQA.assets.trees.L_Tree import L_Tree
from NOQA.assets.grass.grass import Grass
from NOQA.assets.cactus.cactus import Cactus
from NOQA.assets.bushes.bushes import Bushes
from NOQA.assets.stone.stone import Stone
from NOQA.assets.iron.iron import Iron
from NOQA.assets.coal import Coal

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
        self.debug_draw_mode: int = 0
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

        self.water_anim_timer = 0.0
        self.water_anim_frame = 0
        self.water_anim_speed = 0.5

        self.chunk_size = 10

        self.floor_chunks = {}
        self.object_chunks = {}

        self.spawnable_land_tiles = []
        self.ai_spawn_friendly_count = 50
        self.ai_spawn_enemy_count = 30

        self.create_new_world_data()

        ## HUD instantiation ##
        self.HUD_font = pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", 25)

        self.head_box = pygame.image.load("gfx/ui/HUD/head_bg.png").convert_alpha()
        self.head_box_rect = self.head_box.get_rect(bottomleft=(10, self.YRes - 10))

        self.blank_bar = pygame.image.load("gfx/ui/HUD/blank_bar.png").convert_alpha()
        self.blank_right = self.blank_bar.get_rect(bottomright=(self.head_box_rect.right - 7.5, self.head_box_rect.top + 5))
        self.blank_left = self.blank_bar.get_rect(bottomleft=(self.head_box_rect.left + 7.5, self.head_box_rect.top + 5))

        self.hp_bar = pygame.image.load("gfx/ui/HUD/hp_bar.png").convert_alpha()
        self.hp_bar_rect = self.hp_bar.get_rect(bottomright=(self.head_box_rect.right - 7.5, self.head_box_rect.top + 5))

        self.hp_text = self.settings_font.render("HP", True, "white")
        self.hp_text_rect = self.hp_text.get_rect(bottomright=(self.head_box_rect.right - 5, self.head_box_rect.top - 95))

        self.stam_bar = pygame.image.load("gfx/ui/HUD/stam_bar.png").convert_alpha()
        self.stam_bar_rect = self.stam_bar.get_rect(bottomleft=(self.head_box_rect.left + 7.5, self.head_box_rect.top + 5))

        self.stam_text = self.settings_font.render("SP", True, "white")
        self.stam_text_rect = self.stam_text.get_rect(bottomleft=(self.head_box_rect.left + 7.5, self.head_box_rect.top - 195))

        # Create player after world
        CC([self.player, self.render_items])

        self.spawn_ai_population(
            friendly_count=self.ai_spawn_friendly_count,
            enemy_count=self.ai_spawn_enemy_count,
        )

    def is_on_screen_rect(self, rect):
        screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        return rect.colliderect(screen_rect)

    def get_world_view_rect(self):
        return pygame.Rect(
            self.cameraX,
            self.cameraY,
            self.screen_width,
            self.screen_height
        )

    def get_player_sprite(self):
        sprites = self.player.sprites()
        return sprites[0] if sprites else None

    def get_player_world_hitbox(self):
        player = self.get_player_sprite()
        if player is None:
            return None

        base_hitbox = player.hitbox if hasattr(player, "hitbox") else player.rect
        return base_hitbox.move(self.cameraX, self.cameraY)

    def get_nearby_tiles(self, world_x, world_y, radius=2):
        tile_x = int((world_x + self.world_width_offset) // self.tile_size)
        tile_y = int((world_y + self.world_height_offset) // self.tile_size)

        nearby = []
        for y in range(tile_y - radius, tile_y + radius + 1):
            for x in range(tile_x - radius, tile_x + radius + 1):
                tile = self.tile_lookup.get((x, y))
                if tile is not None:
                    nearby.append(tile)
        return nearby

    def get_nearby_objects(self, world_x, world_y, radius=2):
        tile_x = int((world_x + self.world_width_offset) // self.tile_size)
        tile_y = int((world_y + self.world_height_offset) // self.tile_size)

        nearby = []
        seen = set()

        for y in range(tile_y - radius, tile_y + radius + 1):
            for x in range(tile_x - radius, tile_x + radius + 1):
                chunk_key = self.get_chunk_key_from_tile(x, y)
                chunk = self.object_chunks.get(chunk_key)

                if not chunk:
                    continue

                for obj in chunk:
                    obj_id = id(obj)
                    if obj_id not in seen:
                        nearby.append(obj)
                        seen.add(obj_id)

        return nearby

    def can_move_to(self, new_camera_x, new_camera_y):
        player = self.get_player_sprite()
        if player is None:
            return True

        base_hitbox = player.hitbox if hasattr(player, 'hitbox') else player.rect
        future_player_hitbox = base_hitbox.move(new_camera_x, new_camera_y)

        center_x = future_player_hitbox.centerx
        center_y = future_player_hitbox.centery

        nearby_tiles = self.get_nearby_tiles(center_x, center_y, radius=2)
        for tile in nearby_tiles:
            try:
                tile_hitbox = tile.hitbox if hasattr(tile, 'hitbox') else tile.rect
                blocked = getattr(tile, '_isSolid', False) or getattr(tile, '_tile_type', '') in {'deep_water'}
                if blocked and tile_hitbox.colliderect(future_player_hitbox):
                    return False
            except Exception:
                pass

        nearby_objects = self.get_nearby_objects(center_x, center_y, radius=2)
        for obj in nearby_objects:
            try:
                obj_hitbox = obj.hitbox if hasattr(obj, 'hitbox') else obj.rect
                if getattr(obj, '_isSolid', False) and obj_hitbox.colliderect(future_player_hitbox):
                    return False
            except Exception:
                pass

        for ai in self.AI:
            try:
                if getattr(ai, 'is_dead', False):
                    continue
                if ai.hitbox.colliderect(future_player_hitbox):
                    return False
            except Exception:
                pass

        return True

    def get_chunk_key_from_tile(self, tile_x, tile_y):
        return (tile_x // self.chunk_size, tile_y // self.chunk_size)

    def add_floor_tile_to_chunk(self, tile_x, tile_y, tile):
        chunk_key = self.get_chunk_key_from_tile(tile_x, tile_y)

        if chunk_key not in self.floor_chunks:
            self.floor_chunks[chunk_key] = []

        self.floor_chunks[chunk_key].append(tile)

    def get_visible_floor_chunks(self, cull_rect):
        left_tile = int((cull_rect.left + self.world_width_offset) // self.tile_size)
        right_tile = int((cull_rect.right + self.world_width_offset) // self.tile_size)
        top_tile = int((cull_rect.top + self.world_height_offset) // self.tile_size)
        bottom_tile = int((cull_rect.bottom + self.world_height_offset) // self.tile_size)

        left_chunk = left_tile // self.chunk_size
        right_chunk = right_tile // self.chunk_size
        top_chunk = top_tile // self.chunk_size
        bottom_chunk = bottom_tile // self.chunk_size

        visible_chunks = []

        for cy in range(top_chunk, bottom_chunk + 1):
            for cx in range(left_chunk, right_chunk + 1):
                chunk = self.floor_chunks.get((cx, cy))
                if chunk:
                    visible_chunks.append(chunk)

        return visible_chunks

    def add_object_to_chunk(self, obj):
        if not hasattr(obj, "rect"):
            return

        left_tile = int((obj.rect.left + self.world_width_offset) // self.tile_size)
        right_tile = int((obj.rect.right + self.world_width_offset) // self.tile_size)
        top_tile = int((obj.rect.top + self.world_height_offset) // self.tile_size)
        bottom_tile = int((obj.rect.bottom + self.world_height_offset) // self.tile_size)

        left_chunk = left_tile // self.chunk_size
        right_chunk = right_tile // self.chunk_size
        top_chunk = top_tile // self.chunk_size
        bottom_chunk = bottom_tile // self.chunk_size

        for cy in range(top_chunk, bottom_chunk + 1):
            for cx in range(left_chunk, right_chunk + 1):
                chunk_key = (cx, cy)

                if chunk_key not in self.object_chunks:
                    self.object_chunks[chunk_key] = []

                self.object_chunks[chunk_key].append(obj)

    def get_visible_object_chunks(self, cull_rect):
        left_tile = int((cull_rect.left + self.world_width_offset) // self.tile_size)
        right_tile = int((cull_rect.right + self.world_width_offset) // self.tile_size)
        top_tile = int((cull_rect.top + self.world_height_offset) // self.tile_size)
        bottom_tile = int((cull_rect.bottom + self.world_height_offset) // self.tile_size)

        left_chunk = left_tile // self.chunk_size
        right_chunk = right_tile // self.chunk_size
        top_chunk = top_tile // self.chunk_size
        bottom_chunk = bottom_tile // self.chunk_size

        visible_chunks = []

        for cy in range(top_chunk, bottom_chunk + 1):
            for cx in range(left_chunk, right_chunk + 1):
                chunk = self.object_chunks.get((cx, cy))
                if chunk:
                    visible_chunks.append(chunk)

        return visible_chunks

    def get_object_screen_rect(self, obj):
        return obj.rect.move(-self.cameraX, -self.cameraY)

    def is_object_visible(self, obj, cull_rect):
        if not hasattr(obj, "rect"):
            return False

        return obj.rect.colliderect(cull_rect)

    def world_to_tile(self, world_x, world_y):
        tile_x = int((world_x + self.world_width_offset) // self.tile_size)
        tile_y = int((world_y + self.world_height_offset) // self.tile_size)
        return tile_x, tile_y

    def tile_to_world_center(self, tile_x, tile_y):
        world_x = (tile_x * self.tile_size) - self.world_width_offset + (self.tile_size // 2)
        world_y = (tile_y * self.tile_size) - self.world_height_offset + (self.tile_size // 2)
        return world_x, world_y

    def tile_to_world_spawn_pos(self, tile_x, tile_y):
        world_x = (tile_x * self.tile_size) - self.world_width_offset + (self.tile_size // 2)
        world_y = (tile_y * self.tile_size) - self.world_height_offset + self.tile_size
        return world_x, world_y

    def is_tile_walkable(self, tile_x, tile_y, ignore_entity=None, consider_player=True):
        if tile_x < 0 or tile_y < 0:
            return False

        if tile_x >= self.world_tiles_w or tile_y >= self.world_tiles_h:
            return False

        tile = self.tile_lookup.get((tile_x, tile_y))
        if tile is None:
            return False

        if getattr(tile, '_tile_type', '') in {'deep_water', 'shallow_water'}:
            return False

        tile_rect = pygame.Rect(
            (tile_x * self.tile_size) - self.world_width_offset,
            (tile_y * self.tile_size) - self.world_height_offset,
            self.tile_size,
            self.tile_size,
        )

        nearby_objects = self.get_nearby_objects(tile_rect.centerx, tile_rect.centery, radius=1)
        for obj in nearby_objects:
            if obj is ignore_entity or getattr(obj, 'is_dead', False):
                continue

            obj_hitbox = obj.hitbox if hasattr(obj, 'hitbox') and obj.hitbox is not None else obj.rect
            if getattr(obj, '_isSolid', False) and obj_hitbox.colliderect(tile_rect):
                return False

        for ai in self.AI:
            if ai is ignore_entity or getattr(ai, 'is_dead', False):
                continue
            if ai.hitbox.colliderect(tile_rect):
                return False

        if consider_player:
            player_hitbox = self.get_player_world_hitbox()
            if player_hitbox is not None and player_hitbox.colliderect(tile_rect):
                return False

        return True

    def can_ai_move_to(self, entity, new_world_x, new_world_y):
        future_hitbox = entity.get_future_hitbox(new_world_x, new_world_y)
        center_x = future_hitbox.centerx
        center_y = future_hitbox.centery

        nearby_tiles = self.get_nearby_tiles(center_x, center_y, radius=2)
        for tile in nearby_tiles:
            tile_hitbox = tile.hitbox if hasattr(tile, 'hitbox') else tile.rect
            blocked = getattr(tile, '_isSolid', False) or getattr(tile, '_tile_type', '') in {'deep_water', 'shallow_water'}

            if blocked and tile_hitbox.colliderect(future_hitbox):
                return False

        nearby_objects = self.get_nearby_objects(center_x, center_y, radius=2)
        for obj in nearby_objects:
            if obj is entity or getattr(obj, 'is_dead', False):
                continue

            obj_hitbox = obj.hitbox if hasattr(obj, 'hitbox') and obj.hitbox is not None else obj.rect
            if getattr(obj, '_isSolid', False) and obj_hitbox.colliderect(future_hitbox):
                return False

        player_hitbox = self.get_player_world_hitbox()
        if player_hitbox is not None and player_hitbox.colliderect(future_hitbox):
            return False

        for ai in self.AI:
            if ai is entity or getattr(ai, 'is_dead', False):
                continue
            if ai.hitbox.colliderect(future_hitbox):
                return False

        return True

    def find_path(self, start_world_pos, goal_world_pos, ignore_entity=None, max_nodes=1200):
        start_tile = self.world_to_tile(start_world_pos[0], start_world_pos[1])
        goal_tile = self.world_to_tile(goal_world_pos[0], goal_world_pos[1])

        if start_tile == goal_tile:
            return []

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_heap = []
        heapq.heappush(open_heap, (0, start_tile))

        came_from = {}
        g_score = {start_tile: 0}
        closed = set()

        nodes_checked = 0

        while open_heap and nodes_checked < max_nodes:
            _, current = heapq.heappop(open_heap)

            if current in closed:
                continue

            closed.add(current)
            nodes_checked += 1

            if current == goal_tile:
                break

            x, y = current
            neighbours = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
            ]

            for neighbour in neighbours:
                if neighbour in closed:
                    continue

                nx, ny = neighbour

                if neighbour != goal_tile:
                    if not self.is_tile_walkable(nx, ny, ignore_entity=ignore_entity, consider_player=False):
                        continue

                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get(neighbour, 10**9):
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g
                    f_score = tentative_g + heuristic(neighbour, goal_tile)
                    heapq.heappush(open_heap, (f_score, neighbour))

        if goal_tile not in came_from:
            return []

        path_tiles = []
        current = goal_tile

        while current != start_tile:
            path_tiles.append(current)
            current = came_from[current]

        path_tiles.reverse()

        return [self.tile_to_world_center(x, y) for x, y in path_tiles]

    def spawn_ai_population(self, friendly_count=8, enemy_count=5):
        if not self.spawnable_land_tiles:
            return

        available_tiles = self.spawnable_land_tiles.copy()
        random.shuffle(available_tiles)

        def spawn_entity(entity_cls, groups):
            while available_tiles:
                tile_x, tile_y = available_tiles.pop()
                spawn_pos = self.tile_to_world_spawn_pos(tile_x, tile_y)
                entity = entity_cls(groups, spawn_pos)

                if self.can_ai_move_to(entity, entity.world_x, entity.world_y):
                    return entity

                entity.kill()

            return None

        for _ in range(friendly_count):
            spawn_entity(FriendlyAI, [self.AI, self.friendlyAI, self.render_items])

        for _ in range(enemy_count):
            spawn_entity(EnemyAI, [self.AI, self.enemiesAI, self.render_items])

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

    def create_new_world_data(self):
        world_data, obj_data = generate_world_data()

        with open(
            'NOQA/world_generation/configs/world_gen_configs.json',
            'r',
            encoding='utf-8',
        ) as f:
            configs = json.load(f)

        self.world_tiles_w = int(configs['window']['width'])
        self.world_tiles_h = int(configs['window']['height'])

        self.world_width_offset = self.world_tiles_w * self.tile_size / 2
        self.world_height_offset = self.world_tiles_h * self.tile_size / 2

        self.tile_lookup.clear()
        self.floor_chunks.clear()
        self.object_chunks = {}
        self.spawnable_land_tiles = []

        self.floor_tiles.empty()
        self.world.empty()
        self.assets.empty()
        self.resources.empty()
        self.scenery.empty()
        self.AI.empty()
        self.friendlyAI.empty()
        self.enemiesAI.empty()

        for row in world_data:
            for j in row:
                tile_x = j['pos'][0]
                tile_y = j['pos'][1]

                world_x = (tile_x * self.tile_size) - self.world_width_offset
                world_y = (tile_y * self.tile_size) - self.world_height_offset

                tile = None

                if j['type'] == 'grassland':
                    tile = Grassland([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'deep_water':
                    tile = Deep_Water([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'shallow_water':
                    tile = Shallow_Water([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'beach':
                    tile = Beach([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'forest':
                    tile = Forest([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'swamp':
                    tile = Swamp([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'savanna':
                    tile = Savanna([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'desert':
                    tile = Desert([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'hill':
                    tile = Hill([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'mountain':
                    tile = Mountain([self.floor_tiles, self.world], (world_x, world_y))
                elif j['type'] == 'snow':
                    tile = Snow([self.floor_tiles, self.world], (world_x, world_y))

                if tile is not None:
                    self.tile_lookup[(tile_x, tile_y)] = tile
                    self.add_floor_tile_to_chunk(tile_x, tile_y, tile)

        for row in obj_data:
            for j in row:
                if j['type'] is None:
                    continue

                tile_x = j['pos'][0]
                tile_y = j['pos'][1]

                world_x = (tile_x * self.tile_size) - self.world_width_offset
                world_y = (tile_y * self.tile_size) - self.world_height_offset

                obj = None

                if j['type'] == 'tree':
                    obj = L_Tree([self.assets, self.scenery, self.render_items], (world_x, world_y + self.tile_size))

                if j['type'] == 'grass':
                    obj = Grass([self.assets, self.scenery, self.render_items], (world_x, world_y + self.tile_size))

                if j['type'] == 'cactus':
                    obj = Cactus([self.assets, self.scenery, self.render_items], (world_x, world_y + self.tile_size))

                if j['type'] == 'bush':
                    obj = Bushes([self.assets, self.scenery, self.render_items], (world_x, world_y + self.tile_size))

                if j['type'] == 'stone':
                    obj = Stone([self.assets, self.scenery, self.render_items], (world_x, world_y + self.tile_size))

                if j['type'] == 'iron':
                    obj = Iron([self.assets, self.scenery, self.render_items], (world_x, world_y + self.tile_size))

                if j['type'] == 'coal':
                    obj = Coal([self.assets, self.scenery, self.render_items], (world_x, world_y + self.tile_size))

                if obj is not None:
                    try:
                        obj.update()
                    except Exception:
                        pass

                    self.add_object_to_chunk(obj)

        for tile_y in range(self.world_tiles_h):
            for tile_x in range(self.world_tiles_w):
                if self.is_tile_walkable(tile_x, tile_y, ignore_entity=None, consider_player=False):
                    self.spawnable_land_tiles.append((tile_x, tile_y))

        self.cameraX = -self.screen_width // 2
        self.cameraY = -self.screen_height // 2

    def display_HUD(self):
        player = self.get_player_sprite()

        self.screen.blit(self.head_box, self.head_box_rect)

        hp_percent = (player.hp / player._max_hp) * 10 if player.hp > 0 else 0
        stam_percent = (player.stamina / player._max_stamina) * 20 if player.stamina > 0 else 0

        increment = 0
        for i in range(20):
            increment += 1
            self.screen.blit(self.blank_bar, self.blank_left.move(0, (increment * 10) * -1))

        increment = 0
        for i in range(10):
            increment += 1
            self.screen.blit(self.blank_bar, self.blank_right.move(0, (increment * 10) * -1))

        increment = 0
        for i in range(int(hp_percent)):
            increment += 1
            self.screen.blit(self.hp_bar, self.hp_bar_rect.move(0, (increment * 10) * -1))

        increment = 0
        for i in range(int(stam_percent)):
            increment += 1
            self.screen.blit(self.stam_bar, self.stam_bar_rect.move(0, (increment * 10) * -1))

        self.screen.blit(self.hp_text, self.hp_text_rect)
        self.screen.blit(self.stam_text, self.stam_text_rect)

    def draw_debug_overlays(self, visible_floor_chunks, visible_entities, player, cull_rect):
        if self.debug_draw_mode == 0:
            return

        screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        full_debug = self.debug_draw_mode == 2

        # Floor hitboxes
        for chunk in visible_floor_chunks:
            for sprite in chunk:
                if not sprite.rect.colliderect(cull_rect):
                    continue

                try:
                    hitbox = sprite.hitbox.move(-self.cameraX, -self.cameraY)
                    if hitbox.colliderect(screen_rect):
                        pygame.draw.rect(self.screen, (255, 0, 0), hitbox, 1)
                except Exception:
                    pass

        # Entities / objects / AI / player
        for _, _, _, sprite in visible_entities:
            if sprite == player:
                try:
                    if player.hitbox.colliderect(screen_rect):
                        pygame.draw.rect(self.screen, (0, 255, 0), player.hitbox, 1)
                except Exception:
                    pass

                try:
                    if getattr(player, 'attack_box', None) is not None:
                        if player.attack_box.colliderect(screen_rect):
                            pygame.draw.rect(self.screen, (0, 0, 255), player.attack_box, 1)
                except Exception:
                    pass

                if full_debug:
                    try:
                        if player.rect.colliderect(screen_rect):
                            pygame.draw.rect(self.screen, (255, 255, 0), player.rect, 1)
                    except Exception:
                        pass

                continue

            try:
                if getattr(sprite, 'hitbox', None) is not None:
                    hitbox = sprite.hitbox.move(-self.cameraX, -self.cameraY)
                    if hitbox.colliderect(screen_rect):
                        pygame.draw.rect(self.screen, (255, 0, 0), hitbox, 1)
            except Exception:
                pass

            try:
                if getattr(sprite, 'attack_box', None) is not None:
                    attack_box = sprite.attack_box.move(-self.cameraX, -self.cameraY)
                    if attack_box.colliderect(screen_rect):
                        pygame.draw.rect(self.screen, (0, 0, 255), attack_box, 1)
            except Exception:
                pass

            if full_debug:
                try:
                    image_rect = sprite.rect.move(-self.cameraX, -self.cameraY)
                    if image_rect.colliderect(screen_rect):
                        pygame.draw.rect(self.screen, (255, 255, 0), image_rect, 1)
                except Exception:
                    pass

                try:
                    if sprite in self.AI:
                        center_x = int(sprite.world_x - self.cameraX)
                        center_y = int(sprite.world_y - self.cameraY)

                        if hasattr(sprite, 'view_radius'):
                            pygame.draw.circle(
                                self.screen,
                                (120, 120, 255),
                                (center_x, center_y),
                                int(sprite.view_radius),
                                1
                            )

                        if hasattr(sprite, 'stop_radius'):
                            pygame.draw.circle(
                                self.screen,
                                (255, 120, 120),
                                (center_x, center_y),
                                int(sprite.stop_radius),
                                1
                            )

                        if hasattr(sprite, 'flee_radius'):
                            pygame.draw.circle(
                                self.screen,
                                (255, 200, 80),
                                (center_x, center_y),
                                int(sprite.flee_radius),
                                1
                            )

                        if hasattr(sprite, 'path') and sprite.path:
                            prev_point = (center_x, center_y)

                            for node_x, node_y in sprite.path:
                                node_screen = (
                                    int(node_x - self.cameraX),
                                    int(node_y - self.cameraY),
                                )

                                if screen_rect.collidepoint(node_screen):
                                    pygame.draw.circle(self.screen, (0, 255, 255), node_screen, 3)

                                pygame.draw.line(self.screen, (0, 200, 255), prev_point, node_screen, 1)
                                prev_point = node_screen
                except Exception:
                    pass

    def render(self):
        self.screen.fill('black')

        view_rect = self.get_world_view_rect()
        cull_rect = view_rect.inflate(self.tile_size * 2, self.tile_size * 2)

        visible_floor_blits = []
        visible_entities = []

        player = self.get_player_sprite()

        visible_floor_chunks = self.get_visible_floor_chunks(cull_rect)
        for chunk in visible_floor_chunks:
            for sprite in chunk:
                if sprite.rect.colliderect(cull_rect):
                    draw_pos = (
                        sprite.rect.x - self.cameraX,
                        sprite.rect.y - self.cameraY,
                    )

                    if hasattr(sprite, 'frames'):
                        visible_floor_blits.append((sprite.frames[self.water_anim_frame], draw_pos))
                    else:
                        visible_floor_blits.append((sprite.image, draw_pos))

        if visible_floor_blits:
            self.screen.blits(visible_floor_blits)

        visible_object_chunks = self.get_visible_object_chunks(cull_rect)
        seen = set()

        for chunk in visible_object_chunks:
            for sprite in chunk:
                sprite_id = id(sprite)
                if sprite_id in seen:
                    continue
                seen.add(sprite_id)

                if self.is_object_visible(sprite, cull_rect):
                    sort_rect = sprite.hitbox if hasattr(sprite, 'hitbox') and sprite.hitbox is not None else sprite.rect
                    visible_entities.append(
                        (
                            getattr(sort_rect, 'bottom', sprite.rect.bottom),
                            sprite.image,
                            (sprite.rect.x - self.cameraX, sprite.rect.y - self.cameraY),
                            sprite,
                        )
                    )

        for ai in self.AI:
            if getattr(ai, 'is_dead', False):
                continue

            if self.is_object_visible(ai, cull_rect):
                sort_rect = ai.hitbox if ai.hitbox is not None else ai.rect
                visible_entities.append(
                    (
                        sort_rect.bottom,
                        ai.image,
                        (ai.rect.x - self.cameraX, ai.rect.y - self.cameraY),
                        ai,
                    )
                )

        if player is not None:
            player_world_hitbox = self.get_player_world_hitbox()
            player_sort_bottom = player_world_hitbox.bottom if player_world_hitbox is not None else player.rect.bottom

            visible_entities.append(
                (
                    player_sort_bottom,
                    player.image,
                    player.rect.topleft,
                    player,
                )
            )

        visible_entities.sort(key=lambda item: item[0])

        if visible_entities:
            self.screen.blits([(img, pos) for _, img, pos, _ in visible_entities])

        if self.debug and player is not None:
            debug404(
                [
                    'ALONE: No Rescue | vDev-Kit 0.1 pre-Alpha',
                    f'FPS: {int(self.clock.get_fps())}',
                    f'Cursor XY: {self.cusror.location[0]} / {self.cusror.location[1]}',
                    f'Camera XY: {round(self.cameraX, 2)} / {round(self.cameraY, 2)}',
                    f'Visible Floor: {len(visible_floor_blits)}',
                    f'Visible Entities: {len(visible_entities)}',
                    f'Friendly AI: {len(self.friendlyAI.sprites())}',
                    f'Enemy AI: {len(self.enemiesAI.sprites())}',
                    f'Player HP: {player.hp}',
                    f'Player State: {getattr(player, "state", "N/A")}',
                    f'Player Direction: {getattr(player, "direction", "N/A")}',
                    f'Player Attack Cooldown: {round(getattr(player, "attack_cooldown", 0), 2)}',
                    f'Func Cooldown: {self.f_cooldown}',
                    f'Debug Draw Mode: {self.debug_draw_mode}',
                ]
            )

        self.draw_debug_overlays(visible_floor_chunks, visible_entities, player, cull_rect)

        self.display_HUD()
        self.cusror.draw()

    def game_updates(self):
        self.cusror.update()

        self.f_cooldown -= 0.05
        if self.f_cooldown < 0:
            self.f_cooldown = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if keys[pygame.K_F1] and self.f_cooldown <= 0:
            self.debug = not self.debug
            self.f_cooldown = 1

        if keys[pygame.K_F2] and self.f_cooldown <= 0:
            self.debug_draw_mode = (self.debug_draw_mode + 1) % 3
            self.f_cooldown = 1

        if keys[pygame.K_F3] and self.f_cooldown <= 0:
            count = 0
            os.makedirs('screenshots', exist_ok=True)
            for path in os.listdir('screenshots/'):
                if os.path.isfile(os.path.join('screenshots/', path)):
                    count += 1

            pygame.image.save(self.screen, f'screenshots/screenshot{count}.png')
            self.f_cooldown = 1

        view_rect = self.get_world_view_rect()
        cull_rect = view_rect.inflate(self.tile_size * 2, self.tile_size * 2)

        visible_object_chunks = self.get_visible_object_chunks(cull_rect)
        seen = set()

        for chunk in visible_object_chunks:
            for sprite in chunk:
                sprite_id = id(sprite)
                if sprite_id in seen:
                    continue
                seen.add(sprite_id)

                if self.is_object_visible(sprite, cull_rect):
                    try:
                        sprite.update()
                    except Exception:
                        pass

        self.player.update()
        player = self.get_player_sprite()

        if player is None:
            return

        player.perform_attack(self.friendlyAI, self.enemiesAI, self.cameraX, self.cameraY)

        self.AI.update(self)

        self.water_anim_timer += self.dt
        if self.water_anim_timer >= self.water_anim_speed:
            self.water_anim_timer = 0
            self.water_anim_frame = (self.water_anim_frame + 1) % 3

        move_x = 0
        move_y = 0

        if player.state not in ['hit', 'death'] and player.attack_cooldown <= 0:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                move_y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move_y += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x += 1

            speed = player.sprint_speed if getattr(player, 'is_sprinting', False) else player.walk_speed

            if move_x != 0 or move_y != 0:
                length = (move_x ** 2 + move_y ** 2) ** 0.5
                move_x = (move_x / length) * speed
                move_y = (move_y / length) * speed

                new_camera_x = self.cameraX + move_x
                new_camera_y = self.cameraY + move_y

                if self.can_move_to(new_camera_x, new_camera_y):
                    self.cameraX = new_camera_x
                    self.cameraY = new_camera_y

    def run(self):
        self.screen.fill("black")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.game_updates()
        self.render()