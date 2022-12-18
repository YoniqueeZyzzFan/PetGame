from datetime import datetime
from piano import *
import pygame.threads
from pygame import mixer
from tkinter import messagebox

from button import *
from data_from_osu import *

import webbrowser

import tkinter
import tkinter.filedialog

import cv2  # rp
import numpy as np  # rp
import pyautogui  # rp
import threading  # rp

fourcc = cv2.VideoWriter_fourcc(*"XVID")  # rp
out = cv2.VideoWriter("output.avi", fourcc, 20.0, (width, height))  # rp

width = windll.user32.GetSystemMetrics(0)
height = windll.user32.GetSystemMetrics(1)

# number of maps, wbtnmap, wbttext
place1920 = [30, 700, 600]
place1366 = [15, 400, 400]
place = []
if width > 1366:
    place = place1920
elif width <= 1366:
    place = place1366
pygame.mixer.pre_init(frequency=44100, size=-16, channels=4, buffer=512, devicename=None)

mixer.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height), pygame.SCALED, vsync=1)
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 38)

menu_sound = pygame.mixer.Sound("assets/Menu.mp3")
menu_sound.set_volume(0.3)
menu_channel = menu_sound.play()

list_of_maps = []
list_of_diff = []

approach_rate_converter = {5: 15, 9.7: 15}


def error(string):
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


def reload_map():
    """Check maps in the folder"""
    try:
        files = os.listdir('maps/')
    except OSError:
        error('Something wrong w/ map\'s folder')
    for i in files:
        try:
            map_data = os.listdir('maps/' + i)
            if i in list_of_maps:
                continue
            for k in map_data:
                if k.find('.osu') != -1:
                    list_of_maps.append(i)
                    continue
                if k.find('diff.txt') != -1:
                    d = open('maps/' + i + '/' + 'diff.txt')
                    data = d.readline()
                    list_of_diff.append(data)
                    d.close()
            if len(list_of_diff) < len(list_of_maps):
                list_of_diff.append('Unknown')
        except OSError:
            continue


class HitGame:
    """Сlass for game.
            Keyword arguments:
            hit_sound - sound on the click
            combobreak_sound - sound on the missclick
            combo - the number of consecutive notes pressed at the moment
            hit - hit rate
            acc - accuracy
            all - number of notes
            end - is responsible for deleting pressed notes
            speed - note speed
            song - song
            note_time - note display time
            min - map beginning
            map_rect - note data
        """

    def __init__(self, path, index_map):
        # self.bg = pygame.image.load("assets/game_bg.jpg").convert()
        # self.bg.set_alpha(40)
        self.hit_sound = pygame.mixer.Sound("assets/hit.wav")
        self.hit_sound.set_volume(0.18)
        self.combobreak_sound = pygame.mixer.Sound("assets/combo_break.mp3")
        self.combobreak_sound.set_volume(0.12)
        self.combo = 0
        self.hit = 0
        self.acc = 1
        self.all = 0
        self.end = 0
        self.speed = int(index_map)
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
        """Loads a map and selects a note position depending on the screen resolution
            Keyword arguments:
                map_data - map path
        """
        try:
            sp = float(list_of_diff[self.speed])
            self.speed = approach_rate_converter[sp]
        except Exception as e:
            self.speed = 10
        rects = []
        try:
            file = open(map_data + ".txt", 'r')
        except Exception:
            raise Exception('no such a map')
        while True:
            data = file.readline()
            if data == "":
                break
            else:
                x, y, t = re.split(r',', data)
                x = int(x)
                if x == 1:
                    x = float(width) / 2 - 150 + 15
                elif x == 2:
                    x = float(width) / 2 - 50 + 15
                elif x == 3:
                    x = float(width) / 2 + 50 + 15
                elif x == 4:
                    x = float(width) / 2 + 150 + 15
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

    def pause(self):
        """Pause the game."""
        pause = font.render("PAUSE", True, "white")
        screen.blit(pause, (width / 2 - 300, height / 2))
        unpause = font.render("Unpause: press esc (will start in 3 seconds)", True, "white")
        screen.blit(unpause, (width / 2 - 300, height / 2 - 200))
        esc_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(width / 2, height / 2 + 200),
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
                        self.end = self.min
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

    def start_game_r(self):  # rp
        """Running the game along with screen recording."""
        screen.fill((0, 0, 0))
        t1 = threading.Thread(target=self.start_game)  # rp
        t2 = threading.Thread(target=self.record)  # rp
        t2.start()
        t1.run()

    def record(self):  # rp
        """Running the game without screen recording."""
        while self.min != self.end:  # rp
            img = pyautogui.screenshot()  # rp
            frame = np.array(img)  # rp
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # rp
            out.write(frame)  # rp
        out.release()  # rp

    def start_game(self):
        """Start the game."""
        try:
            map_sound = pygame.mixer.Sound(self.song + ".mp3")
        except Exception as e:
            error('mp3 file could not be found')
            return
        map_sound.set_volume(0.25)  # menu_channel.get_volume() - 0.1
        t1 = datetime.now()
        map_channel = map_sound.play()
        while True:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        t3 = datetime.now()
                        map_channel.pause()
                        x = self.pause()
                        if x == 1:
                            map_channel.stop()
                            return
                        map_channel.unpause()
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
                    self.map_rect[rect].y += self.speed
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
                    if self.map_rect[rect].x == float(width) / 2 - 150 + 15:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[0].rect)
                    elif self.map_rect[rect].x == float(width) / 2 - 50 + 15:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[1].rect)
                    elif self.map_rect[rect].x == float(width) / 2 + 50 + 15:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[2].rect)
                    else:
                        pygame.draw.rect(screen, (178, 34, 34), self.keys[3].rect)
                    self.combobreak_sound.play()
                    self.combo = 0
            text = font.render("combo:" + str(self.combo), True, "white")
            screen.blit(text, (100, 150))
            if self.all != 0:
                self.acc = self.hit * 100 / self.all
            else:
                self.acc = 100
            self.acc = round(self.acc, 2)
            accuracy = font.render("acc:" + str(self.acc), True, "white")
            screen.blit(accuracy, (100, 100))
            pygame.display.update()
        map_sound.stop()
        self.result()

    def result(self):
        """Show statistics after a map is played."""
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


class PlayWindow:
    """A class for displaying the map selection window and the start of the game.
                Keyword arguments:
               bg - background
               smth_btn - When the button is pressed, the smth happens
                change - shows the map selection window
                quit - back to the main window
                record - turn on/turn off the record
                page - next page
               sound - current map
               curr_sonud - font for rectangle
               curr_page - If there are too many maps, there will be several pages
               curr_ind - is responsible for the number of cards on the page
            """

    def __init__(self):
        self.bg = pygame.image.load("assets/background.png").convert()
        self.start_btn = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(width / 2, height / 2 - 150),
                                text_input="Start", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.change_map = Button(image=pygame.image.load("assets/Change_map.png"), pos=(width / 2, height / 2 + 50),
                                 text_input="Change map", font=get_font(30), base_color="#d7fcd4",
                                 hovering_color="RED")
        self.quit_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(width / 2, height / 2 + 150),
                               text_input="Back", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.record_btn = Button(image=pygame.image.load("assets/Quit Rect.png"),
                                 pos=(width / 2 + 250, height / 2 + 150),
                                 text_input="NoRecord", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.sound = "Not selected"
        self.curr_sound = get_font(30).render(self.sound, True, "#b68f40")
        self.sound_count = 0
        self.curr_page = 1
        self.curr_ind = 0
        self.page = int(len(list_of_maps) / place[0]) + 1
        self.page_btn = Button(image=pygame.image.load("assets/Quit Rect.png"),
                               pos=(width / 2, height / 2 + 200),
                               text_input="Page:" + str(self.curr_page) + '/' + str(self.page), font=get_font(30),
                               base_color="#d7fcd4",
                               hovering_color="RED")
        self.btns = [self.start_btn, self.change_map, self.quit_btn, self.record_btn]

    def open(self):
        print(list_of_maps)
        """Open the window."""
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
                    if self.record_btn.checkForInput(menu_mouse_pos):
                        if self.record_btn.text_input == "Record":
                            self.record_btn.text_input = "NoRecord"
                        else:
                            self.record_btn.text_input = "Record"
                    if self.start_btn.checkForInput(menu_mouse_pos):
                        try:
                            menu_channel.pause()
                            temp = 0
                            for i in range(0, len(list_of_maps)):
                                if list_of_maps[i] == self.sound:
                                    temp = i
                                    break
                            try:
                                g = HitGame("maps/" + self.sound + "/" + self.sound, temp)
                            except Exception as e:
                                error('no such a map')
                                menu_channel.unpause()
                                screen.blit(self.bg, (0, 0))
                                pygame.display.flip()
                                break
                            if self.record_btn.text_input == "Record":
                                g.start_game_r()
                            else:
                                g.start_game()
                            menu_channel.unpause()
                            screen.blit(self.bg, (0, 0))
                            pygame.display.flip()
                        except ValueError as exc:
                            menu_channel.unpause()
                            error(str(exc))
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
                            self.page_btn.changeColor(menu_mouse_pos)
                            self.page_btn.update(screen)
                            column = 0
                            for songs in range(self.curr_ind, self.curr_ind + int(place[0])):
                                if songs >= len(list_of_maps):
                                    break
                                wt = 0
                                ht = 0
                                w = 0
                                h = 0
                                if column < int(place[0]) / 2:
                                    w = place[1]  # 500
                                    wt = place[1] - 250  # 200
                                    ht = (int(songs) - self.curr_ind + 1) * 50 + 100  # (int(songs)+1)*50 +100
                                    h = (
                                                    int(songs) - self.curr_ind + 1) * 50 + 100 + 15  # (int(songs) + 1) * 50 + 100 + 15
                                else:
                                    w = place[2] + width / 2  # 1420
                                    wt = place[1] + place[2]  # 1120
                                    ht = (int(songs) - int(
                                        place[0]) / 2 - self.curr_ind + 1) * 50 + 100  # (int(songs)+1)*50 +100
                                    h = (int(songs) - int(place[
                                                              0]) / 2 - self.curr_ind + 1) * 50 + 100 + 15  # (int(songs) + 1) * 50 + 100 + 15
                                btn = Button(image=None, pos=(w, h),
                                             text_input=(list_of_maps[songs][:6]), font=get_font(30),
                                             base_color="#d7fcd4",
                                             hovering_color="GREEN")
                                diff_text = get_font(30).render("diff-" + list_of_diff[songs], True, "#b68f40")
                                screen.blit(diff_text, (wt, ht))
                                btn.changeColor(menu_mouse_pos)
                                btn.update(screen)
                                column += 1
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
                                    if self.page_btn.checkForInput(menu_mouse_pos):
                                        if self.page == 1:
                                            break
                                        if self.page == self.curr_page:
                                            self.curr_page = 1
                                            self.curr_ind = 0
                                        elif self.page > self.curr_page:
                                            self.curr_page += 1
                                            self.curr_ind = self.curr_ind + int(place[0])
                                        self.page_btn.text_input = "Page:" + str(self.curr_page) + '/' + str(self.page)
                                        screen.blit(self.bg, (0, 0))
                                        pygame.display.flip()
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

            beta = get_font(20).render("Not recommended for a good playing experience.", True, "Red")
            screen.blit(beta, (width / 2 + 200, height / 2 + 200))
            beta2 = get_font(20).render("Still in beta .", True, "Red")
            screen.blit(beta2, (width / 2 + 200, height / 2 + 250))

            screen.blit(menu_text, (width / 2 - 80, height / 2 - 300))
            screen.blit(self.curr_sound, (width / 2 - 80, height / 2 - 70))

            for button in self.btns:
                button.changeColor(menu_mouse_pos)
                button.update(screen)

            pygame.display.update()


class MainWindow:
    """Сlass for main window.
                Keyword arguments:
                bg - background
                smth_btn - When the button is pressed, the smth happens
                 credits - links to the social media
                 play - opens a window with choosing maps and start
                 imp - import map from osu
                 quit - quit from the app
                 sc/vu/vd - text on the main window
            """

    def __init__(self):
        self.bg = pygame.image.load("assets/background.png").convert()
        self.creditsgh_btn = Button(image=pygame.image.load("assets/gh.jpg"), pos=(width - 100, height - 50),
                                    text_input="", font=get_font(0), base_color="#d7fcd4", hovering_color="RED")
        self.creditsds_btn = Button(image=pygame.image.load("assets/ds.jpg"), pos=(width - 200, height - 50),
                                    text_input="", font=get_font(0), base_color="#d7fcd4", hovering_color="RED")
        self.play_btn = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(width / 2, height / 2 - 150),
                               text_input="Play", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.piano_btn = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(width / 2, height / 2 - 222),
                                text_input="Piano", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.imp = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(width / 2, height / 2 - 50),
                          text_input="Import", font=get_font(30), base_color="#d7fcd4",
                          hovering_color="RED")
        self.quit_btn = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(width / 2, height / 2 + 50),
                               text_input="Quit", font=get_font(30), base_color="#d7fcd4", hovering_color="RED")
        self.sc = font.render("Sound control:", True, "Gray")
        self.vu = font.render("Volume up - up arrow", True, "Gray")
        self.vd = font.render("Volume down - down arrow", True, "Gray")
        self.menu_text = get_font(30).render("MAIN MENU", True, "#b68f40")
        self.btns = [self.play_btn, self.piano_btn, self.imp, self.quit_btn, self.creditsgh_btn, self.creditsds_btn]

    def open(self):
        """Open the main window."""
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
                    if self.piano_btn.checkForInput(menu_mouse_pos):
                        menu_channel.pause()
                        try:
                            piano = PianoGame(screen, width, height, font)
                            piano.start()
                        except Exception as oe:
                            error(oe)
                        menu_channel.unpause()
                        screen.blit(self.bg, (0, 0))
                        pygame.display.flip()
                    if self.play_btn.checkForInput(menu_mouse_pos):
                        play_window = PlayWindow()
                        play_window.open()
                    if self.imp.checkForInput(menu_mouse_pos):
                        file_name = ''
                        try:
                            top = tkinter.Tk()
                            top.withdraw()  # hide window
                            file_name = tkinter.filedialog.askopenfilename(parent=top)
                            top.destroy()
                        except Exception as exc:
                            error(str(exc))
                        if file_name != '':
                            try:
                                convert(file_name)
                                error('Loading completed')
                            except ValueError as exc:
                                error(str(exc))
                        reload_map()
                    if self.creditsgh_btn.checkForInput(menu_mouse_pos):
                        webbrowser.open('https://github.com/YoniqueeZyzzFan')
                    if self.creditsds_btn.checkForInput(menu_mouse_pos):
                        webbrowser.open('https://discord.com/invite/C7TABmzKCu')
                    if self.quit_btn.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()
            screen.blit(self.sc, (50, 100))
            screen.blit(self.vu, (50, 150))
            screen.blit(self.vd, (50, 200))
            menu_rect = self.menu_text.get_rect(center=(width / 2, height / 2 - height / 3))

            screen.blit(self.menu_text, menu_rect)

            for button in self.btns:
                button.changeColor(menu_mouse_pos)
                button.update(screen)

            pygame.display.update()


if __name__ == "__main__":
    p = os.getcwd()
    files = os.listdir(p + '/piano_assets')
    check = False
    for i in files:
        if i == 'piano_background.jpg':
            check = True
            break
    if not check:
        messagebox.showerror("ERROR", "Missing some assets files (pictures)")
        exit(1)
    files = []
    files = os.listdir(p + '/assets')
    print(files)
    check = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    k = 0
    for i in range(0, len(files)):
        if files[i] == '1.png':
            check[k] = True
            k += 1
            continue
        if files[i] == 'Background.png':
            check[k] = True
            k += 1
            continue
        if files[i] == 'Change_map.png':
            check[k] = True
            k += 1
            continue
        if files[i] == 'combo_break.mp3':
            check[k] = True
            k += 1
            continue
        if files[i] == 'ds.jpg':
            check[k] = True
            k += 1
            continue
        if files[i] == 'gh.jpg':
            check[k] = True
            k += 1
            continue
        if files[i] == 'hit.wav':
            check[k] = True
            k += 1
            continue
        if files[i] == 'icon.png':
            check[k] = True
            k += 1
            continue
        if files[i] == 'JosefinSans-Bold.ttf':
            check[k] = True
            k += 1
            continue
        if files[i] == 'JosefinSans-LightItalic.ttf':
            check[k] = True
            k += 1
            continue
        if files[i] == 'Menu.mp3':
            check[k] = True
            k += 1
            continue
        if files[i] == 'Options Rect.png':
            check[k] = True
            k += 1
            continue
        if files[i] == 'Play Rect.png':
            check[k] = True
            k += 1
            continue
        if files[i] == 'Quit Rect.png':
            check[k] = True
            k += 1
            continue
        if files[i] == 'ResultTable.mp3':
            check[k] = True
            k += 1
            continue
    for i in check:
        if not i:
            messagebox.showerror("ERROR", "Missing some assets files (pictures or mp3)")
            exit(1)
    pygame.init()
    pygame.display.set_caption('Rhythm game')
    pygame.display.set_icon(pygame.image.load('assets/icon.png'))
    reload_map()
    menu = MainWindow()
    menu.open()
