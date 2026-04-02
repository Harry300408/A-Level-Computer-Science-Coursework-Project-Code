import pygame
from NOQA.settings_handling import *
from NOQA.engine import *

if __name__ == "__main__":
    settings = load_settings()
    window_configs = settings_to_window_configs(settings)
    game_engine = engine(window_configs, settings["language"], settings)

    while True:
        if game_engine.menu_state == "start_menu":
            game_engine.main_menu()
        elif game_engine.menu_state == "game":
            game_engine.run()
        elif game_engine.menu_state == "pause_menu":
            game_engine.pause_menu()
        elif game_engine.menu_state == "settings_menu":
            game_engine.settings_menu()
        elif game_engine.menu_state == "game_over_menu":
            game_engine.game_over_menu()
        
        pygame.display.flip()

        game_engine.dt = game_engine.clock.tick(game_engine.FPS) / 1000 
