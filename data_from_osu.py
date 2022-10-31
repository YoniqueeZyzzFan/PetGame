import codecs
import os
import re

from ctypes import *
width = windll.user32.GetSystemMetrics(0)
height = windll.user32.GetSystemMetrics(1)

def get_configuration(data, path):
    list_of_notes = []
    f = open(path+'temp_conf.txt', 'w')
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

def convert(path):
    old_path = path
    path = ""
    try:
        path = old_path[:len(old_path) - 4]
        os.mkdir("maps/" + path)
    except OSError:
        return
    path_to_data = "maps/" + str(path)
    new_path = path + '.txt'
    os.rename(old_path, new_path)
    file = codecs.open(new_path, "r", "utf_8_sig")
    while True:
        data = file.readline()
        #if data.find('Mode:') != -1:
           # d = data[:len(data)-2]
            #if d[len(d)-1] != 3:
                #raise Exception("wrong gamemode map")
        if data.find('[HitObjects]') == -1:
            continue
        else:
            data = file.read()
            break
    file.close()
    data = get_configuration(data, path_to_data)
    # data is list - x,y,time , we should change osu xy to ours
    new_data = []
    for i in range(0, len(data)):
        x, y, time, type = re.split(r",", data[i])
        if int(x) == 64:
            x = int(width/2 - 150)
        elif int(x) == 192:
            x = int(width/2 - 50)
        elif int(x) == 320:
            x = int(width/2 + 50)
        elif int(x) == 448:
            x = int(width/2 + 150)
        else:
            continue
        if int(type) != 1:
            continue
        y = 0
        new_conf = str(x) + ',' + str(y) + ',' + str(time)
        new_data.append(new_conf)
    data = new_data
    path = path_to_data + '/' + path + '_uni.txt'
    f = open(path, 'w')
    for i in range(0, len(data)):
        f.write(data[i] + '\n')
    f.close()
    os.rename(new_path, old_path)
    f = open('maps/maps.txt', 'r')
    f.close()

#if __name__ == "__main__":
    #convert('need.osu')