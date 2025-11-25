import pygame, sys
from NOQA.ui._base_ui_element import ui_element


class switcher(ui_element):
    def __init__(self, pos, img_off = None, img_on = None, hint_text = "MISSING_HINT_TEXT"): # NONE is default image
        self.x_pos = pos[0]
        self.y_pos = pos[1]