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

def get_learn_info(username, filename, settings):
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

        start_measurements = item_settings[number_is][6].copy()

    else:
        start_measurements = [0, 0, 0, start_scores[0]]

    return list_item, item_settings, start_scores, start_procent, first_time_learned, number_is, learn_method, start_measurements

# learn item
def learn(username, filename, settings):
    learn_info = list(get_learn_info(username, filename, settings))
    learn_method = learn_info[6]

    while True:
        # shuffle list
        shuffle(learn_info[0])

        # count words on niveau 1 and on niveau 0.1
        number_words_niveau_1 = 0
        number_words_niveau_01 = 0
        for listitem in learn_info[0]:
            if listitem[2] == 1: number_words_niveau_1 = number_words_niveau_1 + 1
            if listitem[2] == 0 and listitem[3] == 1: number_words_niveau_01 = number_words_niveau_01 + 1

        # get lowest times had and highest times in a row correct
        lowest = 100
        highest = 0
        for wordnumber in range(len(learn_info[0])):
            if lowest > learn_info[0][wordnumber][5] and learn_info[0][wordnumber][2] > 0:
                lowest = learn_info[0][wordnumber][5]
            if highest < learn_info[0][wordnumber][3]:
                highest = learn_info[0][wordnumber][3]

        # get owa words
        owa = []
        for wordnumber in range(len(learn_info[0])):
            try:
                owa.append([wordnumber, learn_info[0][wordnumber][5] / learn_info[0][wordnumber][4]])
            except ZeroDivisionError:
                continue

        owa = list(reversed(sort(owa.copy(), 1)))
        owa = owa[settings[27]:].copy()
        owa_numbers = []

        for item in owa:
            owa_numbers.append(item[0])

        # select words from learn method
        chosen_words = []

        # select random words when this is the first time the user is learning this item
        if learn_info[4]:
            for number in range(settings[25]):
                count = 0
                rnd = randint(0, len(learn_info[0]) - 1)
                while rnd in chosen_words:
                    rnd = randint(0, len(learn_info[0]) - 1)
                    count = count + 1
                    if count > 10:
                        break
                if rnd not in chosen_words:
                    chosen_words.append(rnd)

        # select a lot of words looking in the settings
        for niveau in learn_method:
            chosen = False
            for wordnumber in range(len(learn_info[0])):
                # if the niveau is matching, and this word not in chosen_words, add
                if learn_info[0][wordnumber][2] == niveau and wordnumber not in chosen_words:
                    # when niveau is 0.1, add
                    if niveau == 0 and learn_info[0][wordnumber][3] == 1:
                        chosen_words.append(wordnumber)
                        chosen = True
                    # when niveau is 0.0, check the number of words in niveau 1
                    elif niveau == 0 and learn_info[0][wordnumber][3] == 0:
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
            for wordnumber in range(len(learn_info[0])):
                # check if the word is difficult: if the number of mistakes × 4 more than the number of opportunities, it's difficult
                # if the word is niveau 3, the user answered the word 2+ times correct in a type question, so he know the word surely
                # if the word is answered 3+ times correct, the user know this word also surely
                if (learn_info[0][wordnumber][4] * 4) > learn_info[0][wordnumber][5] and learn_info[0][wordnumber][2] < 3 and learn_info[0][wordnumber][3] < 3:
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
            for wordnumber in range(len(learn_info[0])):
                # if the user had this word (don't mark unknown words as not often had) and the times had is equal to the lowest number, add
                if learn_info[0][wordnumber][5] == lowest and learn_info[0][wordnumber][2] > 0:
                    # als het woord nog niet in woorden zit
                    if wordnumber not in chosen_words:
                        # add
                        chosen_words.append(wordnumber)
                        # count words
                        count_select_words = count_select_words + 1
                    # mark as not often had
                    not_often_had.append(wordnumber)
                if count_select_words == settings[4]:
                    break

        # select often wrong answered words
        if settings[27] > 0:
            # count words
            count_select_words = 0
            for wordnumber in range(len(learn_info[0])):
                # if the user had this word (don't mark unknown words as not often had) and the times had is equal to the lowest number, add
                if wordnumber in owa_numbers and learn_info[0][wordnumber][2] > 0:
                    # als het woord nog niet in woorden zit
                    if wordnumber not in chosen_words:
                        # add
                        chosen_words.append(wordnumber)
                        # count words
                        count_select_words = count_select_words + 1
                    log_data(username, 'Selected owa: ' + str(wordnumber) + '    ' + str(learn_info[0][wordnumber]))
                if count_select_words == settings[27]:
                    break

        # select often had words to delete
        for i in range(settings[5]):
            if len(chosen_words) > 1:
                for wordnumber in range(len(learn_info[0])):
                    # if the user had this word the most times in a row correct
                    # and this word is already chosen
                    if learn_info[0][wordnumber][3] == highest and learn_info[0][wordnumber][2] == 3 and wordnumber in chosen_words:
                        # delete word
                        try:
                            chosen_words.remove(wordnumber)
                        except:
                            pass
                        break

        output = learn_session(chosen_words, username, filename, settings, learn_info, not_often_had, difficult)
        if output == 'Quit':
            return ''

def learn_all(username, filename, settings):
    learn_info = list(get_learn_info(username, filename, settings))
    chosen_words = []
    for wordnumber in range(len(learn_info[0])):
        chosen_words.append(wordnumber)
    learn_session(chosen_words, username, filename, settings, learn_info, repeat = False)
        
def learn_session(chosen_words, username, filename, settings, learn_info = None, not_often_had = [], difficult = [], repeat = True):
    # set variables
    good_answered = 0
    mistakes = 0
    number_words = len(chosen_words)
    count_user = 1
    count_loop = 0
    dont_choice = []
    chosen_at = []

    if not learn_info:
        learn_info = list(get_learn_info(username, filename))

    log_data(username, 'New session, chosen_words: ' + str(chosen_words) + ', not_often_had: ' + str(not_often_had) + ', difficult: ' + str(difficult))

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
                    for wordnumber in range(len(learn_info[0])):
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
                    wordnumber = randint(0, len(learn_info[0]) - 1)
                    if wordnumber not in may_not_chose:
                        chosen_by = 'by random word not in may_not_chose'
                        chosen = True
                        chosen_words.append(wordnumber)
                        count_user = count_user - 1

                if count_choice_word > 1000:
                    for wordnumber in range(len(learn_info[0])):
                        if wordnumber not in may_not_chose:
                            chosen_by = 'by a word in list not in may_not_chose'
                            chosen = True
                            chosen_words.append(wordnumber)
                            count_user = count_user - 1

                if count_choice_word > 1001:
                    wordnumber = randint(0, len(learn_info[0]) - 1)
                    count_user = count_user - 1
                    chosen_by = 'by random word'
                    chosen_words.append(wordnumber)
                    chosen = True

                count_choice_word = count_choice_word + 1

            log_data(username, 'Not chose: ' + str(may_not_chose) + ', ' + chosen_by + ' ' + str(wordnumber))
            
            # check words are difficult
            for difficult_word in difficult:
                if (learn_info[0][difficult_word][4] * 4) <= learn_info[0][difficult_word][5]:
                    difficult.remove(difficult_word)

            # get scores
            scores = get_scores(learn_info[0], settings)
            procent_met_leren, punten, max_punten = scores[0], scores[4], scores[5]
            # generate info for user
            info = ''
            # process in this session
            info = info + str(count_user) + '/' + str(number_words) + '    '
            # number of good, mistakes and difficult words
            info = info + '\x1b[1;49;32m' + str(good_answered) + '\x1b[0m '
            if good_answered == 1:
                info = info + 'time'
            else:
                info = info + 'times'
            info = info + ' good     '
            info = info + '\x1b[1;49;31m' + str(mistakes) + '\x1b[0m '
            if mistakes == 1:
                info = info + 'mistake'
            else:
                info = info + 'mistakes'
            info = info + '    \x1b[1;49;33m' + str(len(difficult)) + '\x1b[0m '
            if difficult == 1:
                info = info + 'word'
            else:
                info = info + 'words'
            info = info + ' difficult    '
            # learning process
            info = info + (('\x1b[1;49;32mLearned!!!\x1b[0m') if procent_met_leren == 100 else ('You\'re at ' + str(round(procent_met_leren)) + '% with learn.'))
            info = info + ' (' + str(round(punten * 3)) + '/' + str(round(max_punten * 3)) + ')'

            # split pipe
            info = info + '  \x1b[1m|\x1b[0m  '

            # times in a row good
            if learn_info[0][wordnumber][3] < 2 or learn_info[0][wordnumber][2] < 3:
                info = info + '\x1b[1;49;33m' + str(learn_info[0][wordnumber][3]) + '\x1b[0m'
            else:
                info = info + '\x1b[1;49;32m' + str(learn_info[0][wordnumber][3]) + '\x1b[0m'
            if learn_info[0][wordnumber][3] == 1:
                info = info + ' time'
            else:
                info = info + ' times'
            # niveau
            info = info + ' good at niveau ' + str(learn_info[0][wordnumber][2])
            # show number of mistakes
            info = info + '    \x1b[1;49;31m' + str(learn_info[0][wordnumber][4]) + '\x1b[0m '
            if learn_info[0][wordnumber][4] == 1:
                info = info + 'mistake    '
            else:
                info = info + 'mistakes    '
            # show number of times had
            info = info + str(learn_info[0][wordnumber][5])
            if learn_info[0][wordnumber][5] == 1:
                info = info + ' time had'
            else:
                info = info + ' times had'

            # target
            if learn_info[1][learn_info[5]][3] > 0:
                # split pipe
                info = info + '  \x1b[1m|\x1b[0m  '

                if learn_info[1][learn_info[5]][4] == 'w':
                    info = info + str(learn_info[1][learn_info[5]][3] - learn_info[1][learn_info[5]][6][0]) + ' words to reach target.'
                if learn_info[1][learn_info[5]][4] == 's':
                    info = info + str(learn_info[1][learn_info[5]][3] - learn_info[1][learn_info[5]][6][1]) + ' sessions to reach target.'
                if learn_info[1][learn_info[5]][4] == '%':
                    info = info + str(learn_info[1][learn_info[5]][3] - learn_info[1][learn_info[5]][6][2]) + ' procent to reach target.'

            # newline
            info = info + '\n'

            # als je het woord vaak fout hebt, dat tonen
            if wordnumber in difficult and settings[3] > 0:
                info = info + '\n\x1b[1;49;33mThis word is difficult.\x1b[0m        '
                info = info + 'You have to answer it ' + str((learn_info[0][wordnumber][4] * 4) - learn_info[0][wordnumber][5])
                if ((learn_info[0][wordnumber][4] * 4) - learn_info[0][wordnumber][5]) == 1:
                    info = info + ' time'
                else:
                    info = info + ' times'
                info = info + ' good to remove it from difficult words.\n'

            # als je het woord niet vaak hebt gehad, dat tonen
            if wordnumber in not_often_had and settings[4]:
                info = info + '\n\x1b[1;49;33mYou haven\'t had this word often.\x1b[0m\n'

            # clear screen
            cls()

            # niveau 0: new word: show word to user
            if learn_info[0][wordnumber][2] == 0:
                # show info
                s_out(info)

                if learn_info[0][wordnumber][3] == 0:
                    # show word
                    show_word(learn_info[0][wordnumber])
                else:
                    # retype word
                    retype(learn_info[0][wordnumber])

                # mark as good answered
                output = True

            # niveau 1: multiple choice
            elif learn_info[0][wordnumber][2] == 1:
                # find more words to show in a multiple-choice question
                words_multiple_choice = [learn_info[0][wordnumber]]

                count_multiple_choice = 0
                while len(words_multiple_choice) < settings[8] and count_multiple_choice < (len(learn_info[0]) * 100):
                    woord_meerkeuze = learn_info[0][randint(0, len(learn_info[0]) - 1)]
                    if woord_meerkeuze not in words_multiple_choice:
                        words_multiple_choice.append(woord_meerkeuze)
                    count_multiple_choice = count_multiple_choice + 1

                # ask question
                output = multiple_choise(words_multiple_choice, settings, 'learn', info, learn_info[0])[0]

            # niveau 2: sentence/type
            elif learn_info[0][wordnumber][2] == 2:
                # if the word has enough words, ask sentence question
                if learn_info[0][wordnumber][1].count(' ') > (settings[9] - 2) and learn_info[0][wordnumber][3] < (settings[17] / 2):
                    output = sentence(learn_info[0][wordnumber], settings, 'learn', info, learn_info[0])[0]
                # else, ask type question
                else:
                    s_out(info)
                    output = type_ex(learn_info[0][wordnumber], settings, 'learn', learn_info[0])[0]

            # niveau 3: type
            elif learn_info[0][wordnumber][2] == 3:
                # show info
                s_out(info)

                # ask question
                output = type_ex(learn_info[0][wordnumber], settings, 'learn', learn_info[0])[0]

        # close learn session when a event happend
        except KeyboardInterrupt:
            cls()
            output = s_inp('Do you want to quit or save? (y/n/s)   > ')
            while output not in ['y', 'n', 's']:
                print('\x1b[1;49;31mThat isn\'t a option!\x1b[0m')
                output = s_inp('Do you want to quit or save? (y/n/s)   > ')

            if output == 'y':
                overwrite(username, learn_info[0], 'items/' + filename)
                list_scores = get_list(username, 'list_items')
                for i in range(len(list_scores)):
                    if list_scores[i][0] == filename:
                        list_scores[i][1] = len(learn_info[0])
                        list_scores[i][2] = get_procent(*get_scores(learn_info[0], settings))
                overwrite(username, list_scores, 'list_items')
                overwrite(username, learn_info[1], 'item_settings')
                return 'Quit'

            elif output == 's':
                save(username, filename, chosen_words, not_often_had, difficult)
                return 'Quit'

            else:
                continue

        except ClosedTerminalError:
            overwrite(username, learn_info[0], 'items/' + filename)
            list_scores = get_list(username, 'list_items')
            for i in range(len(list_scores)):
                if list_scores[i][0] == filename:
                    list_scores[i][1] = len(learn_info[0])
                    list_scores[i][2] = get_procent(*get_scores(learn_info[0], settings))
            overwrite(username, list_scores, 'list_items')
            overwrite(username, learn_info[1], 'item_settings')
            raise ClosedTerminalError

        except ProcessKilledError:
            overwrite(username, learn_info[0], 'items/' + filename)
            list_scores = get_list(username, 'list_items')
            for i in range(len(list_scores)):
                if list_scores[i][0] == filename:
                    list_scores[i][1] = len(learn_info[0])
                    list_scores[i][2] = get_procent(*get_scores(learn_info[0], settings))
            overwrite(username, list_scores, 'list_items')
            overwrite(username, learn_info[1], 'item_settings')
            raise ProcessKilledError

        # count info
        # good answered
        if output:
            # niveau 0.0: don't remove word, it will be asked again
            if learn_info[0][wordnumber][2] == 0 and learn_info[0][wordnumber][3] == 0:
                dont_choice.append([wordnumber, count_loop])

            # times in a row good answered
            learn_info[0][wordnumber][3] = learn_info[0][wordnumber][3] + 1
            # count times good answered
            good_answered = good_answered + 1
            # update niveau
            if learn_info[0][wordnumber][2] == 0 and learn_info[0][wordnumber][3] > 1:
                learn_info[0][wordnumber][2] = 1
                learn_info[0][wordnumber][3] = 0
            if learn_info[0][wordnumber][2] == 1 and learn_info[0][wordnumber][3] > (settings[16] - 1):
                learn_info[0][wordnumber][2] = 2
                learn_info[0][wordnumber][3] = 0
            if learn_info[0][wordnumber][2] == 2 and learn_info[0][wordnumber][3] > (settings[17] - 1):
                learn_info[0][wordnumber][2] = 3
                learn_info[0][wordnumber][3] = 0

            # update target measurements
            learn_info[1][learn_info[5]][6][0] = learn_info[1][learn_info[5]][6][0] + 1

        # mistakes
        else:
            # times in a row good answered
            learn_info[0][wordnumber][3] = learn_info[0][wordnumber][3] - 3
            # number of mistakes
            learn_info[0][wordnumber][4] = learn_info[0][wordnumber][4] + 1
            # update niveau
            if learn_info[0][wordnumber][3] < 0:
                learn_info[0][wordnumber][2] = learn_info[0][wordnumber][2] - 1
                if learn_info[0][wordnumber][2] == 0:
                    learn_info[0][wordnumber][3] = learn_info[0][wordnumber][3] + 2
                    if learn_info[0][wordnumber][3] < 0:
                        learn_info[0][wordnumber][3] = 0

                if learn_info[0][wordnumber][2] == 1:
                    learn_info[0][wordnumber][3] = learn_info[0][wordnumber][3] + settings[16]
                    if learn_info[0][wordnumber][3] < 0:
                        learn_info[0][wordnumber][3] = 0

                if learn_info[0][wordnumber][2] == 2:
                    learn_info[0][wordnumber][3] = learn_info[0][wordnumber][3] + settings[17]
                    if learn_info[0][wordnumber][3] < 0:
                        learn_info[0][wordnumber][3] = 0
            
            # count mistakes
            mistakes = mistakes + 1
            if settings[6]:
                # don't remove word
                dont_choice.append([wordnumber, count_loop])

            # update difficult
            if (learn_info[0][wordnumber][4] * 4) > (learn_info[0][wordnumber][5] + 1):
                difficult.append(wordnumber)

        try:
            chosen_words.remove(wordnumber)
        except:
            pass

        # count times had
        learn_info[0][wordnumber][5] = learn_info[0][wordnumber][5] + 1

        # add to chosen_at
        chosen_at.append([wordnumber, count_loop])

        count_user = count_user + 1

        # update item settings
        if (learn_info[1][learn_info[5]][2] + learn_info[1][learn_info[5]][1]) < time():
            learn_info[1][learn_info[5]][6][2] = learn_info[1][learn_info[5]][6][2] + (get_scores(learn_info[0], settings)[0] - learn_info[3])

        else:
            learn_info[1][learn_info[5]][6][0] = 0
            learn_info[1][learn_info[5]][6][1] = 0
            learn_info[1][learn_info[5]][6][2] = 0

        learn_info[1][learn_info[5]][6][3] = get_scores(learn_info[0], settings)[0]
        learn_info[3] = get_scores(learn_info[0], settings)[0]

        count_loop = count_loop + 1

    # update item settings
    learn_info[1][learn_info[5]][6][1] = learn_info[1][learn_info[5]][6][1] + 1

    # get stats
    cls()
    s_out('\x1b[1;49;32mGood: ' + str(good_answered) + '\x1b[0m')
    s_out('\x1b[1;49;31mMistakes: ' + str(mistakes) + '\x1b[0m')
    s_out()
    procent = show_learn_process(learn_info[0], settings)

    if show_target_info(learn_info[1][learn_info[5]], learn_info[7]):
        learn_info[1][learn_info[5]][6][0] = 0
        learn_info[1][learn_info[5]][6][1] = 0
        learn_info[1][learn_info[5]][6][2] = 0
        learn_info[1][learn_info[5]][2] = time()
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
        learn_info[0] = sort(learn_info[0], settings[23])
    overwrite(username, learn_info[0], 'items/' + filename)
    list_scores = get_list(username, 'list_items')
    for i in range(len(list_scores)):
        if list_scores[i][0] == filename:
            list_scores[i][1] = len(learn_info[0])
            list_scores[i][2] = get_procent(*get_scores(learn_info[0], settings))
    overwrite(username, list_scores, 'list_items')

    # save item settings
    overwrite(username, learn_info[1], 'item_settings')
    
    # ask user to continue
    s_out('\r                ', end = '')
    if repeat:
        while True:
            to_continue = s_inp('Do you want to continue, view the item settings or change item content? (y/n/s/c)   > ')
            options = ['y', 'n', 's', 'c']
            while to_continue not in options:
                s_out('\x1b[1;49;31mThat isn\'t a option!!!\x1b[0m')
                to_continue = s_inp('Do you want to continue, view the item settings or change item content? (y/n/s/c)   > ')

            if to_continue == 'y':
                break
            if to_continue == 'n':
                return 'Quit'
            if to_continue == 's':
                item_options(username, filename, settings)
            if to_continue == 'c':
                learn_info[0] = change_content(username, filename, settings, learn_info[0].copy())

    else:
        s_inp('Press enter to go back. ')

def save(username, filename, chosen_words, not_often_had, difficult):
    try:
        while filename == '' or filename in os.listdir(ch_path('~/' + username + '/saved_sessions/')):
            if filename in os.listdir(ch_path('~/' + username + '/saved_sessions/')):
                filename = s_inp('This name already exist. Choose another name or press ctrl + c to overwrite.   > ', invalid_characters = ['/', '\\'])
            else:
                filename = s_inp('Choose the name to save this session.   > ', invalid_characters = ['/', '\\'])

        # create file
        create_file(username, 'saved_sessions/' + filename)

    except KeyboardInterrupt:
        if filename == '':
            s_out('Can\'t accept no input.')
            save_reviewsession(list_words, difficult_words, type, times_wrong, times_good, number_words_had, total_number_of_words, times_in_a_row_good, all_words, username)
            return '' 

        else:
            s_out('Overwrite.')

    # overwrite
    overwrite(username, [['learn'], [filename], chosen_words, not_often_had, difficult])

def continue_learn(username, filename, chosen_words, not_often_had, difficult):
    learn_session(username, filename[0], chosen_words, not_often_had, difficult)

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

