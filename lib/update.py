# import modules
import shutil
import sys
import os
from time import sleep as wait, time

from extern.save_output import save_output as s_out, cls
from extern.save_input import save_input as s_inp

from file_browser import browser
from errors import log_error

version = '3.1'

# update the program
def update(path_info):
    # set some default variables
    try:
        file = open(path_info)
        info = eval(file.read())
        file.close()
    except Exception as error:
        log_error()
        s_out('Error: Can\'t open info file (' + path_info + ').')
        s_out(error)
        s_inp('Press enter to close the program. ')
        exit(1)

    if path_info != info['path_info']:
        s_out('Warning: \'' + path_info + '\' is not the same as \'' + info['path_info'] + '\'.')
        s_inp('Press enter to continue. ')

    path_setup = info['path_setup']
    path_lib = info['path_lib']
    path_users = info['path_users']
    path_log = info['path_log']

    quote = '\''
    slash = '\\' if os.name == 'nt' else '/'
    home = 'os.path.expanduser(\'~\') + '
    homedir = os.path.expanduser('~')
    
    # help user to download the new version and to unzip it
    cls()
    s_out('Download the new version of the program.')
    s_inp('Press enter to continue. ')

    s_out('Unzip the downloaded zip file.')
    s_inp('Press enter to continue. ')

    s_out('Open the directory of the new version.')
    s_inp('Press enter to do it! ')

    # open the new version
    while True:
        try:
            installer_dir = browser(homedir, mode = 'open', type = 'd', message = 'Directory of the new version of the learning program')
            break
        except Exception as error:
            log_error()
            s_out(error)
            s_inp('Press enter to try again. ')
            continue

    sys.path.append(installer_dir)

    import copy_files

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
        log_error()
        s_out('Error: Can\'t create info file.')
        s_out(error)
        input('Press enter to close the program. ')
        exit(1)
    
    
    
    ###############
    # end updater #
    ###############
    
    cls()
    
    s_out('Your learning program has been updated!')
    s_out('Execute ' + path_setup + ' to run the program.')
    input('Press enter to close the updater. ')

