# import modules
import os
import sys

if os.name != 'nt':
    import termios

default = termios.tcgetattr(sys.stdin)

# get single character
def getch(echo = False):
    # windows
    if os.name == 'nt':
        # use msvcrt
        from msvcrt import getwch
        # get character
        ch = getwch()
        # there are some diffrences between this output and the output on other systems, it will change them
        # go to begin of line will be newline
        if ch == '\r':
            return '\n'
        # backspace (windows 08 other 7f) and ctrl + backspace (windows 7f other 08) exchange
        elif ch == '\x08':
            return '\x7f'
        elif ch == '\x7f':
            return '\x08'
        # escape or special keys (like arrows, home/end, insert/delete, f-keys) is on windows 'à' and on other systems 1b
        elif ch == 'à':
            return '\x1b'
        else:
            return ch

    # other
    else:
        fd = sys.stdin.fileno()
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ICANON
        if not echo:
            new[3] = new[3] & ~termios.ECHO
        new[6][termios.VMIN] = 1
        new[6][termios.VTIME] = 0

        try:
            termios.tcsetattr(fd, termios.TCSAFLUSH, new)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, default)

def start(echo = False):
    if os.name == 'nt':
        return

    fd = sys.stdin.fileno()
    orig = termios.tcgetattr(fd)

    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON
    new[3] = new[3] & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0

    termios.tcsetattr(fd, termios.TCSAFLUSH, new)

def getch_():
    if os.name == 'nt':
        return getch()

    return sys.stdin.read(1)

def stop():
    if os.name == 'nt':
        return

    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSAFLUSH, default)

