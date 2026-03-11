import math

from NOQA.entities.base_entity import BaseEntity


class EnemyAI(BaseEntity):
    def __init__(self, groups, pos, image_path=None):
        super().__init__(
            groups,
            pos,
            image_path=image_path,
            fallback_color=(210, 90, 90),
            image_size=(28, 36),
            entity_type='enemy',
            max_hp=45,
            move_speed=1.8,
            attack_damage=5,
            attack_range=50,
            attack_cooldown_max=3.0,
            heal_on_kill=12,
            solid=True,
        )

        self.view_radius = 220
        self.stop_radius = 34
        self.path = []
        self.path_refresh_timer = 0
        self.hit_flash_color = (255, 60, 60)

    def update(self, engine=None):
        super().update(engine)

        if self.is_dead or engine is None:
            return

        player = engine.get_player_sprite()
        player_hitbox = engine.get_player_world_hitbox()

        if player is None or player_hitbox is None:
            return

        player_x, player_y = player_hitbox.center
        dist_to_player = self.distance_to(player_x, player_y)

        self.face_towards(player_x, player_y)

        if dist_to_player <= self.stop_radius:
            self.state = 'idle'
            self.attack_player_if_possible(player, player_hitbox)
            return

        if dist_to_player > self.view_radius:
            self.state = 'idle'
            self.path.clear()
            return

        self.path_refresh_timer -= 1

        if self.path_refresh_timer <= 0 or not self.path:
            self.path = engine.find_path(
                (self.world_x, self.world_y),
                (player_x, player_y),
                ignore_entity=self,
                max_nodes=1200,
            )
            self.path_refresh_timer = 15

        if self.path:
            target_x, target_y = self.path[0]

            if math.hypot(target_x - self.world_x, target_y - self.world_y) <= max(4, self.move_speed + 1):
                self.path.pop(0)
            else:
                moved = self.move_towards(target_x, target_y, self.move_speed, engine)
                if not moved:
                    self.path_refresh_timer = 0
        else:
            self.move_towards(player_x, player_y, self.move_speed, engine)