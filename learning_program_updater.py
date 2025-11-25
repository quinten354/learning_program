# learning program updater
# Autor:   Quinten Taminiau
# Date:    25-11-2025
# Version: 3.1
# Python:  3.11

version = '3.1'

# import modules
import os
import shutil
import inspect
import logging
import sys
import datetime
from time import sleep as wait, time
import copy_files

installer_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(installer_dir + '/lib')
from file_browser import browser

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
# lib/database.py           <path_to_users>            path_users
# lib/main.py               <path_to_info>             path_info

def cls():
    print('\x1b[2J\x1b[3J\x1b[H', end = '')

logging.basicConfig(filename = 'install.log', level = logging.ERROR)

def log():
    logging.exception('learning_program_installer.py - ' + str(datetime.datetime.now()))

# set standard variables
quote = '\''
slash = '\\' if os.name == 'nt' else '/'
home = 'os.path.expanduser(\'~\') + '
homedir = os.path.expanduser('~')

# ask user for info file
print('Open the info file that is created by installing the program.')
input('Press enter to continue. ')

while True:
    try:
        path_info = browser(homedir, mode = 'open', type = 'f', message = 'Info file')
        break
    except Exception as error:
        log()
        print(error)
        input('Press enter to try again. ')
        continue

cls()

# get paths of files/dirs in the program
try:
    file = open(path_info)
    info = eval(file.read())
    file.close()

    if path_info != info['path_info']:
        print('Warning: \'' + path_info + '\' is not the same as \'' + info['path_info'] + '\'.')
        input('Press enter to continue. ')

    path_setup = info['path_setup']
    path_lib   = info['path_lib']
    path_users = info['path_users']
    path_log   = info['path_log']

except Exception as error:
    log()
    print('Error: Can\'t get info from the info file.')
    print(error)
    input('Press enter to close the program. ')
    exit(1)

copy_files.main(path_lib, path_log, path_users, path_setup, path_info)



####################
# update info file #
####################

try:
    info['version'].append(version)
    info['time_installed'].append(time())

    file = open(path_info, mode = 'w')
    file.write(str(info))
    file.close()

except Exception as error:
    log()
    print('Error: Can\'t create info file.')
    print(error)
    input('Press enter to close the program. ')
    exit(1)



###############
# end updater #
###############

cls()

print('Your learning program has been updated!')
print('Execute ' + path_setup + ' to run the program.')
input('Press enter to close the updater. ')

