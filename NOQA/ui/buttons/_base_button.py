import pygame, sys
from NOQA.ui._base_ui_element import ui_element


class Button(ui_element):
    def __init__(self, pos, img, hover_img, button_txt, fontsize, font_colour, hover_colour, hint_text = "MISSING_HINT_TEXT"):
        super().__init__(pos, img, hint_text)

        if hover_img == None:                   self.hover_img = pygame.image.load('gfx/ui/defaults/ui_element.png').convert_alpha()
        else:                                   self.hover_img = pygame.image.load(hover_img).convert_alpha()

        self.bg = self.img

        self.fontsize               = fontsize
        self.font_colour            = font_colour
        self.text                   = button_txt
        self.button_text_font       = pygame.font.Font("gfx/fonts/ui/Enhance 1.0.ttf", self.fontsize)
        self.button_txt             = self.button_text_font.render(self.text, True, self.font_colour)
        self.button_txt_rect        = self.button_txt.get_rect(center=(self.x_pos, self.y_pos))
        self.hover_colour           = hover_colour
        self.hovered                = False    


    def update(self):
        self.draw_self()

        self.mouse_pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(self.mouse_pos): 
            self.on_hover()
            self.bg         = self.hover_img
            self.button_txt = self.button_text_font.render(self.text, True, self.hover_colour)
            self.hovered    = True

        else:
            if self.hovered:
                self.bg         = self.img
                self.button_txt = self.button_text_font.render(self.text, True, self.font_colour)
                self.hovered    = False
            else: 
                pass

    def draw_self(self):
        pygame.display.get_surface().blit(self.bg, self.rect)
        pygame.display.get_surface().blit(self.button_txt, self.button_txt_rect)

    
