import pygame, sys
from _base_ui_element import ui_element


class Button(ui_element):
    def __init__(self, pos, img, hover_img, button_txt, fontsize, hover_colour, hint_text = "MISSING_HINT_TEXT"):
        self.x_pos = pos[0]
        self.y_pos = pos[1]

        if img == None:                         self.img = pygame.image.load('gfx/ui/defaults/button.png').convert_alpha()
        else:                                   self.img = pygame.image.load(img).convert_alpha()

        if hover_img == None:                   self.hover_img = pygame.image.load('gfx/ui/defaults/button.png').convert_alpha()
        else:                                   self.hover_img = pygame.image.load(hover_img).convert_alpha()
        
        self.rect = self.img.get_rect(center=(self.x_pos, self.y_pos))

        self.bg = self.img

        self.fontsize               = fontsize
        self.text                   = button_txt
        self.button_text_font       = pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", self.fontsize)
        self.button_txt             = self.button_text_font.render(self.text, True, (255, 255, 255))
        self.button_txt_rect        = self.button_txt.get_rect(center=(self.x_pos, self.y_pos))
        self.hover_colour           = hover_colour

        self.hint_text          = hint_text
        self.hint_box_font      = pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", 20)
        self.textbox_txt        = self.hint_box_font.render(self.hint_text, True, (255, 255, 255))
        self.textbox_txt_rect   = self.textbox_txt.get_rect()

    def update(self):
        self.draw_self()

        self.mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(self.mouse_pos): 
            self.on_hover()
            self.bg = self.hover_img
            self.button_txt = self.button_text_font.render(self.text, True, self.hover_colour)
        else:
            self.bg         = self.img
            self.button_txt = self.button_text_font.render(self.text, True, (255, 255, 255))

    def draw_self(self):
        pygame.display.get_surface().blit(self.bg, self.rect)
        pygame.display.get_surface().blit(self.button_txt, self.button_txt_rect)

    def check_for_update(self):
        if self.rect.collidepoint(self.mouse_pos):  return True
        else:                                       return False
