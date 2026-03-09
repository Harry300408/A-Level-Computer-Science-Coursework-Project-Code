import pygame

class Asset(pygame.sprite.Sprite):
    def __init__(
        self,
        groups,
        pos,
        _isSolid,
        _obj_type,
        _interactable=False,
        _asset_type="default",
        rect_anchor="topleft",
        hitbox_mode="full",
        hitbox_shrink_x=0,
        hitbox_shrink_y=0,
        hitbox_bottom_height=None
    ):
        super().__init__(groups)

        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]

        self._asset_type = _asset_type
        self._isSolid = _isSolid
        self._obj_type = _obj_type
        self._interacterble = _interactable
        self._ID = f"a{pos[0]}{pos[1]}"

        self.rect_anchor = rect_anchor
        self.hitbox_mode = hitbox_mode
        self.hitbox_shrink_x = hitbox_shrink_x
        self.hitbox_shrink_y = hitbox_shrink_y
        self.hitbox_bottom_height = hitbox_bottom_height

        self.image = None
        self.rect = None
        self.hitbox = None
        self.interact_box = None

        self.set_img()
        self.refresh_bounds()

    def get_image_path(self):
        return f"gfx/assets/{self._asset_type}.png"

    def set_img(self):
        self.image = pygame.image.load(self.get_image_path()).convert_alpha()

        if self.rect_anchor == "bottomleft":
            self.rect = self.image.get_rect(bottomleft=self.pos)
        else:
            self.rect = self.image.get_rect(topleft=self.pos)

    def build_hitbox(self):
        if not self._isSolid:
            return None

        if self.hitbox_mode == "full":
            return self.rect.inflate(-self.hitbox_shrink_x, -self.hitbox_shrink_y)

        if self.hitbox_mode == "bottom":
            height = self.hitbox_bottom_height if self.hitbox_bottom_height is not None else max(16, self.rect.height // 5)
            width = self.rect.width - self.hitbox_shrink_x
            x = self.rect.left + (self.hitbox_shrink_x // 2)
            y = self.rect.bottom - height
            return pygame.Rect(x, y, width, height)

        return self.rect.copy()

    def build_interact_box(self):
        if not self._interacterble:
            return None
        return self.rect.inflate(20, 20)

    def refresh_bounds(self):
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.hitbox = self.build_hitbox()
        self.interact_box = self.build_interact_box()

    def update(self):
        self.refresh_bounds()