import pygame
from NOQA.tiles.liquid.base_liquid import Liquid

class Deep_Water(Liquid):
    def __init__(self, groups, pos: tuple):
        super().__init__(groups, pos, "deep_water")
        self.hitbox = self.rect.inflate(-10, -10)
        self._isSolid = True