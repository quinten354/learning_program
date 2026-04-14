# import modules
import os
from time import time

from extern.save_input import save_input as s_inp
from extern.getchar import getch_ as getch, start as getch_start, stop as getch_stop
from extern.timeout import timeout
from extern.save_output import save_output as s_out, cls

from manage_files import move, ch_path, get_list, create, overwrite, delete
from errors import log_error
from functions import ch_time, ch_size, get_user_size

# the user can choose his username
def choose_user():
    selection = 0
    try:
        list_users = os.listdir(ch_path('~/'))
    except FileNotFoundError:
        os.mkdir(ch_path('~/'))
        list_users = os.listdir(ch_path('~/'))

    if len(list_users) > 0:
        getch_start()
        while True:
            cls()
            s_out('Choose your username or press \'n\' to create a new user.')
            s_out()
            s_out('Name' + (' ' * (os.get_terminal_size().columns - 19)) + 'Time ago  Size')
            for name in range(len(list_users)):
                # print username
                if name == selection:
                    s_out('\x1b[7m' + list_users[name] + '\x1b[0m', end = '')
                else:
                    s_out(list_users[name], end = '')
 
                try:
                    # calculate the time ago
                    data = get_list(list_users[name], 'userinfo')
                    if len(data) == 5:
                        last_time_learned = data[1]
                    else:
                        last_time_learned = 0
   
                    # print the time ago
                    s_out(' ' * ((os.get_terminal_size().columns - len(list_users[name])) - 15), end = '')
                    t = ch_time(time() - last_time_learned)[0]
                    s_out(t, end = '')
                    s_out(' ' * (10 - len(t)), end = '')

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
                    getch_stop()
                    return list_users[selection]
                # down
                if ch == 'j' or ch == 's':
                    selection = selection + 1
                # up
                if ch == 'k' or ch == 'w':
                    selection = selection - 1
                # ctrl + c
                if ch == '\x03':
                    getch_stop()
                    raise KeyboardInterrupt
                # ctrl + d
                if ch == '\x04':
                    getch_stop()
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
                    getch_stop()
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
                getch_stop()
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

    name = s_inp('Type your new username.   > ', mode = 'path')
    while name == '' or name in os.listdir(ch_path('~/')):
        s_out('\x1b[1;49;31mThis name already exist. Choose another name.\x1b[0m')
        name = s_inp('Type your new username.   > ', mode = 'path')
    return name

def login(name = ''):   
    if name == '':
        name = choose_user()
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
    return name, userinfo

def logout(name, userinfo):
    userinfo[1] = time()
    userinfo[2] = userinfo[2] + (time() - userinfo[3])
    userinfo[4] = True
    overwrite(name, userinfo, 'userinfo')

