import pygame, sys

class mouse():                                                                                                      ## Mouse class
    def __init__(self) -> None:                                                                                     ## Instantiation method
        pygame.mouse.set_visible(False)                                                                             ## Makes the Windows' mouse invisible
        self.screen = pygame.display.get_surface()                                                                  ## Gets the surface
        self.state = None
        self.location = pygame.mouse.get_pos()                                                                      ## Get's mouse pos on the window
        self.mouse_info = None
        self.frames = {
            0   :       pygame.image.load("gfx/gui/mouse/mouse1.png").convert_alpha(),                                        ## Default mouse image
            1   :       pygame.image.load("gfx/gui/mouse/mouse2.png").convert_alpha(),                                        ## Mouse click image
            2   :       pygame.image.load("gfx/gui/mouse/mouse3.png").convert_alpha(),                                        ## Typing image (unused)
            3   :       pygame.image.load("gfx/gui/mouse/mouse4.png").convert_alpha(),                                        ## Unavalible image (unused)

            4   :       pygame.image.load("gfx/gui/mouse/throbber/frame1.png").convert_alpha(),                                   ## Throbber frame 1
            5   :       pygame.image.load("gfx/gui/mouse/throbber/frame2.png").convert_alpha(),                                   ## Throbber frame 2 
            6   :       pygame.image.load("gfx/gui/mouse/throbber/frame3.png").convert_alpha(),                                   ## Throbber frame 3
            7   :       pygame.image.load("gfx/gui/mouse/throbber/frame4.png").convert_alpha(),                                   ## Throbber frame 4
            8   :       pygame.image.load("gfx/gui/mouse/throbber/frame5.png").convert_alpha(),                                   ## Throbber frame 5
            9   :       pygame.image.load("gfx/gui/mouse/throbber/frame6.png").convert_alpha(),                                   ## Throbber frame 6
            10  :       pygame.image.load("gfx/gui/mouse/throbber/frame7.png").convert_alpha(),                                  ## Throbber frame 7
            11  :       pygame.image.load("gfx/gui/mouse/throbber/frame8.png").convert_alpha(),                                   ## Throbber frame 8
        
            12  :       pygame.image.load("gfx/tools/Hoe.png").convert_alpha(), 
            13  :       pygame.image.load("gfx/tools/Hammer.png").convert_alpha(),  
            14  :       pygame.image.load("gfx/tools/Watering Can.png").convert_alpha(),  
            15  :       pygame.image.load("gfx/tools/Fertlizer.png").convert_alpha(),    
            16  :       pygame.image.load("gfx/tools/Shovel.png").convert_alpha(),     
            17  :       pygame.image.load("gfx/tools/Scythe.png").convert_alpha(),      
                         
        }
        self.image = self.frames[0]                                  ## Default image
        self.imagerect = self.image.get_rect(center=self.location)                                                  ## Sets rect for the image referencing the position
    
        self.wheelofdeath_frame = 0                                                                                 ## Current throbber frame
        self.throb = False                                                                                          ## If throbing (loading)
        self.throb_anim_time = 200                                                                                  ## Anim time (used for cool down)
        self.throb_time = 0                                                                                         ## Sets throb time to 0 (later refs ticks)

        self.temp = False                                                                                           ## For unused images, skips parts but functionality is there

    def update_img(self):                                                                                           ## Update img method
        keys = pygame.mouse.get_pressed()                                                                           ## Gets pressed mouse key

        if keys[0]:                                                                                                 ## Checks to see if right key
            self.image = self.frames[1]                                                                                          ## Sets image to clicking 

        elif self.temp: ## TODO - Update with func                                                                  
            self.image = self.frames[3]                                                                             ## Unavalible gfx for unusable items n' stuff
        
        elif self.temp: ## TODO - Update with func
            self.image = self.frames[2]                                                                             ## For typing (most likly will never be used)
        
        elif self.temp: ## TODO - Update with func                                                                  ## Loading wheel cycle
            if self.wheelofdeath_frame == 8:
                self.wheelofdeath_frame = 0
            
            if not self.throb: 

                if self.wheelofdeath_frame == 0:
                    self.image = self.frames[4]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 

                elif self.wheelofdeath_frame == 1:
                    self.image = self.frames[5]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 2:
                    self.image = self.frames[6]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 3:
                    self.image = self.frames[7]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 4:
                    self.image = self.frames[8]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 5:
                    self.image = self.frames[9]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 6:
                    self.image = self.frames[10]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 
            
                elif self.wheelofdeath_frame == 7:
                    self.image = self.frames[11]
                    self.wheelofdeath_frame += 1
                    self.throb = True
                    self.throb_time = pygame.time.get_ticks() 

        else:                                                                                                       ## Defaults to orignial image
            self.image = self.frames[0]                                                                             ## Sets image to default
    
    def throbcooldown(self):                                                                                        ## Cooldown timer for throber
        current_time = pygame.time.get_ticks()                                                                      ## Gets current tick
        if self.throb:                                                                                              ## Check to see if loading (throbbing)
            if current_time - self.throb_time >= self.throb_anim_time:                                              ## Little bit of maths to calc if time passed is sufficient
                self.throb = False                                                                                  ## Allows it to move to the next anim

    def draw(self):                                                                                                 ## Draw mouse method
        self.location = pygame.mouse.get_pos()                                                                      ## Gets mouse pos
        self.imagerect = self.image.get_rect(center=self.location)                                                  ## Gets rect four image and pos        
        
        
                                                                                             
    def update(self, extra_info, game_state):                                                                                               ## Update method
        self.mouse_info = extra_info                                                                                  ## Gets the extra info (used for other classes)
        self.throbcooldown()                                                                                        ## Checks the cooldown
        self.update_img()