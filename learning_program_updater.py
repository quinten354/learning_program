# learning program updater
# Autor:   Quinten Taminiau
# Date:    14-04-2026
# Version: 4.0
# Develop: Python 3.13 Linux

version = '4.0'

# import modules
import os
import shutil
import inspect
import logging
import sys
import datetime
from time import sleep as wait, time
import copy_files

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

# ask user for info file
s_out('Open the info file that is created by installing the program.')
s_inp('Press enter to continue. ')

while True:
    try:
        path_info = browser(homedir, mode = 'open', type = 'f', message = 'Info file')
        break
    except Exception as error:
        if type(error) == KeyboardInterrupt:
            exit()
        log()
        s_out(error)
        s_inp('Press enter to try again. ')
        continue

cls()

# get paths of files/dirs in the program
try:
    file = open(path_info)
    info = eval(file.read())
    file.close()

    if path_info != info['path_info']:
        s_out('Warning: \'' + path_info + '\' is not the same as \'' + info['path_info'] + '\'.')
        s_inp('Press enter to continue. ')

    path_setup = info['path_setup']
    path_lib   = info['path_lib']
    path_users = info['path_users']
    path_log   = info['path_log']

except Exception as error:
    log()
    s_out('Error: Can\'t get info from the info file.')
    s_out(error)
    s_inp('Press enter to close the program. ')
    s_out()
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
    s_out('Error: Can\'t create info file.')
    s_out(error)
    s_inp('Press enter to close the program. ')
    s_out()
    exit(1)



###############
# end updater #
###############

cls()

s_out('Your learning program has been updated!')
s_out('Execute ' + path_setup + ' to run the program.')
s_inp('Press enter to close the updater. ')
s_out()

