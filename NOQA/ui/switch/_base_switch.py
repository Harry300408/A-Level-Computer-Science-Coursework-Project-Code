import pygame, sys
from NOQA.ui._base_ui_element import ui_element


class switcher(ui_element):
    def __init__(self, pos, img_off = None, img_on = None, hint_text = "MISSING_HINT_TEXT"): # NONE is default image
        super().__init__(pos, img_off, hint_text)
        if img_on == None:                  self.img_on = pygame.image.load('gfx/ui/defaults/ui_element.png').convert_alpha()
        else:                               self.img_on = pygame.image.load(img_on).convert_alpha()