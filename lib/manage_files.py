# import modules
import os
import inspect
import shutil
import datetime
from time import time

from extern.zip import ezip, unzip

path_learning_program = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
path_user_dir = <path_to_users>

# change path
def ch_path(path, mode = 'user'):
    if mode == 'user':
        path = path.replace('~/', path_user_dir + '/')
    elif mode == 'system':
        path = path.replace('~/', path_learning_program + '/')
    else:
        raise ValueError('Mode ' + str(mode) + ' is not \'user\' or \'system\'.')

    if os.name == 'nt':
        path = path.replace('/', '\\')

    return path

# create a environment
def create(username):
    if not os.path.exists(ch_path('~/')):
        os.mkdir(ch_path('~/'))
    if os.path.exists(ch_path('~/' + username)):
        list_dir = os.listdir(ch_path('~/' + username))
        if 'items' not in list_dir:
            create_dir(username, 'items/')
        if 'settings' not in list_dir:
            shutil.copy(ch_path('~/basic_files/settings', mode = 'system'), ch_path('~/' + username + '/settings'))
        if 'trash' not in list_dir:
            create_dir(username, 'trash/')
        if 'list_items' not in list_dir:
            create_file(username, 'list_items')
        if 'saved_reviewsessions' not in list_dir:
            create_dir(username, 'saved_reviewsessions/')
        if 'hided_items' not in list_dir:
            create_file(username, 'hided_items')
        if 'warned_items' not in list_dir:
            create_file(username, 'warned_items')
        if 'userinfo' not in list_dir:
            create_file(username, 'userinfo')
            overwrite(username, [time(), time(), 0, time(), False], 'userinfo')
        if 'backups' not in list_dir:
            create_dir(username, 'backups')
        if 'item_settings' not in list_dir:
            create_file(username, 'item_settings')
            
    else:
        create_dir(username)
        create_dir(username, 'items/')
        shutil.copy(ch_path('~/basic_files/settings', mode = 'system'), ch_path('~/' + username + '/settings'))
        create_dir(username, 'trash/')
        create_file(username, 'list_items')
        create_dir(username, 'saved_reviewsessions/')
        create_file(username, 'hided_items')
        create_file(username, 'warned_items')
        create_file(username, 'userinfo')
        overwrite(username, [time(), time(), 0, time(), False], 'userinfo')
        create_dir(username, 'backups')
        create_file(username, 'item_settings')
        return True

    return False
        
# create file
def create_file(username, locatie):
    open(ch_path('~/' + username + '/' + locatie), mode = 'x').close()

# create directory
def create_dir(username, locatie = ''):
    os.mkdir(ch_path('~/' + username + '/' + locatie))

# overwrite file
def overwrite(username, lijst, locatie):
    string = ''
    for i in lijst:
        string = string + str(i) + '\n'

    file = open(ch_path('~/' + username + '/' + locatie), mode = 'w')
    file.write(string)
    file.close()

# read file
def get_list(username, filename, text = False):
    file = open(ch_path('~/' + username + '/' + filename))
    data = file.read()
    file.close()

    return create_list(data, text)

def create_list(data, text = False):
    lijst = data.split('\n')
    while len(lijst) > 0:
        if lijst[len(lijst) - 1] in ['', ' ']:
            del lijst[len(lijst) - 1]
        else:
            break

    lijst2 = []
    for i in lijst:
        try:
            lijst2.append(eval(i))
        except:
            if text:
                return lijst
            
            raise ValueError

    return lijst2

# move/rename file
def move(username, locatie1, locatie2):
    shutil.move(ch_path('~/' + username + '/' + locatie1), ch_path('~/' + username + '/' + locatie2))

# copy file
def copy(username, locatie1, locatie2):
    shutil.copy(ch_path('~/' + username + '/' + locatie1), ch_path('~/' + username + '/' + locatie2))

# delete file
def delete_file(username, locatie):
    os.remove(ch_path('~/' + username + '/' + locatie))

# delete all files in directory
def delete_all(username, locatie):
    for name in os.listdir(ch_path('~/' + username + '/' + locatie)):
        os.remove(ch_path('~/' + username + '/' + locatie + name))

# delete environment
def delete(username):
    shutil.rmtree(ch_path('~/' + username))

def create_backup(username):
    ezip([ch_path('~/' + username + '/settings'), ch_path('~/' + username + '/hided_items'), ch_path('~/' + username + '/userinfo'), ch_path('~/' + username + '/item_settings')], [ch_path('~/' + username + '/items/'), ch_path('~/' + username + '/trash/'), ch_path('~/' + username + '/saved_reviewsessions/')], ch_path('~/' + username + '/backups/' + str(datetime.datetime.now()) + '.zip'))

def restore_backup(username, filename):
    shutil.rmtree(ch_path('~/' + username + '/items'))
    shutil.rmtree(ch_path('~/' + username + '/trash'))
    shutil.rmtree(ch_path('~/' + username + '/saved_reviewsessions'))
    os.remove(ch_path('~/' + username + '/settings'))
    os.remove(ch_path('~/' + username + '/list_items'))
    os.remove(ch_path('~/' + username + '/hided_items'))
    os.remove(ch_path('~/' + username + '/warned_items'))
    os.remove(ch_path('~/' + username + '/userinfo'))
    os.remove(ch_path('~/' + username + '/item_settings'))
    unzip(ch_path('~/' + username + '/backups/' + filename), ch_path('~/' + username + '/'))

def remove_backup(username, filename):
    os.remove(ch_path('~/' + username + '/backups/' + filename))

def remove_all_backups(username):
    delete_all(username, 'backups/')

def log_data(username, data):
    file = open(ch_path('~/' + username + '/debug.log'), mode = 'a')
    file.write(str(datetime.datetime.now()) + ': ' + (data if data[-1] == '\n' else data + '\n'))
    file.close()

