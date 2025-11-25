import sys
import os
import inspect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from manage_files import ch_path, create_list

file = open(ch_path('~/basic_files/not-supported_characters', mode = 'system'))
data = file.read()
file.close()
not_printable_characters = create_list(data)

def cls():
    save_output('\x1b[2J\x1b[3J\x1b[H', end = '')

def save_output(*args, sup = '', end = '\n', location = sys.stdout, remove_not_printable_characters = True):
    string = ''
    for count in range(len(args)):
        if count != 0:
            string = string + str(sup)
        string = string + str(args[count])
        
    string = string + end
    
    if remove_not_printable_characters:
        for not_printable_character in not_printable_characters:
            string = string.replace(not_printable_character[0], '\x1b[1;49;31m�\033[0m')

    write(string, location)
    
def write(string, location):
    try:
        location.write(string)
        location.flush()
    except UnicodeEncodeError:
        for karakter in string:
            try:
                location.write(karakter)
                location.flush()
            except UnicodeEncodeError:
                location.write('\x1b[1;49;31m�\033[0m')
                location.flush()

