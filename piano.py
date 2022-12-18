from button import *
import sys
from playsound import *
from ctypes import *

width = windll.user32.GetSystemMetrics(0)
height = windll.user32.GetSystemMetrics(1)

def get_font(size):
    """Returns Press-Start-2P in the desired size."""
    return pygame.font.Font("assets/JosefinSans-Bold.ttf", size)

def error2(string, screen):
    """Calls up an error window in the program if something went wrong.
       Keyword arguments:
           string - error text
    """
    bg = pygame.image.load("assets/background.png").convert()
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    back_btn = Button(image=None,
                      pos=(width / 2, height / 2),
                      text_input="Okay", font=get_font(30), base_color="#d7fcd4",
                      hovering_color="GREEN")
    while True:
        menu_mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.checkForInput(menu_mouse_pos):
                    screen.blit(bg, (0, 0))
                    return
        error_text = get_font(30).render(string, True, "RED")
        error_rect = error_text.get_rect(center=(width / 2, height / 2 - 150))
        screen.blit(error_text, error_rect)
        back_btn.changeColor(menu_mouse_pos)
        back_btn.update(screen)
        pygame.display.update()


class PianoGame:
    """Сlass for piano game.
            Keyword arguments:
            hit_sound - sound on the click
        """

    def __init__(self, screen, width, height, font):
        self.font = font
        self.bg = pygame.image.load("piano_assets/piano_background.jpg").convert()
        self.width = width
        self.height = height
        self.screen = screen
        self.escape = font.render("Press escape to leave", True, "Gray")
        self.keys = [
            Key(float(self.width) / 2 - 350, float(self.height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_s),  # 100
            Key(float(self.width) / 2 - 250, float(self.height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_d),  # 200
            Key(float(self.width) / 2 - 150, float(self.height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_f),  # 300
            Key(float(self.width) / 2 - 50, float(self.height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_g),  # 400
            Key(float(self.width) / 2 + 50, float(self.height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_j),  # 400
            Key(float(self.width) / 2 + 150, float(self.height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_k),  # 400
            Key(float(self.width) / 2 + 250, float(self.height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_l),  # 400
        ]
    def start(self):
        self.start_game()

    def start_game(self):
        """Start the game."""
        self.screen.fill((0, 0, 0))
        for key in self.keys:
            pygame.draw.rect(self.screen, key.color2, key.rect)
        while True:
            pygame.display.flip()
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.bg, (self.width / 2 - 350, self.height / 2 - 380))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.screen.fill((0, 0, 0))
                        return
                    if event.key == pygame.K_s:
                         playsound('piano_assets/C.mp3', block=False)
                    if event.key == pygame.K_d:
                        playsound('piano_assets/Do.mp3', block=False)
                    if event.key == pygame.K_f:
                        playsound('piano_assets/Fa.mp3', block=False)
                    if event.key == pygame.K_g:
                        playsound('piano_assets/Lya.mp3', block=False)
                    if event.key == pygame.K_j:
                        playsound('piano_assets/Mi.mp3', block=False)
                    if event.key == pygame.K_k:
                        playsound('piano_assets/Re.mp3', block=False)
                    if event.key == pygame.K_l:
                        playsound('piano_assets/Sol.mp3', block=False)

            k = pygame.key.get_pressed()
            for key in self.keys:
                if k[key.key]:
                    pygame.draw.rect(self.screen, key.color1, key.rect)
                    key.handled = False
                if not k[key.key]:
                    pygame.draw.rect(self.screen, key.color2, key.rect)
                    key.handled = True
