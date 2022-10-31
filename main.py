import sys
from datetime import datetime
from pygame import mixer

from button import *
from data_from_osu import *
from ctypes import *

import webbrowser

# import cv2
# import numpy as np
# import pyautogui
# import threading

# fourcc = cv2.VideoWriter_fourcc(*"XVID")
# out = cv2.VideoWriter("output.avi", fourcc, 20.0, (width, height))

width = windll.user32.GetSystemMetrics(0)
height = windll.user32.GetSystemMetrics(1)

pygame.mixer.pre_init(frequency=44100, size=-16, channels=4, buffer=512, devicename=None)

mixer.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height), pygame.SCALED, vsync=1)
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 38)

menu_sound = pygame.mixer.Sound("assets/Menu.mp3")
menu_sound.set_volume(0.3)
menu_channel = menu_sound.play()


def error(string):
    bg = pygame.image.load("assets/background.png").convert()
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    back_btn = Button(image=pygame.image.load("assets/Options Rect.png"),
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
        self.hit_sound.set_volume(0.1)
        self.combobreak_sound = pygame.mixer.Sound("assets/combo_break.mp3")
        self.combobreak_sound.set_volume(0.05)
        self.combo = 0
        self.hit = 0
        self.acc = 1
        self.all = 0
        self.end = 0
        self.song = path
        self.keys = [
            Key(float(width) / 2 - 150, float(height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_a),  # 100
            Key(float(width) / 2 - 50, float(height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_s),  # 200
            Key(float(width) / 2 + 50, float(height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_j),  # 300
            Key(float(width) / 2 + 150, float(height) - 150, (0, 0, 0), (220, 220, 220), pygame.K_k),  # 400
        ]
        self.note_time = []
        self.min = 0
        self.map_rect = self.load(path)

    def load(self, map_data):
        rects = []
        file = open(map_data + ".txt", 'r')
        while True:
            data = file.readline()
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

    @staticmethod
    def pause():
        pause = font.render("PAUSE", True, "white")
        screen.blit(pause, (width / 2 - 300, height / 2))
        unpause = font.render("Unpause: press esc (will start in 3 seconds)", True, "white")
        screen.blit(unpause, (width / 2 - 300, height / 2 - 200))
        esc_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(width / 2, height / 2 + 400),
                         text_input="Exit", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        clock_time = pygame.time.Clock()
        while True:
            pygame.display.update()
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            menu_mouse_pos = pygame.mouse.get_pos()
            esc_btn.changeColor(menu_mouse_pos)
            esc_btn.update(screen)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if esc_btn.checkForInput(menu_mouse_pos):
                        return 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        start_ticks = pygame.time.get_ticks()  # starter tick
                        screen.fill((0, 0, 0))
                        while True:
                            seconds = (pygame.time.get_ticks() - start_ticks) / 1000
                            time = font.render(str(seconds), True, "white")
                            screen.fill((0, 0, 0))
                            screen.blit(time, (width / 2 - 300, height / 2))
                            pygame.display.update()
                            clock_time.tick(30)
                            if seconds > 3:
                                return 0
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    # def start_game_r(self):
    #    t1 = threading.Thread(target=self.start_game)
    #    t2 = threading.Thread(target=self.record)
    #    t1.start()
    #    t2.start()

    # def record(self):
    #    while True:
    #        img = pyautogui.screenshot()
    #        frame = np.array(img)
    #        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #        out.write(frame)
    #    out.release()

    def start_game(self):
        map_sound = pygame.mixer.Sound(self.song + ".mp3")
        map_sound.set_volume(menu_channel.get_volume())
        t1 = datetime.now()
        map_sound.play()
        while True:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        t3 = datetime.now()
                        pygame.mixer.pause()
                        x = self.pause()
                        if x == 1:
                            return
                        pygame.mixer.unpause()
                        t4 = datetime.now()
                        t1 += t4 - t3
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

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
                    self.map_rect[rect].y += 13
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
                    if self.map_rect[rect].x == float(width) / 2 - 150:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[0].rect)
                    elif self.map_rect[rect].x == float(width) / 2 - 50:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[1].rect)
                    elif self.map_rect[rect].x == float(width) / 2 + 50:
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
        result_sound.set_volume(0.4)
        channel_res = result_sound.play()
        quit_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(width / 2, height / 2 + 150),
                          text_input="Okay", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        while True:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            screen.fill((0, 0, 0))
            menu_mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if quit_btn.checkForInput(menu_mouse_pos):
                        channel_res.stop()
                        return
            quit_btn.update(screen)
            quit_btn.changeColor(menu_mouse_pos)
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
        self.start_btn = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(width / 2, height / 2 - 150),
                                text_input="Start", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.change_map = Button(image=pygame.image.load("assets/Change_map.png"), pos=(width / 2, height / 2 + 50),
                                 text_input="Change map", font=get_font(30), base_color="#d7fcd4",
                                 hovering_color="RED")
        self.quit_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(width / 2, height / 2 + 150),
                               text_input="Back", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.sound = "Not selected"
        self.curr_sound = get_font(30).render(self.sound, True, "#b68f40")
        self.btns = [self.start_btn, self.change_map, self.quit_btn]

    def open(self):
        screen.blit(self.bg, (0, 0))
        pygame.display.flip()
        back_to_main_menu = False
        while True:
            menu_mouse_pos = pygame.mouse.get_pos()
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_btn.checkForInput(menu_mouse_pos):
                        try:
                            menu_channel.pause()
                            g = HitGame("maps/" + self.sound + "/" + self.sound)
                            g.start_game()
                            menu_channel.unpause()
                            screen.blit(self.bg, (0, 0))
                            pygame.display.flip()
                        except OSError:
                            menu_channel.unpause()
                            error('There is no such a map')
                        break
                    if self.change_map.checkForInput(menu_mouse_pos):
                        screen.blit(self.bg, (0, 0))
                        exit_change = False
                        while True:
                            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                            menu_mouse_pos = pygame.mouse.get_pos()
                            choose = get_font(40).render("Choose", True, "RED")
                            screen.blit(choose, (width / 2 - 80, height / 2 - 500))
                            back_btn = Button(image=pygame.image.load("assets/Options Rect.png"),
                                              pos=(width / 2, height / 2 + 300),
                                              text_input="Back", font=get_font(30), base_color="#d7fcd4",
                                              hovering_color="GREEN")
                            back_btn.changeColor(menu_mouse_pos)
                            back_btn.update(screen)
                            for songs in range(0, len(list_of_maps)):
                                btn = Button(image=None, pos=(380, (int(songs) + 1) * 50 + 100 + 15),
                                             text_input=list_of_maps[songs], font=get_font(30), base_color="#d7fcd4",
                                             hovering_color="GREEN")
                                diff_text = get_font(30).render("diff-" + list_of_diff[songs], True, "#b68f40")
                                screen.blit(diff_text, (200, (int(songs) + 1) * 50 + 100))

                                btn.changeColor(menu_mouse_pos)
                                btn.update(screen)
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if btn.checkForInput(menu_mouse_pos):
                                        self.sound = list_of_maps[songs]
                                        self.curr_sound = get_font(30).render(self.sound, True, "#b68f40")
                                        exit_change = True
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    if back_btn.checkForInput(menu_mouse_pos):
                                        exit_change = True
                            pygame.display.update()
                            if exit_change:
                                screen.blit(self.bg, (0, 0))
                                break
                    if self.quit_btn.checkForInput(menu_mouse_pos):
                        back_to_main_menu = True
                        break
            if back_to_main_menu:
                screen.blit(self.bg, (0, 0))
                break
            menu_mouse_pos = pygame.mouse.get_pos()
            menu_text = get_font(30).render("Let's start!", True, "#b68f40")

            screen.blit(menu_text, (width / 2 - 80, height / 2 - 300))
            screen.blit(self.curr_sound, (width / 2 - 80, height / 2 - 70))

            for button in self.btns:
                button.changeColor(menu_mouse_pos)
                button.update(screen)

            pygame.display.update()


class MainWindow:
    def __init__(self):
        self.bg = pygame.image.load("assets/background.png").convert()
        self.creditsgh_btn = Button(image=pygame.image.load("assets/gh.jpg"), pos=(width - 100, height / 2 + 500),
                                    text_input="", font=get_font(0), base_color="#d7fcd4", hovering_color="RED")
        self.creditsds_btn = Button(image=pygame.image.load("assets/ds.jpg"), pos=(width - 200, height / 2 + 500),
                                    text_input="", font=get_font(0), base_color="#d7fcd4", hovering_color="RED")
        self.play_btn = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(width / 2, height / 2 - 150),
                               text_input="Play", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.export = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(width / 2, height / 2 - 50),
                             text_input="Export", font=get_font(30), base_color="#d7fcd4",
                             hovering_color="RED")
        self.quit_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(width / 2, height / 2 + 50),
                               text_input="Quit", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.sc = font.render("Sound control:", True, "Gray")
        self.vu = font.render("Volume up - up arrow", True, "Gray")
        self.vd = font.render("Volume down - down arrow", True, "Gray")
        self.menu_text = get_font(30).render("MAIN MENU", True, "#b68f40")
        self.btns = [self.play_btn, self.export, self.quit_btn, self.creditsgh_btn, self.creditsds_btn]

    def open(self):
        screen.blit(self.bg, (0, 0))
        pygame.display.flip()
        while True:
            menu_mouse_pos = pygame.mouse.get_pos()
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        menu_channel.set_volume(menu_channel.get_volume() + 0.1)
                    if event.key == pygame.K_DOWN:
                        menu_channel.set_volume(menu_channel.get_volume() - 0.1)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_btn.checkForInput(menu_mouse_pos):
                        play_window = PlayWindow()
                        play_window.open()
                    if self.export.checkForInput(menu_mouse_pos):
                        break
                    if self.creditsgh_btn.checkForInput(menu_mouse_pos):
                        webbrowser.open('https://github.com/YoniqueeZyzzFan')
                    if self.creditsds_btn.checkForInput(menu_mouse_pos):
                        webbrowser.open('https://discord.com/invite/C7TABmzKCu')
                    if self.quit_btn.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()
            screen.blit(self.sc, (250, 100))
            screen.blit(self.vu, (250, 150))
            screen.blit(self.vd, (250, 200))
            menu_rect = self.menu_text.get_rect(center=(width / 2, height / 2 - height / 3))

            screen.blit(self.menu_text, menu_rect)

            for button in self.btns:
                button.changeColor(menu_mouse_pos)
                button.update(screen)

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
            list_of_diff.append(map_set[len(map_set) - 2:])
            list_of_maps.append(map_set[:len(map_set) - 2])
    f.close()
    menu = MainWindow()
    menu.open()
# - record play
# CHECK AUDIO IN - OSU CONF FILE AND + IT IN IF pygame draw rect
# more maps
# y += 10 is 5 approachtime (almost)
# music after hover on sound
