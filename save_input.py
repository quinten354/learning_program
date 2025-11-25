# import modules
from getch import getch
import os
import sys

s_out = sys.stdout.write
flush = sys.stdout.flush

# set functions
# show user input
def print_input(prompt, input, position_cursor, insert = False, hide = False):
    try:
        columns = os.get_terminal_size().columns
    except:
        columns = 120
    # when hidden, show stars
    if hide:
        input = '*' * len(input)
    # change tabs for spaces
    input = input.replace('\x89', '').replace('\x1b', '\\')
    begin = False
    end = False

    while len(prompt + input) > (columns - 9):
        if position_cursor > (len(input) / 2):
            input = input[1:]
            position_cursor = position_cursor - 1
            begin = True
        else:
            input = input[:-1]
            end = True

    txt = '\r' + prompt + ('«' if begin else '') + input + ('»' if end else '')
    txt = txt + (' ' * ((columns - 3) - len(txt)) + ('I' if insert else ' ') + ('V' if hide else ' ') + ' ')
    try:
        s_out(txt)
    except UnicodeEncodeError:
        for karakter in txt:
            try:
                s_out(karakter)
            except UnicodeEncodeError:
                s_out('\x1b[1;49;31mX\x1b[0m')

    txt = '\r' + ('\x1b[C' * len(prompt + ('«' if begin else '') + input[:position_cursor]))
    try:
        s_out(txt)
    except UnicodeEncodeError:
        for karakter in txt:
            try:
                s_out(karakter)
            except UnicodeEncodeError:
                s_out('\x1b[1;49;31mX\x1b[0m')
    flush()

def save_input(prompt = '', valid_characters = [], invalid_characters = [], input = '', enter_characters = [], hide = False):
    lijst_stringen = prompt.split('\n')
    if len(lijst_stringen) > 1:
        for regel in lijst_stringen[:-1]:
            s_out(regel + '\n')
        prompt = lijst_stringen[-1]

    try:
        columns = os.get_terminal_size().columns
    except:
        columns = 120
    while len(prompt) > (columns - 25):
        s_out(prompt[:columns] + '\n')
        prompt = prompt[columns:]

    position_cursor = len(input)
    insert = False

    print_input(prompt, input, position_cursor, insert, hide)

    while True:
        niet_toevoegen = False
        ch = getch()

        if ch in invalid_characters:
            continue

        if ch in enter_characters:
            return input, ch

        if ch == '\x1b' or ch == '\x00':
            c1 = getch()
            if (ch + c1) in enter_characters:
                return input, ch + c1
            toegevoegd = True
            if os.name != 'nt':
                if c1 == '[':
                    c2 = getch()
                    if (ch + c1 + c2) in enter_characters:
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
                            return input, ch + c1 + c2 + c3
                        if position_cursor < len(input):
                            input = input[:position_cursor] + input[position_cursor + 1:]
                    elif c2 == '2':
                        c3 = getch()
                        if (ch + c1 + c2 + c3) in enter_characters:
                            return input, ch + c1 + c2 + c3
                        insert = not insert
                    elif c2 == 'H' or c2 == 'A':
                        position_cursor = 0
                    elif c2 == 'F' or c2 == 'B':
                        position_cursor = len(input)
                    elif c2 == '1':
                        c3 = getch()
                        if (ch + c1 + c2 + c3) in enter_characters:
                            return input, ch + c1 + c2 + c3
                        if c3 == ';':
                            c4 = getch()
                            # ;2 --> shift, ;5 --> ctrl of alt, ;7 --> ctrl and alt, ;6 --> shift and ctrl, ;4 --> shift and alt, ;8 --> shift and ctrl and alt
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
                    toegevoegd = False

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
                    toegevoegd = False

            if not toegevoegd:
                karakters1 = '\x01\x02\x05\x06\x07\x0b\x0c\x0e\x10\x14\x15\x16\x17\x18\x1e\x1f'
                karakters2 = ['^A', '^B', '^E', '^F', '^G', '^K', '^L', '^N', '^P', '^T', '^U', '^V', '^W', '^X', '^^', '^_']
                for i in range(len(karakters1)):
                    if c1 == karakters1[i]:
                        c1 = karakters2[i]

                if c1 == '\x1b' or c1 == '\x00':
                    c1 = ''
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
            raise EOFError
        elif ch == '\x03':
            raise KeyboardInterrupt
        elif ch == '\x12':
            if len(prompt) > 0:
                s_out('\n')
                flush()
                prompt = prompt[columns:]

        elif ch == '\n':
            if os.name == 'nt':
                s_out('\n')
                flush()
            return input

        else:
            karakters1 = '\x01\x02\x05\x06\x07\x0b\x0c\x0e\x10\x14\x15\x16\x17\x18\x1e\x1f'
            karakters2 = ['^A', '^B', '^E', '^F', '^G', '^K', '^L', '^N', '^P', '^T', '^U', '^V', '^W', '^X', '^^', '^_']
            for i in range(len(karakters1)):
                if ch == karakters1[i]:
                    ch = karakters2[i]

            if ch == '\x1b' or ch == '\x00':
                ch = '^['

            if insert:
                input = input[:position_cursor] + ch + input[position_cursor + len(ch):]
            else:
                input = input[:position_cursor] + ch + input[position_cursor:]
            position_cursor = position_cursor + len(ch)

        input = input.replace('\x1b', '^[') 

        if len(valid_characters) > 0:
            for input in input:
                if input not in valid_characters:
                    input.replace(input, '')

        for ongeldige_karakter in invalid_characters:
            input = input.replace(ongeldige_karakter, '')

        print_input(prompt, input, position_cursor, insert, hide)

