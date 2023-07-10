import pygame

class Key:
    """Basic class for keys.
           Keyword arguments:
            x,y, - position on the screen
            size - height and width of the button
            color1 - color of text
            color2 - The color of the text when the mouse is hovered
            key - key
            """

    def __init__(self, x, y, color1, color2=None, key=None, size=[89, 40]):
        self.x = x
        self.y = y
        self.color1 = color1
        self.color2 = color2
        self.key = key
        self.rect = pygame.Rect(self.x, self.y, size[0], size[1])
        self.handled = False

class Button:
    """Basic class for creating buttons.
       Keyword arguments:
        image - background for button
        pos - position on the screen in pixels x,y
        text_input - button text
        font - font
        base_color - color of text
        hovering color - The color of the text when the mouse is hovered
        """
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        """Draws a button on the screen."""
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        """Changes color when the mouse is over the button"""
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        """Changes color of text"""
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
