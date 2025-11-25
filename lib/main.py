# import modules
import os
import math
import datetime
import signal
import sys
import shutil
from time import sleep as wait, time

from extern.save_input import save_input as s_inp
from extern.getch import getch
from extern.timeout import timeout
from extern.save_output import save_output as s_out, cls

from menu import learn_menu
from manage_files import move, ch_path, get_list, create, overwrite, delete, create_backup, restore_backup, remove_backup, remove_all_backups
from errors import ClosedTerminalError, ProcessKilledError, log_error
from functions import user_choice_items, ch_time, ch_size, get_user_size
from update import update
from file_browser import browser

# set functions
def help():
    #TODO
    pass

# the user can choose his username
def choose_name():
    selection = 0
    try:
        list_users = os.listdir(ch_path('~/'))
    except FileNotFoundError:
        os.mkdir(ch_path('~/'))
        list_users = os.listdir(ch_path('~/'))

    if len(list_users) > 0:
        while True:
            cls()
            s_out('Choose your username or press \'n\' to create a new user.')
            s_out()
            s_out('Name' + (' ' * (os.get_terminal_size().columns - 18)) + 'Time ago')
            for name in range(len(list_users)):
                # print username
                if name == selection:
                    s_out('\x1b[7m' + list_users[name] + '\x1b[0m', end = '')
                else:
                    s_out(list_users[name], end = '')
 
                try:
                    # calculate the time ago
                    last_time_learned = get_list(list_users[name], 'userinfo')[1]
   
                    # print the time ago
                    s_out(' ' * ((os.get_terminal_size().columns - len(list_users[name])) - 14), end = '')
                    s_out(ch_time(time() - last_time_learned)[0], end = ' ')

                    # print total size
                    s_out(ch_size(get_user_size(list_users[name])))

                except:
                    log_error()
                    s_out()
    
            # print prompt
            s_out()
            s_out('\r   > ', end = '')
            try:
                # get user input
                ch = timeout(getch, 10)
                # new user
                if ch == 'n':
                    cls()
                    break
                # enter
                if ch == '\n':
                    return list_users[selection]
                # down
                if ch == 'j' or ch == 's':
                    selection = selection + 1
                # up
                if ch == 'k' or ch == 'w':
                    selection = selection - 1
                # ctrl + c
                if ch == '\x03':
                    raise KeyboardInterrupt
                # ctrl + d
                if ch == '\x04':
                    raise EOFError
                # delete/remove
                if ch == 'd' or ch == 'r':
                    s_out()
                    if s_inp('Are you sure to delete \'' + list_users[selection] + '\'? It can\'t be undone. (yes/no)   > ') == 'yes':
                        if os.path.isdir(ch_path('~/' + list_users[selection])):
                            delete(list_users[selection])
                        else:
                            os.remove(ch_path('~/' + list_users[selection]))
                        list_users = os.listdir(ch_path('~/'))

                # quit
                if ch == 'q':
                    s_out()
                    exit()
                if ch == '\x1b' or ch == '\x00':
                    c1 = getch()
                    if c1 == '[':
                        c2 = getch()
                        # down
                        if c2 == 'B':
                            selection = selection + 1
                        # up
                        if c2 == 'A':
                            selection = selection - 1
                        # home
                        if c2 == 'H':
                            selection = 0
                        # end
                        if c2 == 'F':
                            selection = len(list_users) - 1
                    # down
                    elif c1 == 'P':
                        selection = selection + 1
                    # up
                    elif c1 == 'H':
                        selection = selection - 1
                    # home
                    elif c1 == 'G':
                        selection = 0
                    # end
                    elif c1 == 'O':
                        selection = len(list_users) - 1

            except KeyboardInterrupt:
                s_out()
                exit()
            except TimeoutError:
                continue

            if selection < 0:
                selection = len(list_users) - 1
            if selection >= len(list_users):
                selection = 0

    else:
        cls()
        s_out('There are none users. You must create one.')
        s_out()

    name = s_inp('Type your new username   > ')
    while name == '' or '/' in name or name in os.listdir(ch_path('~/')):
        if '/' in name:
            s_out('\x1b[1;49;31mCan\'t use this character: \'/\'\x1b[0m')
        if name in os.listdir(ch_path('~/')):
            s_out('\x1b[1;49;31mThis name already exist. Choose another name.\x1b[0m')
        name = s_inp('Type je nieuwe gebruiker in   > ')
    return name

def login(name = ''):   
    if name == '':
        name = choose_name()
    s_out()

    # create userenvironment if it not exist
    new = create(name)

    # printen dat de gebruiker welkom is
    s_out('Welcome in the learning program, ' + name)
    # if the user is new, ask to show the help menu
    if new:
        userinfo = [time(), time(), 0, time(), False]
        if s_inp('Do you want to see the help menu? (yes/no)   > ') == 'yes':
            help()

    else:
        userinfo = get_list(name, 'userinfo')
        if len(userinfo) < 5:
            userinfo = [time(), time(), 0, time(), False]
        if not userinfo[4]:
            s_out('The program doesn\'t close correctly. Try to close the program next time good.')
        userinfo[4] = False
        userinfo[3] = time()

        try:
            s_inp('Press enter to continue. ')
        except KeyboardInterrupt:
            s_out()
            exit()

    overwrite(name, userinfo, 'userinfo')
    menu(name, userinfo)

def logout(name, userinfo):
    userinfo[1] = time()
    userinfo[2] = userinfo[2] + (time() - userinfo[3])
    userinfo[4] = True
    overwrite(name, userinfo, 'userinfo')

def menu(name, userinfo):
    logged_out = False
    while True:
        cls()
        # list with options
        options = ['l', 'h', 'u', 'c', 'b', 's', 'q', 'd', 'o', 'U']

        # show options
        s_out('Wat wil je doen?')
        s_out('Learn --> l')
        s_out('Help menu --> h')
        s_out('See userinfo --> u')
        s_out('Change username --> c')
        s_out('Backup menu --> b')
        s_out('Quit --> s/q')
        s_out('Delete userenvironment --> d')
        s_out('Log out --> o')
        s_out('Update --> U')

        # ask user to do something
        try:
            choice = s_inp('   > ')
    
            if choice not in options:
                # if the input isn't correctly, ask again
                cls()
                s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                wait(1)
                continue
    
            if choice == 'l':
                # learn
                learn_menu(name)
                
            if choice == 'h':
                # help menu
                help()
    
            if choice == 'u':
                cls()
                time_created = str(datetime.datetime.fromtimestamp(userinfo[0]))
                time_created = time_created[:time_created.find('.')]
                s_out('     Time created: ' + str(time_created))
                time_changed = str(datetime.datetime.fromtimestamp(userinfo[1]))
                time_changed = time_changed[:time_changed.find('.')]
                s_out('Last time learned: ' + str(time_changed))
                s_out('     Time learned: ' + ch_time(userinfo[2] + (time() - userinfo[3]))[0])
                s_out()
                s_inp('Press enter to continue. ')

            if choice == 'c':
                cls()
                s_out('Current username: ' + name)
                new_name = s_inp('Type the new username.   > ', input = name)
                shutil.move(ch_path('~/' + name), ch_path('~/' + new_name))
                name = new_name

            if choice == 'b':
                try:
                    backup_menu(name)
                except KeyboardInterrupt:
                    continue
    
            if choice == 's' or choice == 'q':
                logout(name, userinfo)
                exit()
    
            if choice == 'd':
                try:
                    if s_inp('Are you sure to delete your account? It can\'t be undone. (yes/no)   >  ') == 'yes':
                        delete(name)
                        logged_out = True
                        login()
                except KeyboardInterrupt:
                    continue

            if choice == 'o':
                logout(name, userinfo)
                logged_out = True
                login()

            if choice == 'U':
                logout(name, userinfo)
                logged_out = True
                update(<path_to_info>)
                exit()

        except (KeyboardInterrupt, ClosedTerminalError, ProcessKilledError):
            if not logged_out:
                logout(name, userinfo)
            s_out()
            exit()

        finally:
            if not logged_out:
                logout(name, userinfo)

def backup_menu(username):
    while True:
        cls()
        backups = os.listdir(ch_path('~/' + username + '/backups/'))
        options = ['c', 'i', 'q']
        # show options
        s_out('What do you want to do?')
        s_out('Create backup --> c')
        if len(backups) > 0:
            s_out('Restore from backup --> r')
            options.append('r')
            s_out('Delete backup --> d')
            options.append('d')
            s_out('Delete all backups --> D')
            options.append('D')
            s_out('Export backup --> e')
            options.append('e')
        s_out('Import backup --> i')
        s_out('Quit --> q')
    
        # ask user
        choice = s_inp('   > ')

        if choice not in options:
            cls()
            s_out('That isn\'t a option!!!')
            wait(1.5)
            continue

        if choice == 'c':
            create_backup(username)
            s_out('Succesvol created!')
            wait(1.5)

        if choice == 'r':
            filename = user_choice_items(backups)
            restore_backup(username, filename)
            s_inp('Backup restored! Press enter to continue. ')

        if choice == 'd':
            filename = user_choice_items(backups)
            remove_backup(username, filename)

        if choice == 'D':
            remove_all_backups(username)

        if choice == 'e':
            filename = user_choice_items(backups)
            #location = s_inp('Type the full path of the location where you want to export this backup. If you press enter, it will be exported in the home directory.   > ')
            print('Select a directory to export the backup.')
            s_inp('Press enter to do it! ')
            location = browser(filename = filename, mode = 'create', type = 'f', message = 'Export to a file')
            try:
                shutil.copy(ch_path('~/' + username + '/backups/' + filename), os.path.expanduser('~') if len(location) == 0 else location)
            except Exception as error:
                log_error()
                print('Error by exporting: ')
                print(error)
                s_inp('Press enter to continue. ')
                continue

        if choice == 'i':
            #location = s_inp('Type the full path of the backup file you want to import.   > ')
            print('Select a file to import.')
            s_inp('Press enter to do it! ')
            location = browser(mode = 'open', type = 'f', message = 'Import backup file')
            try:
                shutil.copy(location, ch_path('~/' + username + '/backups/'))
            except Exception as error:
                log_error()
                print('Error by importing: ')
                print(error)
                s_inp('Press enter to continue. ')
                continue

        if choice == 'q':
            return ''

if __name__ == '__main__':
    login()

