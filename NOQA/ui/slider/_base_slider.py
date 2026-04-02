import pygame

class Slider():
        def __init__(self, pos: tuple, size: tuple, initial_val: float, min_value: int, max_value: int) -> None:
                self.pos = pos
                self.size = size
                self.handle_offset = 5
               
                self.slider_left_pos = self.pos[0] - (size[0]//2)
                self.slider_right_pos = self.pos[0] + (size[0]//2)
                self.slider_top_pos = self.pos[1] - (size[1]//2)
                self.travel_width = max(1, self.size[0] - (self.handle_offset * 2))
               
                self.min = min_value
                self.max = max_value
                self.dragging = False
               
                self.container_rect = pygame.Rect(
                        self.slider_left_pos,
                        self.slider_top_pos,
                        self.size[0],
                        self.size[1]
                )

                self.button_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, 20, self.size[1])
                self.set_normalized_value(initial_val)
                

        def update(self, display):
                # Draw slider bar
                pygame.draw.rect(display, "#671E1EFF", self.container_rect, border_radius=10)
                pygame.draw.circle(display, "#AE2424FF", (self.button_rect.x + 5, self.button_rect.y + (self.size[1]//2)), 15)
                

                # Mouse logic
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()[0]

                if self.button_rect.collidepoint(mouse_pos) and mouse_pressed:
                        self.dragging = True

                if not mouse_pressed:
                        self.dragging = False

                if self.dragging:
                        self.button_rect.x = mouse_pos[0] - self.handle_offset
                        self.button_rect.x = max(self.slider_left_pos,
                                                 min(self.button_rect.x, self.slider_right_pos - (self.handle_offset * 2)))

                return self.get_value()

        def get_value(self):
                # Convert slider position to value
                relative_pos = self.button_rect.x - self.slider_left_pos
                value = (relative_pos / self.travel_width) * (self.max - self.min) + self.min
                return value

        def set_normalized_value(self, normalized_value: float):
                normalized_value = max(0, min(1, float(normalized_value)))
                self.button_rect.x = self.slider_left_pos + int(self.travel_width * normalized_value)

        def set_value(self, value: float):
                value = max(self.min, min(self.max, float(value)))

                if self.max == self.min:
                        normalized_value = 0
                else:
                        normalized_value = (value - self.min) / (self.max - self.min)

                self.set_normalized_value(normalized_value)
