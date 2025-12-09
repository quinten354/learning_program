# import modules
from random import randint, shuffle, choice
from time import sleep as wait, time
import os

from extern.save_input import save_input as s_inp
from extern.timeout import timeout
from extern.save_output import save_output as s_out, cls

from manage_files import get_list, ch_path, overwrite, move, delete_file, delete_all
from questions import type_ex, multiple_choise, sentence, retype, show_word
from functions import is_warned, warn, sort, ch_time, get_list_index, show_target_info, show_item_settings, select, lower, no_punctuation_marks, no_accents, show_learn_process, get_procent, get_scores
from solve import solve
from errors import ClosedTerminalError, ProcessKilledError, NotInListError, log_error

# show item information
def get_item_information(username, filename, settings):
    list = get_list(username, 'items/' + filename)
    cls()
    show_learn_process(list, settings)
    s_out()
    show_item_settings(username, filename, settings)
    s_out()
    s_inp('Press enter to continue. ')

def item_options(username, filename, settings):
    # set default settings
    default_settings = [filename, 0, 0, 0, 'w', [], [0, 0, 0, 0]]
    # [filename, time between learning, last time learned, target number, target kind, changed learning method, target measurements]

    # get items with the same filename
    item_settings = get_list(username, 'item_settings')
    items = []
    for number in range(len(item_settings)):
        if item_settings[number][0] == filename:
            items.append(item_settings[number])

    write = False

    # delete items if there are more than 1 items with the same filename
    while len(items) > 1:
        item_settings.remove(items[0])
        write = True

    # if there is no item with this filename, create one with default settings
    if len(items) == 0:
        item_settings.append(default_settings)
        items.append(default_settings)
        write = True

    # write
    if write:
        overwrite(username, item_settings, 'item_settings')

    number = item_settings.index(items[0])
    while True:
        # ask user
        cls()
        print('Filename: ' + item_settings[number][0] + '        Last time learned: ' + str(item_settings[number][2]))
        print()
        print('What do you want to change?')
        print('Now: ' + (ch_time(item_settings[number][1])[0] if item_settings[number][1] > 0 else 'off') + '   Change learn-at-time time between learning --> t')
        print('Now: ' + str(item_settings[number][3]) + str(item_settings[number][4]) + '    Change learn-at-time target --> T')
        print('Now: ' + (str(item_settings[number][5])[1:-1] if len(item_settings[number][5]) > 0 else 'off') + '    Change learn method only for this item --> m')
        print('Reset settings to default settings --> r')
        print('Load settings from last save --> l')
        print('Save and quit --> s')
        print('Quit --> q')
        choice = s_inp('   > ')

        options = ['t', 'T', 'm', 'r', 'l', 's', 'q']

        if choice not in options:
            cls()
            print('\x1b[1;49;31mThat isn\'t a option!\x1b[0m')
            wait(1.5)
            continue

        if choice == 't':
            while True:
                inp = s_inp('Type the learn-at-time time between learning in seconds. Now: ' + str(item_settings[number][1]) + '. Type 0 to set this function off.   > ')
                if inp.isdigit():
                    item_settings[number][1] = int(inp)
                    break
                else:
                    print('No number!')
                    continue

        if choice == 'T':
            inp = ''
            while inp not in ['procent', '%', 'sessions', 's', 'words', 'w']:
                inp = s_inp('Wich kind of value do you want? Choose between procent (%), sessions (s) or words (w).   > ')
            if inp == 'procent':
                inp = '%'
            if inp == 'sessions':
                inp = 's'
            if inp == 'words':
                inp = 'w'

            item_settings[number][4] = inp

            while True:
                inp = s_inp('Type the number of procent/sessions/words you want to learn when it\'s time to learn.   > ')
                if inp.isdigit():
                    item_settings[number][3] = int(inp)
                    break
                else:
                    print('\x1b[1;49;31mNo number!\x1b[0m')
                    continue

        if choice == 'm':
            number = 0
            while True:
                cls()
                s_out('Try to do the learn method under 8 questions.')
                s_out('Use the arrows to select a niveau.')
                s_out('Press \'q\' to quit.')
                s_out()
                if number == 0:
                    s_out('Niveau 0: Unknown words.')
                if number == 1:
                    s_out('Niveau 1: You have seen this words, but don\'t know them good.')
                if number == 2:
                    s_out('Niveau 2: You know this words, but not really.')
                if number == 3:
                    s_out('Niveau 3: You know this words good, it\'s sensible to repeat them.')

                s_out()

                string = '\r'

                for i in range(4):
                    string = string + str(i) + ': ' + str(item_settings[number][5].count(i)) + '    '

                string = string + '\r'

                for i in range(number + 1):
                    string = string + str(i) + ': ' + str(item_settings[number][5].count(i)) + '    '

                string = string[:-4]

                s_out(string, end = '')

                ch = getch()
                # ctrl + c
                if ch == '\x03':
                    raise KeyboardInterrupt

                # ctrl + d
                if ch == '\x04':
                    raise EOFError

                if ch == '\x1b' or ch == '\x00':
                    c1 = getch()
                    if c1 == '[' and os.name != 'nt':
                        c2 = getch()
                        # arrow up
                        if c2 == 'A' and item_settings[number][5].count(number) > 0:
                            item_settings[number][5].remove(number)
                        
                        # arrow down
                        if c2 == 'B' and item_settings[number][5].count(number) < 8:
                            item_settings[number][5].append(number)

                        # arrow left
                        if c2 == 'D':
                            number = number - 1
                            if number < 0:
                                number = 3

                        # arrow right
                        if c2 == 'C':
                            number = number + 1
                            if number > 3:
                                number = 0

                        # home
                        if c2 == 'H':
                            number = 0
    
                        # end
                        if c2 == 'F':
                            number = 3

                        # page up
                        if c2 == '5':
                            getch()
                            for aantal in range(item_settings[number][5].count(number)):
                                item_settings[number][5].remove(number)

                        # page down
                        if c2 == '6':
                            getch()
                            for aantal in range(8 - item_settings[number][5].count(number)):
                                item_settings[number][5].append(number)

                    if os.name == 'nt':
                        # arrow up
                        if c1 == 'H':
                            item_settings[number][5].remove(number)

                        # arrow down
                        if c1 == 'P':
                            item_settings[number][5].append(number)

                        # arrow left
                        if c1 == 'K':
                            number = number - 1
                            if number < 0:
                                number = 3

                        # arrow right
                        if c1 == 'M':
                            number = number + 1
                            if number > 3:
                                number = 0

                        # home
                        if c1 == 's':
                            number = 0

                        # end
                        if c1 == 't':
                            number = 3

                        # page up
                        if c1 == 'I':
                            for aantal in range(item_settings[number][5].count(number)):
                                item_settings[number][5].remove(number)

                        # page down
                        if c1 == 'Q':
                            for aantal in range(8 - item_settings[number][5].count(number)):
                                item_settings[number][5].append(number)

                if ch == 'q' or ch == 's':
                    break

                item_settings[number][5].sort()

        if choice == 'r':
            item_settings[number] = default_settings

        if choice == 'l':
            return item_options(username, filename, settings)

        if choice == 's':
            overwrite(username, item_settings, 'item_settings')
            return ''

        if choice == 'q':
            return ''

# add item
def add_list(username, settings):
    # ask name of item
    name_item = s_inp('Name your item.   > ', invalid_characters = ['/', '\\'])
    while name_item == '' or name_item in os.listdir(ch_path('~/' + username + '/items')):
        try:
            if name_item in os.listdir(ch_path('~/' + username + '/items')):
                s_out('This name already exist. Press ctrl + c to overwrite.')
            name_item = s_inp('Name your item.   > ', input = name_item)
        except KeyboardInterrupt:
            keuze = s_inp('Do you want to cancel or replace the name? (c/r)   > ')
            if keuze == 'r':
                pass
            else:
                return ''

    list_item = add_words(username, name_item, [], settings)

    if not list_item:
        change_list(username, name_item, settings)
        return ''

    if settings[23] != -1:
        list_item = sort(list_item, settings[23])
    overwrite(username, list_item, 'items/' + name_item)

def add_words(username, name_item, list_item, settings, sc_menu = True):
    undoed = []
    while True:
        cls()
        # ask user to type words
        if sc_menu:
            s_out(name_item + '        ' + str(len(list_item)) + '        Press ctrl + c to quit, u to undo or n to start up change menu.')
        else:
            s_out(name_item + '        ' + str(len(list_item)) + '        Press ctrl + c to quit or u to undo.')
        s_out()
        # show previous words
        if len(list_item) > 0:
            s_out('Previous:')
            s_out('Given:   ' + list_item[-1][0])
            s_out('Unknown: ' + list_item[-1][1])
            s_out()

        try:
            # ask to type words
            word1 = ''

            while word1 == '':
                if len(undoed) > 0:
                    if len(list_item) > 0:
                        word1 = s_inp('  Type the given word   > ', input = undoed[-1][0], enter_characters = ['\x0e', '\x15'] if sc_menu else ['\x15'])
                    else:
                        word1 = s_inp('  Type the given word   > ', input = undoed[-1][0], enter_characters = ['\x0e'] if sc_menu else [])
                else:
                    if len(list_item) > 0:
                        word1 = s_inp('  Type the given word   > ', enter_characters = ['\x0e', '\x15'] if sc_menu else ['\x15'])
                    else:
                        word1 = s_inp('  Type the given word   > ', enter_characters = ['\x0e'] if sc_menu else [])
                if type(word1) == tuple:
                    if word1[1] == '\x15':
                        undoed.append(list_item[-1].copy())
                        del list_item[len(list_item) - 1]
                        continue
                    elif word1[1] == '\x0e':
                        change_content(username, name_item, settings, list_item)
                        return None
                    else:
                        word1 = word1[0]
    
                try:
                    while word1[0] == ' ':
                        word1 = word1[1:]
                    while word1[-1] == ' ':
                        word1 = word1[:-1]
                except:
                    pass

            word2 = ''

            while word2 == '':
                if len(undoed) > 0:
                    if len(list_item) > 0:
                        word2 = s_inp('Type the unknown word   > ', input = undoed[-1][1], enter_characters = ['\x0e', '\x15'] if sc_menu else ['\x15'])
                    else:
                        word2 = s_inp('Type the unknown word   > ', input = undoed[-1][1], enter_characters = ['\x0e'] if sc_menu else [])
                else:
                    if len(list_item) > 0:
                        word2 = s_inp('Type the unknown word   > ', enter_characters = ['\x0e', '\x15'] if sc_menu else ['\x15'])
                    else:
                        word2 = s_inp('Type the unknown word   > ', enter_characters = ['\x0e'] if sc_menu else [])
                if type(word2) == tuple:
                    if word2[1] == '\x15':
                        continue
                    elif word1[1] == '\x0e':
                        change_content(username, name_item, settings, list_item)
                        return None
                    else:
                        word2 = word2[0]
    
                try:
                    while word2[0] == ' ':
                        word2 = word2[1:]
                    while word2[-1] == ' ':
                        word2 = word2[:-1]
                except IndexError:
                    pass

        except KeyboardInterrupt:
            return list_item
    
        except ClosedTerminalError:
            if settings[23] != -1:
                list_item = sort(list_item, settings[23])
            overwrite(username, list_item, 'items/' + name_item)
            raise ClosedTerminalError
        
        except ProcessKilledError:
            if settings[23] != -1:
                list_item = sort(list_item, settings[23])
            overwrite(username, list_item, 'items/' + name_item)
            raise ProcessKilledError

        if len(undoed) > 0:
            del undoed[-1]

        # add item
        list_item.append([word1, word2, 0, 0, 0, 0])

# change item
def change_list(username, filename, settings):
    hided_items = get_list(username, 'hided_items', True)
    item_settings = get_list(username, 'item_settings')
    number_item_settings = -1
    for number in range(len(item_settings)):
        if item_settings[number] == filename:
            number_item_settings = number
    error = False
    # get warnings/errors
    try:
        list_item = get_list(username, 'items/' + filename)
        warning = is_warned(list_item)
        get_scores(list_item, settings)
        del list_item
    
    except:
        log_error()
        error = True
        warning = False
        list_scores = get_list(username, 'list_items')
        for woord in list_scores:
            if woord[0] == filename:
                list_scores.remove(woord)
        overwrite(username, list_scores, 'list_items')

    # ask user
    while True:
        cls()
        # options
        options = ['n', 'h', 'q', 's']

        if error:
            options.append('p')
        else:
            options.append('c')

        # show options
        if error:
            s_out('\x1b[1;49;33mCan\'t read the content.\x1b[0m')
            s_out()
        s_out('What do you want to change?')
        s_out('Name --> n')
        if error:
            s_out('Solve problems --> p')
        else:
            s_out('Content --> c' if not warning else 'Content --> c          \x1b[1;49;33mWarning(s)\x1b[0m')
        s_out('Hide/show --> h')
        s_out('quit --> s/q')

        # ask user
        choice = s_inp('   > ')

        if choice not in options:
            cls()
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue

        # rename
        if choice == 'n':
            cls()
            # get hiding
            hiden = filename in hided_items

            # ask new name
            try:
                new_name = s_inp('What will be the new name?   > ', input = filename, invalid_characters = ['/', '\\'])
            except KeyboardInterrupt:
                continue

            cancel = False
            while new_name == '' or new_name in os.listdir(ch_path('~/' + username + '/items')):
                try:
                    if new_name in os.listdir(ch_path('~/' + username + '/items')):
                        s_out('This name already exist. Choose another name.')
                    new_name = s_inp('What will be the new name?   > ', input = new_name)
                except KeyboardInterrupt:
                    s_out()
                    keuze = s_inp('Do you want to cancel or overwrite? (c/o)   > ')
                    if keuze == 'o':
                        break
                    else:
                        cancel = True
                        break
            
            if cancel:
                continue

            # rename
            move(username, 'items/' + filename, 'items/' + new_name)
            
            # if the item is hided, ask if that now also must be
            if hiden:
                cls()
                if s_inp('This item was hidden. Do you want the list is now also hidden?   > ') == 'yes':
                    hided_items.append(new_name)
                    overwrite(username, hided_items, 'hided_items')

            if number_item_settings != -1:
                item_settings[number_item_settings][0] = new_name

            filename = new_name

        # change content
        if choice == 'c':
            change_content(username, filename, settings)

        # solve problems
        if choice == 'p':
            solve(ch_path('~/' + username + '/items/' + filename))

        # show/hide
        if choice == 'h':
            if filename in hided_items:
                hided_items.remove(filename)
                s_out('This item will be showed in the menu.')
            else:
                hided_items.append(filename)
                s_out('This item willn\'t be showed in the menu.')
            overwrite(username, hided_items, 'hided_items')
            wait(1.5)

        # quit
        if choice == 's' or choice == 'q':
            if warning:
                lijst_waarschuwingen = get_list(username, 'warned_items', True)
                if filename not in lijst_waarschuwingen:
                    lijst_waarschuwingen.append(bestandsusername)
                overwrite(username, lijst_waarschuwingen, 'warned_items')

            return ''

# change content
def change_content(username, filename, settings, list_item = None):
    if not list_item:
        list_item = get_list(username, 'items/' + filename)
    start_list_item = list_item.copy()
    warning = is_warned(get_list(username, 'items/' + filename))
    while True:
        options = ['w', 'sw', 'd', 't', 's', 'q']
        if settings[23] == -1:
            options.append('ls')

        cls()
        # show options
        s_out('What do you want to do?')
        s_out('Words --> w' if not warning else 'Words --> w          \x1b[1;49;33mWarning\x1b[0m')
        s_out('Sort words --> sw' if settings[23] == -1 else '\x1b[2;49;2mSort words\x1b[0m --> Turn off auto sort in the settings.')
        s_out('Delete user data in this item --> d')
        s_out('Turn around words --> t')
        s_out('Save and quit --> s')
        s_out('Quit (don\'t save) --> q')
        # ask user
        choice_1 = s_inp('   > ')

        if choice_1 not in options:
            cls()
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue

        # words
        if choice_1 == 'w':
            list_item = change_words(username, filename, list_item.copy(), settings)

        # leervooruitgang terugzetten
        if choice_1 == 'd':
            # om bevestiging vragen
            permision = s_inp('Are you sure? It can\'t be undone. (yes/no)   > ')
            options = ['yes', 'no']
            while permision not in options:
                permision = s_inp('Are you sure? It can\'t be undone. (yes/no)   > ')
                
            if permision == 'yes':
                for i in range(len(list_item)):
                    list_item[i][2] , list_item[i][3] , list_item[i][4] , list_item[i][5] = 0, 0, 0, 0
                cls()
                s_out('The user process is deleted.')
                wait(1.2)

        # turn around
        if choice_1 == 't':
            for i in range(len(list_item)):
                list_item[i][0], list_item[i][1], list_item[i][2], list_item[i][3], list_item[i][4], list_item[i][5] = list_item[i][1], list_item[i][0], list_item[i][2], list_item[i][3], list_item[i][4], list_item[i][5]
            cls()
            s_out('The words are turned around.')
            wait(1.5)

        # sort
        if choice_1 == 'sw':
            if len(list_item) > 0:
                s_out('How do you want to sort?')
                s_out('0 --> given word')
                s_out('1 --> unknown word')
                s_out('2 --> niveau')
                s_out('3 --> times in a row good')
                s_out('4 --> number of mistakes')
                s_out('5 --> times had')
                number = s_inp('   > ')
                if number.isdigit():
                    if -1 < int(number) < 6:
                        list_item = sort(list_item, int(number))
                    else:
                        s_out('That can\'t. Not 0-5.')
                        wait(1.5)
                else:
                    s_out('That can\'t. Not a number.')
                    wait(1.5)
            else:
                s_out('That can\'t. No words.')
                wait(1.5)

        # save and quit
        if choice_1 == 's':
            if settings[23] != -1:
                list_item = sort(list_item, settings[23])
            overwrite(username, list_item, 'items/' + filename)
            list_scores = get_list(username, 'list_items')
            for i in range(len(list_scores)):
                if list_scores[i][0] == filename:
                    list_scores[i][1] = len(list_item)
                    list_scores[i][2] = get_procent(*get_scores(list_item, settings))
            overwrite(username, list_scores, 'list_items')

            if is_warned(list_item):
                lijst_waarschuwingen = get_list(username, 'warned_items', True)
                if filename not in lijst_waarschuwingen:
                    lijst_waarschuwingen.append(filename)
                overwrite(username, lijst_waarschuwingen, 'warned_items')

            return list_item

        # quit
        if choice_1 == 'q':
            return start_list_item

# change words
def change_words(username, filename, list_item, settings):
    view_userinfo = False
    txt_search = ''
    show_agreements = False
    while True:
        cls()
        num_found = 0
        s_out('Get warnings...')
        try:
            warned_wordnumber = timeout(warn, 1, list_item)
        except TimeoutError:
            warned_wordnumber = []
            s_out('Timeout...')
            wait(1.5)

        cls()
        # show words
        for wordnumber in range(len(list_item)):
            # filter search
            if show_agreements:
                if settings[21]:
                    if lower(no_punctuation_marks(no_accents(txt_search))) in (str(wordnumber + 1) + ': '):
                        show = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in lower(str(list_item[wordnumber][0]) + ': '):
                        show = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in lower(str(list_item[wordnumber][1]) + ': '):
                        show = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in (str(list_item[wordnumber][2]) + ': '):
                        show = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in (str(list_item[wordnumber][3]) + ': '):
                        show = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in (str(list_item[wordnumber][4]) + ': '):
                        show = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in (str(list_item[wordnumber][5]) + ': '):
                        show = True
                    else:
                        show = False

                else:
                    if txt_search in (str(wordnumber + 1) + ': '):
                        show = True
                    elif txt_search in (str(list_item[wordnumber][0]) + ': '):
                        show = True
                    elif txt_search in (str(list_item[wordnumber][1]) + ': '):
                        show = True
                    elif txt_search in (str(list_item[wordnumber][2]) + ': '):
                        show = True
                    elif txt_search in (str(list_item[wordnumber][3]) + ': '):
                        show = True
                    elif txt_search in (str(list_item[wordnumber][4]) + ': '):
                        show = True
                    elif txt_search in (str(list_item[wordnumber][5]) + ': '):
                        show = True
                    else:
                        show = False

            else:
                show = True

            if show:
                # show warning
                if wordnumber in warned_wordnumber: s_out('\x1b[1;49;33mWarning\x1b[0m')
                # show known word
                s_out(select(str(wordnumber + 1) + ': ' + (' ' * (5 - len(str(wordnumber + 1) + ': '))) + '      Known word: ' + str(list_item[wordnumber][0]), txt_search))
                # show unknown word
                s_out(select('         Unknown word: ' + str(list_item[wordnumber][1]), txt_search))
                if view_userinfo:
                    # show niveau
                    s_out(select('                 Niveau: ' + str(list_item[wordnumber][2]), txt_search))
                    # show times in a row good
                    s_out(select('    Times in a row good: ' + str(list_item[wordnumber][3]), txt_search))
                    # show number of mistakes
                    s_out(select('               Mistakes: ' + str(list_item[wordnumber][4]), txt_search))
                    # show times had
                    s_out(select('              Times had: ' + str(list_item[wordnumber][5]), txt_search))

                s_out()
                num_found = num_found + 1

        if len(txt_search) > 0 and show_agreements:
            s_out(str(num_found) + ' agreements with your search \'' + txt_search + '\'.')
            s_out()

        # ask user
        s_out('What do you want to do?')
        s_out('Quit --> q')
        s_out('Save --> s')
        s_out('Change word --> number')
        s_out('Add word --> a')
        s_out('Add words --> A')
        s_out('View/hide user info --> u')
        s_out('Search with agreements --> ?')
        s_out('Search --> /')
        choice_2 = s_inp('   > ')

        if len(choice_2) == 0:
            cls()
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue

        options = ['s', 'q', 'a', 'A', 'u', '?', '/']
        if (choice_2 not in options) and (not choice_2.isdigit()) and choice_2[0] != '/' and choice_2[0] != '?':
            cls()
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue
        
        if choice_2.isdigit():
            # check the word exist
            if 0 < int(choice_2) < (len(list_item) + 1):
                options = ['1', '2', 'd', 'b']
                # ask user
                s_out('What do you want to do?')
                s_out('Known word:   ' + list_item[int(choice_2) - 1][0] + ' --> 1')
                s_out('Unknown word: ' + list_item[int(choice_2) - 1][1] + ' --> 2')
                s_out('Delete --> d')
                s_out('Back --> b')
                choice_3 = s_inp('   > ')

                if choice_3 not in options:
                    cls()
                    s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                    wait(1.5)
                    continue
                    
                if choice_3 == '1':
                    list_item[int(choice_2) - 1][0], list_item[int(choice_2) - 1][2], list_item[int(choice_2) - 1][3], list_item[int(choice_2) - 1][4], list_item[int(choice_2) - 1][5] = s_inp('Change the given word.   > ', input = list_item[int(choice_2) - 1][0]), 0, 0, 0, 0
                if choice_3 == '2':
                    list_item[int(choice_2) - 1][1], list_item[int(choice_2) - 1][2], list_item[int(choice_2) - 1][3], list_item[int(choice_2) - 1][4], list_item[int(choice_2) - 1][5] = s_inp('Change the unknown word.   > ', input = list_item[int(choice_2) - 1][1]), 0, 0, 0, 0
                if choice_3 == 'd':
                    del list_item[int(choice_2) - 1]
                    
            else:
                s_out('\x1b[1;49;31mThis word dosn\'t exist...\x1b[0m')
                wait(1.5)

        # add word
        if choice_2 == 'a':
            list_item.append([s_inp('What\'s the given word?     > '), s_inp('What\'s the unknown word?   > '), 0, 0, 0, 0])

        # add words
        if choice_2 == 'A':
            list_item = add_words(username, name, list_item.copy, settings, False)
            
        if choice_2 == 'q':
            return list_item

        if choice_2 == 's':
            overwrite(username, list_item, 'items/' + filename)
        
        if choice_2 == 'u':
            view_userinfo = True if not view_userinfo else False
        
        if choice_2[0] == '/':
            if choice_2 == '/':
                txt_search = s_inp('Search: ')
            else:
                txt_search = choice_2[1:]

            show_agreements = False

        if choice_2[0] == '?':
            if choice_2 == '?':
                txt_search = s_inp('Search: ')
            else:
                txt_search = choice_2[1:]

            show_agreements = True

# split item
def split_list(username, filename, settings):
    splitted_items = []
    number_items = ''
    # get list
    list_item = get_list(username, 'items/' + filename)
    cls()
    # show options
    s_out('How do you want to split the list?')
    s_out('Fair share --> f')
    s_out('Learned/not learned (2) --> l')
    s_out('Not learned (1) --> n')
    s_out('Cancel --> c')

    # ask user
    choice = ''
    options = ['d', 'g', 'n', 'a']
    while choice not in options:
        if choice != '':
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0')
        choice = s_inp('   > ')

    # cancel
    if choice == 'c':
        return ''

    # fair share
    if choice == 'd':
        while not number_items.isdigit():
            number_items = s_inp('In how many parts do you want to split (number)   > ')

        number_items = int(number_items)

        for i in range(number_items):
            splitted_items.append([])

    # learned/not learned
    if choice == 'l':
        for i in range(2):
            splitted_items.append([])

    # not learned
    if choice == 'n':
        splitted_items.append([])

    # split
    for listnumber in range(len(list_item)):
        item = list_item[listnumber]
        if choice == 'd':
            splitted_items[listnumber % number_items].append(item)
        if choice == 'g':
            splitted_items[0 if item[2] >= 3 else 1].append(item)
        if choice == 'n':
            if item[2] < 3:
                splitted_items[0].append(item)

    # write to disk
    cls()
    for number in range(len(splitted_items)):
        # ask to itemname
        itemname = ''
        while itemname == '' or itemname in os.listdir(ch_path('~/' + username + '/items')):
            if itemname in os.listdir(ch_path('~/' + username + '/items')):
                s_out('\x1b[1;49;31mThis name already exist.\033[0m')

            if choice == 'd':
                if str(number)[-1] == '1':
                    a = 'st'
                elif str(number)[-1] == '2':
                    a = 'nd'
                else:
                    a = 'rd'
                itemname = s_inp('Name your ' + str(number) + a + ' item   > ', invalid_characters = ['/', '\\'])
            if choice == 'g' and number == 0:
                itemname = s_inp('Name your item with known words   > ', invalid_characters = ['/', '\\'])
            if choice == 'g' and number == 1:
                itemname = s_inp('Name your item with unknown words   > ', invalid_characters = ['/', '\\'])
            if choice == 'n':
                itemname = s_inp('Name your item with unknown words   > ', invalid_characters = ['/', '\\'])

        # create file
        create_file(username, 'items/' + itemname)
        # write
        if settings[23] != -1:
            data = sort(splitted_items[number], settings[23])
        else:
            data = splitted_items[number].copy()
        overwrite(username, data, 'items/' + itemname)

# trash
def show_trash(username):
    while True:
        # get items in trash
        items_trash = os.listdir(ch_path('~/' + username + '/trash/'))
        # clear screen
        cls()
        # show items
        for list in range(len(items_trash)):
            s_out(str(list + 1) + ': ' + items_trash[list])
        # add newline
        if len(items_trash) > 0:
            s_out()

        # show options
        s_out('Delete --> d')
        s_out('Restore --> r')
        s_out('Delete all --> a')
        s_out('Back --> b/q')
        choice = s_inp('   > ')
        
        options = ['d', 'r', 'a', 'b', 'q']
        if choice not in options:
            cls()
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue

        # delete item
        if choice == 'd':
            if len(items_trash) != 0:
                # ask number
                nummer = s_inp('Type the number you want to delete.   > ')
                # check number is a number
                if nummer.isdigit():
                    # check item exist
                    if 0 < int(nummer) < (len(items_trash) + 1):
                        delete_file(username, 'trash/' + items_trash[int(nummer) - 1])
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. This item doesn\'t exist.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. Is not a number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to delete.\x1b[0m')
                wait(1.5)

        # restore item
        if choice == 'r':
            if len(items_trash) != 0:
                # ask number
                nummer = s_inp('Type the number you want to restore.   > ')
                # check number is a number
                if nummer.isdigit():
                    # check item exist
                    if 0 < int(nummer) < (len(items_trash) + 1):
                        # check item exist out of trash
                        if items_trash[int(nummer) - 1] not in os.listdir(ch_path('~/' + username + '/items')):
                            move(username, 'trash/' + items_trash[int(nummer) - 1], 'items/')
                        else:
                            s_out('\x1b[1;49;31mThat can\'t. This item exist out of the trash.\x1b[0m')
                            wait(1.5)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. This item doesn\'t exist.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. Is not a number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to restore.\x1b[0m')
                wait(1.5)

        # delete all
        if choice == 'a':
            # ask permision
            if s_inp('Are you sure to delete all files in the trash? It can\'t be undone. (y/n)   > ') == 'y':
                delete_all(username, 'trash/')

        # back
        if choice == 'b' or choice == 'q':
            return ''

