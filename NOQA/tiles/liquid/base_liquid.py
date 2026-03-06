import pygame
from NOQA.tiles.base_tile import Tile

class Liquid(Tile):
    frame_cache = {}

    def __init__(self, groups, pos: tuple, _tile_type: str = "default"):
        self.tile_type = _tile_type

        if _tile_type not in Liquid.frame_cache:
            Liquid.frame_cache[_tile_type] = self.load_frames(_tile_type)

        self.frames = Liquid.frame_cache[_tile_type]

        super().__init__(groups, pos, _tile_type)

        self._ID = f"l{pos[0]} {pos[1]}"

    def set_img(self):
        self.image: pygame.Surface = self.frames[0]
        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)

    @classmethod
    def load_frames(cls, tile_type):
        frames = []
        for i in range(0, 3):
            frame = pygame.image.load(
                f"gfx/tiles/{tile_type}/{tile_type}_{i}.png"
            ).convert_alpha()
            frames.append(frame)
        return frames