import codecs
import os
import re
import shutil

from ctypes import *

width = windll.user32.GetSystemMetrics(0)
height = windll.user32.GetSystemMetrics(1)


def get_configuration(data, path):
    list_of_notes = []
    f = open(path + 'temp_conf.txt', 'w')
    f.write(data)
    f.close()
    f = open(path + 'temp_conf.txt', 'r')
    while True:
        line = f.readline()
        if line == "\n":
            continue
        elif line == "":
            break
        else:
            line, trash = re.split(r',\d{1,6},\d{1,6}:', line)
            list_of_notes.append(line)
    f.close()
    os.remove(path + 'temp_conf.txt')
    return list_of_notes


def convert(path1):
    temp = path1.split('/')[-1]
    path_m = temp[:len(temp) - 4] + '.mp3'
    path_m2 = 'audio.mp3'
    path_m3 = 'audio.ogg'
    path = temp
    try:
        files = os.listdir(path1[:len(path1) - len(path)])
    except OSError:
        raise ValueError('Something wrong :c')
    check = False
    for i in files:
        if i == path_m:
            check = True
            break
        if i == path_m2:
            path_m = i
            check = True
            break
        if i == path_m3:
            path_m = i
            check = True
            break
    if not check:
        raise ValueError('No mp3 file. It should be next to .osu.')
    if os.path.exists(path1):
        try:
            os.mkdir("maps/" + path[:len(path) - 4])
            destination_path = 'maps/' + path[:len(path) - 4]
            shutil.copyfile(path1, destination_path + '/' + path)
            shutil.copyfile(path1[:len(path1) - len(path)] + path_m, destination_path + '/' + path_m)
            os.rename(destination_path + '/' + path_m, destination_path + '/' + temp[:len(temp) - 4] + '.mp3')
        except OSError:
            raise ValueError('This folder is already exists')
        file = codecs.open(destination_path + '/' + path, "r", "utf_8_sig")
        data = ''
        while True:
            data = file.readline()
            if data.find('ApproachRate:') != -1:
                f = open('maps/' + path[:len(path) - 4] + '/diff.txt', 'w')
                f.write(data[13:])
                f.close()
            if data.find('Mode:') != -1:
                d = data[:len(data) - 2]
                t = d[len(d) - 1]
                if int(t) != 3:
                    file.close()
                    shutil.rmtree("maps/" + path[:len(path) - 4])
                    raise ValueError("wrong gamemode map")
            if data.find('[HitObjects]') == -1:
                continue
            else:
                data = file.read()
                break
        file.close()
        data = get_configuration(data, 'maps/' + temp[:len(temp) - 4])
        # data is list - x,y,time , we should change osu xy to ours
        new_data = []
        for i in range(0, len(data)):
            x, y, time, type = re.split(r",", data[i])
            if int(x) == 64:
                x = 1
            elif int(x) == 192:
                x = 2
            elif int(x) == 320:
                x = 3
            elif int(x) == 448:
                x = 4
            else:
                continue
            if int(type) != 1 and int(type) !=5 and int(type) != 128:
                continue
            y = 0
            new_conf = str(x) + ',' + str(y) + ',' + str(time)
            new_data.append(new_conf)
        if len(new_data) < 1:
            shutil.rmtree("maps/" + path[:len(path) - 4])
            raise ValueError("wrong gamemode map, only 4 buttons map")
        map_data = destination_path + '/' + path[:len(path) - 4] + '.txt'
        data = new_data
        f = open(map_data, 'w')
        for i in range(0, len(data)):
            f.write(data[i] + '\n')
        f.close()
    else:
        raise ValueError('no such a file')

# if __name__ == "__main__":
# convert('G:\Course3\CourseAisd\\guitar\\need.osu')
