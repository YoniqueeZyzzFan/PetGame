import sys
from datetime import datetime

import pygame
from pygame import mixer

from button import *
from data_from_osu import *

pygame.mixer.pre_init(frequency=44100, size=-16, channels=4, buffer=512, devicename=None)

mixer.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 700), pygame.SCALED, vsync=1)
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 38)


class Key:
    def __init__(self, x, y, color1, color2=None, key=None, size=[89, 40]):
        self.x = x
        self.y = y
        self.color1 = color1
        self.color2 = color2
        self.key = key
        self.rect = pygame.Rect(self.x, self.y, size[0], size[1])
        self.handled = False


class HitGame:
    def __init__(self, path):
        self.hit_sound = pygame.mixer.Sound("assets/hit.wav")
        self.hit_sound.set_volume(0.01)
        self.combobreak_sound = pygame.mixer.Sound("assets/combo_break.mp3")
        self.combobreak_sound.set_volume(0.01)
        self.combo = 0
        self.hit = 0
        self.acc = 1
        self.all = 0
        self.end = 0
        self.song = path
        self.keys = [
            Key(100, 600, (0, 0, 0), (220, 220, 220), pygame.K_a),
            Key(200, 600, (0, 0, 0), (220, 220, 220), pygame.K_s),
            Key(300, 600, (0, 0, 0), (220, 220, 220), pygame.K_j),
            Key(400, 600, (0, 0, 0), (220, 220, 220), pygame.K_k),
        ]
        self.note_time = []
        self.min = 0
        self.map_rect = self.load(path)

    def load(self, map_data):
        rects = []
        f = open(map_data + ".txt", 'r')
        while True:
            data = f.readline()
            if data == "":
                break
            else:
                x, y, t = re.split(r',', data)
                if len(rects) > 0:
                    if rects[len(rects) - 1].x == int(x):
                        if self.note_time[len(self.note_time) - 1] == float(t):
                            continue
                        elif abs(self.note_time[len(self.note_time) - 1] - float(t)) < 300:
                            continue
                rects.append(pygame.Rect(int(x), 0, 50, 25))  # horizontal / vertical/ width / height
                self.note_time.append(float(t))
        self.end = len(rects)
        return rects

    def start_game(self):
        map_sound = pygame.mixer.Sound(self.song + ".mp3")
        map_sound.set_volume(0.04)
        t1 = datetime.now()
        map_sound.play()
        while True:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # handle key events
            k = pygame.key.get_pressed()
            for key in self.keys:
                if k[key.key]:
                    pygame.draw.rect(screen, key.color1, key.rect)
                    key.handled = False
                if not k[key.key]:
                    pygame.draw.rect(screen, key.color2, key.rect)
                    key.handled = True
            # start dropping hit sounds
            if self.min == self.end:
                break
            for rect in range(self.min, len(self.map_rect)):
                t2 = datetime.now()
                t = t2 - t1
                t = t.total_seconds() * 1000
                if t > self.note_time[rect] - 998:
                    pygame.draw.rect(screen, (200, 200, 200), self.map_rect[rect])
                    self.map_rect[rect].y += 10
                for key in self.keys:
                    if key.rect.colliderect(self.map_rect[rect]) and not key.handled:  # hit_square on hit_button
                        self.min += 1
                        self.hit_sound.play()
                        self.combo += 1
                        self.all += 1
                        self.hit += 1
                        key.handled = True
                        break
                if self.keys[0].rect.bottom < \
                        self.map_rect[rect].y:  # if the key is  lower than the key remove hit sound
                    self.min += 1
                    self.all += 1
                    if self.map_rect[rect].x == 119:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[0].rect)
                    elif self.map_rect[rect].x == 219:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[1].rect)
                    elif self.map_rect[rect].x == 319:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[2].rect)
                    else:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[3].rect)
                    self.combobreak_sound.play()
                    self.combo = 0
            text = font.render("combo:" + str(self.combo), True, "white")
            screen.blit(text, (550, 500))
            if self.all != 0:
                self.acc = self.hit * 100 / self.all
            else:
                self.acc = 100
            self.acc = round(self.acc, 2)
            accuracy = font.render("acc:" + str(self.acc), True, "white")
            screen.blit(accuracy, (550, 457))
            pygame.display.update()
        map_sound.stop()
        self.result()

    def result(self):
        result_sound = pygame.mixer.Sound("assets/ResultTable.mp3")
        result_sound.set_volume(0.3)
        result_sound.play()
        while True:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            text = font.render("Number of notes:" + str(self.all), True, "white")
            screen.blit(text, (250, 100))
            if self.all != 0:
                self.acc = self.hit * 100 / self.all
            else:
                self.acc = 100
            self.acc = round(self.acc, 2)
            accuracy = font.render("Accuracy:" + str(self.acc), True, "white")
            screen.blit(accuracy, (250, 150))
            hit_rate = font.render("Hit rate:" + str(self.hit), True, 'white')
            screen.blit(hit_rate, (250, 200))
            pygame.display.update()


def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/JosefinSans-Bold.ttf", size)


class PlayWindow:
    def __init__(self):
        self.bg = pygame.image.load("assets/background.png").convert()
        # self.credits = Button(50, 40, 200, 60, font, "Credits", lambda: webbrowser.open("https://vk.com/yoniquee"))
        self.start_btn = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(400, 500),
                                text_input="Start", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.change_map = Button(image=pygame.image.load("assets/Change_map.png"), pos=(400, 250),
                                 text_input="Change map", font=get_font(30), base_color="#d7fcd4",
                                 hovering_color="RED")
        self.quit_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(400, 600),
                               text_input="Back", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.sound = "Not selected"
        self.curr_sound = get_font(30).render(self.sound, True, "#b68f40")
        self.curr_rect = self.curr_sound.get_rect(center=(400, 350))
        self.btns = [self.start_btn, self.change_map, self.quit_btn]

    def open(self):
        screen.blit(self.bg, (0, 0))
        pygame.display.flip()
        exit = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            menu_mouse_pos = pygame.mouse.get_pos()
            menu_text = get_font(30).render("Let's start!", True, "#b68f40")
            menu_rect = menu_text.get_rect(center=(400, 50))

            screen.blit(menu_text, menu_rect)
            screen.blit(self.curr_sound, self.curr_rect)

            for button in self.btns:
                button.changeColor(menu_mouse_pos)
                button.update(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_btn.checkForInput(menu_mouse_pos):
                        try:
                            HitGame(self.sound)
                        except OSError:
                            screen.blit(self.bg, (0, 0))
                            pygame.display.flip()
                            exit_error = False
                            while True:
                                menu_mouse_pos = pygame.mouse.get_pos()
                                error_text = get_font(30).render("This map doesn't exist", True, "RED")
                                error_rect = error_text.get_rect(center=(400, 50))
                                screen.blit(error_text, error_rect)
                                back_btn = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(400, 250),
                                                  text_input="Back", font=get_font(30), base_color="#d7fcd4",
                                                  hovering_color="GREEN")
                                back_btn.changeColor(menu_mouse_pos)
                                back_btn.update(screen)
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        if back_btn.checkForInput(menu_mouse_pos):
                                            exit_error = True
                                            break
                                if exit_error:
                                    screen.blit(self.bg, (0, 0))
                                    break
                                pygame.display.update()
                        break
                    if self.change_map.checkForInput(menu_mouse_pos):
                        screen.blit(self.bg, (0, 0))
                        while True:
                            menu_mouse_pos = pygame.mouse.get_pos()
                            choose = get_font(30).render("Choose", True, "RED")
                            choose_rect = choose.get_rect(center=(400, 50))
                            screen.blit(choose, choose_rect)
                            back_btn = Button(image=None, pos=(400, 670),
                                              text_input="Back", font=get_font(30), base_color="#d7fcd4",
                                              hovering_color="GREEN")
                            back_btn.changeColor(menu_mouse_pos)
                            back_btn.update(screen)
                            for songs in range(0, len(list_of_maps)):
                                btn = Button(image=None, pos=(100, 30 + (int(songs) + 1) * 50),
                                             text_input=list_of_maps[songs], font=get_font(20), base_color="#d7fcd4",
                                             hovering_color="GREEN")
                                btn.changeColor(menu_mouse_pos)
                                btn.update(screen)
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                            pygame.display.update()
                        screen.blit(self.bg, (0, 0))
                        break
                    if self.quit_btn.checkForInput(menu_mouse_pos):
                        exit = True
                        break
            if exit:
                screen.blit(self.bg, (0, 0))
                break
            pygame.display.update()


class MainWindow:
    def __init__(self):
        self.bg = pygame.image.load("assets/background.png").convert()
        # self.credits = Button(50, 40, 200, 60, font, "Credits", lambda: webbrowser.open("https://vk.com/yoniquee"))
        self.play_btn = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(400, 150),
                               text_input="Play", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.export = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(400, 250),
                             text_input="Export", font=get_font(30), base_color="#d7fcd4",
                             hovering_color="RED")
        self.quit_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(400, 350),
                               text_input="Quit", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.btns = [self.play_btn, self.export, self.quit_btn]

    def open(self):
        screen.blit(self.bg, (0, 0))
        pygame.display.flip()
        while True:
            menu_mouse_pos = pygame.mouse.get_pos()
            menu_text = get_font(30).render("MAIN MENU", True, "#b68f40")
            menu_rect = menu_text.get_rect(center=(400, 50))

            screen.blit(menu_text, menu_rect)

            for button in self.btns:
                button.changeColor(menu_mouse_pos)
                button.update(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_btn.checkForInput(menu_mouse_pos):
                        play_window = PlayWindow()
                        play_window.open()
                    if self.export.checkForInput(menu_mouse_pos):
                        break
                    if self.quit_btn.checkForInput(menu_mouse_pos):
                        pygame.quit()

            pygame.display.update()


list_of_maps = []
list_of_diff = []

if __name__ == "__main__":
    pygame.init()
    f = open("maps/maps.txt")
    while True:
        map_set = f.readline()
        if map_set == "":
            break
        else:
            list_of_diff.append(map_set[len(map_set) - 1:])
            list_of_maps.append(map_set[:len(map_set) - 1])
    f.close()
    menu = MainWindow()
    menu.open()

# Add choosing maps - already created the buttons for list
# - back button on resulttalbe
# - record play
# - menu
# CHECK AUDIO IN - OSU CONF FILE AND + IT IN IF pygame draw rect
# result table
# game menu
# bg
# more maps
# y += 10 is 5 approachtime (almost)
# etc
