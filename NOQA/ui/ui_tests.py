import pygame,sys
from _base_ui_element import ui_element
from mouse.mouse import mouse
from buttons._base_button import Button
from switch._base_switch import switcher
from slider._base_slider import Slider

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    
    uielement = ui_element((200, 50), None, "Ben is amazing")
    
    cursor = mouse()
    
    slider = Slider((300, 500), (200, 20), 0.5, 0, 100)
    
    test_button = Button((300, 300), "gfx/ui/menus/button/button_bg.png", "gfx/ui/menus/button/button_pressed.png", "Jimmy", 40, (0, 0, 25), (0, 0, 25), "This is a test button being hovered")
    test_button2 = Button((300, 200), "gfx/ui/menus/button/menu_button.png", "gfx/ui/menus/button/menu_button_hovered.png", "Test Button", 40, (255, 100, 25), (0, 0, 25), "This is a test button being hovered")
    test_button3 = Button((300, 400), None, None, "No Img Button", 40, (25, 0, 25), (0, 0, 25), "This is a test button being hovered")
    
    switch = switcher((300, 100), "gfx/ui/menus/switcher/switcher_off.png", "gfx/ui/menus/switcher/switcher_on.png", True, "This is a test switch being \nhovered")

    gui_elements = [test_button, test_button2, test_button3, switch, uielement]
    buttons = [test_button, test_button2, test_button3]
    switches = [switch]

    

    while True:
        screen.fill((0, 0, 0))
        
        slider.update(screen)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in buttons:
                    if i.check_for_update():
                        print("Clicked")

                for i in switches:
                    if i.check_for_update():
                        i.state = not i.state


        for i in gui_elements:
            i.update()

        cursor.update()
        cursor.draw()

        pygame.display.flip()


