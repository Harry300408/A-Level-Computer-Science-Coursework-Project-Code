import pygame, sys
from mouse.mouse import mouse

class ui_element():
    def __init__(self, pos, img, hint_text = "MISSING_HINT_TEXT"):
        self.x_pos = pos[0]
        self.y_pos = pos[1]

        if img == None:                 self.img = pygame.image.load('gfx/ui/defaults/ui_element.png').convert_alpha()
        else:                           self.img = pygame.image.load(img).convert_alpha()
            
        self.rect = self.img.get_rect(center=(self.x_pos, self.y_pos))
        
        self.mouse_pos = pygame.mouse.get_pos()
        
        ## TEXTBOX
        self.hint_text = hint_text
        self.hint_box_font = pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", 20)
        self.textbox_txt = self.hint_box_font.render(self.hint_text, True, (255, 255, 255))
        self.textbox_txt_rect = self.textbox_txt.get_rect()

    def update(self):
        self.draw_self()

        self.mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(self.mouse_pos): self.on_hover()

    def draw_self(self):
        pygame.display.get_surface().blit(self.img, self.rect)
     

    def on_hover(self):
        pygame.draw.rect(pygame.display.get_surface(), (43, 43, 43), pygame.Rect(self.mouse_pos[0] + 5, self.mouse_pos[1] + 10, self.textbox_txt_rect.width + 20, self.textbox_txt_rect.height + 10))  
        pygame.draw.rect(pygame.display.get_surface(), (97, 97, 97), pygame.Rect(self.mouse_pos[0] + 8, self.mouse_pos[1] + 13, self.textbox_txt_rect.width + 14.5, self.textbox_txt_rect.height + 4.25))  
        pygame.display.get_surface().blit(self.textbox_txt, (self.mouse_pos[0] + 15, self.mouse_pos[1] + 15))
