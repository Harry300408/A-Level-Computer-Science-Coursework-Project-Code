import pygame


class CC(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        self.screen = pygame.display.get_surface()

        self.x = pygame.display.get_surface().get_width() / 2
        self.y = pygame.display.get_surface().get_height() / 2
        self.pos = (self.x, self.y)

        self._ID = 'CharacterController'

        self.hp = 100
        self._max_hp = 100
        self._min_hp = 0

        self.stamina = 200
        self._max_stamina = 200
        self._min_stamina = 0

        self.walk_speed = 5
        self.sprint_speed = 8
        self.is_sprinting = False
        self.sprint_drain = 1
        self.walk_stamina_regen = 0.25
        self.idle_stamina_regen = 0.75

        self.attack_damage = 12
        self.attack_range = 42
        self.attack_box = None
        self.attack_has_hit = False

        self.held_item = 'sword'

        self.state = 'idle'
        self.direction = 'down'
        self.attack_cooldown = 0
        self.frame = 0

        self.image = pygame.image.load(
            f'gfx/player/{self.direction}/{self.state}/{self.state}{self.frame}.png'
        ).convert_alpha()

        self.rect = self.image.get_rect(
            center=(self.screen.get_width() / 2, self.screen.get_height() / 2)
        )
        self.rect = self.rect.scale_by(-2)
        self.rect = self.rect.inflate(0, -40)

        self.hitbox = self.image.get_rect(
            center=(self.screen.get_width() / 2, self.screen.get_height() / 2)
        )
        self.hitbox = self.hitbox.scale_by(0.5)
        self.hitbox = self.hitbox.inflate(-10, -10)
        self.hitbox = self.hitbox.move(0, 35)

        self.update_attack_box()

    def clamp_stats(self):
        if self.stamina < self._min_stamina:
            self.stamina = self._min_stamina
        if self.stamina > self._max_stamina:
            self.stamina = self._max_stamina

        if self.hp < self._min_hp:
            self.hp = self._min_hp
        if self.hp > self._max_hp:
            self.hp = self._max_hp

    def heal(self, amount):
        self.hp += amount
        self.clamp_stats()

    def take_damage(self, amount):
        self.hp -= amount
        self.state = 'hit'
        self.frame = 0
        self.clamp_stats()

        if self.hp <= 0:
            self.hp = 0
            self.state = 'death'
            self.frame = 0

    def updateimg(self):
        self.image = pygame.image.load(
            f'gfx/player/{self.direction}/{self.state}/{self.state}{int(self.frame)}.png'
        ).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 2)

    def update_attack_box(self):
        self.attack_box = pygame.Rect(0, 0, self.attack_range, self.attack_range)

        if self.direction == 'up':
            self.attack_box.midbottom = self.hitbox.midtop
        elif self.direction == 'down':
            self.attack_box.midtop = self.hitbox.midbottom
        elif self.direction == 'left':
            self.attack_box.midright = self.hitbox.midleft
        else:
            self.attack_box.midleft = self.hitbox.midright

    def get_world_attack_box(self, camera_x, camera_y):
        self.update_attack_box()
        return self.attack_box.move(camera_x, camera_y)

    def perform_attack(self, friendly_group, enemy_group, camera_x, camera_y):
        if self.state != 'attack' or self.attack_has_hit:
            return

        world_attack_box = self.get_world_attack_box(camera_x, camera_y)

        for target in list(friendly_group.sprites()) + list(enemy_group.sprites()):
            if getattr(target, 'is_dead', False):
                continue

            target_hitbox = target.hitbox if getattr(target, 'hitbox', None) is not None else target.rect
            if target_hitbox.colliderect(world_attack_box):
                target.take_damage(self.attack_damage, self)

        self.attack_has_hit = True

    def update(self):
        self.updateimg()

        keys = pygame.key.get_pressed()

        moving = (
            keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d] or
            keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
        )

        sprint_key = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction = 'up'
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction = 'down'
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction = 'left'
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction = 'right'

        if keys[pygame.K_1]:
            self.held_item = 'sword'
        if keys[pygame.K_2]:
            self.held_item = 'axe'
        if keys[pygame.K_3]:
            self.held_item = 'pickaxe'

        self.attack_cooldown -= 0.05
        if self.attack_cooldown < 0:
            self.attack_cooldown = 0
            if self.state not in ['death', 'hit']:
                self.state = 'idle'

        self.is_sprinting = (
            moving and
            sprint_key and
            self.stamina > 0 and
            self.state not in ['hit', 'attack', 'death'] and
            self.attack_cooldown <= 0
        )

        if self.attack_cooldown == 0:
            if moving:
                if self.state not in ['hit', 'attack', 'death']:
                    self.state = 'walk'
            else:
                if self.state not in ['hit', 'attack', 'death']:
                    self.state = 'idle'

        mousekeys = pygame.mouse.get_pressed()
        if (keys[pygame.K_SPACE] or mousekeys[0]) and self.attack_cooldown <= 0:
            if self.state not in ['hit', 'death']:
                self.state = 'attack'
                self.frame = -0.2
                self.attack_cooldown = 1
                self.is_sprinting = False
                self.attack_has_hit = False

        if self.state not in ['hit', 'attack', 'death']:
            if self.is_sprinting:
                self.stamina -= self.sprint_drain
                if self.stamina <= 0:
                    self.stamina = 0
                    self.is_sprinting = False
            elif moving:
                self.stamina += self.walk_stamina_regen
            else:
                self.stamina += self.idle_stamina_regen

        self.clamp_stats()
        self.update_attack_box()

        self.frame += 0.2

        if self.state == 'idle':
            if self.frame > 11:
                self.frame = 0

        if self.state == 'walk':
            if self.frame > 5:
                self.frame = 0

        if self.state == 'hit':
            if self.frame > 3:
                self.frame = 0
                if self.hp > 0:
                    self.state = 'idle'

        if self.state == 'attack':
            if self.frame > 6:
                self.frame = 0

        if self.state == 'death':
            if self.frame > 7:
                self.frame = 7