import pygame
import random
from NOQA.assets.base_asset import Asset

class L_Tree(Asset):
    def __init__(self, groups, pos):
        self.rand = random.randint(0, 5)
        super().__init__(
            groups,
            pos,
            True,
            "L_Tree",
            False,
            "tree",
            rect_anchor="bottomleft",
            hitbox_mode="bottom",
            hitbox_shrink_x=160
            
            ,
            hitbox_bottom_height=28
        )

    def get_image_path(self):
        return f"gfx/assets/trees/tree{self.rand}.png"