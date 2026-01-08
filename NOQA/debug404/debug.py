import pygame
pygame.font.init() 
font = pygame.font.Font(None,22)                                            

def debug404(info: list, y = 10, x = 10):                                           
    display_info = ""
    for i in info:
        if display_info == "":
            display_info += str(i)

        else:
            display_info += f"{str(i)}"
        
        display_info += "\n"
            
    display_suface = pygame.display.get_surface()                           
    
    debug_surf = font.render(str(display_info), True, "White").convert_alpha()    
    
    debug_rect = debug_surf.get_rect(topleft = (x, y))                    
    
    display_suface.blit(debug_surf, debug_rect)  # type: ignore                          