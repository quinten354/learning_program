# import modules
import os
import shutil
import inspect
import logging
import sys
import datetime
from time import sleep as wait, time

# path_installer            var_installer              path_linux                           path_windows
# lib                       path_lib                   /usr/local/lib/learning_program/     ~\AppData\local\learning_program\
# learning_program          path_setup                 /usr/local/bin/learning_program      ~\Desktop\learning_program
# [user(s)]                 path_users                 ~/.learning_program/<username>       ~\.learning_program\<username>
# [log]                     path_log                   /var/log/learning_program.log        ~\AppData\local\learning_program.log
# [info]                    path_info                  ~/.learning_program.info             ~.learning_program.info

# file                      var                        replacing
# learning_program          <path_to___init__.py>      path_lib + '/__init__.py'
# learning_program          <path_to_python>           sys.executable
# learning_program          <path_to_log>              path_log
# lib/__init__.py           <path_to_log>              path_log
# lib/__init__.py           <path_to_log>              path_info
# lib/errors.py             <path_to_log>              path_log
# lib/manage_files.py           <path_to_users>            path_users
# lib/main.py               <path_to_info>             path_info

version = '3.1'

def cls():
    print('\x1b[2J\x1b[3J\x1b[H', end = '')

# set standard variables
quote = '\''
slash = '\\' if os.name == 'nt' else '/'
home = 'os.path.expanduser(\'~\') + '
homedir = os.path.expanduser('~')
installer_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

logging.basicConfig(filename = installer_dir + '/install.log', level = logging.ERROR)

def log():
    logging.exception('learning_program_installer.py - ' + str(datetime.datetime.now()))

def main(path_lib, path_log, path_users, path_setup, path_info):
    # ask user for changing home dir (homedir) to home, to switch automaticly between users
    if homedir in path_users or homedir in path_log:
        print('Do you want to change the home directory (' + homedir + ') into a program that set the home directory?')
        print('This is for the user-directory and the log directory.')
        inp = input('If another user login, data will be saved in that home directory, not in yours. (yes/no)   > ')
        while inp not in ['yes', 'no']:
            inp = input('If another user login, data will be saved in that home directory, not in yours. (yes/no)   > ')

        if inp == 'yes':
            if homedir in path_users:
                fpath_users = home + quote + path_users.replace(homedir, '') + quote
            else:
                fpath_users = quote + path_users + quote
            if homedir in path_log:
                fpath_log = home + quote + path_log.replace(homedir, '') + quote
            else:
                fpath_log = quote + path_log + quote

        else:
            fpath_users = quote + path_users + quote
            fpath_log = quote + path_log + quote

    else:
        fpath_users = quote + path_users + quote
        fpath_log = quote + path_log + quote

    fpath_lib = quote + path_lib + quote
    fpath_setup = quote + path_setup + quote
    fpath_info = quote + path_info + quote
    fpath_lib = fpath_lib.replace('\\', '\\\\')
    fpath_log = fpath_log.replace('\\', '\\\\')
    fpath_users = fpath_users.replace('\\', '\\\\')
    fpath_setup = fpath_setup.replace('\\', '\\\\')
    fpath_info = fpath_info.replace('\\', '\\\\')



    ################################
    # install lib/learning_program #
    ################################

    cls()

    # delete all files in path_lib

    try:
        os.chmod(path_lib, 0o777)
    except:
        log()

    listdir = os.listdir(path_lib)

    # ask permission to delete all items in lib
    try:
        if len(listdir) > 0:
            print('Press enter to delete this files/dirs in lib (' + path_lib + '):')
            for item in listdir:
                print(path_lib + slash + item)
        
            input()
        
            # delete all items in lib
            for item in listdir:
                if os.path.isfile(path_lib + slash + item):
                    os.remove(path_lib + slash + item)
                elif os.path.isdir(path_lib + slash + item):
                    shutil.rmtree(path_lib + slash + item)

    except Exception as error:
        log()
        print('Error: Can\'t remove files/dirs in \'' + path_lib + '\'.')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

    # copy files and dirs
    try:
        listdir = os.listdir(installer_dir + slash + 'lib')
        for item in listdir:
            if os.path.isfile(installer_dir + slash + 'lib' + slash + item):
                shutil.copy(installer_dir + slash + 'lib' + slash + item, path_lib + slash + item)
                os.chmod(path_lib + slash + item, 0o666)
            elif os.path.isdir(installer_dir + slash + 'lib' + slash + item):
                shutil.copytree(installer_dir + slash + 'lib' + slash + item, path_lib + slash + item)
                os.chmod(path_lib + slash + item, 0o777)

        os.chmod(path_lib + slash + '__init__.py', 0o777)

    except Exception as error:
        log()
        print('Error: Can\'t copy files/dirs from \'' + installer_dir + slash + 'lib' + '\'.')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

    # change var <path_to_users> in manage_files.py

    try:
        file = open(path_lib + slash + 'manage_files.py')
        data = file.read()
        file.close()
        data = data.replace('<path_to_users>', fpath_users)
        file = open(path_lib + slash + 'manage_files.py', mode = 'w')
        file.write(data)
        file.close()
    except Exception as error:
        log()
        print('Error: Can\'t edit file manage_files.py (' + path_lib + slash + 'manage_files.py' + ').')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

    # change var <path_to_log> in errors.py

    try:
        file = open(path_lib + slash + 'errors.py')
        data = file.read()
        file.close()
        data = data.replace('<path_to_log>', fpath_log)
        file = open(path_lib + slash + 'errors.py', mode = 'w')
        file.write(data)
        file.close()
    except Exception as error:
        log()
        print('Error: Can\'t edit file errors.py (' + path_lib + slash + 'errors.py' + ').')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

    # change var <path_to_log> and <path_to_info> in __init__.py

    try:
        file = open(path_lib + slash + '__init__.py')
        data = file.read()
        file.close()
        data = data.replace('<path_to_log>', fpath_log)
        data = data.replace('<path_to_info>', fpath_info)
        file = open(path_lib + slash + '__init__.py', mode = 'w')
        file.write(data)
        file.close()
    except Exception as error:
        log()
        print('Error: Can\'t edit file __init__.py (' + path_lib + slash + '__init__.py' + ').')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

    # change var <path_to_info> in main.py

    try:
        file = open(path_lib + slash + 'main.py')
        data = file.read()
        file.close()
        data = data.replace('<path_to_info>', fpath_info)
        file = open(path_lib + slash + 'main.py', mode = 'w')
        file.write(data)
        file.close()
    except Exception as error:
        log()
        print('Error: Can\'t edit file main.py (' + path_lib + slash + 'main.py' + ').')
        print(error)
        input('Press enter to close the program. ')
        exit(1)



    #########################################
    # install learning_program (setup file) #
    #########################################

    try:
        if not os.path.exists(path_setup):
            open(path_setup, mode = 'x').close()

    except Exception as error:
        log()
        print('Error: Can\'t create learning_program (setup file) (' + path_setup + ').')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

    try:
        os.chmod(path_setup, 0o777)
    except:
        log()

    try:
        f1 = open(installer_dir + slash + 'learning_program', mode = 'br')
        f2 = open(path_setup, mode = 'bw')
        f2.write(f1.read())
        f1.close()
        f2.close()

    except Exception as error:
        log()
        print('Error: Can\'t copy learning_program (setup file) (' + installer_dir + slash + 'learning_program' + ').')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

    try:
        file = open(path_setup)
        data = file.read()
        file.close()
        data = data.replace('<path_to___init__.py>', quote + path_lib.replace('\\', '\\\\') + slash.replace('\\', '\\\\') + '__init__.py' + quote)
        data = data.replace('<path_to_python>', sys.executable.replace('\\', '\\\\'))
        data = data.replace('<path_to_log>', fpath_log)
        file = open(path_setup, mode = 'w')
        file.write(data)
        file.close()

    except Exception as error:
        log()
        print('Error: Can\'t edit file learning_program (setup file) (' + installer_dir + slash + 'learning_program' + ').')
        print(error)
        input('Press enter to close the program. ')
        exit(1)

if __name__ == '__main__':
    main(*sys.argv[1:])

