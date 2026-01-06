import pygame, sys, os
class CC(pygame.sprite.Sprite): # Character Controller
    def __init__(self, groups):
        super().__init__(groups)
        
        self.screen = pygame.display.get_surface()
        
        self.x = pygame.display.get_surface().get_width() / 2
        self.y = pygame.display.get_surface().get_height() / 2
        self.pos = (self.x, self.y)
        
        
        self.state = "idle"
        self.direction = "down"
        self.frame = 0
        self.image = pygame.image.load(f"gfx/player/{self.direction}/{self.state}/{self.state}{self.frame}.png").convert_alpha()
        self.rect = self.image.get_rect(bottomright = (self.screen.get_width() / 2, self.screen.get_height() / 2))
        
        #
    
    def updateimg(self):
        self.image = pygame.image.load(f"gfx/player/{self.direction}/{self.state}/{self.state}{int(self.frame)}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.rect.width * 2, self.rect.height * 2)) 
        
        
    def update(self): #TODO
        
        
        self.updateimg()
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.state = "walk"
            self.direction = "up"
        elif keys[pygame.K_s]:
            self.state = "walk"
            self.direction = "down"
        elif keys[pygame.K_a]:
            self.state = "walk"
            self.direction = "left"
        elif keys[pygame.K_d]:
            self.state = "walk"
            self.direction = "right"
        else:
            if self.state != "hit" and self.state != "attack" and self.state != "death":
                self.state = "idle"
        
        self.frame += 0.2
        
        if self.state == "idle":
            if self.frame > 11:
                self.frame = 0 
                
        if self.state == "walk":
            if self.frame > 5:
                self.frame = 0
        
        if self.state == "hit":
            if self.frame > 3:
                self.frame = 0
                self.state = "idle"
        
        if self.state == "attack":
            if self.frame > 6:
                self.frame = 0
                self.state = "idle"
        
        if self.state == "death":
            if self.frame > 7:
                self.frame = 7