import pygame, sys, os
class CC(pygame.sprite.Sprite): # Character Controller
    def __init__(self, groups, x = 0, y = 0):
        super().__init__(groups)
        
        self.x = x
        self.y = y
        
        self.pos = (self.x, self.y)
        
    def update(self): #TODO
        pass 