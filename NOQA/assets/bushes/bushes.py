import pygame
import random
from NOQA.assets.base_asset import Asset

class Bushes(Asset):
    def __init__(self, groups, pos):
        self.rand = random.randint(1, 5)

        offset_x = random.randint(-6, 6)
        offset_y = random.randint(-6, 6)

        pos = (pos[0] + offset_x, pos[1] + offset_y)

        super().__init__(
            groups,
            pos,
            False,
            "Bushes",
            False,
            "bushes",
            rect_anchor="bottomleft"
        )

    def get_image_path(self):
        return f"gfx/assets/bushes/bush{self.rand}.png"