# Learning program installer
# Autor:   Quinten Taminiau
# Date:    14-04-2026
# Version: 4.0
# Develop: Python 3.13 Linux

version = '4.0'

# import modules
import os
import inspect
import shutil
import sys
import logging
import datetime
import copy_files
from timeout import timeout
from getchar import getch
from time import sleep as wait, time

# path_installer            var_installer              path_linux                           path_windows
# lib                       path_lib                   /usr/local/lib/learning_program/     ~\AppData\Local\learning_program\
# learning_program          path_setup                 /usr/local/bin/learning_program      ~\Desktop\learning_program
# [user(s)]                 path_users                 ~/.learning_program/<username>       ~\.learning_program\<username>
# [log]                     path_log                   /var/log/learning_program.log        ~\AppData\Local\learning_program.log
# [info]                    path_info                  ~/.learning_program.info             ~.learning_program.info

# file                      var                        replacing
# learning_program          <path_to___init__.py>      path_lib + '/__init__.py'
# learning_program          <path_to_python>           sys.executable
# learning_program          <path_to_log>              path_log
# lib/__init__.py           <path_to_log>              path_log
# lib/__init__.py           <path_to_info>              path_info
# lib/errors.py             <path_to_log>              path_log
# lib/database.py           <path_to_users>            path_users
# lib/main.py               <path_to_info>             path_info

logging.basicConfig(filename = 'install.log', level = logging.ERROR)

def log():
    logging.exception('learning_program_installer.py - ' + str(datetime.datetime.now()))

# set standard variables
quote = '\''
slash = '\\' if os.name == 'nt' else '/'
home = 'os.path.expanduser(\'~\') + '
homedir = os.path.expanduser('~')
installer_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.insert(0, installer_dir + slash + 'lib' + slash)
sys.path.insert(0, installer_dir + slash + 'lib' + slash + 'extern' + slash)
from file_browser import browser
from save_input import save_input as s_inp
from save_output import save_output as s_out, cls

# set posible locations on disk
if os.name == 'nt':
    path_lib   = homedir + '\\AppData\\Local\\learning_program'
    path_setup = homedir + '\\learning_program.py'
    path_users = homedir + '\\.learning_program'
    path_log   = homedir + '\\AppData\\Local\\learning_program.log'
    path_info  = homedir + '\\.learning_program.info'

elif os.name == 'posix':
    path_lib   = '/usr/local/lib/learning_program' if os.geteuid() == 0 else homedir + '/.local/share/learning_program'
    path_setup = '/usr/local/bin/learning_program' if os.geteuid() == 0 else homedir + '/learning_program'
    path_users = homedir + '/.learning_program'
    path_log   = '/var/log/learning_program.log'   if os.geteuid() == 0 else homedir + '/.local/share/learning_program.log'
    path_info  = homedir + '/.learning_program.info'

else:
    path_lib   = homedir
    path_setup = homedir
    path_users = homedir
    path_log   = homedir
    path_info  = homedir

# ask user
s_out('Select a directory for the lib files of the program. You can set it anywhere if the program can write, read and execute in that directory.')
s_inp('Press enter to continue. ')

while True:
    try:
        path_lib = browser(path_lib,   mode = 'create', type = 'd', message = 'Lib files')
        break
    except Exception as error:
        log()
        s_out(error)
        s_inp('Press enter to try again. ')
        continue

cls()

s_out('Select a file for setup file of the program. You must execute it to start the program. Choose a filename such as \'~/Desktop/learning_program\' or if you want to run it as command, somethings like \'/usr/local/bin/learning_program\'.')
s_inp('Press enter to continue. ')

while True:
    try:
        path_setup = browser(path_setup, mode = 'create', type = 'f', message = 'Setup file')
        break
    except Exception as error:
        log()
        s_out(error)
        s_inp('Press enter to try again. ')
        continue

cls()

s_out('Select a directory for the user data of the program. The program must can read and write in that directory.')
s_inp('Press enter to continue. ')

while True:
    try:
        path_users = browser(path_users, mode = 'create', type = 'd', message = 'User data')
        break
    except Exception as error:
        log()
        s_out(error)
        s_inp('Press enter to try again. ')
        continue

cls()

s_out('Select a file for the log file of the program. You can set it anywhere if the program can write and read to that file. It\'s not a problem if this file become cleared.')
s_inp('Press enter to continue. ')

while True:
    try:
        path_log = browser(path_log,   mode = 'create', type = 'f', message = 'Log file')
        break
    except Exception as error:
        log()
        s_out(error)
        s_inp('Press enter to try again. ')
        continue

cls()

s_out('Select a file for the installing info of the program. By automaticly updating, this file is needed.')
s_inp('Press enter to continue. ')

while True:
    try:
        path_info = browser(path_info,   mode = 'create', type = 'f', message = 'Info file')
        break
    except Exception as error:
        log()
        s_out(error)
        s_inp('Press enter to try again. ')
        continue

cls()

s_out('Lib files:  ' + path_lib)
s_out('Setup file: ' + path_setup)
s_out('User data:  ' + path_users)
s_out('Log file:   ' + path_log)
s_out('Info file:  ' + path_info)
s_inp('Press enter to continue. ')

cls()

copy_files.main(path_lib, path_log, path_users, path_setup, path_info)



####################
# create info file #
####################

try:
    if not os.path.exists(path_info):
        open(path_info, mode = 'x').close()

    os.chmod(path_info, 0o666)

    info = {'version': [version], 'time_installed': [time()], 'path_setup': path_setup, 'path_lib': path_lib, 'path_users': path_users, 'path_log': path_log, 'path_info': path_info}

    file = open(path_info, mode = 'w')
    file.write(str(info))
    file.close()

except Exception as error:
    log()
    s_out('Error: Can\'t create info file.')
    s_out(error)
    s_inp('Press enter to close the program. ')
    s_out()
    exit(1)



#################
# end installer #
#################

cls()

s_out('Your learning program has been installed!')
s_out('Execute ' + path_setup + ' to run the program.')
s_inp('Press enter to close the installer. ')
s_out()

