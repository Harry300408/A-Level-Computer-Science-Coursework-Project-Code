import math
import random

from NOQA.entities.base_entity import BaseEntity


class FriendlyAI(BaseEntity):
    def __init__(self, groups, pos, image_path=None):
        super().__init__(
            groups,
            pos,
            image_path=image_path,
            fallback_color=(80, 200, 120),
            image_size=(26, 34),
            entity_type='friendly',
            max_hp=30,
            move_speed=1.4,
            attack_damage=0,
            attack_range=0,
            attack_cooldown_max=0.0,
            heal_on_kill=6,
            solid=True,
        )

        self.flee_radius = 110
        self.panic_timer = 0
        self.wait_timer = random.randint(20, 80)
        self.move_timer = 0
        self.roam_vector = (0, 0)
        self.hit_flash_color = (255, 180, 60)

    def take_damage(self, amount, source=None):
        super().take_damage(amount, source)

        if not self.is_dead:
            self.panic_timer = 180

    def _candidate_directions(self):
        return [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (-1, 1), (1, -1), (-1, -1),
        ]

    def pick_random_roam_direction(self, engine):
        directions = self._candidate_directions()
        random.shuffle(directions)

        for dx, dy in directions:
            test_x = self.world_x + (dx * self.move_speed)
            test_y = self.world_y + (dy * self.move_speed)

            if engine.can_ai_move_to(self, test_x, test_y):
                self.roam_vector = (dx, dy)
                self.move_timer = random.randint(30, 110)
                return True

        self.roam_vector = (0, 0)
        self.move_timer = 0
        self.wait_timer = random.randint(25, 60)
        return False

    def pick_escape_direction(self, engine, player_x, player_y):
        best_dir = None
        best_score = -1

        for dx, dy in self._candidate_directions():
            test_x = self.world_x + (dx * self.move_speed)
            test_y = self.world_y + (dy * self.move_speed)

            if not engine.can_ai_move_to(self, test_x, test_y):
                continue

            score = math.hypot(test_x - player_x, test_y - player_y)
            if score > best_score:
                best_score = score
                best_dir = (dx, dy)

        if best_dir is None:
            return False

        self.roam_vector = best_dir
        return True

    def update(self, engine=None):
        super().update(engine)

        if self.is_dead or engine is None:
            return

        player_hitbox = engine.get_player_world_hitbox()
        if player_hitbox is None:
            return

        player_x, player_y = player_hitbox.center
        dist_to_player = self.distance_to(player_x, player_y)

        if self.panic_timer > 0:
            self.panic_timer -= 1

        should_flee = self.panic_timer > 0 or dist_to_player < self.flee_radius

        if should_flee:
            escaped = self.move_away_from(player_x, player_y, self.move_speed * 1.2, engine)
            if not escaped:
                self.pick_escape_direction(engine, player_x, player_y)
                dx, dy = self.roam_vector
                self.try_move(dx * self.move_speed, dy * self.move_speed, engine)
            return

        if self.wait_timer > 0:
            self.wait_timer -= 1
            self.state = 'idle'
            return

        if self.move_timer <= 0 or self.roam_vector == (0, 0):
            if random.random() < 0.35:
                self.wait_timer = random.randint(20, 70)
                self.state = 'idle'
                return
            self.pick_random_roam_direction(engine)

        dx, dy = self.roam_vector
        moved = self.try_move(dx * self.move_speed, dy * self.move_speed, engine)

        if not moved:
            if not self.pick_random_roam_direction(engine):
                self.state = 'idle'
                return

        self.move_timer -= 1