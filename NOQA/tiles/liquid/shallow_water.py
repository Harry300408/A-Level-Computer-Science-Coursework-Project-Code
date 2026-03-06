import pygame
from NOQA.tiles.liquid.base_liquid import Liquid

class Shallow_Water(Liquid):
    def __init__(self, groups, pos: tuple):
        super().__init__(groups, pos, "shallow_water")