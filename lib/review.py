# import modules
import os
import datetime
from random import randint, choice as choice_item
from time import sleep as wait

from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out, cls

from manage_files import create_file, delete_file, ch_path, get_list, overwrite, delete_all
from questions import type_ex, multiple_choise, sentence
from learn import learn
from functions import sort
from errors import ClosedTerminalError, ProcessKilledError

# set functions
# review
def review(list_words, username, settings):
    while True:
        cls()
        # show options
        s_out('What kind of questions do you want?')
        s_out('Type questions --> t')
        s_out('Multiple-choise questions --> m')
        s_out('Sentence (or type) questions --> s')
        s_out('Random --> r')
        s_out('Cancel --> c')
        # ask user
        keuze = s_inp('   > ')
    
        if keuze == 't':
            type_question = 'type'
            break
        elif keuze == 'm':
            type_question = 'multiple choice'
            break
        elif keuze == 's':
            type_question = 'sentence'
            break
        elif keuze == 'r':
            type_question = 'random'
            break
        elif keuze == 'c':
            return ''
        else:
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue

    output = review_words(list_words, settings, username, type_question)

    if len(output[0]) > 0 and output[1] != 'home':
        if output[1] == 'new list':
            # save difficult words as new item
            save_as_new_list(output, username, settings)
        
        if output[1] == 'learn':
            # save difficult words and learn them
            save_and_learn(output, username, settings)

        if output[1] == 'review':
            # re-review the difficult words
            rereview(output, username, settings)

        if output[1] == 'new list and review':
            # save difficult words and re-review them
            save_and_review(output, username, settings)

    # if there are no difficult words
    elif len(output[0]) == 0 and output[1] != 'home':
        s_out('There are none difficult words.')
        wait(1.5)

    # something went wrong
    elif output[1] != 'home':
        s_out('Something went wrong.')
        wait(1.5)
        
    return ''

# review words
def review_words(list_words, settings, username, type, difficult_words = [], times_wrong = 0, times_good = 0, number_words_had = 0, total_number_of_words = -1, times_in_a_row_good = 0, all_words = -1):
    if total_number_of_words == -1:
        total_number_of_words = len(list_words)
    if all_words == -1:
        all_words = list_words.copy()
    stopped = False
    while len(list_words) > 0:
        number_words_had = number_words_had + 1

        # choice word
        rnd = randint(0, len(list_words) - 1)
        word = list_words[rnd]

        cls()
        # show stats
        info = str(number_words_had) + '/' + str(total_number_of_words) + ' (' + str(round(((number_words_had - 1) / total_number_of_words) * 100)) + '%)    \x1b[1;49;32mGood: ' + str(times_good) + '\x1b[0m    \x1b[1;49;31mMistakes: ' + str(times_wrong) + '\x1b[0m    Current score: ' + (str(round(((times_good / (number_words_had - 1)) * 9) + 1, 2)) if number_words_had > 1 else '-') + '    In a row good: ' + str(times_in_a_row_good) + '    Type ctrl + c to quit.\n'

        # get type question
        type_question = type if type != 'random' else choice_item(['type', 'multiple choice', 'sentence'])
        
        try:
            # ask question
            if type_question == 'multiple choice':
                words_multiple_choise = [word]

                # find alternative answers
                count = 0
                while len(words_multiple_choise) < settings[8] and count < (len(all_words) * 100):
                    woord_meerkeuze = all_words[randint(0, len(all_words) - 1)]
                    if woord_meerkeuze not in words_multiple_choise:
                        words_multiple_choise.append(woord_meerkeuze)
                    count = count + 1

                # ask question
                output = multiple_choise(words_multiple_choise, settings, 'review', info, list_words)

            elif type_question == 'type':
                s_out(info)
                output = type_ex(word, settings, 'review', list_words)

            elif type_question == 'sentence':
                if word[1].count(' ') > (settings[9] - 2):
                    output = sentence(word, settings, 'review', info, list_words)
                else:
                    if type == 'random' and randint(0, 1) == 0:
                        # choice words
                        words_multiple_choise = [word]

                        count = 0
                        while len(words_multiple_choise) < settings[8] and count < (len(all_words) * 100):
                            woord_meerkeuze = all_words[randint(0, len(all_words) - 1)]
                            if woord_meerkeuze not in words_multiple_choise:
                                words_multiple_choise.append(woord_meerkeuze)
                            count = count + 1

                        # ask question
                        output = multiple_choise(words_multiple_choise, settings, 'review', info, list_words)

                    else:
                        s_out(info)
                        output = type_ex(word, settings, 'review', list_words)

            else:
                s_out('Something went wrong.')
                s_inp('Press enter to continue.')
                continue

        except KeyboardInterrupt:
            cls()
            keuze = s_inp('Do you want to save your session (y/n)   > ')
            if keuze == 'n':
                cls()
                s_out('Quitting.')
                wait(1.5)
                stopped = True
                return difficult_words, 'home'
            
            else:
                save_reviewsession(list_words, difficult_words, '\'' + type + '\'', times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words, username)
                s_out('Successful saved!!!')
                wait(1.5)
                return difficult_words, 'home'

        except ClosedTerminalError:
            save_reviewsession(list_words, difficult_words, '\'' + type + '\'', times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words, username, str(datetime.datetime.now()))
            raise ClosedTerminalError

        except ProcessKilledError:
            save_reviewsession(list_words, difficult_words, '\'' + type + '\'', times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words, username, str(datetime.datetime.now()))
            raise ProcessKilledError

        # check output
        if output[0]:
            # update stats
            times_good = times_good + 1
            times_in_a_row_good = times_in_a_row_good + 1
            del list_words[rnd]

        else:
            # update stats
            is_difficult = False
            for i in difficult_words:
                if word == i[0]:
                    i[1] = output[1]
                    is_difficult = True
            if not is_difficult: difficult_words.append([word, output[1]])
            times_wrong = times_wrong + 1
            times_in_a_row_good = 0
            if not settings[7]: del list_words[rnd]
            if settings[7]: total_number_of_words = total_number_of_words + 1

    cls()
    # show stats
    s_out('\x1b[1;49;32mGood: ' + str(times_good) + '\x1b[0m')
    s_out('\x1b[1;49;31mMistakes: ' + str(times_wrong) + '\x1b[0m')
    s_out('Grade: ' + str(round(((times_good / total_number_of_words) * 9) + 1, 2)))

    if len(difficult_words) > 0 and not stopped:
        # ask user
        show_difficult_words = s_inp('Do you want to see the difficult words? (y/n)   > ')
        options = ['y', 'n']
        while show_difficult_words not in options:
            # ask again
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            show_difficult_words = s_inp('Do you want to see the difficult words? (y/n)   > ')
        
        if show_difficult_words == 'y':
            # show difficult words
            s_out('\nDifficult words: ')
            for i in range(len(difficult_words)):
                difficult_words[i][0][2], difficult_words[i][0][3], difficult_words[i][0][4], difficult_words[i][0][5] = 0, 0, 0, 0
                s_out('Given word: ' + str(difficult_words[i][0][0]) + ((' ' * (40 - len(str(difficult_words[i][0][0])))) if len(str(difficult_words[i][0][0])) < 36 else '    '), end = '')
                s_out('\x1b[1;49;31mWrong answer: ' + str(difficult_words[i][1]) + '\x1b[0m' + ((' ' * (40 - len(str(difficult_words[i][1])))) if len(str(difficult_words[i][1])) < 36 else '    '), end = '')
                s_out('\x1b[1;49;32mGood answer: ' + str(difficult_words[i][0][1]) + '\x1b[0m')
   
            s_inp('Press enter to continue. ')
    
        # ask user
        cls()
        choice = 'q'
        options = ['q', 's', 'l', 'r', 'n']
        while True:
            if choice not in options: s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            s_out('Wat wil je doen?')
            s_out('Quit --> q')
            s_out('Save as new item --> s')
            s_out('Save and learn --> l')
            s_out('Save and review --> r')
            s_out('Review (not save) --> n')
            choice = s_inp('   > ')
            if choice in options:
                break
    
        if choice == 's':
            # save as new item
            return difficult_words, 'new list'
    
        if choice == 'l':
            # save and learn
            return difficult_words, 'learn'
    
        if choice == 'n':
            # review
            return difficult_words, 'review'
    
        if choice == 'r':
            # save and review
            return difficult_words, 'new list and review'
    
        if choice == 'q':
            # home
            return difficult_words, 'home'

    elif not stopped:
        s_out()
        s_out('You have none mistakes!!!')
        s_inp('Press enter to continue. ')
        return difficult_words, 'home'

# save a reviewsession
def save_reviewsession(list_words, difficult_words, type, times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words, username, filename = ''):
    try:
        while filename == '' or filename in os.listdir(ch_path('~/' + username + '/saved_reviewsessions/')):
            if filename in os.listdir(ch_path('~/' + username + '/saved_reviewsessions/')):
                filename = s_inp('This name already exist. Choose another name or press ctrl + c to overwrite.   > ', invalid_characters = ['/', '\\'])
            else:
                filename = s_inp('Choose the name to save this session.   > ', invalid_characters = ['/', '\\'])

        # create file
        create_file(username, 'saved_reviewsessions/' + filename)

    except KeyboardInterrupt:
        if filename == '':
            s_out('Can\'t accept no input.')
            save_reviewsession(list_words, difficult_words, type, times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words, username)
            return ''

        else:
            s_out('Overwrite.')

    # overwrite
    overwrite(username, [list_words, difficult_words, type, times_wrong, times_good, number_words_had - 1, total_number_of_words, times_in_a_row_good, all_words], 'saved_reviewsessions/' + filename)

# save difficult words
def save_as_new_list(output, username, settings, filename = ''):
    # ask name
    create = True
    if filename == '': filename = s_inp('What will be the new name?   > ')
    while filename == '' or filename in os.listdir(ch_path('~/' + username + '/items')):
        try:
            s_out('This name already exist. Choose another name.')
            filename = s_inp('What will be the new name?   > ', input = filename)
        except KeyboardInterrupt:
            create = False
            break

    # rebuilt the list
    difficult_words = []
    for i in range(len(output[0])):
        difficult_words.append(output[0][i][0])
    # create file
    if create: create_file(username, 'items/' + filename)
    # overwrite file
    if settings[23] != -1:
        difficult_words = sort(difficult_words, settings[23])
    overwrite(username, difficult_words, 'items/' + filename)

# save and learn
def save_and_learn(output, username, settings, filename = ''):
    # vragen wat de naam van de lijst met moeilijke woorden wordt
    create = True
    if filename == '': filename = s_inp('What will be the new name?   > ')
    while filename == '' or filename in os.listdir(ch_path('~/' + username + '/items')):
        try:
            s_out('This name already exist. Choose another name.')
            filename = s_inp('What will be the new name?   > ', input = filename)
        except KeyboardInterrupt:
            create = False
            break

    # rebuilt the list
    difficult_words = []
    for i in range(len(output[0])):
        difficult_words.append(output[0][i][0])
    # create file
    if create: create_file(username, 'items/' + filename)
    # overwrite file
    if settings[23] != -1:
        difficult_words = sort(difficult_words, settings[23])
    overwrite(username, difficult_words, 'items/' + filename)
    # learn
    learn(username, filename, settings)

# re-review
def rereview(output, username, settings):
    # rebuilt the list
    difficult_words = []
    for i in range(len(output[0])):
        difficult_words.append(output[0][i][0])
    # review
    review(difficult_words, username, settings)

# save and review
def save_and_review(output, username, settings, filename = ''):
    # vragen wat de naam van de lijst met moeilijke woorden wordt
    create = True
    if filename == '': filename = s_inp('What will be the new name?   > ')
    while filename == '' or filename in os.listdir(ch_path('~/' + username + '/items')):
        try:
            s_out('This name already exist. Choose another name.')
            filename = s_inp('What will be the new name?   > ', input = filename)
        except KeyboardInterrupt:
            create = False
            break

    # rebuilt the list
    difficult_words = []
    for i in range(len(output[0])):
        difficult_words.append(output[0][i][0])
    # create file
    if create: create_file(username, 'items/' + filename)
    # overwrite file
    if settings[23] != -1:
        difficult_words = sort(difficult_words, settings[23])
    overwrite(username, difficult_words, 'items/' + filename)
    # review
    review(difficult_words, username, settings)

# view saved reviewsessions
def show_saved_reviewsessions(username):
    while True:
        # get saved reviewsessions
        saved_reviewsessions = os.listdir(ch_path('~/' + username + '/saved_reviewsessions/'))
        # clear screen
        cls()
        # show saved reviewsessions
        for list_words in range(len(saved_reviewsessions)):
            s_out(str(list_words + 1) + ': ' + saved_reviewsessions[list_words])
        # add newline
        if len(saved_reviewsessions) > 0:
            s_out()

        # show options
        s_out('Continue review --> r')
        s_out('Delete --> d')
        s_out('Delete all --> a')
        s_out('Back --> b/q')
        choice = s_inp('   > ')
        
        options = ['r', 'd', 'a', 'b', 'q']
        if choice not in options:
            cls()
            s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
            wait(1.5)
            continue

        # review
        if choice == 'r':
            if len(saved_reviewsessions) != 0:
                # ask wich item
                number = s_inp('Type the number to review.   > ')
                # check is a number
                if number.isdigit():
                    # check exist
                    if 0 < int(number) < (len(saved_reviewsessions) + 1):
                        # get content
                        list_words = get_list(username, 'saved_reviewsessions/' + saved_reviewsessions[int(number) - 1])

                        # set variables
                        difficult_words = list_words[1]
                        type = list_words[2]
                        times_wrong = list_words[3]
                        times_good = list_words[4]
                        number_words_had = list_words[5]
                        total_number_of_words = list_words[6]
                        times_in_a_row_good = list_words[7]
                        all_words = list_words[8]
                        list_words = list_words[0]
                    
                        # review
                        output = review_words(list_words, settings, username, type, difficult_words, times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words)
                        if len(output[0]) > 0 and output[1] != 'home':
                            # save as new list
                            if output[1] == 'new list':
                                save_as_new_list(output, username, settings)
                            
                            # save and learn
                            if output[1] == 'learn':
                                save_and_learn(output, username, settings)
                    
                            # review
                            if output[1] == 'review':
                                rereview(output, username, settings)
                    
                            # save and review
                            if output[1] == 'new list and review':
                                save_and_review(output, username, settings)
        
                        elif len(output[0]) == 0 and output[1] != 'home':
                            s_out('You have none mistakes!!!')
                            wait(1.5)
                    
                        elif output[1] != 'home':
                            s_out('Something went wrong.')
                            wait(1.5)
                
                    else:
                        s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to review.\x1b[0m')
                wait(1.5)

        # delete
        if choice == 'd':
            if len(saved_reviewsessions) != 0:
                # ask number
                number = s_inp('Type the number to delete.   > ')
                # check is a number
                if number.isdigit():
                    # check exist
                    if 0 < int(number) < (len(saved_reviewsessions) + 1):
                        # delete
                        delete_file(username, 'saved_reviewsessions/' + saved_reviewsessions[int(number) - 1])

                        cls()
                        s_out('Successful deleted.')
                        wait(1.5)

                    else:
                        s_out('\x1b[1;49;31mThat can\'t. No available number.\x1b[0m')
                        wait(1.5)
                else:
                    s_out('\x1b[1;49;31mThat can\'t. None number.\x1b[0m')
                    wait(1.5)
            else:
                s_out('\x1b[1;49;31mThat can\'t. There is nothing to review.\x1b[0m')
                wait(1.5)

        # delete all
        if choice == 'a':
            # ask permision
            if s_inp('Are you sure to delete all? It can\'t be undone. (yes/no)   > ') == 'yes':
                delete_all(username, 'saved_reviewsessions/')
                
        # back
        if choice == 'b' or choice == 'q':
            return ''

# proceed the review session
def proceed_review(username, settings):
    saved_reviewsessions = os.listdir(ch_path('~/' + username + '/saved_reviewsessions/'))
    while True:
        cls()
        for saved_reviewsession in range(len(saved_reviewsessions)):
            s_out(str(saved_reviewsession + 1) + ': ' + saved_reviewsessions[saved_reviewsession])

        if len(saved_reviewsessions) > 0:
            s_out()
    
        try:
            number = s_inp('Type the number or q to quit.   > ')
        except KeyboardInterrupt:
            return ''

        if number == 'q':
            return ''

        if not number.isdigit():
            continue

        if not 0 < int(number) < (len(saved_reviewsessions) + 1):
            continue

        filename = saved_reviewsessions[int(number) - 1]
        break

    # get content
    list_words = get_list(username, 'saved_reviewsessions/' + filename)

    # set variables
    difficult_words = list_words[1]
    type = list_words[2]
    times_wrong = list_words[3]
    times_good = list_words[4]
    number_words_had = list_words[5]
    total_number_of_words = list_words[6]
    times_in_a_row_good = list_words[7]
    all_words = list_words[8]
    list_words = list_words[0]

    # review
    output = review_words(list_words, settings, username, type, difficult_words, times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words)
    if len(output[0]) > 0 and output[1] != 'home':
        # save as new list
        if output[1] == 'new list':
            save_as_new_list(output, username, settings)
        
        # save and learn
        if output[1] == 'learn':
            save_and_learn(output, username, settings)

        # review
        if output[1] == 'review':
            rereview(output, username, settings)

        # save and review
        if output[1] == 'new list and review':
            save_and_review(output, username, settings)

    elif len(output[0]) == 0 and output[1] != 'home':
        s_out('You have none mistakes!!!')
        wait(1.5)

    elif output[1] != 'home':
        s_out('Something went wrong.')
        wait(1.5)
        
    return ''

