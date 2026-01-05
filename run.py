import pygame
from NOQA.settings_handling import *
from NOQA.engine import *

if __name__ == "__main__":
    window_configs = window_configs_setup()
    LANG = game_lang_load()
    game_engine = engine(window_configs, LANG)

    while True:
        game_engine.run()
        pygame.display.flip()

        game_engine.dt = game_engine.clock.tick() / 1000
