# import modules
import os
import shutil
import datetime
from time import sleep as wait, time

from extern.save_input import save_input as s_inp
from extern.getch import getch
from extern.save_output import save_output as s_out, cls

from manage_files import get_list, overwrite, ch_path, delete_file, create_file, create_list, move, copy
from review import review, proceed_review, show_saved_reviewsessions
from manage_items import change_list, add_list, item_options, split_list, get_item_information, show_trash
from go_through import go_through
from learn import learn, review_and_learn
from functions import is_warned, ch_size, ch_time, get_scores, get_procent, synchronize, select, lower, no_punctuation_marks, no_accents
from errors import WordIndexError, log_error
from file_browser import browser

# set functions
# learn menu
def learn_menu(username):
    # get settings
    settings = get_list(username, 'settings')
    # synchronize when the user it wants
    if settings[18]:
        s_out('Synchronizing.')
        synchronize(username, settings)
    # set variables
    show_all = False
    txt_search = ''
    show_agreements = False
    errors = []

    while True:
        # clear screen
        cls()
        # get the names of all files in items
        list_names = os.listdir(ch_path('~/' + username + '/items'))
        number_items = len(list_names)
        try:
            # get the scores
            list_scores = get_list(username, 'list_items')
            # get the list with the warned items
            warned_items = get_list(username, 'warned_items', True)
        except:
            log_error()
            list_scores = []
            warned_items = []
        # get the list with the hided items
        hided_items = get_list(username, 'hided_items', True)
        # get the list with the timed items
        item_settings = get_list(username, 'item_settings')
        # get the number of columns
        columns = os.get_terminal_size().columns

        # width_screen is the number of columns for the name of the item that will be showed
        width_screen = columns

        # item number
        width_screen = width_screen - 6

        # last modified
        if settings[24][0]:
            width_screen = width_screen - 22
        
        # size
        if settings[24][1]:
            width_screen = width_screen - 6

        # number of words
        if settings[24][2]:
            width_screen = width_screen - 5
        
        # availability
        if settings[24][3]:
            width_screen = width_screen - 4

        # score
        if settings[24][4]:
            width_screen = width_screen - 18

        # item settings
        if settings[24][5]:
            width_screen = width_screen - 10

        # delete item settings that are unused
        save_is = False
        for item_setting in item_settings:
            if item_setting[0] not in list_names:
                item_settings.remove(item_setting)
                save_is = True

        if save_is:
            overwrite(username, item_settings, 'item_settings')

        # if there are items in hided_items that don't exist, remove
        write_hidden = False
        for hided_item in hided_items:
            if hided_item not in list_names:
                hided_items.remove(hided_item)
                write_hidden = True

        if write_hidden:
            overwrite(username, hided_items, 'hided_items')

        # write_scores is False, if it is True, it will write the updated scores to disk
        write_scores = False
        # search to unused scores and remove them
        for i in list_scores:
            if i[0] not in list_names:
                # delete score and set write_scores to write to disk
                list_scores.remove(i)
                write_scores = True

        # remove hided items out list_names
        if not show_all:
            for hided_item in hided_items:
                if hided_item in list_names:
                    list_names.remove(hided_item)

        # show legend
        if settings[26] and len(list_names) > 0:
            s_out('Num   Name' + (' ' * (width_screen - 4)), end = '')
            if settings[24][0]:
                s_out('Last modified         ', end = '')
            if settings[24][1]:
                s_out('Size  ', end = '')
            if settings[24][2]:
                s_out('\x1b[DWords ', end = '')
            if settings[24][3]:
                s_out('W/E ', end = '')
            if settings[24][4]:
                s_out('Info      ', end = '')
            if settings[24][5]:
                s_out('Learn process     ', end = '')
            s_out()

        # sort names
        if settings[15] == 1: list_names.sort()

        count = 0
        write_warnings = False
        for i in range(len(list_names)):
            # set variables
            number_words = ''
            score = ''
            show_item = False
            error = False

            # get the scores
            for j in list_scores:
                if j[0] == list_names[i]:
                    number_words = j[1]
                    score = j[2]

            # if there no score, calculate it
            if number_words == '' or score == '':
                try:
                    item_list = get_list(username, 'items/' + list_names[i])
                except (UnicodeDecodeError, ValueError):
                    log_error()
                    error = True
                    errors.append(i)
                    number_words = '-'
                    score = '-'

                else:
                    number_words = len(item_list)

                    # calculate score
                    try:
                        score = get_procent(*get_scores(item_list, settings))
                        list_scores.append([list_names[i], number_words, score])
                        if is_warned(item_list):
                            if list_names[i] not in warned_items:
                                warned_items.append(list_names[i])
                                write_warnings = True
                                
                    except WordIndexError:
                        score = '-'
                        error = True
                        errors.append(i)

                    # set write_scores to write to disk
                    write_scores = True

            if show_agreements:
                # low sensitivity to search
                if settings[21]:
                    if lower(no_punctuation_marks(no_accents(txt_search))) in (str(i + 1) + ': '):
                        show_item = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in lower(no_punctuation_marks(no_accents(list_names[i]))):
                        show_item = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in str(number_words):
                        show_item = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in score:
                        show_item = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in no_punctuation_marks(str(datetime.datetime.fromtimestamp(os.path.getmtime(ch_path('~/' + username + '/items/' + list_names[i]))))):
                        show_item = True
                    elif lower(no_punctuation_marks(no_accents(txt_search))) in lower(no_punctuation_marks(ch_size(os.path.getsize(ch_path('~/' + username + '/items/' + list_names[i]))))):
                        show_item = True

                # high sensitivity to search
                else:
                    if txt_search in (str(i + 1) + ': '):
                        show_item = True
                    elif txt_search in list_names[i]:
                        show_item = True
                    elif txt_search in str(number_words):
                        show_item = True
                    elif txt_search in score:
                        show_item = True
                    elif txt_search in str(datetime.datetime.fromtimestamp(os.path.getmtime(ch_path('~/' + username + '/items/' + list_names[i])))):
                        show_item = True
                    elif txt_search in ch_size(os.path.getsize(ch_path('~/' + username + '/items/' + list_names[i]))):
                        show_item = True

            else:
                show_item = True

            if show_item:
                # show item number
                s_out(select(str(i + 1) + ': ', txt_search) + (' ' * (4 - len(str(i + 1)))), end = '')

                # show item name
                max_length = width_screen - 6
                name_item = list_names[i]
                while len(name_item) >= max_length and max_length > 10:
                    show_name_item = name_item[:max_length] + '      \x1b[1;49;37m|\x1b[0m\n  \x1b[1;49;37m\\\x1b[0m   '
                    name_item = name_item[max_length:]
                    s_out(select(show_name_item, txt_search), end = '')

                s_out(select(name_item, txt_search), end = '')

                # complete line with spaces or lines
                s_out('\x1b[2;49;2m' + ((' ' if count % 6 != 2 else '-') * (width_screen - len(name_item))) + '\x1b[0m', end = '')

                # show last change
                if settings[24][0]:
                    s_out(select(str(datetime.datetime.fromtimestamp(os.path.getmtime(ch_path('~/' + username + '/items/' + list_names[i])))).split('.')[0], txt_search) + '   ', end = '')

                # show size
                if settings[24][1]:
                    s_out(select(ch_size(os.path.getsize(ch_path('~/' + username + '/items/' + list_names[i]))), txt_search).replace('K', '\x1b[1;49;33mK\x1b[0m').replace('M', '\x1b[1;49;33mM\x1b[0m').replace('G', '\x1b[1;49;33mG\x1b[0m').replace('T', '\x1b[1;49;33mT\x1b[0m') + ' ', end = '')

                # show number of words
                if settings[24][2]:
                    s_out(select(str(number_words), txt_search) + ((' ' * (5 - len(str(number_words)))) if len(str(number_words)) < 5 else ' '), end = '')

                # show state
                if settings[24][3]:
                    spaces = 4
                    if error:
                        s_out('\x1b[1;49;31m' + select('E', txt_search) + '\x1b[0m', end = '')
                        spaces = spaces - 1
                    if list_names[i] in hided_items:
                        s_out('\x1b[1;49;33m' + select('H', txt_search) + '\x1b[0m', end = '')
                        spaces = spaces - 1
                    if list_names[i] in warned_items:
                        s_out('\x1b[1;49;33m' + select('W', txt_search) + '\x1b[0m', end = '')
                        spaces = spaces - 1
                    for item_setting in item_settings:
                        try:
                            if item_setting[0] == list_names[i] and item_setting[1] != 0:
                                if (item_setting[1] + item_setting[2]) < time():
                                    s_out('\x1b[1;49;33m' + select('T', txt_search) + '\x1b[0m', end = '')
                                else:
                                    s_out('\x1b[1;49;37m' + select('t', txt_search) + '\x1b[0m', end = '')
                                spaces = spaces - 1

                        except IndexError:
                            s_out('\x1b[1;49;31m' + select('T', txt_search) + '\x1b[0m', end = '')
                            spaces = spaces - 1

                    if spaces == 4:
                        s_out('\x1b[1;49;37m' + select('G', txt_search) + '\x1b[0m', end = '')
                        spaces = spaces - 1

                    s_out(' ' * spaces, end = '')

                # show item settings
                if settings[24][5]:
                    try:
                        count_is = 0
                        for item_setting in item_settings:
                            if item_setting[0] == list_names[i] and item_setting[1] != 0:
                                curtime = time()
                                if (item_setting[1] - (curtime - item_setting[2])) > 0:
                                    s_out(select(ch_time(item_setting[1] - (curtime - item_setting[2]))[0], txt_search), end = '')
                                    s_out(' ' * (6 - len(ch_time(curtime - item_setting[2])[0])), end = '')
                                else:
                                    s_out(select('\x1b[1;49;33mNow\x1b[0m   ', txt_search), end = '')

                                s_out(select(str(item_setting[3]) + str(item_setting[4]), txt_search), end = '')
                                s_out(' ' * (4 - len(str(item_setting[3]) + str(item_setting[4]))), end = '')
                                count_is = count_is + 1
                                break

                        if count_is == 0:
                            s_out('\x1b[1;49;36m' + select('None info', txt_search) + '\x1b[0m ', end = '')

                    except IndexError:
                        log_error()
                        s_out('\x1b[1;49;31m' + select('ERROR!', txt_search) + '   \x1b[0m ', end = '')
                        

                # show score
                if settings[24][4]:
                    s_out(select(score, txt_search))

                count = count + 1

        # overwrite if it needed
        if write_scores:
            overwrite(username, list_scores, 'list_items')
        if write_warnings:
            overwrite(username, warned_items, 'warned_items')

        # show extra info
        if count > 0:
            s_out('_' * columns)
            s_out()
            s_out((str(count) + ' agreement' + ('s' if count > 1 else '') + ' with your search \'' + str(txt_search) + '\'    ' if show_agreements else '') + str(len(list_names)) + (' showed    ' if not show_agreements else ' showed without your search    ') + str(number_items) + ' available')
            s_out()
        
        elif show_agreements:
            s_out('There are none agreements with your search \'' + str(txt_search) + '\'.')
            s_out()

        # show options
        s_out('What do you want to do?')
        s_out('Quit --> q')
        s_out('Synchronize --> y')
        s_out('Settings --> s')
        s_out('Add --> a')
        s_out('Delete --> d')
        s_out('Change --> c')
        s_out('Learn --> l')
        s_out('Review --> r')
        s_out('Go through --> t')
        s_out('Advenched functions --> f')
        s_out('Item options --> o')
        s_out('Show hided items: ' + ('yes' if show_all else 'no') + ' --> h')
        s_out('Search and show agreements --> ?')
        s_out('Search --> /')

        # ask input
        try:
            choice = s_inp('   > ')
        except KeyboardInterrupt:
            cls()
            try:
                if s_inp('Do you want to go back? (yes/no)   > ') == 'yes':
                    return ''
            except KeyboardInterrupt:
                return ''

            continue

        if choice == '':
            wait(0.1)
            continue

        # if the input isn't a option, ask again
        options = ['q', 'y', 's', 'a', 'd', 'c', 'l', 'r', 't', 'f', 'o', 'h', '/', '?']
        if choice not in options and choice[0] != '/' and choice[0] != '?':
            cls()
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue

        # back to home
        if choice == 'q':
            return ''

        # synchronize
        if choice == 'y':
            s_out('Synchronizing.')
            try:
                synchronize(username, settings)
            except KeyboardInterrupt:
                continue

        # change settings
        if choice == 's':
            ch_settings(username)
            settings = get_list(username, 'settings')

        # add item
        if choice == 'a':
            try:
                add_list(username, settings)
            except KeyboardInterrupt:
                continue

        # delete item
        if choice == 'd':
            # check number of items
            if len(list_names) != 0:
                # ask the number of the item
                try:
                    number = s_inp('Type the number you want to delete.   > ')
                except KeyboardInterrupt:
                    continue

                # check the input is a number
                if number.isdigit():
                    # check the item exist
                    if 0 < int(number) < (len(list_names) + 1):
                        try:
                            # move to trash
                            move(username, 'items/' + list_names[int(number) - 1], 'trash/')
                        except:
                            log_error()
                            cls()
                            s_out('Can\'t move to trash.')
                            # check the item already exist in trash
                            if list_names[int(number) - 1] in os.listdir(ch_path('~/' + username + '/trash/')):
                                # ask
                                if s_inp('\'' + list_names[int(number) - 1] + '\' already exist in the trash. Do you want to replace it? (yes/no)   > ') == 'yes':
                                    try:
                                        # delete old item out trash
                                        delete_file(username, 'trash/' + list_names[int(number) - 1])
                                        # move item to trash
                                        move(username, 'items/' + list_names[int(number) - 1], 'trash/')
                                    except:
                                        log_error()
                                        s_out()
                                        s_out('Can\'t replace.')
                                        s_inp('Press enter to continue. ')

                            else:
                                s_inp('Press enter to continue. ')
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to delete.\x1b[0m')
                wait(1.5)

        # change item
        if choice == 'c':
            # check number of items
            if len(list_names) != 0:
                # ask the number of the item
                try:
                    number = s_inp('Type the number you want to change.   > ')
                except KeyboardInterrupt:
                    continue

                # check the input is a number
                if number.isdigit():
                    # check the item exist
                    if 0 < int(number) <= len(list_names):
                        try:
                            change_list(username, list_names[int(number) - 1], settings)
                        except KeyboardInterrupt:
                            cls()
                            s_out('Back to home.')
                            wait(1.5)
                            continue

                    else:
                        s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to delete.\x1b[0m')
                wait(1.5)

        # learn item
        if choice == 'l':
            # check number of items
            if len(list_names) != 0:
                # ask the number of the item
                try:
                    number = s_inp('Type the number you want to learn.   > ')
                except KeyboardInterrupt:
                    continue

                # check the input is a number
                if number.isdigit():
                    # check the item exist
                    if 0 < int(number) <= len(list_names):
                        if (int(number) - 1) not in errors:
                            try:
                                learn(username, list_names[int(number) - 1], settings)
                            except KeyboardInterrupt:
                                cls()
                                s_out('Back to home.')
                                wait(1.5)
                                continue

                        else:
                            s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                            wait(1.5)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to learn.\x1b[0m')
                wait(1.5)

        # review item(s)
        if choice == 'r' or choice == 't':
            # check number of items
            if len(list_names) != 0:
                list_selected_words = []
                quit = False
                while True:
                    try:
                        number = s_inp('Type the number of a item to add, c to cancel or d if you\'re done.   > ')
                    except KeyboardInterrupt:
                        quit = True
                        break

                    # done and review
                    if number == 'd':
                        break

                    # quit
                    if number == 'c':
                        quit = True
                        break

                    # check the input is a number
                    elif number.isdigit():
                        # check the item exist
                        if 0 < int(number) <= (len(list_names)):
                            if (int(number) - 1) not in errors:
                                for word in get_list(username, 'items/' + list_names[int(number) - 1]):
                                    list_selected_words.append(word)
                            else:
                                s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                        else:
                            s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')

                    elif '.' in number:
                        numbers = number.split('.')
                        # check the numbers are numbers
                        if numbers[0].isdigit() and numbers[1].isdigit():
                            for number in range(int(numbers[0]), int(numbers[1]) + 1):
                                if 0 < int(number) <= len(list_names):
                                    if (int(number) - 1) not in errors:
                                        for word in get_list(username, 'items/' + list_names[number - 1]):
                                            list_selected_words.append(word)

                                    else:
                                        s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                                else:
                                    s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                        else:
                            s_out('\x1b[1;49;31mThat can\'t. None numbers.\x1b[0m')
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. None number, c or d.\x1b[0m')

                if quit:
                    continue

                # check the user selected words
                if len(list_selected_words) > 0:
                    for i in range(len(list_selected_words)):
                        list_selected_words[i][2], list_selected_words[i][3], list_selected_words[i][4], list_selected_words[i][5] = 0, 0, 0, 0
                    try:
                        if choice == 'r':
                            review(list_selected_words, username, settings)
                        if choice == 't':
                            go_through(list_selected_words, username, settings)

                    except KeyboardInterrupt:
                        cls()
                        s_out('Back to home.')
                        wait(1.5)
                        continue

                else:
                    s_out('\x1b[1;49;31mYou haven\'t selected words.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to select.\x1b[0m')
                wait(1.5)

        if choice == 'f':
            # geanvanceerde functies
            try:
                advenched(list_names, username, settings, errors)
            except KeyboardInterrupt:
                cls()
                s_out('Back to home.')
                wait(1.5)
                continue

        if choice == 'o':
            # check number of items
            if len(list_names) != 0:
                # ask the number of the item
                try:
                    number = s_inp('Type the number you want to change item options.   > ')
                except KeyboardInterrupt:
                    continue

                # check the input is a number
                if number.isdigit():
                    # check the item exist
                    if 0 < int(number) <= len(list_names):
                        try:
                            item_options(username, list_names[int(number) - 1], settings)
                        except KeyboardInterrupt:
                            cls()
                            s_out('Back to home.')
                            wait(1.5)
                            continue

                    else:
                        s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to change item options.\x1b[0m')
                wait(1.5)

        if choice == 'h':
            show_all = not show_all

        if choice[0] == '/':
            # zoeken
            if choice == '/':
                try:
                    txt_search = s_inp('Search   > ')
                except KeyboardInterrupt:
                    continue

            else:
                txt_search = choice[1:]

            show_agreements = False

        if choice[0] == '?':
            # zoeken
            if choice == '?':
                try:
                    txt_search = s_inp('Search   > ')
                except KeyboardInterrupt:
                    continue

            else:
                txt_search = choice[1:]

            show_agreements = True

# advenched functions
def advenched(list_names, username, settings, errors):
    # set options
    options = ['r', 'sr', 'cr', 'i', 'h', 'c', 's', 'E', 'I', 't', 'b', 'q']

    # show options
    s_out('Review and save correct answered words as learned --> r')
    s_out('View saved reviewsessions --> sr')
    s_out('Continue reviewing a saved reviewsession --> cr')
    s_out('Show item information --> i')
    s_out('Hide/show items --> h')
    s_out('Combine items --> c')
    s_out('Split item --> s')
    s_out('Export item --> E')
    s_out('Import item --> I')
    s_out('Trash --> t')
    s_out('Back --> b/q')
    
    # ask user
    choice = ''
    while choice not in options:
        if choice != '':
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
        try:
            choice = s_inp('   > ')
        except KeyboardInterrupt:
            return ''

    if choice == 'i':
        # check number of items
        if len(list_names) != 0:
            # ask the number of the item
            number = s_inp('Type the number to see the learn process.   > ')
            # check the input is a number
            if number.isdigit():
                # check the item exist
                if 0 < int(number) <= len(list_names):
                    if (int(number) - 1) not in errors:
                        get_item_information(username, list_names[int(number) - 1], settings)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                wait(1.5)
        else:
            s_out('\x1b[1;49;31mThat can\'t. There is nothing to learn.\x1b[0m')
            wait(1.5)

    # trash
    if choice == 't':
        show_trash(username)

    # show saved reviewsessions
    if choice == 'sr':
        show_saved_reviewsessions(username)

    # review and save correct answered words as learned
    if choice == 'r':
        # check number of items
        if len(list_names) != 0:
            # ask the number of the item
            number = s_inp('Type a number to review.   > ')
            # check the input is a number
            if number.isdigit():
                # check the item exist
                if 0 < int(number) < (len(list_names) + 1):
                    if (int(number) - 1) not in errors:
                        review_and_learn(username, list_names[int(number) - 1], settings)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                wait(1.5)
        else:
            s_out('\x1b[1;49;31mThat can\'t. There is nothing to learn.\x1b[0m')
            wait(1.5)

    # continue review
    if choice == 'cr':
        proceed_review(username, settings)

    # hide/show items
    if choice == 'h':
        # get hided items
        hided_items = get_list(username, 'hided_items', True)
        while True:
            # show options
            cls()
            s_out('Hide item(s) --> h')
            s_out('Unhide item(s) --> u')
            s_out('Quit (save) --> s')
            s_out('Quit (not save) --> q')
            choice = s_inp('What do you want to do?   > ')

            # check user input
            options = ['h', 'u', 's', 'q']
            if choice not in options:
                cls()
                s_out('\x1b[1;49;31mThat isn\'t a option!\x1b[0m')
                wait(1.5)
                continue

            # hide item(s)
            if choice == 'h':
                txt_search = ''
                while True:
                    # sort
                    if settings[15]: list_names.sort()
                    try:
                        # show showed items
                        cls()
                        for i in range(len(list_names)):
                            s_out(str(i + 1) + (' ' * (4 - len(str(i + 1)))) + list_names[i].replace(txt_search, '\x1b[7m' + txt_search + '\x1b[0m'))
                        s_out()

                        # ask user input
                        number = s_inp('Type a number to hide, q to quit or / to search.   > ')

                        # quit
                        if number == 'q':
                            break

                        # check input is a number
                        elif number.isdigit():
                            if 0 < int(number) < (len(list_names) + 1):
                                # hide item
                                hided_items.append(list_names[int(number) - 1])
                                del list_names[int(number) - 1]
                            else:
                                cls()
                                s_out('\x1b[1;49;31mThat\'s not a available number!!!\x1b[0m')
                                wait(1.5)

                        # hide a range of numbers
                        elif '.' in number:
                            numbers = number.split('.')
                            if numbers[0].isdigit() and numbers[1].isdigit():
                                for i in range((int(numbers[1]) - int(numbers[0])) + 1):
                                    if 0 < int(numbers[0]) < (len(list_names) + 1):
                                        # hide
                                        hided_items.append(list_names[int(numbers[0]) - 1])
                                        del list_names[int(numbers[0]) - 1]

                                    else:
                                        cls()
                                        s_out('ERROR')
                                        wait(1.5)
                            else:
                                cls()
                                s_out('Your numbers aren\'t available numbers.')
                                wait(1.5)

                        # search
                        elif len(number) > 0:
                            if number == '/':
                                txt_search = s_inp('Search   > ')
                            if number[0] == '/':
                                txt_search = number[1:]

                        else:
                            cls()
                            s_out('\x1b[1;49;31mYour input isn\'t a number, / or q!!!\x1b[0m')
                            wait(1.5)

                    except KeyboardInterrupt:
                        break

            # show item(s)
            if choice == 'u':
                txt_search = ''
                while True:
                    # sort
                    if settings[15]: hided_items.sort()
                    try:
                        # show hided items
                        cls()
                        for i in range(len(hided_items)):
                            s_out(str(i + 1) + (' ' * (4 - len(str(i + 1)))) + hided_items[i].replace(txt_search, '\x1b[7m' + txt_search + '\x1b[0m'))
                        s_out()

                        # ask user input
                        number = s_inp('Type a number to hide, ctrl + c to quit or / to search.   > ')
            
                        # quit
                        if number == 'q':
                            break

                        # check input is a number
                        elif number.isdigit():
                            if 0 < int(number) <= len(hided_items):
                                # show
                                list_names.append(hided_items[int(number) - 1])
                                del hided_items[int(number) - 1]

                            else:
                                cls()
                                s_out('\x1b[1;49;31mNot a valid number!\x1b[0m')
                                wait(1.5)

                        # show a range of items
                        elif '.' in number:
                            numbers = number.split('.')
                            if numbers[0].isdigit() and numbers[1].isdigit():
                                for i in range((int(numbers[1]) - int(numbers[0])) + 1):
                                    if 0 < int(numbers[0]) <= len(hided_items):
                                        # show
                                        list_names.append(hided_items[int(numbers[0]) - 1])
                                        del hided_items[int(numbers[0]) - 1]

                                    else:
                                        cls()
                                        s_out('ERROR')
                                        wait(1.5)
                            else:
                                cls()
                                s_out('Your numbers aren\'t available numbers.')
                                wait(1.5)

                        # zoeken
                        elif len(number) > 0:
                            if number == '/':
                                txt_search = s_inp('Search   > ')
                            if number[0] == '/':
                                txt_search = number[1:]

                        else:
                            cls()
                            s_out('\x1b[1;49;31mYour input isn\'t a number, / or q!!!\x1b[0m')
                            wait(1.5)

                    except KeyboardInterrupt:
                        break

            # quit
            if choice == 'q':
                return ''

            # save and quit
            if choice == 's':
                overwrite(username, hided_items, 'hided_items')
                cls()
                s_out('Successful saved!!!')
                wait(1.5)
                return ''

    # combine items
    if choice == 'c':
        # check number of items
        if len(list_names) != 0:
            try:
                choice2 = s_inp('Do you want to create a new item or add to a existing item? (n/e)   > ')
                options = ['n', 't']
                while choice2 not in options:
                    s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                    choice2 = s_inp('Do you want to create a new item or add to a existing item? (n/e)   > ')

                # new item
                if choice2 == 'n':
                    listname = s_inp('What will be the name of the new item?   > ', invalid_characters = ['/', '\\'])
                    while listname == '' or listname in os.listdir(ch_path('~/' + username + '/items')):
                        if listname in os.listdir(ch_path('~/' + username + '/items')):
                            s_out('This item already exist. Press ctrl + c to cancel.')
                        listname = s_inp('What will be the name of the new item?   > ', invalid_characters = ['/', '\\'])

                    # create file
                    create_file(username, 'items/' + listname)
                    
                # add to existing item
                if choice2 == 't':
                    number = s_inp('Type the number of the item   > ')
                    if number.isdigit():
                        if 0 < int(number) <= len(list_names):
                            listname = list_names[int(number) - 1]
                        else:
                            s_out('Your input isn\'t a available number.')
                            wait(1.5)
                            return ''
                    else:
                        s_out('Your input isn\'t a number.')
                        wait(1.5)
                        return ''

            except KeyboardInterrupt:
                return ''

            # get list of selected items (if the user created a new list, there are none items and if the user selected a item, this is the content of that item)
            list_selected_words = get_list(username, 'items/' + listname)
            while True:
                # select items to combine
                try:
                    number = s_inp('Press a number to add, c to cancel or d if you\'re done.   > ')
                except KeyboardInterrupt:
                    return ''

                # done
                if number == 'd':
                    break

                # cancel
                if number == 'c':
                    return ''

                # check the input is a number
                elif number.isdigit():
                    # check the item exist
                    if 0 < int(number) < (len(list_names) + 1):
                        if (int(number) - 1) not in errors:
                            # add
                            for word in get_list(username, 'items/' + list_names[int(number) - 1]):
                                list_selected_words.append(word)
                        else:
                            s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')

                elif '.' in number:
                    numbers = number.split('.')
                    if numbers[0].isdigit() and numbers[1].isdigit():
                        for number in range(int(numbers[0]), int(numbers[1]) + 1):
                            if 0 < number < (len(list_names) + 1):
                                if (int(number) - 1) not in errors:
                                    # add
                                    for word in get_list(username, 'items/' + list_names[number - 1]):
                                        list_selected_words.append(word)

                                else:
                                    s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                            else:
                                s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')

                    else:
                        s_out('\x1b[1;49;31mThat can\'t. None numbers.\x1b[0m')
                else:
                    s_out('\x1b[1;49;31mThat can\'t. None number, d or c.\x1b[0m')

            # check the user selected words
            if len(list_selected_words) > 0:
                for i in range(len(list_selected_words)):
                    list_selected_words[i][2], list_selected_words[i][3], list_selected_words[i][4], list_selected_words[i][5] = 0, 0, 0, 0
                overwrite(username, list_selected_words, 'items/' + listname)

                list_scores = get_list(username, 'list_items')
                for i in range(len(list_scores)):
                    if list_scores[i][0] == listname:
                        list_scores[i][1] = len(list_selected_words)
                        list_scores[i][2] = get_procent(*get_scores(list_selected_words, settings))
                overwrite(username, list_scores, 'list_items')

            else:
                s_out('\x1b[1;49;31mYou haven\'t selected items.\x1b[0m')
                wait(1.5)
        else:
            s_out('\x1b[1;49;31mThat can\'t. There is nothing to combine.\x1b[0m')
            wait(1.5)

    # split
    if choice == 's':
        # check number of items
        if len(list_names) > 0:
            # ask user input
            number = s_inp('Type the number to split   > ')
            # check input is a number
            if number.isdigit():
                # check item exist
                if 0 < int(number) <= len(list_names):
                    if (int(number) - 1) not in errors:
                        # split item
                        split_list(username, list_names[int(number) - 1], settings)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. The data in this item is invalid.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                wait(1.5)
        else:
            s_out('\x1b[1;49;31mThat can\'t. There is nothing to split.\x1b[0m')
            wait(1.5)

    if choice == 'E':
        # export
        if len(list_names) > 0:
            number = s_inp('Type the number to export   > ')
            if number.isdigit():
                if 0 < int(number) <= len(list_names):
                    locatie = browser(filename = list_names[int(number) - 1], mode = 'create', type = 'f', message = 'Select a file to export')
                    try:
                        shutil.copy(ch_path('~/' + username + '/items/' + list_names[int(number) - 1]), locatie)
                    except:
                        log_error()
                        s_out('Something went wrong.')
                        wait(1.5)
                    else:
                        s_out('Your item is exported!')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                wait(1.5)
        else:
            s_out('\x1b[1;49;31mThat can\'t. There is nothing to export.\x1b[0m')
            wait(1.5)

    if choice == 'I':
        # import
        locatie = browser(mode = 'open', type = 'f', message = 'Select a file to import')
        try:
            shutil.copy(locatie, ch_path('~/' + username + '/items/'))
        except:
            log_error()
            s_out('Something went wrong.')
            wait(1.5)
        else:
            s_out('Your item is imported!')
            wait(1.5)

# change settings
def ch_settings(username):
    settings = get_list(username, 'settings')
    while True:
        try:
            # show current settings
            cls()

            # general
            s_out('\x1b[1;49;34mGeneral settings\x1b[0m')
            s_out('Synchronize automatic when the program starts up: ' + ('yes' if settings[18] else 'no') + ' --> sa')
            s_out('Low search sensitivity: ' + ('yes' if settings[21] else 'no') + ' --> ss')
            s_out('Show legend bar in learn menu: ' + ('yes' if settings[26] else 'no') + ' --> lb')

            s_out()

            # learn
            s_out('\x1b[1;49;34mLearn settings\x1b[0m')
            s_out('Learning method: ' + str(settings[0])[1:][:-1] + ' --> lm')
            s_out('Number of good answered questions for a word to go from niveau 1 to niveau 2: ' + str(settings[16]) + ' --> g1')
            s_out('Number of good answered questions for a word to go from niveau 2 to niveau 3: ' + str(settings[17]) + ' --> g2')
            s_out('Number of new words when you start with learn: ' + str(settings[25]) + ' --> ns')

            s_out()

            s_out('Maximum number of difficult words in a learn session: ' + str(settings[3]) + ' --> md')
            s_out('Maximum number of not often seen words in a learn session: ' + str(settings[4]) + ' --> nn')
            s_out('Maximum number of often seen words deleted out a learn session: ' + str(settings[5]) + ' --> no')
            s_out('Maximum number of words in niveau 1 when words in niveau 0 will be chosen: ' + str(settings[14]) + ' --> nw')

            s_out()

            # mistakes
            s_out('\x1b[1;49;34mSettings for mistakes\x1b[0m')
            s_out('Show good answer by a mistake by learn: ' + ('yes' if settings[1] else 'no') + ' --> al')
            s_out('Show good answer by a mistake by review: ' + ('yes' if settings[2] else 'no') + ' --> ar')
            s_out('Repeat questions with a mistake by learn: ' + ('yes' if settings[6] else 'no') + ' --> rl')
            s_out('Repeat questions with a mistake by review: ' + ('yes' if settings[7] else 'no') + ' --> rr')

            s_out()

            # questions
            s_out('\x1b[1;49;34mSettings for questions\x1b[0m')
            s_out('Number of options by a multiple-choice question: ' + str(settings[8]) + ' --> om')
            s_out('Minumum number of words in a sentence to give a sentence question: ' + str(settings[9]) + ' --> ws')
            s_out('Answer multiple-choice questions to: ' + ('Select answer or type number' if settings[19] else 'Type answer or number') + ' --> am')
            s_out('Answer sentence questions to: ' + ('Select word or type number' if settings[20] else 'Type sentence, word or number') + ' --> as')

            s_out()

            # check
            s_out('\x1b[1;49;34mSettings to check\x1b[0m')
            s_out('Case sensitivity: ' + ('yes' if settings[10] else 'no') + ' --> cs')
            s_out('Punctuation sensitivity: ' + ('yes' if settings[11] else 'no') + ' --> ps')
            s_out('Accent sensitivity: ' + ('yes' if settings[12] else 'no') + ' --> acs')
            s_out('Space sensitivity: ' + ('yes' if settings[13] else 'no') + ' --> sps')
            s_out('Apostrophe sensitivity: ' + ('yes' if settings[22] else 'no') + ' --> aps')

            s_out()

            # sorting and information
            s_out('\x1b[1;49;34mSettings to sort and show information\x1b[0m')
            s_out('Way of sorting: ', end = '')
            if settings[15] == 0: s_out('don\'t sort', end = '')
            elif settings[15] == 1: s_out('alphabetically', end = '')
            else: s_out('ERROR', end = '')
            s_out(' --> st')

            s_out('Show information of items: ', end = '')
            if settings[24][0]: s_out('last modified, ', end = '')
            if settings[24][1]: s_out('size, ', end = '')
            if settings[24][2]: s_out('state (W/E), ', end = '')
            if settings[24][3]: s_out('number of words, ', end = '')
            if settings[24][4]: s_out('score, ', end = '')
            s_out('\x1b[D\x1b[D --> ii')

            s_out('Sort automatically the words in a item: ', end = '')
            if settings[23] == -1: s_out('don\'t sort', end = '')
            elif settings[23] == 0: s_out('alphabetically with known word', end = '')
            elif settings[23] == 1: s_out('alphabetically with unknown word', end = '')
            elif settings[23] == 2: s_out('niveau', end = '')
            elif settings[23] == 3: s_out('number of times in a row correct', end = '')
            elif settings[23] == 4: s_out('number of mistakes', end = '')
            elif settings[23] == 5: s_out('number of times answered', end = '')
            s_out(' --> si')

            s_out()

            # save and quit
            s_out('\x1b[1;49;34mSave and quit\x1b[0m')
            s_out('Save --> s')
            s_out('Quit --> q')
            s_out('Load settings --> l')
            s_out('Reset to default --> r')

            # lijst met opties voor de gebruiker
            options = ['lb', 'sa', 'ss', 'lm', 'g1', 'g2', 'md', 'nn', 'no', 'nw', 'al', 'ar', 'rl', 'rr', 'om', 'ws', 'am', 'as', 'cs', 'ps', 'acs', 'sps', 'aps', 'st', 'ii', 'si', 'ns', 's', 'q', 'l', 'r']
            # ask user
            choice = s_inp('   > ')

            # ask again when the input not a option is
            if choice not in options:
                cls()
                s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                wait(1.5)
                continue

            # change learn method
            if choice == 'lm':
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
                        string = string + str(i) + ': ' + str(settings[0].count(i)) + '    '

                    string = string + '\r'

                    for i in range(number + 1):
                        string = string + str(i) + ': ' + str(settings[0].count(i)) + '    '

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
                            if c2 == 'A' and settings[0].count(number) > 0:
                                settings[0].remove(number)
                            
                            # arrow down
                            if c2 == 'B' and settings[0].count(number) < 8:
                                settings[0].append(number)

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
                                for aantal in range(settings[0].count(number)):
                                    settings[0].remove(number)

                            # page down
                            if c2 == '6':
                                getch()
                                for aantal in range(8 - settings[0].count(number)):
                                    settings[0].append(number)

                        if os.name == 'nt':
                            # arrow up
                            if c1 == 'H':
                                settings[0].remove(number)

                            # arrow down
                            if c1 == 'P':
                                settings[0].append(number)

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
                                for aantal in range(settings[0].count(number)):
                                    settings[0].remove(number)

                            # page down
                            if c1 == 'Q':
                                for aantal in range(8 - settings[0].count(number)):
                                    settings[0].append(number)

                    if ch == 'q' or ch == 's':
                        break

                    settings[0].sort()

            # show legend bar
            if choice == 'lb':
                cls()
                settings[25] = s_inp('Show legend bar in the learn menu (y/n)   > ') == 'y'

            # show the good answer by learn
            if choice == 'al':
                cls()
                settings[1] = s_inp('Show good answer by learn (yes/no)   > ') == 'yes'

            # show the good answer by review
            if choice == 'ar':
                cls()
                settings[2] = s_inp('Show good answer by review (yes/no)   > ') == 'yes'

            # repeat hard words
            if choice == 'md':
                number = -1
                while number < 0 or number > 3:
                    cls()
                    number = int(s_inp('Maximum number of difficult words in a learn session (number)   > '))
                settings[3] = int(number)

            # repeat not often had words
            if choice == 'nn':
                number = -1
                while number < 0 or number > 3:
                    cls()
                    number = int(s_inp('Maximum number of not often had words in a learn session (number)   > '))
                settings[4] = int(number)

            # delete easy words
            if choice == 'no':
                number = -1
                while number < 0 or number > 3:
                    cls()
                    number = int(s_inp('Maximum number of often had words to delete out a learn session (number)   > '))
                settings[5] = int(number)

            # repeat words with mistakes by learn
            if choice == 'rl':
                cls()
                settings[6] = s_inp('Repeat words with mistakes by learn (yes/no)   > ') == 'yes'

            # repeat words with mistakes by review
            if choice == 'rr':
                cls()
                settings[7] = s_inp('Repeat words with mistakes by review (yes/no)   > ') == 'yes'

            # number of words to be showed in a multiple-choice question
            if choice == 'om':
                number = 1
                while number < 2 or number > 9:
                    cls()
                    number = int(s_inp('Type the number of words in a multiple-choice question (number)   > '))
                settings[8] = int(number)

            # minimum number of words by a sentence question
            if choice == 'ws':
                number = 1
                while number < 2 or number > 6:
                    cls()
                    number = int(s_inp('Type the minimum number of words in a sentence question (number)   > '))
                settings[9] = int(number)

            # case sensitivity
            if choice == 'cs':
                cls()
                settings[10] = s_inp('Case sensitivity (yes/no)   > ') == 'yes'

            # punctuation sensitivity
            if choice == 'ps':
                cls()
                settings[11] = s_inp('Punctuation sensitivity (yes/no)   > ') == 'yes'

            # accent sensitivity
            if choice == 'acs':
                cls()
                settings[12] = s_inp('Accent sensitivity (yes/no)   > ') == 'yes'

            # space sensitivity
            if choice == 'sps':
                cls()
                settings[13] = s_inp('Space sensitivity (yes/no)   > ') == 'yes'

            # number of words when you learn new words
            if choice == 'nw':
                number = 0
                while number < 1 or number > 10:
                    cls()
                    number = int(s_inp('Type the maximum number of words when you learn new words (number)   > '))
                settings[14] = int(number)

            # way of sort
            if choice == 'st':
                number = -1
                while True:
                    cls()
                    s_out('Choose the way of sort.')
                    s_out('0 --> Not sorted')
                    s_out('1 --> Alphabetically')
                    number = s_inp('   > ')
                    if number.isdigit():
                        if -1 < int(number) < 2:
                            break
                settings[15] = int(number)

            # way of sort between words
            if choice == 'si':
                number = -2
                while True:
                    cls()
                    s_out('Choose the way of sort between words.')
                    s_out('-1 --> Not sorted')
                    s_out('0  --> Alphabetically by known word')
                    s_out('1  --> Alphabetically by unknown word')
                    s_out('2  --> Niveau')
                    s_out('3  --> Number of times in a row correct')
                    s_out('4  --> Number of mistakes')
                    s_out('5  --> Number of times answered')
                    number = s_inp('   > ')
                    if number.isdigit() or number == '-1':
                        if -2 < int(number) < 6:
                            break
                settings[23] = int(number)

            # go from niveau 1 to niveau 2
            if choice == 'g1':
                number = 0
                while not 0 < number < 8:
                    cls()
                    number = int(s_inp('Number of times in a row correct to go from niveau 1 to niveau 2 (number)   > '))
                settings[16] = number

            # het aantal keer dat je een woord achter elkaar goed moet hebben om het van niveau 2 naar niveau 3 te laten gaan
            if choice == 'g2':
                number = 0
                while not 1 < number < 10:
                    cls()
                    number = int(s_inp('Number of times in a row correct to go from niveau 2 to niveau 3 (number)   > '))
                settings[17] = number

            # automatically synchronize
            if choice == 'sa':
                cls()
                settings[18] = s_inp('Synchronize automatically the items by startup (yes/no)   > ') == 'yes'

            if choice == 'am':
                cls()
                s_out('Choose the way to answer multiple-choice questions:')
                s_out('Type numbers or select answer --> 0')
                s_out('Type numbers or word --> 1')
                settings[19] = s_inp('   > ') == '0'

            if choice == 'as':
                cls()
                s_out('Choose the way to answer sentence questions:')
                s_out('Type numbers or select word --> 0')
                s_out('Type numbers, sentence or word --> 1')
                settings[20] = s_inp('   > ') == '0'

            if choice == 'ss':
                cls()
                settings[21] = s_inp('Low search sensitivity (yes/no)   > ') == 'yes'

            # apostrophe sensitivity
            if choice == 'aps':
                cls()
                settings[22] = s_inp('Apostrophe sensitivity (yes/no)   > ') == 'yes'

            # information from items on menu
            if choice == 'ii':
                while True:
                    cls()
                    s_out('Choose what will be showed on the menu:')
                    s_out(('Showed ' if settings[24][0] else 'Hided  ') + ' Last change --> l')
                    s_out(('Showed ' if settings[24][1] else 'Hided  ') + ' Size --> z')
                    s_out(('Showed ' if settings[24][2] else 'Hided  ') + ' State (W/E; Warnings or Errors) --> t')
                    s_out(('Showed ' if settings[24][3] else 'Hided  ') + ' Number of words --> w')
                    s_out(('Showed ' if settings[24][4] else 'Hided  ') + ' Score --> c')
                    s_out(('Showed ' if settings[24][5] else 'Hided  ') + ' Info --> i')
                    s_out('Quit --> s/q')

                    options = ['l', 'z', 't', 'w', 'c', 'i', 's', 'q']

                    d = s_inp('   > ')

                    if d not in options:
                        s_out('That isn\'t a option!!!')
                        wait(1.5)
                        continue

                    if d == 'l':
                        settings[24][0] = not settings[24][0]

                    if d == 'z':
                        settings[24][1] = not settings[24][1]

                    if d == 't':
                        settings[24][2] = not settings[24][2]

                    if d == 'w':
                        settings[24][3] = not settings[24][3]

                    if d == 'c':
                        settings[24][4] = not settings[24][4]

                    if d == 'c':
                        settings[24][5] = not settings[24][5]

                    if d == 's' or d == 'q':
                        break

            # start with unknown words
            if choice == 'ns':
                number = 0
                while not 0 < number < 10:
                    cls()
                    number = int(s_inp('Number of new words when you start with learn (number) (1-9)   > '))
                settings[25] = number

            # save
            if choice == 's':
                # check learn method
                for i in 0, 1, 2, 3:
                    if i not in settings[0]:
                        settings[0].append(i)
                # save settings
                overwrite(username, settings, 'settings')
                s_out('Successful saved!')

            # home
            if choice == 'q':
                return ''

            # load settings
            if choice == 'l':
                settings = get_list(username, 'settings')
                s_out('Successful loaded!')
                wait(1.5)

            # reset settings
            if choice == 'r':
                delete_file(username, 'settings')
                shutil.copy(ch_path('~/basic_files/settings'), ch_path('~/' + username + '/settings'))
                settings = get_list(username, 'settings')
                cls()
                s_out('Successful resetted!')
                wait(1.5)

        except ValueError:
            cls()
            s_out('Invalid input.')
            wait(1.5)
            continue

        except KeyboardInterrupt:
            cls()
            choice = s_inp('Do you want to save? (yes/no/Cancel)   > ')
            if choice == 'yes':
                # check learn method
                for i in 0, 1, 2, 3:
                    if i not in settings[0]:
                        settings[0].append(i)
                # save
                overwrite(username, settings, 'settings')
                return ''

            # cancel
            elif choice == '' or choice == 'cancel':
                continue

            # home
            elif choice == 'no':
                return ''

