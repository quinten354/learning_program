# import modules
from random import randint, shuffle, choice
from time import sleep as wait, time
import os

from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out, cls
from extern.timeout import timeout

from manage_files import get_list, ch_path, overwrite, move, log_data
from manage_items import change_content
from questions import type_ex, multiple_choise, sentence, retype, show_word
from functions import is_warned, warn, sort, ch_time, get_list_index, show_target_info, select, lower, no_punctuation_marks, no_accents, show_learn_process, get_procent, get_scores
from solve import solve
from errors import ClosedTerminalError, ProcessKilledError, NotInListError, log_error

# learn item
def learn(username, filename, settings):
    learn_method = settings[0].copy()
    # get data
    list_item = get_list(username, 'items/' + filename)
    # get settings
    item_settings = get_list(username, 'item_settings')

    start_scores = get_scores(list_item, settings)
    start_procent = start_scores[0]
    first_time_learned = start_scores[1] == 0

    # search the relevant settings
    try:
        number_is = get_list_index(item_settings, filename)
    except NotInListError:
        number_is = -1

    # change the learn method by the settings
    if number_is != -1:
        if len(item_settings[number_is][5]) > 0:
            learn_method = item_settings[number_is][5]

    if number_is != -1:
        start_measurements = item_settings[number_is][6].copy()
    else:
        start_measurements = [0, 0, 0, start_scores[0]]

    while True:
        # shuffle list
        shuffle(list_item)

        # count words on niveau 1 and on niveau 0.1
        number_words_niveau_1 = 0
        number_words_niveau_01 = 0
        for listitem in list_item:
            if listitem[2] == 1: number_words_niveau_1 = number_words_niveau_1 + 1
            if listitem[2] == 0 and listitem[3] == 1: number_words_niveau_01 = number_words_niveau_01 + 1

        # get lowest times had and highest times in a row correct
        lowest = 100
        highest = 0
        for wordnumber in range(len(list_item)):
            if lowest > list_item[wordnumber][5] and list_item[wordnumber][2] > 0:
                lowest = list_item[wordnumber][5]
            if highest < list_item[wordnumber][3]:
                highest = list_item[wordnumber][3]

        # select words from learn method
        chosen_words = []

        # select random words when this is the first time the user is learning this item
        if first_time_learned:
            for number in range(settings[25]):
                count = 0
                rnd = randint(0, len(list_item) - 1)
                while rnd in chosen_words:
                    rnd = randint(0, len(list_item) - 1)
                    count = count + 1
                    if count > 10:
                        break
                if rnd not in chosen_words:
                    chosen_words.append(rnd)

        # select a lot of words looking in the settings
        for niveau in learn_method:
            chosen = False
            for wordnumber in range(len(list_item)):
                # if the niveau is matching, and this word not in chosen_words, add
                if list_item[wordnumber][2] == niveau and wordnumber not in chosen_words:
                    # when niveau is 0.1, add
                    if niveau == 0 and list_item[wordnumber][3] == 1:
                        chosen_words.append(wordnumber)
                        chosen = True
                    # when niveau is 0.0, check the number of words in niveau 1
                    elif niveau == 0 and list_item[wordnumber][3] == 0:
                        # if number of words in niveau 1 less than in the settings, add
                        if number_words_niveau_1 < settings[14] and number_words_niveau_01 < 2:
                            chosen_words.append(wordnumber)
                            chosen = True
                    # if the word not in niveau 0, add
                    else:
                        chosen_words.append(wordnumber)
                        chosen = True
                    if chosen:
                        # when chosen, go to the next niveau (out the for-loop of the list of words, back to the niveau)
                        break

        # select difficult words
        difficult = []
        if settings[3] > 0:
            # count words
            count_select_words = 0
            for wordnumber in range(len(list_item)):
                # check if the word is difficult: if the number of mistakes × 4 more than the number of opportunities, it's difficult
                # if the word is niveau 3, the user answered the word 2+ times correct in a type question, so he know the word surely
                # if the word is answered 3+ times correct, the user know this word also surely
                if (list_item[wordnumber][4] * 4) > list_item[wordnumber][5] and list_item[wordnumber][2] < 3 and list_item[wordnumber][3] < 3:
                    # check this word is not in chosen_words
                    if wordnumber not in chosen_words:
                        # add
                        count_select_words = count_select_words + 1
                        chosen_words.append(wordnumber)
                    # mark as difficult
                    difficult.append(wordnumber)
                if count_select_words == settings[3]:
                     break

        # select not often had words
        not_often_had = []
        if settings[4] > 0:
            # count words
            count_select_words = 0
            for wordnumber in range(len(list_item)):
                # if the user had this word (don't mark unknown words as not often had) and the times had is equal to the lowest number, add
                if list_item[wordnumber][5] == lowest and list_item[wordnumber][2] > 0:
                    # als het woord nog niet in woorden zit
                    if wordnumber not in chosen_words:
                        # woord toevoegen aan de lijst met woorden in deze leersessie
                        chosen_words.append(wordnumber)
                        # count words
                        count_select_words = count_select_words + 1
                    # mark as not often had
                    not_often_had.append(wordnumber)
                if count_select_words == settings[4]:
                    break

        # select often had words to delete
        for i in range(settings[5]):
            if len(chosen_words) > 1:
                for wordnumber in range(len(list_item)):
                    # if the user had this word the most times in a row correct
                    # and this word is already chosen
                    if list_item[wordnumber][3] == highest and list_item[wordnumber][2] == 3 and wordnumber in chosen_words:
                        # delete word
                        try:
                            chosen_words.remove(wordnumber)
                        except:
                            pass
                        break
        
        # set variables
        good_answered = 0
        mistakes = 0
        number_words = len(chosen_words)
        count_user = 1
        count_loop = 0
        dont_choice = []
        chosen_at = []

        log_data(username, 'New session, chosen_words: ' + str(chosen_words))

        # ask questions while there are words
        # (if the user makes a mistake, the word can not be deleted in chosen_words, the user get that word a next time in this session)
        while len(chosen_words) > 0 or len(dont_choice) > 0:
            shuffle(chosen_words)
            try:
                chosen = False
                may_not_chose = []
                # search in dont_choice with words with mistakes if there is a word that can chosen:
                for chosen_word_at in chosen_at:
                    if chosen_word_at[1] < (count_loop - 2):
                        chosen_at.remove(chosen_word_at)
                    else:
                        may_not_chose.append(chosen_word_at[0])

                # if the user makes a mistake, the user get another word, and then the word with the mistake
                for i in dont_choice:
                    if i[1] < (count_loop - 2) and (i[0] not in may_not_chose):
                        wordnumber = i[0]
                        chosen = True
                        dont_choice.remove(i)
                        chosen_words.append(wordnumber)
                        count_user = count_user - 1
                        chosen_by = 'by dont_choice'

                count_choice_word = 0
                while not chosen:
                    for wordnumber in chosen_words:
                        not_in_dont_choice = True
                        for i in dont_choice:
                            if i[0] == wordnumber:
                                not_in_dont_choice = False

                            if not_in_dont_choice and (wordnumber not in may_not_chose):
                                chosen = True
                                chosen_by = 'by chosen_words'
                                break

                        if len(dont_choice) == 0 and (wordnumber not in may_not_chose) and not chosen:
                            chosen = True
                            chosen_by = 'by dont_choice == 0'

                        if chosen:
                            break

                    if count_choice_word > 0:
                        for wordnumber in range(len(list_item)):
                            not_in_dont_choice = True
                            for i in dont_choice:
                                if i[0] == wordnumber:
                                    not_in_dont_choice = False

                            if (not_in_dont_choice or count_choice_word > 1 or len(dont_choice) == 0) and (wordnumber not in may_not_chose):
                                chosen = True
                                chosen_by = 'by all words'
                                chosen_words.append(wordnumber)

                            if chosen:
                                count_user = count_user - 1
                                break

                    if count_choice_word > 1:
                        wordnumber = randint(0, len(list_item) - 1)
                        if wordnumber not in may_not_chose:
                            chosen_by = 'by random word not in may_not_chose'
                            chosen = True
                            chosen_words.append(wordnumber)
                            count_user = count_user - 1

                    if count_choice_word > 1000:
                        for wordnumber in range(len(list_item)):
                            if wordnumber not in may_not_chose:
                                chosen_by = 'by a word in list not in may_not_chose'
                                chosen = True
                                chosen_words.append(wordnumber)
                                count_user = count_user - 1

                    if count_choice_word > 1001:
                        wordnumber = randint(0, len(list_item) - 1)
                        count_user = count_user - 1
                        chosen_by = 'by random word'
                        chosen_words.append(wordnumber)
                        chosen = True

                    count_choice_word = count_choice_word + 1

                log_data(username, 'Not chose: ' + str(may_not_chose) + ', ' + chosen_by + ' ' + str(wordnumber))
                
                # check words are difficult
                for difficult_word in difficult:
                    if (list_item[difficult_word][4] * 4) <= list_item[difficult_word][5]:
                        difficult.remove(difficult_word)

                # get scores
                scores = get_scores(list_item, settings)
                procent_met_leren, punten, max_punten = scores[0], scores[4], scores[5]
                # generate info for user
                info = ''
                # process in this session
                info = info + str(count_user) + '/' + str(number_words) + '    '
                # number of good, mistakes and difficult words
                info = info + 'good: \x1b[1;49;32m' + str(good_answered) + '\x1b[0m    '
                info = info + 'mistakes: \x1b[1;49;31m' + str(mistakes) + '\x1b[0m    '
                info = info + 'difficult: \x1b[1;49;33m' + str(len(difficult)) + '\x1b[0m    '
                # learning process
                info = info + (('\x1b[1;49;32mLearned!!!\x1b[0m') if procent_met_leren == 100 else ('You\'re at ' + str(round(procent_met_leren)) + '% with learn.'))
                info = info + ' (' + str(round(punten * 3)) + '/' + str(round(max_punten * 3)) + ')'

                # split pipe
                info = info + '  \x1b[1m|\x1b[0m  '

                # niveau
                info = info + 'Times good at niveau ' + str(list_item[wordnumber][2]) + ': '
                # times in a row good
                if list_item[wordnumber][3] < 2 or list_item[wordnumber][2] < 3:
                    info = info + '\x1b[1;49;33m' + str(list_item[wordnumber][3]) + '\x1b[0m'
                else:
                    info = info + '\x1b[1;49;32m' + str(list_item[wordnumber][3]) + '\x1b[0m'
                # show number of mistakes
                info = info + '    Mistakes: \x1b[1;49;31m' + str(list_item[wordnumber][4]) + '\x1b[0m'
                # show number of times had
                info = info + '    Times had: ' + str(list_item[wordnumber][5])

                # target
                if item_settings[number_is][3] > 0:
                    # split pipe
                    info = info + '  \x1b[1m|\x1b[0m  '

                    if item_settings[number_is][4] == 'w':
                        info = info + str(item_settings[number_is][3] - item_settings[number_is][6][0]) + ' words to reach target.'
                    if item_settings[number_is][4] == 's':
                        info = info + str(item_settings[number_is][3] - item_settings[number_is][6][1]) + ' sessions to reach target.'
                    if item_settings[number_is][4] == '%':
                        info = info + str(item_settings[number_is][3] - item_settings[number_is][6][2]) + ' procent to reach target.'

                # newline
                info = info + '\n'

                # als je het woord vaak fout hebt, dat tonen
                if wordnumber in difficult and settings[3] > 0:
                    info = info + '\n\x1b[1;49;33mThis word is difficult.\x1b[0m        '
                    info = info + 'You has to answer it ' + str((list_item[wordnumber][4] * 4) - list_item[wordnumber][5]) + ' times good to remove it from difficult words.\n'

                # als je het woord niet vaak hebt gehad, dat tonen
                if wordnumber in not_often_had and settings[4]:
                    info = info + '\n\x1b[1;49;33mYou haven\'t had this word often.\x1b[0m\n'

                # clear screen
                cls()

                # niveau 0: new word: show word to user
                if list_item[wordnumber][2] == 0:
                    # show info
                    s_out(info)

                    if list_item[wordnumber][3] == 0:
                        # show word
                        show_word(list_item[wordnumber])
                    else:
                        # retype word
                        retype(list_item[wordnumber])

                    # mark as good answered
                    output = True

                # niveau 1: multiple choice
                elif list_item[wordnumber][2] == 1:
                    # find more words to show in a multiple-choice question
                    words_multiple_choice = [list_item[wordnumber]]

                    count_multiple_choice = 0
                    while len(words_multiple_choice) < settings[8] and count_multiple_choice < (len(list_item) * 100):
                        woord_meerkeuze = list_item[randint(0, len(list_item) - 1)]
                        if woord_meerkeuze not in words_multiple_choice:
                            words_multiple_choice.append(woord_meerkeuze)
                        count_multiple_choice = count_multiple_choice + 1

                    # ask question
                    output = multiple_choise(words_multiple_choice, settings, 'learn', info, list_item)[0]

                # niveau 2: sentence/type
                elif list_item[wordnumber][2] == 2:
                    # if the word has enough words, ask sentence question
                    if list_item[wordnumber][1].count(' ') > (settings[9] - 2) and list_item[wordnumber][3] < (settings[17] / 2):
                        output = sentence(list_item[wordnumber], settings, 'learn', info, list_item)[0]
                    # else, ask type question
                    else:
                        s_out(info)
                        output = type_ex(list_item[wordnumber], settings, 'learn', list_item)[0]

                # niveau 3: type
                elif list_item[wordnumber][2] == 3:
                    # show info
                    s_out(info)

                    # ask question
                    output = type_ex(list_item[wordnumber], settings, 'learn', list_item)[0]
    
            # close learn session when a event happend
            except KeyboardInterrupt:
                cls()
                if s_inp('Do you want to quit? (yes/no)   > ') == 'yes':
                    overwrite(username, list_item, 'items/' + filename)
                    list_scores = get_list(username, 'list_items')
                    for i in range(len(list_scores)):
                        if list_scores[i][0] == filename:
                            list_scores[i][1] = len(list_item)
                            list_scores[i][2] = get_procent(*get_scores(list_item, settings))
                    overwrite(username, list_scores, 'list_items')
                    overwrite(username, item_settings, 'item_settings')
                    return ''

                else:
                    continue

            except ClosedTerminalError:
                overwrite(username, list_item, 'items/' + filename)
                list_scores = get_list(username, 'list_items')
                for i in range(len(list_scores)):
                    if list_scores[i][0] == filename:
                        list_scores[i][1] = len(list_item)
                        list_scores[i][2] = get_procent(*get_scores(list_item, settings))
                overwrite(username, list_scores, 'list_items')
                overwrite(username, item_settings, 'item_settings')
                raise ClosedTerminalError

            except ProcessKilledError:
                overwrite(username, list_item, 'items/' + filename)
                list_scores = get_list(username, 'list_items')
                for i in range(len(list_scores)):
                    if list_scores[i][0] == filename:
                        list_scores[i][1] = len(list_item)
                        list_scores[i][2] = get_procent(*get_scores(list_item, settings))
                overwrite(username, list_scores, 'list_items')
                overwrite(username, item_settings, 'item_settings')
                raise ProcessKilledError

            # count info
            # good answered
            if output:
                # niveau 0.0: don't remove word, it will be asked again
                if list_item[wordnumber][2] == 0 and list_item[wordnumber][3] == 0:
                    dont_choice.append([wordnumber, count_loop])

                # times in a row good answered
                list_item[wordnumber][3] = list_item[wordnumber][3] + 1
                # count times good answered
                good_answered = good_answered + 1
                # update niveau
                if list_item[wordnumber][2] == 0 and list_item[wordnumber][3] > 1:
                    list_item[wordnumber][2] = 1
                    list_item[wordnumber][3] = 0
                if list_item[wordnumber][2] == 1 and list_item[wordnumber][3] > (settings[16] - 1):
                    list_item[wordnumber][2] = 2
                    list_item[wordnumber][3] = 0
                if list_item[wordnumber][2] == 2 and list_item[wordnumber][3] > (settings[17] - 1):
                    list_item[wordnumber][2] = 3
                    list_item[wordnumber][3] = 0

                # update target measurements
                item_settings[number_is][6][0] = item_settings[number_is][6][0] + 1

            # mistakes
            else:
                # times in a row good answered
                list_item[wordnumber][3] = list_item[wordnumber][3] - 3
                # number of mistakes
                list_item[wordnumber][4] = list_item[wordnumber][4] + 1
                # update niveau
                if list_item[wordnumber][3] < 0:
                    list_item[wordnumber][2] = list_item[wordnumber][2] - 1
                    if list_item[wordnumber][2] == 0:
                        list_item[wordnumber][3] = list_item[wordnumber][3] + 2
                        if list_item[wordnumber][3] < 0:
                            list_item[wordnumber][3] = 0

                    if list_item[wordnumber][2] == 1:
                        list_item[wordnumber][3] = list_item[wordnumber][3] + settings[16]
                        if list_item[wordnumber][3] < 0:
                            list_item[wordnumber][3] = 0

                    if list_item[wordnumber][2] == 2:
                        list_item[wordnumber][3] = list_item[wordnumber][3] + settings[17]
                        if list_item[wordnumber][3] < 0:
                            list_item[wordnumber][3] = 0
                
                # count mistakes
                mistakes = mistakes + 1
                if settings[6]:
                    # don't remove word
                    dont_choice.append([wordnumber, count_loop])

                # update difficult
                if (list_item[wordnumber][4] * 4) > (list_item[wordnumber][5] + 1):
                    difficult.append(wordnumber)

            try:
                chosen_words.remove(wordnumber)
            except:
                pass

            # count times had
            list_item[wordnumber][5] = list_item[wordnumber][5] + 1

            # add to chosen_at
            chosen_at.append([wordnumber, count_loop])

            count_user = count_user + 1

            # update item settings
            if (item_settings[number_is][2] + item_settings[number_is][1]) < time():
                item_settings[number_is][6][2] = item_settings[number_is][6][2] + (get_scores(list_item, settings)[0] - start_procent)

            else:
                item_settings[number_is][6][0] = 0
                item_settings[number_is][6][1] = 0
                item_settings[number_is][6][2] = 0

            item_settings[number_is][6][3] = get_scores(list_item, settings)[0]
            start_procent = get_scores(list_item, settings)[0]

            count_loop = count_loop + 1

        # update item settings
        item_settings[number_is][6][1] = item_settings[number_is][6][1] + 1

        # get stats
        cls()
        s_out('\x1b[1;49;32mGood: ' + str(good_answered) + '\x1b[0m')
        s_out('\x1b[1;49;31mMistakes: ' + str(mistakes) + '\x1b[0m')
        s_out()
        procent = show_learn_process(list_item, settings)

        if show_target_info(item_settings[number_is], start_measurements):
            item_settings[number_is][6][0] = 0
            item_settings[number_is][6][1] = 0
            item_settings[number_is][6][2] = 0
            item_settings[number_is][2] = time()
            s_out()

        # choice comminucation
        comminucation = []
        comminucation.append(choice(['Nice job!', 'Keep it up!', 'Well done!']))
        
        if 45 < round(procent) < 50:
            comminucation.append('You\'re almost halfway there!')

        if round(procent) == 50:
            comminucation.append('You\'re halfway there!')

        if 50 < round(procent) < 55:
            comminucation.append('You\'re just over half way there!')

        if 85 < procent < 100:
            comminucation.append('You\'re almost there!')

        if mistakes == 1:
            comminucation.append('Just that one mistake.')

        if mistakes == 0:
            comminucation.append('You got everything right!')

        if mistakes > good_answered:
            comminucation.append('Unfortunately, you got more wrong than you got right.')

        s_out()
        s_out(choice(comminucation))
        s_out()
        s_out('\rSaving.', end = '')
        
        # save
        if settings[23] != -1:
            list_item = sort(list_item, settings[23])
        overwrite(username, list_item, 'items/' + filename)
        list_scores = get_list(username, 'list_items')
        for i in range(len(list_scores)):
            if list_scores[i][0] == filename:
                list_scores[i][1] = len(list_item)
                list_scores[i][2] = get_procent(*get_scores(list_item, settings))
        overwrite(username, list_scores, 'list_items')

        # save item settings
        overwrite(username, item_settings, 'item_settings')
        
        # ask user to continue
        s_out('\r                ', end = '')
        while True:
            to_continue = s_inp('Do you want to continue, view the item settings or change item content? (y/n/s/c)   > ')
            options = ['y', 'n', 's', 'c']
            while to_continue not in options:
                s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                to_continue = s_inp('Do you want to continue, view the item settings or change item content? (y/n/s/c)   > ')

            if to_continue == 'y':
                break
            if to_continue == 'n':
                return ''
            if to_continue == 's':
                item_options(username, filename, settings)
            if to_continue == 'c':
                list_item = change_content(username, filename, settings, list_item.copy())

# review and save good answered words as learned
def review_and_learn(username, filename, settings):
    list_item = get_list(username, 'items/' + filename)

    # shuffle list
    shuffle(list_item)

    # ask user to choice
    choice = ''
    options = ['a', 'n']
    while choice not in options:
        choice = s_inp('Do you want to review th whole list or alone the unknown words? (w/a)   > ')

    numbers = []
    list_review = []

    # review all unknown words
    if choice == 'a':
        for i in range(len(list_item)):
            # check if the word is learned
            if list_item[i][2] != 3:
                # add to the list for review
                list_review.append(list_item[i].copy())
                numbers.append(i)

        if len(list_review) < 1:
            cls()
            s_out('\x1b[1;49;31mYou have learned everything.\x1b[0m')
            s_out()
            s_out('Check for difficult words.')
            s_inp('Press enter to continue.')
            return ''
    else:
        # select all words
        for i in range(len(list_item)):
            list_review.append(list_item[i].copy())
            numbers.append(i)

    try:
        for number in range(len(list_review)):
            # clear screen
            cls()
            # show process
            s_out(str(number + 1) + ' of ' + str(len(list_review)) + ' (' + str(round((number / len(list_review)) * 100)) + '%)')
            s_out()
    
            # ask question
            try:
                result = type_ex(list_review[number], settings, None, list_item)
            except KeyboardInterrupt:
                cls()
                if s_inp('Do you want to quit? (yes/no)   > ') == 'yes':
                    s_out('Quiting.')
                    wait(1.5)
                    break

            # if the answer is good, save as learned
            if result[0]:
                list_review[number][2] = 3

    # save and exit
    except ClosedTerminalError:
        for i in range(len(list_review)):
            list_item[numbers[i]] = list_review[i]

        if settings[23] != -1:
            list_item = sort(list_item, settings[23])
        overwrite(username, list_item, 'items/' + filename)
        list_scores = get_list(username, 'list_items')
        for i in range(len(list_scores)):
            if list_scores[i][0] == filename:
                list_scores[i][1] = len(list_item)
                list_scores[i][2] = get_procent(*get_scores(list_item, settings))
        overwrite(username, list_scores, 'list_items')
        raise ClosedTerminalError

    except ProcessKilledError:
        for i in range(len(list_review)):
            list_item[numbers[i]] = list_review[i]
    
        if settings[23] != -1:
            list_item = sort(list_item, settings[23])
        overwrite(username, list_item, 'items/' + filename)
        list_scores = get_list(username, 'list_items')
        for i in range(len(list_scores)):
            if list_scores[i][0] == filename:
                list_scores[i][1] = len(list_item)
                list_scores[i][2] = get_procent(*get_scores(list_item, settings))
        overwrite(username, list_scores, 'list_items')
        raise ProcessKilledError

    for i in range(len(list_review)):
        list_item[numbers[i]] = list_review[i]

    if settings[23] != -1:
        list_item = sort(list_item, settings[23])
    overwrite(username, list_item, 'items/' + filename)
    list_scores = get_list(username, 'list_items')
    for i in range(len(list_scores)):
        if list_scores[i][0] == filename:
            list_scores[i][1] = len(list_item)
            list_scores[i][2] = get_procent(*get_scores(list_item, settings))
    overwrite(username, list_scores, 'list_items')
    return ''

