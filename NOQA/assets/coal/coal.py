import pygame
import random
from NOQA.assets.base_asset import Asset

class Coal(Asset):
    def __init__(self, groups, pos):
        self.rand = random.randint(1, 2)

        offset_x = random.randint(-6, 6)
        offset_y = random.randint(-6, 6)

        pos = (pos[0] + offset_x, pos[1] + offset_y)

        super().__init__(
            groups,
            pos,
            True,
            "Coal",
            False,
            "coal",
            rect_anchor="bottomleft"
        )

    def get_image_path(self):
        return f"gfx/assets/coal/coal{self.rand}.png"