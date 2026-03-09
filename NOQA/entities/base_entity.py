import math
import os
import pygame


class BaseEntity(pygame.sprite.Sprite):
    def __init__(
        self,
        groups,
        pos,
        image_path=None,
        fallback_color=(255, 255, 255),
        image_size=(28, 36),
        entity_type='entity',
        max_hp=40,
        move_speed=2.0,
        attack_damage=8,
        attack_range=28,
        attack_cooldown_max=1.0,
        heal_on_kill=0,
        solid=True,
    ):
        super().__init__(groups)

        self.entity_type = entity_type
        self.image_path = image_path
        self.fallback_color = fallback_color
        self.image_size = image_size

        self.uses_loaded_image = bool(self.image_path and os.path.exists(self.image_path))
        self.base_image = self._load_image()
        self.image = self.base_image.copy()

        self.world_x = float(pos[0])
        self.world_y = float(pos[1])

        self.max_hp = max_hp
        self.hp = max_hp
        self.move_speed = move_speed
        self.attack_damage = attack_damage
        self.attack_range = attack_range
        self.attack_cooldown_max = attack_cooldown_max
        self.attack_cooldown = 0.0
        self.heal_on_kill = heal_on_kill

        self._isSolid = solid
        self.direction = 'down'
        self.state = 'idle'
        self.is_dead = False

        self.hit_flash_timer = 0
        self.hit_flash_duration = 10
        self.hit_flash_color = (255, 80, 80)

        self.rect = self.image.get_rect(midbottom=(round(self.world_x), round(self.world_y)))
        self.hitbox = None
        self.attack_box = None

        self.refresh_bounds()

    def _load_image(self):
        if self.uses_loaded_image:
            return pygame.image.load(self.image_path).convert_alpha()

        surf = pygame.Surface(self.image_size, pygame.SRCALPHA)
        pygame.draw.rect(surf, self.fallback_color, surf.get_rect(), border_radius=6)
        return surf

    def update_visuals(self):
        # Only apply damage flash to fallback placeholder entities.
        # If the entity is using a real image, leave the image unchanged.
        if self.uses_loaded_image:
            self.image = self.base_image.copy()
            return

        if self.hit_flash_timer > 0:
            self.image = self.base_image.copy()
            flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash.fill((*self.hit_flash_color, 120))
            self.image.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        else:
            self.image = self.base_image.copy()

    def refresh_bounds(self):
        self.rect = self.image.get_rect(midbottom=(round(self.world_x), round(self.world_y)))

        # Larger hitbox so AI are easier to collide with and hit
        hitbox_w = int(self.rect.width * 0.8)
        hitbox_h = int(self.rect.height * 0.6)

        self.hitbox = pygame.Rect(0, 0, hitbox_w, hitbox_h)
        self.hitbox.midbottom = self.rect.midbottom

        self.attack_box = self.build_attack_box()

    def build_attack_box(self):
        if self.attack_range <= 0:
            return None

        box = pygame.Rect(0, 0, self.attack_range, self.attack_range)

        if self.direction == 'up':
            box.midbottom = self.hitbox.midtop
        elif self.direction == 'down':
            box.midtop = self.hitbox.midbottom
        elif self.direction == 'left':
            box.midright = self.hitbox.midleft
        else:
            box.midleft = self.hitbox.midright

        return box

    def get_future_hitbox(self, new_world_x, new_world_y):
        future_rect = self.image.get_rect(midbottom=(round(new_world_x), round(new_world_y)))

        hitbox_w = max(12, future_rect.width // 2)
        hitbox_h = max(10, future_rect.height // 3)

        future_hitbox = pygame.Rect(0, 0, hitbox_w, hitbox_h)
        future_hitbox.midbottom = future_rect.midbottom
        return future_hitbox

    def face_towards(self, target_x, target_y):
        dx = target_x - self.world_x
        dy = target_y - self.world_y

        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'

        self.attack_box = self.build_attack_box()

    def distance_to(self, target_x, target_y):
        return math.hypot(target_x - self.world_x, target_y - self.world_y)

    def try_move(self, dx, dy, engine):
        if dx == 0 and dy == 0:
            return False

        new_x = self.world_x + dx
        new_y = self.world_y + dy

        if engine.can_ai_move_to(self, new_x, new_y):
            self.world_x = new_x
            self.world_y = new_y
            self.refresh_bounds()
            self.state = 'walk'
            return True

        self.state = 'idle'
        return False

    def move_towards(self, target_x, target_y, speed, engine):
        dx = target_x - self.world_x
        dy = target_y - self.world_y
        dist = math.hypot(dx, dy)

        if dist <= 0.0001:
            return False

        self.face_towards(target_x, target_y)
        return self.try_move((dx / dist) * speed, (dy / dist) * speed, engine)

    def move_away_from(self, target_x, target_y, speed, engine):
        dx = self.world_x - target_x
        dy = self.world_y - target_y
        dist = math.hypot(dx, dy)

        if dist <= 0.0001:
            return False

        away_x = self.world_x + dx
        away_y = self.world_y + dy
        self.face_towards(away_x, away_y)
        return self.try_move((dx / dist) * speed, (dy / dist) * speed, engine)

    def take_damage(self, amount, source=None):
        if self.is_dead:
            return

        self.hp -= amount
        self.state = 'hit'

        if not self.uses_loaded_image:
            self.hit_flash_timer = self.hit_flash_duration

        if self.hp <= 0:
            self.die(source)

    def die(self, killer=None):
        if self.is_dead:
            return

        self.is_dead = True
        self.state = 'death'

        if killer is not None and hasattr(killer, 'heal'):
            killer.heal(self.heal_on_kill)

        self.kill()

    def attack_player_if_possible(self, player, player_world_hitbox):
        if self.attack_cooldown > 0:
            return False

        self.attack_box = self.build_attack_box()
        if self.attack_box is None:
            return False

        if self.attack_box.colliderect(player_world_hitbox):
            player.take_damage(self.attack_damage)
            self.attack_cooldown = self.attack_cooldown_max
            return True

        return False

    def update(self, engine=None):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 0.05
            if self.attack_cooldown < 0:
                self.attack_cooldown = 0

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        self.update_visuals()
        self.refresh_bounds()