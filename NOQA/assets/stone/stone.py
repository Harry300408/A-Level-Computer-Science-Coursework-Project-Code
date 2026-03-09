import pygame
import random
from NOQA.assets.base_asset import Asset

class Stone(Asset):
    def __init__(self, groups, pos):
        self.rand = random.randint(1, 5)

        offset_x = random.randint(-6, 6)
        offset_y = random.randint(-6, 6)

        super().__init__(
            groups,
            pos,
            True,
            "Stone",
            False,
            "stone",
            rect_anchor="bottomleft"
        )

    def get_image_path(self):
        return f"gfx/assets/stone/stone.png"