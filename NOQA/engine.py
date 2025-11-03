import sys, os, pygame, json, configparser

class engine():
    def __init__(self, configs, LANG):
        self.XRES = configs[0]
        self.YRES = configs[1]
        self.FPS = configs[3]
        self.dt = 0
    
        pygame.init()

        self.screen = pygame.display.set_mode((self.XRES, self.YRES))

        if configs[2] == "True":
            self.FULLSCREEN = configs[2]
            pygame.display.toggle_fullscreen()

        self.clock = pygame.time.Clock()

    def run(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()