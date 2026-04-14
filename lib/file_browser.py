from extern.getchar import getch_ as getch, start as getch_start, stop as getch_stop
import os
import datetime
from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out, cls

# ch size to human readable format
def ch_size(size):
    exponent = 0
    while size >= 1024:
        exponent = exponent + 1
        size = size / 1024

    size = str(size)

    try:
        position = size.index('.')
    except:
        position = len(size)

    if position < 3:
        size = size[:4]
    else:
        size = size[:position]

    list_sizes = [' ', 'K', 'M', 'G', 'T']
    size = size + list_sizes[exponent]

    while len(size) < 5:
        size = size + ' '

    return size

# main file browser function
def browser(path = os.path.expanduser('~'), mode = 'open', type = '', filename = '', message = '', root = True, show_point_files = False):
    getch_start()
    output = browser_(path, mode, type, filename, message, root, show_point_files)
    getch_stop()
    return output

def browser_(path = os.path.expanduser('~'), mode = 'open', type = '', filename = '', message = '', root = True, show_point_files = False):
    if os.name == 'nt':
        path = path.replace('/', '\\')

    if not os.path.exists(os.path.dirname(path)):
        path = os.path.expanduser('~')

    if path[-1] == '/' or path[-1] == '\\':
        pass
    elif os.path.isdir(path):
        path = path + ('\\' if os.name == 'nt' else '/')
    else:
        if filename == '': filename = os.path.basename(path)
        path = os.path.dirname(path) + ('\\' if os.name == 'nt' else '/')

    if mode not in ['open', 'create']:
        s_out('Invalid mode, choose between open or create.')
        mode = 'open'

    if type not in ['', 'f', 'd']:
        s_out('Invalid type, choose between \'\' (everything), f (file) or d (directory)')
        type = ''

    cursor = 0
    name = ''

    while True:
        # clear screen
        cls()

        # get items in current directory
        listdir = os.listdir(path)
        listdir.sort()
        listdirlength = len(listdir)
        for number in range(listdirlength):
            if listdir[(listdirlength - 1) - number][0] == '.' and not show_point_files:
                del listdir[(listdirlength - 1) - number]
        width_screen = os.get_terminal_size().columns
        max_length = width_screen - 34

        if filename != '':
            if cursor == 0:
                s_out('\x1b[7;49;33m', end = '')
            else:
                s_out('\x1b[1;49;33m', end = '')
            name_file = filename
            while len(name_file) >= max_length and max_length > 10:
                show_name_file = name_file[:max_length] + '      \x1b[1;49;37m|\x1b[0m'
                if cursor == 0:
                    show_name_file = show_name_file + '\x1b[7;49;33m'
                else:
                    show_name_file = show_name_file + '\x1b[1;49;33m'
                name_file = name_file[max_length:]
                s_out(show_name_file)
            s_out(name_file, end = '')

            # complete line with spaces
            s_out(' ' * (width_screen - 28 - len(name_file)), end = '')

            if type == 'f' or type == '': s_out('Create+select a new file \x1b[0m')
            if type == 'd': s_out('Create+select a new dir  \x1b[0m')

        tcursor = cursor
        if filename != '':
            tcursor = tcursor - 1

        # show items
        for number in range(len(listdir)):
            item = listdir[number]
            if number == tcursor:
                s_out('\x1b[7;49;1m', end = '')
            # show name of item
            name_item = item
            while len(name_item) >= max_length and max_length > 10:
                show_name_item = name_item[:max_length] + '      \x1b[1;49;37m|\x1b[0m'
                if number == tcursor:
                    show_name_item = show_name_item + '\x1b[7;49;1m'
                name_item = name_item[max_length:]
                s_out(show_name_item)
            s_out(name_item, end = '')

            try:
                # complete line with spaces
                s_out(' ' * (width_screen - 28 - len(name_item)), end = '')
    
                # show size
                s_out(ch_size(os.path.getsize(path + item)), end = ' ')
    
                # show last change
                s_out(str(datetime.datetime.fromtimestamp(round(os.path.getmtime(path + item)))))
    
            except:
                s_out()

            if number == tcursor:
                s_out('\x1b[0m', end = '')

        if len(listdir) == 0:
            s_out('None items. Press \'a\' or \'h\' or arrow left to go back.')

        s_out()
        s_out('Current dir: \'' + path + '\'')

        if mode == 'open':
            if type == '':
                s_out('\rSelect a file/dir and press enter. Press \'n\' to create a New dir. ' + message + ' ', end = '')
            if type == 'f':
                s_out('\rSelect a file and press enter. Press \'n\' to create a New dir. ' + message + ' ', end = '')
            if type == 'd':
                s_out('\rSelect a dir and press enter. Press \'n\' to create a New dir. ' + message + ' ', end = '')
        else:
            if type == '':
                s_out('\rSelect a file/dir and press enter. Press \'f\' to select a new file. Press \'n\' to create a New dir. ' + message + ' ', end = '')
            if type == 'f':
                s_out('\rSelect a file and press enter. Press \'f\' to select a new file. Press \'n\' to create a New dir. ' + message + ' ', end = '')
            if type == 'd':
                s_out('\rSelect a dir and press enter. Press \'f\' to select a new file. Press \'n\' to create a New dir. ' + message + ' ', end = '')

        # get user input
        ch = getch()

        if ch == '\x1b' or ch == '\x00':
            c1 = getch()
            if os.name != 'nt':
                if c1 == '[':
                    c2 = getch()
                    # up
                    if c2 == 'A':
                        cursor = cursor - 1
                    # down
                    if c2 == 'B':
                        cursor = cursor + 1
                    # right
                    if c2 == 'C':
                        if len(listdir) > 0:
                            if os.path.isdir(path + listdir[tcursor]) and tcursor >= 0:
                                try:
                                    out = browser_(path + listdir[tcursor] + '/', mode, type, filename, message, root = False, show_point_files = show_point_files)
                                    if out != '':
                                        return out
    
                                except Exception as error:
                                    if type(error) == KeyboardInterrupt:
                                        raise KeyboardInterrupt
                                    s_out(str(error))
                                    s_inp('Press enter to continue. ', getch_start_stop = False)
    
                            elif filename != '' and cursor == 0:
                                try:
                                    if type == 'f' or type == '':
                                        return s_inp('Create and select a new file: ', input = filename, mode = 'path')
                                    else:
                                        return s_inp('Create and select a new directory: ', input = filename, mode = 'path')
                                except KeyboardInterrupt:
                                    continue
                        else:
                            s_out('There are none items.')
                            s_inp('Press enter to continue. ', getch_start_stop = False)

                    # left
                    if c2 == 'D':
                        if root:
                            try:
                                out = browser_(os.path.dirname(path[:-1]), mode, type, filename, message, root = True, show_point_files = show_point_files)
                                if out != '':
                                    return out

                            except Exception as error:
                                if type(error) == KeyboardInterrupt:
                                    raise KeyboardInterrupt
                                s_out(error)
                                s_inp('Press enter to continue. ', getch_start_stop = False)

                        else:
                            return ''

            else:
                # up
                if c1 == 'H':
                    cursor = cursor - 1
                # down
                if c1 == 'P':
                    cursor = cursor + 1
                # right
                if c1 == 'M':
                    if len(listdir) > 0:
                        if os.path.isdir(path + listdir[tcursor]) and tcursor >= 0:
                            try:
                                out = browser_(path + listdir[tcursor] + '/', mode, type, filename, message, root = False, show_point_files = show_point_files)
                                if out != '':
                                    return out
    
                            except Exception as error:
                                if type(error) == KeyboardInterrupt:
                                    raise KeyboardInterrupt
                                s_out(error)
                                s_inp('Press enter to continue. ', getch_start_stop = False)
    
                        elif filename != '' and cursor == 0:
                            try:
                                if type == 'f' or type == '':
                                    return path + s_inp('Create and select a new file: ', input = filename, mode = 'path', getch_start_stop = False)
                                else:
                                    return path + s_inp('Create and select a new directory: ', input = filename, mode = 'path', getch_start_stop = False)
                            except KeyboardInterrupt:
                                continue

                    else:
                        s_out('There are none items.')
                        s_inp('Press enter to continue. ', getch_start_stop = False)

                # left
                if c1 == 'K':
                    if root:
                        try:
                            out = browser_(os.path.dirname(path[:-1]), mode, type, filename, message, root = True, show_point_files = show_point_files)
                            if out != '':
                                return out

                        except Exception as error:
                            if type(error) == KeyboardInterrupt:
                                raise KeyboardInterrupt
                            s_out(error)
                            s_inp('Press enter to continue. ', getch_start_stop = False)

                    else:
                        return ''

        if ch == 'k' or ch == 'K' or ch == 'w' or ch == 'W':
            cursor = cursor - 1
        if ch == 'j' or ch == 'J' or ch == 's' or ch == 'S':
            cursor = cursor + 1
        if ch == 'l' or ch == 'L' or ch == 'd' or ch == 'D':
            if len(listdir) > 0:
                if os.path.isdir(path + listdir[tcursor]) and tcursor >= 0:
                    try:
                        out = browser_(path + listdir[tcursor] + '/', mode, type, filename, message, root = False, show_point_files = show_point_files)
                        if out != '':
                            return out
    
                    except Exception as error:
                        if type(error) == KeyboardInterrupt:
                            raise KeyboardInterrupt
                        s_out(error)
                        s_inp('Press enter to continue. ', getch_start_stop = False)
    
                elif filename != '' and cursor == 0:
                    try:
                        if type == 'f' or type == '':
                            return path + s_inp('Create and select a new file: ', input = filename, mode = 'path', getch_start_stop = False)
                        else:
                            return path + s_inp('Create and select a new directory: ', input = filename, mode = 'path', getch_start_stop = False)
                    except KeyboardInterrupt:
                        continue

            else:
                s_out('There are none items.')
                s_inp('Press enter to continue. ', getch_start_stop = False)

        if ch == 'h' or ch == 'H' or ch == 'a' or ch == 'A':
            if root:
                try:
                    out = browser_(os.path.dirname(path[:-1]), mode, type, filename, message, root = True, show_point_files = show_point_files)
                    if out != '':
                        return out

                except Exception as error:
                    if type(error) == KeyboardInterrupt:
                        raise KeyboardInterrupt
                    s_out(error)
                    s_inp('Press enter to continue. ', getch_start_stop = False)

            else:
                return ''

        if ch == '\n':
            s_out()
            if filename != '' and tcursor == -1:
                try:
                    if type == 'f' or type == '':
                        return path + s_inp('Create and select a new file: ', input = filename, mode = 'path', getch_start_stop = False)
                    else:
                        return path + s_inp('Create and select a new directory: ', input = filename, mode = 'path', getch_start_stop = False)
                except KeyboardInterrupt:
                    continue
            elif len(listdir) > 0:
                isfile = os.path.isfile(path + listdir[tcursor])
                try:
                    if mode == 'open':
                        if type == '' or (type == 'f' and isfile) or (type == 'd' and not isfile):
                            s_inp('Press enter to open ' + ('file' if isfile else 'directory') + ' \'' + path + listdir[tcursor] + '\'. Press ctrl + c to cancel. ', getch_start_stop = False)
                            return path + listdir[tcursor]
                        else:
                            s_out('This is a ' + ('file' if isfile else 'directory') + '.')
                    else:
                        if isfile and (type == '' or type == 'f'):
                            s_inp('Press enter if you want to overwrite file \'' + path + listdir[tcursor] + '\'. Press ctrl + c to cancel. ', getch_start_stop = False)
                            return path + listdir[tcursor]
                        elif (not isfile) and (type == '' or type == 'd'):
                            s_inp('Press enter to open directory \'' + path + listdir[tcursor] + '\'. Any files in this directory can be overwritten. Press ctrl + c to cancel. ', getch_start_stop = False)
                            return path + listdir[tcursor]
                except KeyboardInterrupt:
                    continue
            
            else:
                s_out('There are none items.')
                s_inp('Press enter to continue. ', getch_start_stop = False)
            
        if ch == '\x03':
            raise KeyboardInterrupt
        if ch == '\x04':
            raise EOFError
        if ch == '.':
            show_point_files = not show_point_files
        if ch == 'f' and mode == 'create':
            try:
                return path + s_inp('Create a new file: ', input = filename, invalid_characters = ['/', '\\'], getch_start_stop = False)
            except KeyboardInterrupt:
                continue
        if ch == 'n':
            try:
                inp = s_inp('Create a new directory: ', invalid_characters = ['/', '\\'], getch_start_stop = False)
            except KeyboardInterrupt:
                continue
            os.mkdir(path + inp)

        if ch == ':':
            try:
                s_out()
                to_dir = s_inp('Go to directory   > ', getch_start_stop = False)
                if os.path.exists(to_dir):
                    if os.path.isdir(to_dir):
                        out = browser_(to_dir, mode, type, filename, message, root = True, show_point_files = show_point_files)
                        if out != '':
                            return out

                    else:
                        s_out('Can\'t find directory.')
                        s_inp('Press enter to continue. ', getch_start_stop = False)

                else:
                    s_out('Can\'t find directory.')
                    s_inp('Press enter to continue. ', getch_start_stop = False)

            except Exception as error:
                if type(error) == KeyboardInterrupt:
                    raise KeyboardInterrupt
                s_out(error)
                s_inp('Press enter to continue. ', getch_start_stop = False)

        if cursor < 0:
            if filename == '':
                cursor = len(listdir) - 1
            else:
                cursor = len(listdir)
        if cursor >= len(listdir) and filename == '':
            cursor = 0
        if cursor > len(listdir) and filename != '':
            cursor = 0

