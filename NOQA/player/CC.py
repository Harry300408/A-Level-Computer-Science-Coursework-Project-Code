import pygame, sys, os
class CC(pygame.sprite.Sprite): # Character Controller
    def __init__(self, groups):
        super().__init__(groups)
        
        self.screen = pygame.display.get_surface()
        
        self.x = pygame.display.get_surface().get_width() / 2
        self.y = pygame.display.get_surface().get_height() / 2
        self.pos = (self.x, self.y)
        
        self._ID = "CharacterController"
        
        
        self.state = "idle"
        self.direction = "down"
        self.attack_cooldown = 0
        self.frame = 0
        self.image = pygame.image.load(f"gfx/player/{self.direction}/{self.state}/{self.state}{self.frame}.png").convert_alpha()
        self.rect = self.image.get_rect(center = (self.screen.get_width() / 2, self.screen.get_height() / 2))
        self.rect = self.rect.scale_by(-2)
        self.rect = self.rect.inflate(0, -40)
        
        self.hitbox = self.image.get_rect(center = (self.screen.get_width() / 2, self.screen.get_height() / 2))
        self.hitbox = self.hitbox.scale_by(0.5)
        self.hitbox = self.hitbox.inflate(0, 10)
        self.hitbox = self.hitbox.move(0, 25)
        
    
    def updateimg(self):
        self.image = pygame.image.load(f"gfx/player/{self.direction}/{self.state}/{self.state}{int(self.frame)}.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 2)
        
    def update(self): 
        
        
        self.updateimg()
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.direction = "up"
        elif keys[pygame.K_s]:
            self.direction = "down"
        elif keys[pygame.K_a]:
            self.direction = "left"
        elif keys[pygame.K_d]:
            self.direction = "right"
        
        self.attack_cooldown -= 0.05
        if self.attack_cooldown < 0:
            self.attack_cooldown = 0
            self.state = "idle"
        
        if self.attack_cooldown == 0:
            if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
                self.state = "walk"
                
            else:
                if self.state != "hit" and self.state != "attack" and self.state != "death":
                    self.state = "idle"
                
        mousekeys = pygame.mouse.get_pressed()
        if (keys[pygame.K_SPACE] or mousekeys[0]) and not self.attack_cooldown > 0:
            if self.state != "hit" and self.state != "death":
                self.state = "attack"
                self.frame = -0.2
                self.attack_cooldown = 1
                
        
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
        
        if self.state == "death":
            if self.frame > 7:
                self.frame = 7
        
        