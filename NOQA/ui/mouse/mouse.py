import pygame, sys
sys.path.append("././")

class mouse():
    def __init__(self):
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.get_surface()
        self.location = pygame.mouse.get_pos()
        self.image = pygame.image.load("gfx/ui/mouse/mouse1.png").convert_alpha()
        self.imagerect = self.image.get_rect(center=self.location)
        self.wheelofdeath_frame = 0
        
        self.throb = False
        self.throb_anim_time = 200
        self.throb_time = 0

        self.temp = False

    def update_img(self):
        keys = pygame.mouse.get_pressed()

        if keys[0]:
            self.image = pygame.image.load("gfx/ui/mouse/mouse2.png").convert_alpha()

        elif self.temp: ## TODO - Update with func
            self.image = pygame.image.load("gfx/ui/mouse/mouse4.png").convert_alpha()
        
        elif self.temp: ## TODO - Update with func
            self.image = pygame.image.load("gfx/ui/mouse/mouse3.png").convert_alpha()
        
        elif self.temp: ## TODO - Update with func
            if self.wheelofdeath_frame == 8:
                self.wheelofdeath_frame = 0
            
            if not self.throb: 

                if self.wheelofdeath_frame == 0:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame1.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 

                elif self.wheelofdeath_frame == 1:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame2.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 2:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame3.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 3:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame4.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 4:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame5.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 5:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame6.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 6:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame7.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 7:
                    self.image = pygame.image.load("gfx/ui/mouse/throbber/frame8.png").convert_alpha()
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 

        else:
            self.image = pygame.image.load("gfx/ui/mouse/mouse1.png").convert_alpha()
    
    def throbcooldown(self):
        current_time = pygame.time.get_ticks()
        if self.throb:
            if current_time - self.throb_time >= self.throb_anim_time:
                self.throb = False

    def update(self):
        self.location = pygame.mouse.get_pos()
        self.throbcooldown()
        self.update_img()
        self.imagerect = self.image.get_rect(center=self.location)
        self.screen.blit(self.image, self.imagerect)