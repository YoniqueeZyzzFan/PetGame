import codecs
import os
import re


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
            x = 119
        elif int(x) == 192:
            x = 219
        elif int(x) == 320:
            x = 319
        elif int(x) == 448:
            x = 419
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
    f.write(path + '\n')
    f.close()
