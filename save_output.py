import sys

not_printable_characters = [
['\x00', '\\x00'],
['\x01', '\\x01'],
['\x02', '\\x02'],
['\x03', '\\x03'],
['\x04', '\\x04'],
['\x05', '\\x05'],
['\x06', '\\x06'],
['\x07', '\\x07'],
['\x08', '\\x08'],
['\x0b', '\\x0b'],
['\x0c', '\\x0c'],
['\x0e', '\\x0e'],
['\x0f', '\\x0f'],
['\x10', '\\x10'],
['\x11', '\\x11'],
['\x12', '\\x12'],
['\x13', '\\x13'],
['\x14', '\\x14'],
['\x15', '\\x15'],
['\x16', '\\x16'],
['\x17', '\\x17'],
['\x18', '\\x18'],
['\x19', '\\x19'],
['\x1a', '\\x1a'],
['\x1c', '\\x1c'],
['\x1d', '\\x1d'],
['\x1e', '\\x1e'],
['\x1f', '\\x1f'],
['\x7f', '\\x7f'],
['\x80', '\\x80'],
['\x81', '\\x81'],
['\x82', '\\x82'],
['\x83', '\\x83'],
['\x84', '\\x84'],
['\x85', '\\x85'],
['\x86', '\\x86'],
['\x87', '\\x87'],
['\x88', '\\x88'],
['\x89', '\\x89'],
['\x8a', '\\x8a'],
['\x8b', '\\x8b'],
['\x8c', '\\x8c'],
['\x8d', '\\x8d'],
['\x8e', '\\x8e'],
['\x8f', '\\x8f'],
['\x90', '\\x90'],
['\x91', '\\x91'],
['\x92', '\\x92'],
['\x93', '\\x93'],
['\x94', '\\x94'],
['\x95', '\\x95'],
['\x96', '\\x96'],
['\x97', '\\x97'],
['\x98', '\\x98'],
['\x99', '\\x99'],
['\x9a', '\\x9a'],
['\x9b', '\\x9b'],
['\x9c', '\\x9c'],
['\x9d', '\\x9d'],
['\x9e', '\\x9e'],
['\x9f', '\\x9f'],
['\xa0', '\\xa0'],
['\xad', '\\xad']]

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

