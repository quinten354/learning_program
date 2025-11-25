# import modules
import os
import sys

# get single character
def getch(location = sys.stdin):
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
        # use termios
        import termios

        fd = location.fileno()
        orig = termios.tcgetattr(fd)

        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ICANON
        new[6][termios.VMIN] = 1
        new[6][termios.VTIME] = 0

        try:
            termios.tcsetattr(fd, termios.TCSAFLUSH, new)
            return location.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, orig)

