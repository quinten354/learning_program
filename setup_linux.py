#!/usr/bin/env python3

import subprocess
import signal
from getch import getch
from save_input import save_input as sinp
import os
import inspect
import sys

if os.name == 'nt':
    print('This program can\'t run on windows (nt).')
    input('Press enter to continue. ')
    exit(1)

insdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
slash = '\\' if os.name == 'nt' else '/'
signal.signal(signal.SIGINT, signal.SIG_IGN)

def cls():
    print('\x1b[2J\x1b[3J\x1b[H', end = '')

try:
    while True:
        cls()
        print('\rPress \'i\' if you want to install or \'u\' if you want to update. ', end = '')
        ch = getch()
        if ch == 'i':
            print()
            try:
                subprocess.run([sys.executable, insdir + slash + 'learning_program_installer.py'])
                exit()
            except Exception as error:
                if type(error) != SystemExit:
                    print(error)
                    input('Press enter to continue. ')
        elif ch == 'u':
            print()
            try:
                subprocess.run([sys.executable, insdir + slash + 'learning_program_updater.py'])
                exit()
            except Exception as error:
                if type(error) != SystemExit:
                    print(error)
                    input('Press enter to continue. ')
        elif ch == 'q':
            print()
            exit()

except Exception as error:
    print(error)
    exit(1)

