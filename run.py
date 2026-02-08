import pygame
from NOQA.settings_handling import *
from NOQA.engine import *

if __name__ == "__main__":
    window_configs = window_configs_setup()
    LANG = game_lang_load()
    game_engine = engine(window_configs, LANG)

    while True:
        if game_engine.menu_state == "main_menu":
            game_engine.main_menu()
        elif game_engine.menu_state == "game":
            game_engine.run()
        
        pygame.display.flip()

        game_engine.dt = game_engine.clock.tick(game_engine.FPS) / 1000 
