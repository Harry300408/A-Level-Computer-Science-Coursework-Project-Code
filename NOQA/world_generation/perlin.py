import pygame
import noise
import random

# --------------------
# SETTINGS
# --------------------
WIDTH, HEIGHT = 1000, 800
TILE_SIZE = 6

WORLD_WIDTH = 400
WORLD_HEIGHT = 400

SCALE = 100.0
OCTAVES = 6
PERSISTENCE = 0.5
LACUNARITY = 2.0
SEED = random.randint(0, 100)

CAMERA_SPEED = 10

# --------------------
# INITIALISE PYGAME
# --------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Perlin Biome Generator - WASD Camera")
clock = pygame.time.Clock()

# --------------------
# BIOME COLOURS
# --------------------
BIOMES = {
    "water": (30, 60, 170),
    "beach": (240, 230, 140),
    "plains": (50, 200, 50),
    "forest": (16, 120, 16),
    "desert": (210, 180, 60),
    "mountain": (100, 100, 100),
    "snow": (250, 250, 250),
}

# --------------------
# BIOME LOGIC
# --------------------
def get_biome(e, m):
    if e < -0.05:
        return "water"
    elif e < 0.0:
        return "beach"
    elif e < 0.3:
        if m < -0.1:
            return "desert"
        elif m < 0.2:
            return "plains"
        else:
            return "forest"
    elif e < 0.5:
        return "mountain"
    else:
        return "snow"

# --------------------
# GENERATE WORLD
# --------------------
def generate_world():
    world = []

    for y in range(WORLD_HEIGHT):
        row = []
        for x in range(WORLD_WIDTH):

            elevation = noise.pnoise2(
                x / SCALE,
                y / SCALE,
                octaves=OCTAVES,
                persistence=PERSISTENCE,
                lacunarity=LACUNARITY,
                repeatx=1024,
                repeaty=1024,
                base=SEED
            )

            moisture = noise.pnoise2(
                (x + 500) / SCALE,
                (y + 500) / SCALE,
                octaves=OCTAVES,
                persistence=PERSISTENCE,
                lacunarity=LACUNARITY,
                repeatx=1024,
                repeaty=1024,
                base=SEED + 1
            )

            row.append(get_biome(elevation, moisture))

        world.append(row)

    return world

# --------------------
# DRAW WITH CAMERA
# --------------------
def draw_world(world, cam_x, cam_y):
    start_x = cam_x // TILE_SIZE
    start_y = cam_y // TILE_SIZE

    tiles_x = WIDTH // TILE_SIZE + 2
    tiles_y = HEIGHT // TILE_SIZE + 2

    for y in range(tiles_y):
        for x in range(tiles_x):

            world_x = start_x + x
            world_y = start_y + y

            if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
                biome = world[world_y][world_x]
                color = BIOMES[biome]

                screen_x = x * TILE_SIZE - (cam_x % TILE_SIZE)
                screen_y = y * TILE_SIZE - (cam_y % TILE_SIZE)

                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                )

# --------------------
# MAIN
# --------------------
world = generate_world()

cam_x = 0
cam_y = 0

running = True
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        cam_y -= CAMERA_SPEED
    if keys[pygame.K_s]:
        cam_y += CAMERA_SPEED
    if keys[pygame.K_a]:
        cam_x -= CAMERA_SPEED
    if keys[pygame.K_d]:
        cam_x += CAMERA_SPEED

    # Clamp camera to world bounds
    cam_x = max(0, min(cam_x, WORLD_WIDTH * TILE_SIZE - WIDTH))
    cam_y = max(0, min(cam_y, WORLD_HEIGHT * TILE_SIZE - HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                SEED = random.randint(0, 100)
                world = generate_world()

    draw_world(world, cam_x, cam_y)
    pygame.display.flip()

pygame.quit()