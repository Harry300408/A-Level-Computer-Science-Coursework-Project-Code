import pygame, random
from NOQA.assets.base_asset import Asset

class L_Tree(Asset):
    def __init__(self, groups, pos):
        self.rand = random.randint(0, 5)
        super().__init__(groups, pos, True, "L_Tree", False, "tree")
        self.build_hitbox()

    def set_img(self):
        self.image = pygame.image.load(
            f"gfx/assets/trees/tree{self.rand}.png"
        ).convert_alpha()
        self.rect = self.image.get_rect(bottomleft=self.pos)

    def build_hitbox(self):
        trunk_width = max(20, self.rect.width // 5)
        trunk_height = max(24, self.rect.height // 6)

        self.hitbox = pygame.Rect(
            self.rect.centerx - trunk_width // 2,
            self.rect.bottom - trunk_height,
            trunk_width,
            trunk_height,
        )

    def update(self):
        self.build_hitbox()