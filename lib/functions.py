# import modules
from time import sleep as wait, time
import math
import os
import datetime
import math

from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out, cls

from manage_files import get_list, ch_path, overwrite
from errors import WordIndexError, NotInListError, log_error

# set functions
# warn the user for some situations
def warn(list_words):
    # create lists
    words0 = []
    words = []
    same_words = []
    same_words0 = []
    wordindexerror = []
    typeerror = []
    invalid_info = []
    # repeat for each word
    for number in range(len(list_words)):
        word = list_words[number]
        # every word must have 6 items
        if len(word) < 6:
            wordindexerror.append(number)
            continue

        # the first 2 items must be string, the last 4 must be interger
        if not (type(word[0]) == type(word[1]) == str and type(word[2]) == type(word[3]) == type(word[4]) == type(word[5]) == int):
            typeerror.append(number)
            continue

        # warn for 2 the same words
        if [word[0], word[1]] in words:
            for wordnumber in range(len(list_words)):
                word2 = list_words[wordnumber]
                if word[0] == word2[0] and word[1] == word2[1]:
                    same_words.append(wordnumber)

        # warn for 2 the same questions (a = 1 & a = 2 --> question: a = ?, you don't know the answer (1 or 2))
        if word[0] in words0:
            for wordnumber in range(len(list_words)):
                word2 = list_words[wordnumber]
                if word[0] == word2[0]:
                    same_words0.append(wordnumber)

        # niveau 3 is the highest niveau
        if word[2] > 3:
            invalid_info.append(number)
        # times in a row good, mistakes and times had can't be under 0
        if word[3] < 0:
            invalid_info.append(number)
        if word[4] < 0:
            invalid_info.append(number)
        if word[5] < 0:
            invalid_info.append(number)

        # update lists
        words.append([word[0], word[1]])
        words0.append(word[0])

    # count warnings to 1 list
    warnings = []
    for warned_list in same_words, same_words0, wordindexerror, typeerror, invalid_info:
        for number in warned_list:
            if number not in warnings:
                warnings.append(number)

    # return all warnings
    return warnings

# returns if there are warnings
def is_warned(list_words):
    warnings = warn(list_words)
    return len(warnings) > 0

# shows the mistake with extra info
def show_mistake(user_answer, good_answer, list_words = []):
    colored_answer_user = ''
    colored_answer_good = ''

    for number in range(max(len(user_answer), len(good_answer))):
        if len(good_answer) <= number:
            colored_answer_good = colored_answer_good + '\x1b[1;49;33m—\x1b[0m'
            colored_answer_user = colored_answer_user + '\x1b[1;49;33m' + user_answer[number] + '\x1b[0m'
        elif len(user_answer) <= number:
            colored_answer_user = colored_answer_user + '\x1b[1;49;33m—\x1b[0m'
            colored_answer_good = colored_answer_good + good_answer[number]
        elif user_answer[number] == good_answer[number]:
            colored_answer_user = colored_answer_user + user_answer[number]
            colored_answer_good = colored_answer_good + good_answer[number]
        else:
            colored_answer_user = colored_answer_user + '\x1b[1;49;31m' + user_answer[number] + '\x1b[0m'
            colored_answer_good = colored_answer_good + good_answer[number]

    s_out('Your answer: ' + colored_answer_user)
    s_out('Good answer: ' + colored_answer_good)

    for word in list_words:
        if word[1] != word[0] == user_answer and word[1] == good_answer:
            s_out('You have answered the given word, not the unknown word.')
        if word[1] == user_answer:
            s_out('You have answered the answer of word \'\x1b[0;49;4m' + word[0] + '\x1b[0m\'.')

# sort list with lists
def sort(list_items, sorteernummer = 0):
    relevant_items = []
    for listitem in list_items:
        if listitem[sorteernummer] not in relevant_items:
            relevant_items.append(listitem[sorteernummer])

    relevant_items.sort()
    sorted_list = []
    for item in relevant_items:
        for listitem in list_items:
            if listitem[sorteernummer] == item:
                sorted_list.append(listitem)

    return sorted_list.copy()

# change size (change a long number of bytes to a rounded number of kilo, mega, giga or terra bytes of 5 characters)
def ch_size(size):
    exponent = 0
    while size >= 9999:
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

def user_choice_items(items):
    max_number_size = len(str(len(items)))
    while True:
        cls()
        for number in range(len(items)):
            s_out(str(number + 1) + ': ', end = '')
            s_out(' ' * (max_number_size - (len(str(number + 1)))), end = '')
            s_out(items[number])
        s_out()
        choice = s_inp('Type the number of the item.   > ')
        if choice.isdigit():
            if 0 < int(choice) <= len(items):
                return items[int(choice) - 1]
            else:
                s_out('That can\'t. Not a valid number.')
                wait(1.5)
        else:
            s_out('That can\'t. Not a number.')
            wait(1.5)

def show_item_settings(username, filename, settings):
    item_settings = get_list(username, 'item_settings')
    for item_setting in item_settings:
        if item_setting[0] == filename:
            if item_setting[1] != 0:
                s_out('Learn-at-time time between learning: ' + str(item_setting[1]) + ' seconds')
                if ((item_setting[2] - time()) + item_setting[1]) > 0:
                    s_out('Time between now and when you must learn: ' + str((item_setting[2] - time()) + item_setting[1]))
                else:
                    s_out('Time between now and when you must learn: \x1b[1;49;33mnow\x1b[0m')
                s_out('Last time learned: ' + str(datetime.datetime.fromtimestamp(item_setting[2])) + ' (' + str(item_setting[2]) + ')')
            if item_setting[3] != 0:
                s_out('Learn-at-time target: ' + str(item_setting[3]) + str(item_setting[4]))
            if len(item_setting[5]) != 0:
                s_out('Changed learn method: ' + str(item_setting[5]))

def ch_time(seconds):
    count = 0

    list_strings = ['s', 'm', 'h', 'd', 'y']

    years = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = round(seconds)

    if seconds >= 60:
        minutes = math.floor(seconds / 60)
        seconds = seconds % 60
        count = 1

    if minutes >= 60:
        hours = math.floor(minutes / 60)
        minutes = minutes % 60
        count = 2

    if hours >= 24:
        days = math.floor(hours / 24)
        hours = hours % 24
        count = 3

    if days >= 365.25:
        years = math.floor(days / 365.25)
        days = days % 365.25
        count = 4

    list_time = [seconds, minutes, hours, days, years]

    return str(list_time[count]) + list_strings[count], list_time, count

def get_list_index(list_with_lists, string, search_number = 0):
    for number in range(len(list_with_lists)):
        if list_with_lists[number][search_number] == string:
            return number

    raise NotInListError

def show_target_info(item_settings, start_info):
    reached_target = False
    if item_settings[3] != 0:
        # check reached target
        mode = item_settings[4]
        if (item_settings[3] - item_settings[6][0]) <= 0 and mode == 'w':
            s_out('\x1b[1;49;32mYou have reached your target!\x1b[0m')
        elif mode == 'w':
            s_out('You must learn ' + str(item_settings[3] - item_settings[6][0]) + ' words to reach your target.')
        if (item_settings[3] - item_settings[6][1]) <= 0 and mode == 's':
            s_out('\x1b[1;49;32mYou have reached your target!\x1b[0m')
        elif mode == 's':
            s_out('You must learn ' + str(item_settings[3] - item_settings[6][1]) + ' sessions to reach your target.')
        if (item_settings[3] - item_settings[6][2]) <= 0 and mode == '%':
            s_out('\x1b[1;49;32mYou have reached your target!\x1b[0m')
        elif mode == '%':
            s_out('You must learn ' + str(round(item_settings[3] - item_settings[6][2])) + ' procent to reach your target.')

        s_out()

        # show process after the last time the user has reached his target
        s_out('You have learned ' + str(item_settings[6][0]) + ' words after the last time you have reached your target.')
        s_out('You have learned ' + str(item_settings[6][1]) + ' sessions after the last time you have reached your target.')
        s_out('You have learned ' + str(round(item_settings[6][2])) + ' procent after the last time you have reached your target.')
        reached_target = True

    s_out()

    s_out('You have learned ' + str(item_settings[6][0] - start_info[0]) + ' words this time.')
    s_out('You have learned ' + str(item_settings[6][1] - start_info[1]) + ' sessions this time.')
    s_out('You have learned ' + str(round(item_settings[6][2] - start_info[2])) + ' procent this time.')

    return reached_target

def get_total_size(rootdir):
    size = os.path.getsize(rootdir)
    for root, dirs, files in os.walk(rootdir):
        for dir in dirs:
            size = size + (os.stat(os.path.join(root, dir)).st_blocks * 512)
        for file in files:
            size = size + (os.stat(os.path.join(root, file)).st_blocks * 512)
    return size

def get_user_size(user):
    return get_total_size(ch_path('~/' + user))

# get scores of a item
def get_scores(list_words, settings = []):
    if len(settings) == 0:
        advenched = False
    else:
        advenched = True
    
    # set variables
    default_points = 0
    advenched_points = 0
    max_default_points = len(list_words)
    max_advenched_points = len(list_words)

    for number in range(len(list_words)):
        try:
            if list_words[number][2] == 0:
                if list_words[number][3] == 1:
                    default_points = default_points + (1 / 6)
                if list_words[number][3] > 1:
                    default_points = default_points + (1 / 3)
                    advenched_points = advenched_points + (1 / 3)

            if list_words[number][2] == 1:
                if list_words[number][3] <= settings[16] and advenched:
                    default_points = default_points + (((list_words[number][3] / settings[16]) + 1) / 3)
                else:
                    default_points = default_points + (1 / 3)

                advenched_points = advenched_points + (1 / 3)

            if list_words[number][2] == 2:
                if list_words[number][3] <= settings[17] and advenched:
                    default_points = default_points + (((list_words[number][3] / settings[17]) + 2) / 3)
                else:
                    default_points = default_points + (2 / 3)

                advenched_points = advenched_points + (2 / 3)

            if list_words[number][2] == 3:
                default_points = default_points + 1
                advenched_points = advenched_points + 1

            if advenched:
                if (list_words[number][4] * 4) > list_words[number][5] and list_words[number][2] < 3 and settings[3] > 0 and list_words[number][3] < 3:
                    max_default_points = max_default_points + 1

        except IndexError:
            raise WordIndexError

    try:
        score = default_points / max_default_points * 100
    except ZeroDivisionError:
        score = 0

    return score, default_points, max_default_points, len(list_words), advenched_points, max_advenched_points

# get the score that comes on screen
def get_procent(score, default_points, max_default_points, number_words, advenched_points, max_advenched_points):
    if number_words > 0:
        if default_points == max_default_points:
            procent = '\x1b[1;49;32mLearned!!!\x1b[0m'
        elif default_points == 0:
            procent = '-'
        else:
            procent = str(round(score)) + '%' + ' (' + str(round(advenched_points * 3)) + '/' + str(round(max_advenched_points * 3)) + ')'

    else:
        procent = '\x1b[1;49;33mNo score.\x1b[0m'

    return procent

# show the learn process
def show_learn_process(list_words, settings):
    # set variables
    number_niveau_0 = 0
    number_niveau_1 = 0
    number_niveau_2 = 0
    number_niveau_3 = 0
    number_difficult = 0
    minimum_had = 20
    number_minimum_had = 0
    maximum_had = 0
    number_maximum_had = 0
    minimum_mistakes = 20
    number_minimum_mistakes = 0
    maximum_mistakes = 0
    number_maximum_mistakes = 0
    minimum_in_a_row_good = 0
    number_minimum_in_a_row_good = 0
    maximum_in_a_row_good = 0
    number_maximum_in_a_row_good = 0

    for i in list_words:
        if i[2] == 0:
            number_niveau_0 = number_niveau_0 + 1

        if i[2] == 1:
            number_niveau_1 = number_niveau_1 + 1

        if i[2] == 2:
            number_niveau_2 = number_niveau_2 + 1

        if i[2] == 3:
            number_niveau_3 = number_niveau_3 + 1

        if (i[4] * 4) > i[5] and i[3] < 3 and settings[3] > 0 and i[2] != 3:
            number_difficult = number_difficult + 1

        if i[5] < minimum_had:
            minimum_had = i[5]
            number_minimum_had = 1
    
        if i[5] == minimum_had:
            number_minimum_had = number_minimum_had + 1

        if i[5] > maximum_had:
            maximum_had = i[5]
            number_maximum_had = 1

        if i[5] == maximum_had:
            number_maximum_had = number_maximum_had + 1

        if i[4] < minimum_mistakes:
            minimum_mistakes = i[4]
            number_minimum_mistakes = 1

        if i[4] == minimum_mistakes:
            number_minimum_mistakes = number_minimum_mistakes + 1

        if i[4] > maximum_mistakes:
            maximum_mistakes = i[4]
            number_maximum_mistakes = 1

        if i[4] == maximum_mistakes:
            number_maximum_mistakes = number_maximum_mistakes + 1

        if i[3] < minimum_in_a_row_good:
            minimum_in_a_row_good = i[3]
            number_minimum_in_a_row_good = 1

        if i[3] == minimum_in_a_row_good:
            number_minimum_in_a_row_good = number_minimum_in_a_row_good + 1

        if i[3] > maximum_in_a_row_good:
            maximum_in_a_row_good = i[3]
            number_maximum_in_a_row_good = 1

        if i[3] == maximum_in_a_row_good:
            number_maximum_in_a_row_good = number_maximum_in_a_row_good + 1

    scores = get_scores(list_words, settings)
    procent, default_points, max_default_points = scores[0], scores[4], scores[5]

    # show stats
    s_out('Minimum times had: \x1b[1;49;33m' + str(minimum_had) + '\x1b[0m')
    s_out('Maximum times had: \x1b[1;49;32m' + str(maximum_had) + '\x1b[0m')
    s_out('Number of words that you \x1b[1;49;33m' + str(minimum_had) + '\x1b[0m times had: \x1b[1;49;33m' + str(number_minimum_had) + '\x1b[0m')
    if minimum_had != maximum_had: s_out('Number of words that you \x1b[1;49;32m' + str(maximum_had) + '\x1b[0m times had: \x1b[1;49;32m' + str(number_maximum_had) + '\x1b[0m')
    s_out()
    s_out('Minimum times in a row good: \x1b[1;49;31m' + str(minimum_in_a_row_good) + '\x1b[0m')
    s_out('Maximum times in a row good: \x1b[1;49;32m' + str(maximum_in_a_row_good) + '\x1b[0m')
    if minimum_in_a_row_good != maximum_in_a_row_good: s_out('Number of words that you \x1b[1;49;31m' + str(minimum_in_a_row_good) + '\x1b[0m times in a row good: \x1b[1;49;31m' + str(number_minimum_in_a_row_good) + '\x1b[0m')
    s_out('Number of words that you have \x1b[1;49;32m' + str(maximum_in_a_row_good) + '\x1b[0m times in a row good: \x1b[1;49;32m' + str(number_maximum_in_a_row_good) + '\x1b[0m')
    s_out()
    s_out('Least mistakes: \x1b[1;49;32m' + str(minimum_mistakes) + '\x1b[0m')
    s_out(' Most mistakes: \x1b[1;49;31m' + str(maximum_mistakes) + '\x1b[0m')
    s_out('Number of words where you have \x1b[1;49;32m' + str(minimum_mistakes) + '\x1b[0m mistakes: \x1b[1;49;32m' + str(number_minimum_mistakes) + '\x1b[0m')
    if minimum_mistakes != maximum_mistakes: s_out('Aantal woorden die je \x1b[1;49;31m' + str(maximum_mistakes) + '\x1b[0m keer fout hebt beantwoord: \x1b[1;49;31m' + str(number_maximum_mistakes) + '\x1b[0m')
    s_out()
    if settings[3] > 0: s_out('    Difficult: \x1b[1;49;31m' + str(number_difficult) + '\x1b[0m')
    s_out('      Unknown: \x1b[1;49;33m' + str(number_niveau_0) + '\x1b[0m')
    s_out('       Viewed: \x1b[1;49;33m' + str(number_niveau_1) + '\x1b[0m')
    s_out('A bit learned: \x1b[1;49;33m' + str(number_niveau_2) + '\x1b[0m')
    s_out('      Learned: \x1b[1;49;32m' + str(number_niveau_3) + '\x1b[0m')
    s_out()
    s_out((('You\'re now on ' + str(round(procent)) + '% with learn.') if procent < 100 else ('\x1b[1;49;32mLearned!\x1b[0m')) + ' (' + str(round(default_points * 3)) + '/' + str(round(max_default_points * 3)) + ')')
    return procent

# synchronize
def synchronize(name, settings):
    default_settings = [0, 0, 0, 'w', [], [0, 0, 0, 0]]
    # get names
    list_names = os.listdir(ch_path('~/' + name + '/items'))
    item_settings = get_list(name, 'item_settings')
    if settings[15] == 1: list_names.sort()
    list_scores = []
    list_warnings = []
    error = False
    for i in range(len(list_names)):
        # show process
        s_out('\r' + str(i + 1) + '/' + str(len(list_names)), end = '')
        # get words
        try:
            list_words = get_list(name, 'items/' + list_names[i])
        except:
            log_error()
            s_out('\rError in item \'' + list_names[i] + '\' (' + str(i + 1) + ').')
            error = True
            continue

        # get number of words
        number_words = len(list_words)

        # get score
        try:
            score = get_procent(*get_scores(list_words, settings))
        except WordIndexError:
            s_out('\rInvalid wordindex in item \'' + list_names[i] + '\', word \'' + str(i + 1) + '\'.')
            list_warnings.append(list_names[i])
            error = True
            continue

        # add score to list
        list_scores.append([list_names[i], number_words, score])

        # get warnings
        if is_warned(list_words):
            # add warnings to list
            list_warnings.append(list_names[i])

        exist = False
        for item_setting in item_settings:
            try:
                if item_setting[0] == list_names[i]:
                    exist = True
                if item_setting[0] not in list_names:
                    item_settings.remove(item_setting)
                elif len(item_setting) < 7:
                    item_settings[item_settings.index(item_setting)] = [item_settings[item_settings.index(item_setting)][0]] + default_settings
                    item_settings[item_settings.index(item_setting)][6][3] = get_scores(list_words, settings)[0]
            except Exception as error_is:
                log_error()
                print(error_is)
                error = True

        if not exist:
            item_settings.append([list_names[i]] + default_settings)
            item_settings[-1][6][3] = get_scores(list_words, settings)[0]
    
    # write to disk
    overwrite(name, list_scores, 'list_items')
    overwrite(name, list_warnings, 'warned_items')
    overwrite(name, item_settings, 'item_settings')
    s_out()
    if error:
        s_inp('Press enter to continue. ')

# check answer
def check_answer(good_answer, answer, settings):
    if not settings[10]:
        good_answer = lower(good_answer)
        answer = lower(answer)
    if not settings[11]:
        good_answer = no_punctuation_marks(good_answer)
        answer = no_punctuation_marks(answer)
    if not settings[12]:
        good_answer = no_accents(good_answer)
        answer = no_accents(answer)
    if not settings[13]:
        good_answer = no_spaces(good_answer)
        answer = no_spaces(answer)
    if not settings[22]:
        good_answer = ch_simular_characters(good_answer)
        answer = ch_simular_characters(answer)

    return good_answer == answer

# select text
def select(txt, woord):
    if '\x1b' in txt:
        return txt
    if len(woord) > 0:
        return txt.replace(woord, '\x1b[7m' + woord + '\x1b[0m')
    else:
        return txt

# set text to lower
def lower(string):
    string = string.lower()
    return string

# delete all punctuation marks
def no_punctuation_marks(string):
    punctuation_marks = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ',', '.', '/', '?', '[', ']', '\\', '|', '{', '}', '-', '=', '_', '+', '\'', '\"', '`', '´']
    for punctuation_mark in punctuation_marks:
        string = string.replace(punctuation_mark, '')
    return string

# change accents to default letters
def no_accents(string):
    accents = [['é', 'e'], ['è', 'e'], ['ê', 'e'], ['ẽ', 'e'], ['ú', 'u'], ['ù', 'u'], ['û', 'u'], ['ũ', 'u'], ['ë', 'e'], ['ü', 'u'], ['ñ', 'n'], ['ó', 'o'], ['ò', 'o'], ['ö', 'o'], ['ô', 'o'], ['õ', 'o'], ['á', 'a'], ['ä', 'a'], ['à', 'a'], ['â', 'a'], ['ã', 'a'], ['í', 'i'], ['ì', 'i'], ['ï', 'i'], ['î', 'i'], ['ĩ', 'i']]
    for accent in accents:
        string = string.replace(accent[0], accent[1])
    return string

# delete all spaces
def no_spaces(string):
    return string.replace(' ', '')

# change simular characters
def ch_simular_characters(string):
    return string.replace('´', '\'').replace('`', '\'').replace('’', '\'').replace('‘', '\'').replace('¨', '"').replace('…', '...').replace('¸', ',')

