# import modules
import os
import shutil
import datetime
from time import sleep as wait, time

from extern.save_input import save_input as s_inp
from extern.getchar import getch
from extern.save_output import save_output as s_out, cls

from manage_files import get_list, overwrite, ch_path, delete_file, create_file, create_list, move, copy, delete, create_backup, remove_backup, restore_backup, remove_all_backups
from review import review, proceed_session, show_saved_sessions
from manage_items import change_list, add_list, item_options, split_list, get_item_information, show_trash
from go_through import go_through
from learn import learn, review_and_learn, learn_all
from functions import is_warned, ch_size, ch_time, get_scores, get_procent, synchronize, select, lower, no_punctuation_marks, no_accents, sort, user_choice_items
from errors import WordIndexError, log_error
from file_browser import browser
from users import logout
from update import update

# set functions
def help():
    cls()
    s_out('Quit --> q')
    s_out('Synchronise --> y')
    s_out('Settings --> s')
    s_out('Add --> a')
    s_out('Show/hide hided items --> H')
    s_out('Show this help menu --> h')
    s_out('Backup menu --> b')
    s_out('Show userinfo --> u')
    s_out('Logout --> o')
    s_out('Delete user --> D')
    s_out('Update --> U')
    s_out('Change username --> C')
    s_out('Hide/show items --> e')
    s_out('Trash --> t')
    s_out('View saved sessions --> S')
    s_out('Continue saved session --> c')
    s_out('Import item --> i')
    s_out('Redraw menu --> r')
    s_out('Search --> /')
    s_out('Search and show only agreements --> ?')
    s_out('Move selection up --> k or arrow up')
    s_out('Move selection down --> j or arrow down')
    s_out('Do actions with selected item --> enter')
    s_out('Select multiple items --> tab')
    s_out()
    s_out('When not all items fit on the screen, use \'e\' to hide unused items to clean up the screen.')
    s_out()
    s_inp('Press enter to continue. ')
    
# learn menu
def main_menu(username, userinfo):
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
    refresh = False

    while True:
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
        lines = os.get_terminal_size().lines
        lines = lines - 5

        # width_screen is the number of columns for the name of the item that will be showed
        width_screen = columns

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

        # sort names
        #if settings[15] == 1: list_names.sort()

        # calculate information to show
        item_information = []

        count = 0
        write_warnings = False
        for i in range(len(list_names)):
            item_info = [list_names[i]]
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
                #s_out(select(str(i + 1) + ': ', txt_search) + (' ' * (4 - len(str(i + 1)))), end = '')

                printable_item_name = ''

                # show item name
                max_length = width_screen - 6
                name_item = list_names[i]
                while len(name_item) >= max_length and max_length > 10:
                    show_name_item = name_item[:max_length] + '      \x1b[1;49;37m|\x1b[0m' + (' ' * 64) + '\n'
                    name_item = name_item[max_length:]
                    printable_item_name = printable_item_name + select(show_name_item, txt_search)
                    #s_out(select(show_name_item, txt_search), end = '')

                #s_out(select(name_item, txt_search), end = '')
                printable_item_name = printable_item_name + select(name_item, txt_search)

                # complete line with spaces or lines
                #s_out('\x1b[2;49;2m' + ((' ' if count % 6 != 2 else '-') * (width_screen - len(name_item))) + '\x1b[0m', end = '')
                #printable_item_name = printable_item_name + '\x1b[2;49;2m' + ((' ' if count % 6 != 2 else '-') * (width_screen - len(name_item))) + '\x1b[0m'
                item_info.append(len(name_item))

                item_info.append(printable_item_name)

                # show last change
                if settings[24][0]:
                    #s_out(select(str(datetime.datetime.fromtimestamp(os.path.getmtime(ch_path('~/' + username + '/items/' + list_names[i])))).split('.')[0], txt_search) + '   ', end = '')
                    item_info.append(select(str(datetime.datetime.fromtimestamp(os.path.getmtime(ch_path('~/' + username + '/items/' + list_names[i])))).split('.')[0], txt_search) + '   ')

                # show size
                if settings[24][1]:
                    #s_out(select(ch_size(os.path.getsize(ch_path('~/' + username + '/items/' + list_names[i]))), txt_search).replace('K', '\x1b[1;49;33mK\x1b[0m').replace('M', '\x1b[1;49;33mM\x1b[0m').replace('G', '\x1b[1;49;33mG\x1b[0m').replace('T', '\x1b[1;49;33mT\x1b[0m') + ' ', end = '')
                    item_info.append(select(ch_size(os.path.getsize(ch_path('~/' + username + '/items/' + list_names[i]))), txt_search).replace('K', '\x1b[1;49;33mK\x1b[0m').replace('M', '\x1b[1;49;33mM\x1b[0m').replace('G', '\x1b[1;49;33mG\x1b[0m').replace('T', '\x1b[1;49;33mT\x1b[0m') + ' ')

                # show number of words
                if settings[24][2]:
                    #s_out(select(str(number_words), txt_search) + ((' ' * (5 - len(str(number_words)))) if len(str(number_words)) < 5 else ' '), end = '')
                    item_info.append(select(str(number_words), txt_search) + ((' ' * (5 - len(str(number_words)))) if len(str(number_words)) < 5 else ' '))

                # show state
                if settings[24][3]:
                    printable_text = ''
                    spaces = 4
                    if error:
                        #s_out('\x1b[1;49;31m' + select('E', txt_search) + '\x1b[0m', end = '')
                        printable_text = printable_text + '\x1b[1;49;31m' + select('E', txt_search) + '\x1b[0m'
                        spaces = spaces - 1
                    if list_names[i] in hided_items:
                        #s_out('\x1b[1;49;33m' + select('H', txt_search) + '\x1b[0m', end = '')
                        printable_text = printable_text + '\x1b[1;49;33m' + select('H', txt_search) + '\x1b[0m'
                        spaces = spaces - 1
                    if list_names[i] in warned_items:
                        #s_out('\x1b[1;49;33m' + select('W', txt_search) + '\x1b[0m', end = '')
                        printable_text = printable_text + '\x1b[1;49;33m' + select('W', txt_search) + '\x1b[0m'
                        spaces = spaces - 1
                    for item_setting in item_settings:
                        try:
                            if item_setting[0] == list_names[i] and item_setting[1] != 0:
                                if (item_setting[1] + item_setting[2]) < time():
                                    #s_out('\x1b[1;49;33m' + select('T', txt_search) + '\x1b[0m', end = '')
                                    printable_text = printable_text + '\x1b[1;49;33m' + select('T', txt_search) + '\x1b[0m'
                                else:
                                    #s_out('\x1b[1;49;37m' + select('t', txt_search) + '\x1b[0m', end = '')
                                    printable_text = printable_text + '\x1b[1;49;37m' + select('t', txt_search) + '\x1b[0m'
                                spaces = spaces - 1

                        except IndexError:
                            #s_out('\x1b[1;49;31m' + select('T', txt_search) + '\x1b[0m', end = '')
                            printable_text = printable_text + '\x1b[1;49;31m' + select('T', txt_search) + '\x1b[0m'
                            spaces = spaces - 1

                    if spaces == 4:
                        #s_out('\x1b[1;49;37m' + select('G', txt_search) + '\x1b[0m', end = '')
                        printable_text = printable_text + '\x1b[1;49;37m' + select('G', txt_search) + '\x1b[0m'
                        spaces = spaces - 1

                    #s_out(' ' * spaces, end = '')
                    printable_text = printable_text + ' ' * spaces

                    item_info.append(printable_text)

                # show item settings
                if settings[24][5]:
                    printable_text = ''
                    try:
                        count_is = 0
                        for item_setting in item_settings:
                            if item_setting[0] == list_names[i] and item_setting[1] != 0:
                                curtime = time()
                                if (item_setting[1] - (curtime - item_setting[2])) > 0:
                                    #s_out(select(ch_time(item_setting[1] - (curtime - item_setting[2]))[0], txt_search), end = '')
                                    printable_text = printable_text + select(ch_time(item_setting[1] - (curtime - item_setting[2]))[0], txt_search)
                                    #s_out(' ' * (9 - len(ch_time(curtime - item_setting[2])[0])), end = '')
                                    printable_text = printable_text + ' ' * (9 - len(ch_time(curtime - item_setting[2])[0]))
                                else:
                                    #s_out(select('\x1b[1;49;33mNow\x1b[0m   ', txt_search), end = '')
                                    printable_text = printable_text + select('\x1b[1;49;33mNow\x1b[0m      ', txt_search)

                                #s_out(select(str(item_setting[3]) + str(item_setting[4]), txt_search), end = '')
                                printable_text = printable_text + select(str(item_setting[3]) + str(item_setting[4]), txt_search)
                                #s_out(' ' * (4 - len(str(item_setting[3]) + str(item_setting[4]))), end = '')
                                printable_text = printable_text + ' ' * (4 - len(str(item_setting[3]) + str(item_setting[4])))
                                count_is = count_is + 1
                                break

                        if count_is == 0:
                            #s_out('\x1b[1;49;36m' + select('None info', txt_search) + '\x1b[0m ', end = '')
                            printable_text = printable_text + '\x1b[1;49;36m' + select('None info', txt_search) + '\x1b[0m '

                    except IndexError:
                        log_error()
                        #s_out('\x1b[1;49;31m' + select('ERROR!', txt_search) + '   \x1b[0m ', end = '')
                        printable_text = printable_text + '\x1b[1;49;31m' + select('ERROR!   ', txt_search) + '   \x1b[0m '

                    item_info.append(printable_text)
                        

                # show score
                if settings[24][4]:
                    #s_out(select(score, txt_search))
                    item_info.append(select(score, txt_search))

                #else:
                    #s_out()

                item_information.append(item_info)
                count = count + 1

        # overwrite if it needed
        if write_scores:
            overwrite(username, list_scores, 'list_items')
        if write_warnings:
            overwrite(username, warned_items, 'warned_items')

        # sort
        if settings[15] != -1:
            item_information = sort(item_information, settings[15])

        if settings[28]:
            item_information.reverse()

        if settings[26] and len(item_information) > 0:
            lines = lines - 1

        selection = 0
        selected = []
        start_number = 0
        max_start_number = len(item_information) - lines

        while True:
            # move cursor to (0, 0)
            s_out('\x1b[H', end = '')

            # show legend
            if settings[26] and len(item_information) > 0:
                s_out('\rName' + (' ' * (width_screen - 4)), end = '')
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

            list_names = []
            for item in item_information:
                list_names.append(item[0])

            # show all
            ulines = 0
            show_selection = selection - start_number
            show_selected = []
            for item in selected:
                show_selected.append(item + start_number)
            avail_lines = lines
            for number in range(len(item_information[start_number:])):
                item = item_information[start_number:][number].copy()
                #s_out('\r' + (' ' * columns) + '\r', end = '')
                if number == show_selection and number in show_selected:
                    item[2] = '\x1b[7;49;36m' + str(item[2]) + '\x1b[0m\x1b[2;49;2m' + ((' ' if number % 6 != 2 else '-') * (width_screen - item[1])) + '\x1b[0m'
                elif number in show_selected:
                    item[2] = '\x1b[7;49;33m' + str(item[2]) + '\x1b[0m\x1b[2;49;2m' + ((' ' if number % 6 != 2 else '-') * (width_screen - item[1])) + '\x1b[0m'
                elif number == show_selection:
                    item[2] = '\x1b[7m' + str(item[2]) + '\x1b[0m\x1b[2;49;2m' + ((' ' if number % 6 != 2 else '-') * (width_screen - item[1])) + '\x1b[0m'
                else:
                    item[2] = str(item[2]) + '\x1b[2;49;2m' + ((' ' if number % 6 != 2 else '-') * (width_screen - item[1])) + '\x1b[0m'
                #list_names.append(item[0])
                string = ''
                for number in range(len(item) - 2):
                    string = string + item[number + 2]
                if (string.count('\n') + 1) >= avail_lines:
                    break
                s_out(string)
                avail_lines = avail_lines - (string.count('\n') + 1)
                ulines = ulines + 1

            for i in range(avail_lines):
                s_out(' ' * columns)

            # show extra info
            if count > 0:
                s_out('_' * columns)
                s_out(' ' * columns)
                search_info = (str(count) + ' agreement' + ('s' if count > 1 else '') + ' with your search \'' + str(txt_search) + '\'    ' if show_agreements else '') + str(len(list_names)) + (' showed    ' if not show_agreements else ' showed without your search    ') + str(number_items) + ' available'
                s_out(search_info + (' ' * (columns - len(search_info))))
                s_out(' ' * columns)
                #lines = lines - 4
            
            elif show_agreements:
                s_out('_' * columns)
                s_out(' ' * columns)
                search_info = 'There are none agreements with your search \'' + str(txt_search) + '\'.'
                s_out(search_info + (' ' * (columns - len(search_info))))
                s_out(' ' * columns)
                #lines = lines - 2

            else:
                s_out('_' * columns)
                s_out(' ' * columns)
                search_info = 'There are no items available. Press \'a\' to add one or \'i\' to import one.'
                s_out(search_info + (' ' * (columns - len(search_info))))
                s_out(' ' * columns)

            # ask input
            try:
                prompt_message = 'Type a command or \'h\' to see the help menu.   > '
                prompt_message = prompt_message + (' ' * (columns - len(prompt_message))) + '\r' + ('\x1b[C' * len(prompt_message))
                s_out(prompt_message, end = '')
                choice = getch()
            except KeyboardInterrupt:
                cls()
                try:
                    if s_inp('Do you want to quit? (y/n)   > ') == 'y':
                        logout(username, userinfo)
                        exit()
                except KeyboardInterrupt:
                    exit()

                break

            # if the input isn't a option, ask again
            options = ['q', 'y', 's', 'a', 'H', 'h', 'b', 'u', 'o', 'D', 'U', 'C', 'e', 't', 'S', 'c', 'i', 'r', '\t', 'k', 'j', '/', '?', '\x1b', '\x00', '\n']
            if choice not in options:
                cls()
                s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                wait(1.5)
                continue

            # back to home
            if choice == 'q':
                logout(username, userinfo)
                s_out()
                exit()

            # synchronize
            if choice == 'y':
                s_out('Synchronizing.')
                try:
                    synchronize(username, settings)
                except KeyboardInterrupt:
                    continue

                break

            # change settings
            if choice == 's':
                ch_settings(username)
                settings = get_list(username, 'settings')
                break

            # add item
            if choice == 'a':
                try:
                    add_list(username, settings)
                except KeyboardInterrupt:
                    continue

                break

            # hide/show hided items
            if choice == 'H':
                show_all = not show_all
                break

            # show help menu
            if choice == 'h':
                help()

            # backup menu
            if choice == 'b':
                backup_menu(username)
                break

            # show user information
            if choice == 'u':
                cls()
                time_created = str(datetime.datetime.fromtimestamp(userinfo[0]))
                time_created = time_created[:time_created.find('.')]
                s_out('     Time created: ' + str(time_created))
                time_changed = str(datetime.datetime.fromtimestamp(userinfo[1]))
                time_changed = time_changed[:time_changed.find('.')]
                s_out('Last time learned: ' + str(time_changed))
                s_out('     Time learned: ' + ch_time(userinfo[2] + (time() - userinfo[3]))[0])
                s_out()
                s_inp('Press enter to continue. ')

            # logout
            if choice == 'o':
                return 'logout'

            # delete user
            if choice == 'D':
                try:
                    if s_inp('Are you sure to delete your account? It can\'t be undone. (y/n)   >  ') == 'y':
                        delete(name)
                        return 'logout'
                except KeyboardInterrupt:
                    continue

            # update
            if choice == 'U':
                logout(username, userinfo)
                update(<path_to_info>)
                exit()

            # change username
            if choice == 'C':
                cls()
                s_out('Current username: ' + username)
                new_name = s_inp('Type the new username.   > ', input = username, mode = 'file')
                shutil.move(ch_path('~/' + username), ch_path('~/' + new_name))
                username = new_name
                break

            # hide/show items
            if choice == 'e':
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
                                        hided_items.append(list_names[selection])
                                        del list_names[selection]
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
                                        list_names.append(hided_items[selection])
                                        del hided_items[selection]

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
                        break

                    # save and quit
                    if choice == 's':
                        overwrite(username, hided_items, 'hided_items')
                        cls()
                        s_out('Successful saved!!!')
                        wait(1.5)
                        break
                break

            # go to trash
            if choice == 't':
                show_trash(username)
                break

            # view saved sessions
            if choice == 'S':
                show_saved_sessions(username, settings)
                break

            # continue saved session
            if choice == 'c':
                proceed_session(username, settings)
                break
            
            # import item
            if choice == 'i':
                # import
                location = browser(mode = 'open', type = 'f', message = 'Select a file to import')
                try:
                    shutil.copy(location, ch_path('~/' + username + '/items/'))
                except:
                    log_error()
                    s_out('Something went wrong.')
                    wait(1.5)
                else:
                    s_out('Your item is imported!')

                break
      
            # redraw menu
            if choice == 'r':
                break

            # select multiple items
            if choice == '\t':
                if selection in selected:
                    selected.remove(selection)
                else:
                    selected.append(selection)

            # search
            if choice == '/':
                # search
                try:
                    txt_search = s_inp('Search   > ')
                except KeyboardInterrupt:
                    continue

                show_agreements = False

            # search and show only agreements
            if choice == '?':
                # search
                try:
                    txt_search = s_inp('Search   > ')
                except KeyboardInterrupt:
                    continue

                show_agreements = True

            # move selection up
            if choice == 'k':
                selection = selection - 1

            # move selection down
            if choice == 'j':
                selection = selection + 1

            if choice == '\x1b' or choice == '\x00':
                # TODO make it working on windows systems
                c1 = getch()
                if c1 == '[':
                    c2 = getch()
                    # arrow up: move selection up
                    if c2 == 'A':
                        selection = selection - 1
                    # arrow down: move selection down
                    elif c2 == 'B':
                        selection = selection + 1

            # when the selection goes out of the screen, place it on the other site back
            if selection < 0:
                selection = len(list_names) - 1
            if selection >= len(list_names):
                selection = 0

            #while selection < (start_number + (lines / 2)) and start_number > 0:
            while selection < (start_number + 4) and start_number > 0:
                start_number = start_number - 1

            #while selection > (start_number + (lines / 2)) and start_number <= max_start_number:
            while selection > (start_number + (ulines - 5)) and start_number <= max_start_number:
                start_number = start_number + 1

            # do actions with selection or selected items
            if choice == '\n':
                try:
                    if len(list_names) == 0:
                        continue

                    if len(selected) == 0:
                        item_error = selection in errors
                        
                        cls()
                        if item_error:
                            s_out('There occured an error...')
                            wait(1.5)
                            continue

                        s_out('Delete --> d')
                        s_out('Change --> c')
                        s_out('Learn --> l')
                        s_out('Item options --> o')
                        s_out('Item information --> i')
                        s_out('Split item --> s')
                        s_out('Export --> e')
                        s_out('Learn all words in 1 session --> L')
                        s_out('Review and save all good answered words as learned --> r')
                        s_out('Back to home --> b/q')
                        s_out('\rChoice to do   > ', end = '')
                        choice = getch()

                        options = ['d', 'c', 'l', 'o', 'i', 's', 'e', 'L', 'r', 'b', 'q']

                        if choice not in options:
                            cls()
                            s_out('That isn\'t a option!')
                            wait(1.5)
                            continue

                        # delete item
                        if choice == 'd':
                            try:
                                # move to trash
                                move(username, 'items/' + list_names[selection], 'trash/')
                            except:
                                log_error()
                                cls()
                                s_out('Can\'t move to trash.')
                                # check the item already exist in trash
                                if list_names[selection] in os.listdir(ch_path('~/' + username + '/trash/')):
                                    # ask
                                    if s_inp('\'' + list_names[selection] + '\' already exist in the trash. Do you want to replace it? (y/n)   > ') == 'y':
                                        try:
                                            # delete old item out trash
                                            delete_file(username, 'trash/' + list_names[selection])
                                            # move item to trash
                                            move(username, 'items/' + list_names[selection], 'trash/')
                                        except:
                                            log_error()
                                            s_out()
                                            s_out('Can\'t replace.')
                                            s_inp('Press enter to continue. ')

                                else:
                                    s_inp('Press enter to continue. ')

                        # change item
                        if choice == 'c':
                            try:
                                change_list(username, list_names[selection], settings)
                            except KeyboardInterrupt:
                                cls()
                                s_out('Back to home.')
                                wait(1.5)
                                continue

                        # learn item
                        if choice == 'l':
                            try:
                                learn(username, list_names[selection], settings)
                            except KeyboardInterrupt:
                                cls()
                                s_out('Back to home.')
                                wait(1.5)
                                continue

                        if choice == 'o':
                            try:
                                item_options(username, list_names[selection], settings)
                            except KeyboardInterrupt:
                                cls()
                                s_out('Back to home.')
                                wait(1.5)
                                continue
                        
                        if choice == 'i':
                            get_item_information(username, list_names[selection], settings)
                        
                        if choice == 'r':
                            review_and_learn(username, list_names[selection], settings)
                        
                        if choice == 's':
                            split_list(username, list_names[selection], settings)

                        if choice == 'e':
                            location = browser(filename = list_names[selection], mode = 'create', type = 'f', message = 'Select a file to export')
                            try:
                                shutil.copy(ch_path('~/' + username + '/items/' + list_names[selection]), location)
                            except:
                                log_error()
                                s_out('Something went wrong.')
                                wait(1.5)
                            else:
                                s_out('Your item is exported!')

                        if choice == 'L':
                            learn_all(username, list_names[selection], settings)

                        break

                    else:
                        item_error = False
                        for item in selected:
                            if item in errors:
                                item_error = True
                        
                        cls()
                        if item_error:
                            s_out('There occured an error...')
                            wait(1.5)
                            continue

                        options = ['r', 't', 'c', 'q', 'b']

                        s_out('Review --> r')
                        s_out('Go through --> t')
                        s_out('Combine items --> c')
                        s_out('Back --> q/b')
                        s_out('\rChoice   > ', end = '')
                        choice = getch()

                        # combine items to a new item
                        if choice == 'c':
                            listname = s_inp('What will be the name of the new item?   > ', mode = 'file')
                            while listname == '' or listname in os.listdir(ch_path('~/' + username + '/items')):
                                if listname in os.listdir(ch_path('~/' + username + '/items')):
                                    s_out('This item already exist. Press ctrl + c to cancel.')
                                listname = s_inp('What will be the name of the new item?   > ', mode = 'file')

                            del_process = ''
                            options = ['y', 'n']
                            while del_process not in options:
                                if del_process != '':
                                    s_out('That isn\'t a option!')
                                del_process = s_inp('Do you want to remove your process? (y/n)   > ')

                            list_selected_words = []

                            for item in selected:
                                list_selected_words = list_selected_words + get_list(username, 'items/' + list_names[item])

                            if del_process == 'y':
                                for number in range(len(list_selected_words)):
                                    list_selected_words[number][2], list_selected_words[number][3], list_selected_words[number][4], list_selected_words[number][5] = 0, 0, 0, 0

                            overwrite(username, list_selected_words, 'items/' + listname)

                            list_scores = get_list(username, 'list_items')
                            for i in range(len(list_scores)):
                                if list_scores[i][0] == listname:
                                    list_scores[i][1] = len(list_selected_words)
                                    list_scores[i][2] = get_procent(*get_scores(list_selected_words, settings))
                            overwrite(username, list_scores, 'list_items')

                        # review item(s) or go through item(s)
                        if choice == 'r' or choice == 't':
                            list_selected_words = []
                            for item in selected:
                                list_selected_words = list_selected_words + get_list(username, 'items/' + list_names[item])

                            for number in range(len(list_words)):
                                list_selected_words[number][2], list_selected_words[number][3], list_selected_words[number][4], list_selected_words[number][5] = 0, 0, 0, 0

                            if choice == 'r':
                                review(list_selected_words, username, settings)
                            if choice == 't':
                                go_through(list_selected_words, username, settings)

                                '''
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
                                            if (selection) not in errors:
                                                for word in get_list(username, 'items/' + list_names[selection]):
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
                                                    if (selection) not in errors:
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
                                '''

                        break

                except KeyboardInterrupt:
                    break

'''
# advenched functions
def advenched(list_names, username, settings, errors):
    # set options
    options = ['r', 'ss', 'cs', 'i', 'h', 'c', 's', 'E', 'I', 't', 'b', 'q', 'l']

    # show options
    s_out('Review and save correct answered words as learned --> r')
    s_out('View saved sessions --> ss')
    s_out('Continue with a saved session --> cs')
    s_out('Learn a session with all words in it --> l')
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
                    if (selection) not in errors:
                        get_item_information(username, list_names[selection], settings)
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
    if choice == 'ss':
        show_saved_sessions(username, settings)

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
                    if (selection) not in errors:
                        review_and_learn(username, list_names[selection], settings)
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
    if choice == 'cs':
        proceed_session(username, settings)

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
                                hided_items.append(list_names[selection])
                                del list_names[selection]
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
                                list_names.append(hided_items[selection])
                                del hided_items[selection]

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
                    listname = s_inp('What will be the name of the new item?   > ', mode = 'file')
                    while listname == '' or listname in os.listdir(ch_path('~/' + username + '/items')):
                        if listname in os.listdir(ch_path('~/' + username + '/items')):
                            s_out('This item already exist. Press ctrl + c to cancel.')
                        listname = s_inp('What will be the name of the new item?   > ', mode = 'file')

                    # create file
                    create_file(username, 'items/' + listname)
                    
                # add to existing item
                if choice2 == 't':
                    number = s_inp('Type the number of the item   > ')
                    if number.isdigit():
                        if 0 < int(number) <= len(list_names):
                            listname = list_names[selection]
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
                        if (selection) not in errors:
                            # add
                            for word in get_list(username, 'items/' + list_names[selection]):
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
                                if (selection) not in errors:
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
                    if (selection) not in errors:
                        # split item
                        split_list(username, list_names[selection], settings)
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
                    location = browser(filename = list_names[selection], mode = 'create', type = 'f', message = 'Select a file to export')
                    try:
                        shutil.copy(ch_path('~/' + username + '/items/' + list_names[selection]), location)
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
        location = browser(mode = 'open', type = 'f', message = 'Select a file to import')
        try:
            shutil.copy(location, ch_path('~/' + username + '/items/'))
        except:
            log_error()
            s_out('Something went wrong.')
            wait(1.5)
        else:
            s_out('Your item is imported!')
            wait(1.5)

    if choice == 'l':
        # check number of items
        if len(list_names) > 0:
            # ask user input
            number = s_inp('Type the number to learn   > ')
            # check input is a number
            if number.isdigit():
                # check item exist
                if 0 < int(number) <= len(list_names):
                    if (selection) not in errors:
                        # learn item
                        learn_all(username, list_names[selection], settings)
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
'''

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
            s_out('Maximum number of often wrong answered words in a learn session: ' + str(settings[27]) + ' --> wa')
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
            if settings[15] == -1: s_out('don\'t sort', end = '')
            elif settings[15] == 0: s_out('name', end = '')
            elif settings[15] == 1: s_out('last modified', end = '')
            elif settings[15] == 2: s_out('size', end = '')
            elif settings[15] == 3: s_out('number of words', end = '')
            elif settings[15] == 4: s_out('warnings/errors', end = '')
            elif settings[15] == 5: s_out('info', end = '')
            elif settings[15] == 6: s_out('learn process', end = '')
            else: s_out('\x1b[1;49;31mERROR\x1b[0m', end = '')

            if settings[28]: s_out(', reserved', end = '')

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

            if settings[29]: s_out(', reversed', end = '')
            s_out(' --> si')

            s_out()

            # save and quit
            s_out('\x1b[1;49;34mSave and quit\x1b[0m')
            s_out('Save --> s')
            s_out('Quit --> q')
            s_out('Load settings --> l')
            s_out('Reset to default --> r')

            # lijst met opties voor de gebruiker
            options = ['lb', 'sa', 'ss', 'lm', 'g1', 'g2', 'md', 'nn', 'no', 'nw', 'al', 'ar', 'rl', 'rr', 'om', 'ws', 'am', 'as', 'cs', 'ps', 'acs', 'sps', 'aps', 'st', 'ii', 'si', 'ns', 'wa', 's', 'q', 'l', 'r']
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
                while True:
                    value = s_inp('Show legend bar in the learn menu (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[25] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # show the good answer by learn
            if choice == 'al':
                cls()
                while True:
                    value = s_inp('Show good answer by a mistake in learn (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[1] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # show the good answer by review
            if choice == 'ar':
                cls()
                while True:
                    value = s_inp('Show good answer by a mistake in review (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[2] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # repeat hard words
            if choice == 'md':
                number = -1
                while number < 0 or number > 3:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 0 and 3.')
                    value = s_inp('Maximum number of difficult words in a learn session (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[3] = int(number)

            # repeat not often had words
            if choice == 'nn':
                number = -1
                while number < 0 or number > 3:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 0 and 3.')
                    value = s_inp('Maximum number of not often had words in a learn session (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[4] = int(number)

            # delete easy words
            if choice == 'no':
                number = -1
                while number < 0 or number > 3:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 0 and 3.')
                    value = s_inp('Maximum number of often had words to delete out a learn session (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[5] = int(number)

            # repeat words with mistakes by learn
            if choice == 'rl':
                cls()
                while True:
                    value = s_inp('Repeat words with mistakes by learn (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[6] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # repeat words with mistakes by review
            if choice == 'rr':
                cls()
                while True:
                    value = s_inp('Repeat words with mistakes by review (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[7] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # number of words to be showed in a multiple-choice question
            if choice == 'om':
                number = -1
                while number < 3 or number > 9:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 3 and 9.')
                    value = s_inp('Type the number of words in a multiple-choice question (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[8] = int(number)

            # minimum number of words by a sentence question
            if choice == 'ws':
                number = -1
                while number < 3 or number > 6:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 3 and 6.')
                    value = s_inp('Type the minimum number of words in a sentence question (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[9] = int(number)

            # case sensitivity
            if choice == 'cs':
                cls()
                while True:
                    value = s_inp('Case sensitivity (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[10] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # punctuation sensitivity
            if choice == 'ps':
                cls()
                while True:
                    value = s_inp('Punctuation sensitivity (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[11] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # accent sensitivity
            if choice == 'acs':
                cls()
                while True:
                    value = s_inp('Accent sensitivity (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[12] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # space sensitivity
            if choice == 'sps':
                cls()
                while True:
                    value = s_inp('Space sensitivity (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[13] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # number of words when you learn new words
            if choice == 'nw':
                number = -1
                while number < 1 or number > 10:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 1 and 10.')
                    value = s_inp('Type the maximum number of words in niveau 1 when a new word will be added. (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[14] = int(number)

            # number of often wrong answered words in a learn session
            if choice == 'wa':
                number = -1
                while number < 0 or number > 3:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 0 and 4.')
                    value = s_inp('Type the maximum number of often wrong answered words in a learn session. (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[27] = int(number)

            # way of sort
            if choice == 'st':
                options = ['d', 'D', 'n', 'N', 'm', 'M', 's', 'S', 'w', 'W', 'i', 'I', 'l', 'L']
                while True:
                    cls()
                    s_out('Choose the way of sort.')
                    s_out('Don\'t sort --> d')
                    s_out('Name --> n')
                    s_out('Last modified --> m')
                    s_out('Size --> s')
                    s_out('Warnings/errors --> w')
                    s_out('Info --> i')
                    s_out('Learn process --> l')
                    s_out('Type uppercase for reversed sorting.')
                    sorting = s_inp('   > ')

                    if sorting in options:
                        break

                    s_out('\x1b[1;49;31mThat isn\'t a option!\x1b[0m')
                    wait(1.5)
                    continue

                if sorting == 'd' or sorting == 'D':
                    settings[15] = -1
                if sorting == 'n' or sorting == 'N':
                    settings[15] = 0
                if sorting == 'm' or sorting == 'M':
                    settings[15] = 1
                if sorting == 's' or sorting == 'S':
                    settings[15] = 2
                if sorting == 'w' or sorting == 'W':
                    settings[15] = 3
                if sorting == 'i' or sorting == 'I':
                    settings[15] = 4
                if sorting == 'l' or sorting == 'L':
                    settings[15] = 5

                if sorting.isupper():
                    settings[28] = True
                else:
                    settings[28] = False

            # way of sort between words
            if choice == 'si':
                options = ['d', 'D', 'k', 'K', 'u', 'U', 'n', 'N', 'c', 'C', 'm', 'M', 'h', 'H']
                while True:
                    cls()
                    s_out('Choose the way of sort between words.')
                    s_out('Don\'t sort --> d')
                    s_out('Known word --> k')
                    s_out('Unknown word --> u')
                    s_out('Niveau --> n')
                    s_out('Times in a row correct --> c')
                    s_out('Mistakes --> m')
                    s_out('Times had --> h')
                    sorting = s_inp('   > ')

                    if sorting in options:
                        break

                    s_out('\x1b[1;49;31mThat isn\'t a option!\x1b[0m')
                    wait(1.5)
                    continue

                if sorting == 'd' or sorting == 'D':
                    settings[23] = -1
                if sorting == 'n' or sorting == 'N':
                    settings[23] = 0
                if sorting == 'm' or sorting == 'M':
                    settings[23] = 1
                if sorting == 's' or sorting == 'S':
                    settings[23] = 2
                if sorting == 'w' or sorting == 'W':
                    settings[23] = 3
                if sorting == 'i' or sorting == 'I':
                    settings[23] = 4
                if sorting == 'l' or sorting == 'L':
                    settings[23] = 5

                if sorting.isupper():
                    settings[29] = True
                else:
                    settings[29] = False

            # go from niveau 1 to niveau 2
            if choice == 'g1':
                number = -1
                while number < 1 or number > 7:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 1 and 7.')
                    value = s_inp('Number of times in a row correct to go from niveau 1 to niveau 2 (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[16] = int(number)

            # het aantal keer dat je een woord achter elkaar goed moet hebben om het van niveau 2 naar niveau 3 te laten gaan
            if choice == 'g2':
                number = -1
                while number < 2 or number > 9:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 2 and 9.')
                    value = s_inp('Number of times in a row correct to go from niveau 2 to niveau 3 (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[17] = int(number)

            # automatically synchronize
            if choice == 'sa':
                cls()
                while True:
                    value = s_inp('Synchronize automatically the items by startup (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[18] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            if choice == 'am':
                cls()
                s_out('Choose the way to answer multiple-choice questions:')
                s_out('Type numbers or select answer --> 0')
                s_out('Type numbers or word --> 1')
                while True:
                    value = s_inp('   > ')
                    if value in ['0', '1']:
                        settings[19] = value == '0'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            if choice == 'as':
                cls()
                s_out('Choose the way to answer sentence questions:')
                s_out('Type numbers or select word --> 0')
                s_out('Type numbers, sentence or word --> 1')
                while True:
                    value = s_inp('   > ')
                    if value in ['0', '1']:
                        settings[20] = value == '0'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            if choice == 'ss':
                cls()
                while True:
                    value = s_inp('Low search sensitivity (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[21] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

            # apostrophe sensitivity
            if choice == 'aps':
                cls()
                while True:
                    value = s_inp('Apostrophe sensitivity (y/n)   > ')
                    if value in ['y', 'n']:
                        settings[22] = value == 'y'
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')

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
                number = -1
                while number < 1 or number > 9:
                    cls()
                    if number != -1:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m Choose a value between 1 and 9.')
                    value = s_inp('Number of new words when you start with learn (number)   > ')
                    if value.isdigit():
                        number = int(value)
                    else:
                        s_out('\x1b[1;49;31mThat can\'t!\x1b[0m')
                        number = -1
                settings[25] = int(number)

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
            choice = s_inp('Do you want to save? (y/n/cancel) [cancel]   > ')
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

'''

def main():
    name, userinfo = login()
    try:
        main_menu(name, userinfo)
    except SystemExit:
        exit()
    except Exception as error:
        log_error()
        s_out('Something went wrong.')
    logout(username, userinfo)

    while True:
        cls()
        # list with options
        options = ['l', 'h', 'u', 'c', 'b', 's', 'q', 'd', 'o', 'U']

        # show options
        s_out('What do you want to do?')
        s_out('Learn --> l')
        s_out('Help menu --> h')
        s_out('See userinfo --> u')
        s_out('Change username --> c')
        s_out('Backup menu --> b')
        s_out('Quit --> s/q')
        s_out('Delete userenvironment --> d')
        s_out('Log out --> o')
        s_out('Update --> U')

        # ask user to do something
        try:
            choice = s_inp('   > ')
    
            if choice not in options:
                # if the input isn't correctly, ask again
                cls()
                s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                wait(1)
                continue
    
            if choice == 'l':
                # learn
                learn_menu(name)
                
            if choice == 'h':
                # help menu
                help()
    
            if choice == 'u':
                cls()
                time_created = str(datetime.datetime.fromtimestamp(userinfo[0]))
                time_created = time_created[:time_created.find('.')]
                s_out('     Time created: ' + str(time_created))
                time_changed = str(datetime.datetime.fromtimestamp(userinfo[1]))
                time_changed = time_changed[:time_changed.find('.')]
                s_out('Last time learned: ' + str(time_changed))
                s_out('     Time learned: ' + ch_time(userinfo[2] + (time() - userinfo[3]))[0])
                s_out()
                s_inp('Press enter to continue. ')

            if choice == 'c':
                cls()
                s_out('Current username: ' + name)
                new_name = s_inp('Type the new username.   > ', input = name, mode = 'file')
                shutil.move(ch_path('~/' + name), ch_path('~/' + new_name))
                name = new_name

            if choice == 'b':
                try:
                    backup_menu(name)
                except KeyboardInterrupt:
                    continue
    
            if choice == 's' or choice == 'q':
                logout(username, userinfo)
                exit()
    
            if choice == 'd':
                try:
                    if s_inp('Are you sure to delete your account? It can\'t be undone. (y/n)   >  ') == 'y':
                        delete(name)
                        login()
                except KeyboardInterrupt:
                    continue

            if choice == 'o':
                logout(username, userinfo)
                login()

            if choice == 'U':
                logout(username, userinfo)
                update(<path_to_info>)
                exit()

        except (KeyboardInterrupt, ClosedTerminalError, ProcessKilledError):
            s_out()
            exit()

'''

def backup_menu(username):
    while True:
        cls()
        backups = os.listdir(ch_path('~/' + username + '/backups/'))
        options = ['c', 'i', 'q']
        # show options
        s_out('What do you want to do?')
        s_out('Create backup --> c')
        if len(backups) > 0:
            s_out('Restore from backup --> r')
            options.append('r')
            s_out('Delete backup --> d')
            options.append('d')
            s_out('Delete all backups --> D')
            options.append('D')
            s_out('Export backup --> e')
            options.append('e')
        s_out('Import backup --> i')
        s_out('Quit --> q')
    
        # ask user
        choice = s_inp('   > ')

        if choice not in options:
            cls()
            s_out('That isn\'t a option!!!')
            wait(1.5)
            continue

        if choice == 'c':
            create_backup(username)
            s_out('Succesvol created!')
            wait(1.5)

        if choice == 'r':
            filename = user_choice_items(backups)
            restore_backup(username, filename)
            s_inp('Backup restored! Press enter to continue. ')

        if choice == 'd':
            filename = user_choice_items(backups)
            remove_backup(username, filename)

        if choice == 'D':
            remove_all_backups(username)

        if choice == 'e':
            filename = user_choice_items(backups)
            print('Select a directory to export the backup.')
            s_inp('Press enter to do it! ')
            location = browser(filename = filename, mode = 'create', type = 'f', message = 'Export to a file')
            try:
                shutil.copy(ch_path('~/' + username + '/backups/' + filename), os.path.expanduser('~') if len(location) == 0 else location)
            except Exception as error:
                log_error()
                print('Error by exporting: ')
                print(error)
                s_inp('Press enter to continue. ')
                continue

        if choice == 'i':
            print('Select a file to import.')
            s_inp('Press enter to do it! ')
            location = browser(mode = 'open', type = 'f', message = 'Import backup file')
            try:
                shutil.copy(location, ch_path('~/' + username + '/backups/'))
            except Exception as error:
                log_error()
                print('Error by importing: ')
                print(error)
                s_inp('Press enter to continue. ')
                continue

        if choice == 'q':
            return ''

