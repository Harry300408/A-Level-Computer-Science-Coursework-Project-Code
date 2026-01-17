import pygame

class Slider():
        def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int) -> None:
                self.pos = pos
                self.size = size
               
                self.slider_left_pos = self.pos[0] - (size[0]//2)
                self.slider_right_pos = self.pos[0] + (size[0]//2)
                self.slider_top_pos = self.pos[1] - (size[1]//2)
               
                self.min = min
                self.max = max
                self.dragging = False
               
                self.container_rect = pygame.Rect(
                        self.slider_left_pos,
                        self.slider_top_pos,
                        self.size[0],
                        self.size[1]
                )

                button_x = self.slider_left_pos + int(self.size[0] * initial_val)
                self.button_rect = pygame.Rect(button_x - 5, self.slider_top_pos, 10, self.size[1])

        def render(self, app):
                # Draw slider bar
                pygame.draw.rect(app, "darkgrey", self.container_rect)
                pygame.draw.rect(app, "blue", self.button_rect)

                # Mouse logic
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()[0]

                if self.button_rect.collidepoint(mouse_pos) and mouse_pressed:
                        self.dragging = True

                if not mouse_pressed:
                        self.dragging = False

                if self.dragging:
                        self.button_rect.x = mouse_pos[0] - 5
                        self.button_rect.x = max(self.slider_left_pos,
                                                 min(self.button_rect.x, self.slider_right_pos - 10))

                return self.get_value()

        def get_value(self):
                # Convert slider position to value
                relative_pos = self.button_rect.x - self.slider_left_pos
                value = (relative_pos / self.size[0]) * (self.max - self.min) + self.min
                return value