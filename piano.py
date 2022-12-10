from button import *
import sys
from playsound import *

class PianoGame:
    """Сlass for piano game.
            Keyword arguments:
            hit_sound - sound on the click
        """

    def __init__(self, screen, width, height, font, record=False):
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
        self.record = record
    def start(self):
        if not self.record:
            self.start_game()
        else:
            self.start_game_record()

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

    def start_game_record(self):
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
