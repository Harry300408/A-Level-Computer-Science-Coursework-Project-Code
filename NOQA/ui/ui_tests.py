import pygame,sys
from _base_ui_element import ui_element
from mouse.mouse import mouse
from buttons._base_button import Button
from switch._base_switch import switcher

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    uielement = ui_element((200, 50), None, "Ben is amazing")
    cursor = mouse()
    
    test_button2 = Button((300, 200), "gfx/ui/menus/button/menu_button.png", "gfx/ui/menus/button/menu_button_hovered.png", "Test Button", 40, (255, 100, 25), (0, 0, 25), "This is a test button being hovered")
    switch = switcher((300, 100), None, None, "This is a test switch being hovered")

    gui_elements = [test_button2, switch, uielement]
    buttons = [test_button2]
    switches = [switch]

    while True:
        screen.fill((0, 0, 0))

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
                        print("Toggled")



        for i in gui_elements:
            i.update()

        cursor.update()

        pygame.display.flip()


