# import modules
from getchar import getch_ as getch, start as getch_start, stop as getch_stop
from save_output import save_output as s_out
import os
import inspect

# set functions
# show user input
def print_input(prompt, input, position_cursor, insert = False, hide = False):
    try:
        columns = os.get_terminal_size().columns
    except:
        columns = 120
    if hide:
        input = '*' * len(input)
    begin = False
    end = False
    while len(prompt + input) > (columns - 6):
        if position_cursor > (len(input) / 2):
            input = input[1:]
            position_cursor = position_cursor - 1
            begin = True
        else:
            input = input[:-1]
            end = True

    txt = '\r' + prompt + ('«' if begin else '') + input + ('»' if end else '')
    txt = txt + (' ' * ((columns - 2) - len(txt)) + ('I' if insert else ' ') + ('V' if hide else ' ') + ' ')
    try:
        s_out(txt, end = '')
    except UnicodeEncodeError:
        for karakter in txt:
            try:
                s_out(karakter, end = '')
            except UnicodeEncodeError:
                s_out('\x1b[1;49;31mX\x1b[0m', end = '')
    txt = '\r' + ('\x1b[C' * len(prompt + ('«' if begin else '') + input[:position_cursor]))
    try:
        s_out(txt, end = '')
    except UnicodeEncodeError:
        for karakter in txt:
            try:
                s_out(karakter, end = '')
            except UnicodeEncodeError:
                s_out('\x1b[1;49;31mX\x1b[0m', end = '')

def save_input(prompt = '', valid_characters = [], invalid_characters = [], input = '', enter_characters = [], hide = False, getch_start_stop = True, max_length = 0, mode = None):
    if mode == 'path' or mode == 'file' or mode == 'dir':
        if os.name == 'nt':
            invalid_characters = invalid_characters + ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
            max_length = 255
        else:
            invalid_characters = invalid_characters + ['\\', '/']

    strings = prompt.split('\n')
    if len(strings) > 1:
        for regel in strings[:-1]:
            s_out(regel + '\n', end = '')
        prompt = strings[-1]

    try:
        columns = os.get_terminal_size().columns
    except:
        columns = 120
    while len(prompt) > (columns - 25):
        s_out(prompt[:columns] + '\n', end = '')
        prompt = prompt[columns:]

    position_cursor = len(input)
    insert = False

    print_input(prompt, input, position_cursor, insert, hide)

    getch_start()

    while True:
        ch = getch()

        if ch in invalid_characters:
            print_input(prompt, input, position_cursor, insert, hide)
            continue

        if ch in enter_characters:
            if getch_start_stop:
                getch_stop()
            return input, ch

        if ch == '\x1b' or ch == '\x00':
            c1 = getch()
            if (ch + c1) in enter_characters:
                if getch_start_stop:
                    getch_stop()
                return input, ch + c1
            added = True
            if os.name != 'nt':
                if c1 == '[':
                    c2 = getch()
                    if (ch + c1 + c2) in enter_characters:
                        if getch_start_stop:
                            getch_stop()
                        return input, ch + c1 + c2
                    if c2 == 'D':
                        position_cursor = position_cursor - 1
                        if position_cursor < 0:
                            position_cursor = 0
                    elif c2 == 'C':
                        position_cursor = position_cursor + 1
                        if position_cursor > len(input):
                            position_cursor = len(input) 
                    elif c2 == '3':
                        c3 = getch()
                        if (ch + c1 + c2 + c3) in enter_characters:
                            if getch_start_stop:
                                getch_stop()
                            return input, ch + c1 + c2 + c3
                        if position_cursor < len(input):
                            input = input[:position_cursor] + input[position_cursor + 1:]
                    elif c2 == '2':
                        c3 = getch()
                        if (ch + c1 + c2 + c3) in enter_characters:
                            if getch_start_stop:
                                getch_stop()
                            return input, ch + c1 + c2 + c3
                        insert = not insert
                    elif c2 == 'H' or c2 == 'A':
                        position_cursor = 0
                    elif c2 == 'F' or c2 == 'B':
                        position_cursor = len(input)
                    elif c2 == '1':
                        c3 = getch()
                        if (ch + c1 + c2 + c3) in enter_characters:
                            if getch_start_stop:
                                getch_stop()
                            return input, ch + c1 + c2 + c3
                        if c3 == ';':
                            c4 = getch()
                            # ;2 --> shift, ;5 --> ctrl of alt, ;7 --> ctrl en alt, ;6 --> shift en ctrl, ;4 --> shift en alt, ;8 --> shift en ctrl en alt
                            if c4 == '5':
                                c5 = getch()
                                if c5 == 'D':
                                    position_cursor = 0
                                elif c5 == 'C':
                                    position_cursor = len(input)
                            if c4 == '2' or c4 == '3':
                                c5 = getch()
                                if c5 == 'D':
                                    position_cursor = position_cursor - 4
                                    if position_cursor < 0:
                                        position_cursor = 0
                                if c5 == 'C':
                                    position_cursor = position_cursor + 4
                                    if position_cursor > len(input):
                                        position_cursor = len(input)

                elif c1 == 'O':
                    c2 = getch()
                    if c2 == 'P':
                        hide = not hide
                else:
                    added = False

            if os.name == 'nt':
                if c1 == 'K':
                    position_cursor = position_cursor - 1
                    if position_cursor < 0:
                        position_cursor = 0
                elif c1 == 'M':
                    position_cursor = position_cursor + 1
                    if position_cursor > len(input):
                        position_cursor = len(input)
                elif c1 == 's' or c1 == 'G' or c1 == 'H':
                    position_cursor = 0
                elif c1 == 't' or c1 == 'O' or c1 == 'P':
                    position_cursor = len(input)
                elif c1 == 'S':
                    if position_cursor < len(input):
                        input = input[:position_cursor] + input[position_cursor + 1:]
                elif c1 == 'R':
                    insert = not insert
                elif c1 == ';':
                    hide = not hide
                elif c1 == '\x9b':
                    position_cursor = position_cursor - 4
                    if position_cursor < 0:
                        position_cursor = 0
                elif c1 == '\x9d':
                    position_cursor = position_cursor + 4
                    if position_cursor > len(input):
                        position_cursor = len(input)
                else:
                    added = False

            if not added:
                if insert and os.name == 'nt':
                    input = input[:position_cursor] + 'à' + c1 + input[position_cursor + len('à' + c1):]
                elif os.name == 'nt':
                    input = input[:position_cursor] + 'à' + c1 + input[position_cursor:]
                elif insert:
                    input = input[:position_cursor] + '^[' + c1 + input[position_cursor + len('à' + c1):]
                else:
                    input = input[:position_cursor] + '^[' + c1 + input[position_cursor:]
                if os.name == 'nt':
                    position_cursor = position_cursor + len('à' + c1)
                else:
                    position_cursor = position_cursor + len('^[' + c1)

        elif ch == '\t':
            if insert:
                input = input[:position_cursor] + '    ' + input[position_cursor + 4:]
            else:
                input = input[:position_cursor] + '    ' + input[position_cursor:]
            position_cursor = position_cursor + 4
        elif ch == '\x9b':
            continue
        elif ch == '\x7f':
            if position_cursor > 0:
                input = input[:position_cursor - 1] + input[position_cursor:]
                position_cursor = position_cursor - 1
        elif ch == '\x08':
            input = ''
            position_cursor = 0
        elif ch == '\x04':
            if getch_start_stop:
                getch_stop()
            raise EOFError
        elif ch == '\x03':
            if getch_start_stop:
                getch_stop()
            raise KeyboardInterrupt
        elif ch == '\x12':
            if len(prompt) > 0:
                s_out('\n', end = '')
                prompt = prompt[columns:]

        elif ch == '\n':
            s_out()
            if getch_start_stop:
                getch_stop()
            return input

        else:
            if insert:
                input = input[:position_cursor] + ch + input[position_cursor + len(ch):]
            else:
                input = input[:position_cursor] + ch + input[position_cursor:]
            position_cursor = position_cursor + len(ch)

        if len(valid_characters) > 0:
            for input in input:
                if input not in valid_characters:
                    input.replace(input, '')

        for invalid_character in invalid_characters:
            input = input.replace(invalid_character, '')

        if max_length:
            input = input[:max_length]
        print_input(prompt, input, position_cursor, insert, hide)

    if getch_start_stop:
        getch_stop()

