# import modules
import os
from random import shuffle
from time import sleep as wait

from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out, cls

from functions import show_mistake, check_answer

# set functions
# show word
def show_word(word):
    # view word
    s_out('Given word:   ' + word[0])
    s_out('Unknown word: ' + word[1])
    s_inp('Press enter to continue. ')

# retype word
def retype(word):
    s_out('Given word:   ' + word[0])
    s_out('Unknown word: ' + word[1])
    s_out()
    inp = ''
    while inp != word[1]:
        inp = s_inp('Type the unknown word   > ', input = inp)
        if inp != '' and inp != word[1]:
            s_out('\x1b[1;49;31mThat can\'t!!!\x1b[0m')
            wait(1.5)
    s_out('\x1b[1;49;32mThat\'s correct!!!\x1b[0m')
    wait(1.5)

# give a multiple choise question
def multiple_choise(words, settings, mode, info = '\n', list_words = []):
    good_answer = words[0]
    # shuffle words
    while words[0] == good_answer:
        shuffle(words)

    answers = []
    for i in words:
        answers.append(i[1])

    selected = 0
    check = False
    inp = ''

    while True:
        cls()
        # show info
        s_out(info)
        # show given word
        s_out(good_answer[0])
        # show options
        for i in range(len(words)):
            if selected == i:
                s_out(str(i + 1) + ' \x1b[7m' + words[i][1] + '\x1b[0m')
            else:
                s_out(str(i + 1) + ' ' + words[i][1])

        # ask input
        if settings[19]:
            inp = s_inp('Type a number or select with w/s or k/j.   > ', input = inp, enter_characters = ['w', 's', 'k', 'l', 'd', 'l', 'c', '\x1b[A', '\x1b[B', '\x1b[E'])
        else:
            inp = s_inp('Type a number, the whole word or select with arrows.   > ', input = inp, enter_characters = ['\x1b[A', '\x1b[B', '\x1b[E'])

        if type(inp) == tuple:
            key = inp[1]
            inp = inp[0]
            # up
            if key in ['w', 'k', '\x1b[A']:
                selected = selected - 1
                if selected < 0:
                    selected = len(words) - 1
            # down
            elif key in ['s', 'j', '\x1b[B']:
                selected = selected + 1
                if selected >= len(words):
                    selected = 0
            # check
            elif key in ['d', 'l', '\n', 'c', '\x1b[E']:
                if key == '\x1b[E':
                    s_out(('\x1b[D' * 4) + '     ')
                check = True
                answer = words[selected][1]
            else:
                s_out('Something went wrong... Restarting question...')
                wait(1.5)
                continue

        # numbers
        elif inp.isdigit():
            if 0 < int(inp) <= len(words) and inp in answers:
                choice = s_inp('You have typed \'' + inp + '\', but it\'s a number and a word. Choice \x1b[4mN\x1b[0mumber or \x1b[4mW\x1b[0mord \'' + inp + '\'?   > ', enter_characters = ['n', 'w'], invalid_characters = ['\n'])[1]
                if choice == 'n':
                    check = True
                    answer = words[int(inp) - 1][1]
                    break
                if choice == 'w':
                    check = True
                    answer = inp
                    break

            elif 0 < int(inp) <= len(words):
                check = True
                answer = words[int(inp) - 1][1]
            else:
                s_out('Something went wrong. Trying again.')
                wait(1.5)
                continue

        # some of the words
        elif inp in answers:
            check = True
            answer = inp

        # enter
        elif inp == '':
            check = True
            answer = words[selected][1]

        else:
            s_out('This isn\'t a correct input.')
            s_out('Press ctrl + backspace to delete your input.')
            wait(1.5)
            continue

        # check
        if check:
            if check_answer(good_answer[1], answer, settings):
                s_out('\x1b[1;49;32mThat\'s correct!!!\x1b[0m')
                wait(1.5)
                return True, answer
            
            else:
                s_out('\x1b[1;49;31mThat\'s wrong.\x1b[0m')
                if (settings[1] and mode == 'learn') or (settings[2] and mode == 'review'):
                    show_mistake(answer, good_answer[1], list_words)
                if mode == 'review':
                    ch = s_inp('Press enter to continue or esc to save as correct. ', enter_characters = ['\x1b'])
                    if type(ch) == tuple:
                        return True, answer
                    else:
                        return False, answer
                else:
                    s_inp('Press enter to continue. ')
                    return False, answer

# give a type question
def type_ex(word, settings, mode, list_words = []):
    # show given word
    s_out(word[0])
    s_out()
    # ask user
    iword = s_inp('Type the correct answer.   > ')
    
    # check
    if check_answer(iword, word[1], settings):
        s_out('\x1b[1;49;32mThat\'s correct!!!\x1b[0m')
        wait(1.5)
        return True, iword
    else:
        s_out('\x1b[1;49;31mThat\'s wrong.\x1b[0m')
        if (settings[1] and mode == 'learn') or (settings[2] and mode == 'review'):
            show_mistake(iword, word[1], list_words)
        if mode == 'review':
            ch = s_inp('Press enter to continue or esc to save as correct. ', enter_characters = ['\x1b'])
            if type(ch) == tuple:
                return True, iword
            else:
                return False, iword
        else:
            s_inp('Press enter to continue. ')
            return False, iword

def sentence(word, settings, mode, info, list_words = []):
    # zin splitsen in words_user
    words_user = word[1].split(' ')
    # words_user husselen
    shuffle(words_user)
    sentence_user = []
    selected = 0
    inp = ''
    check = False

    while True:
        cls()
        s_out(info)
        # show given word
        s_out(word[0])
        s_out()
        # show user sentence
        for i in range(len(sentence_user)):
            s_out(sentence_user[i] + ' ', end = '')
        s_out()
        s_out()
        # show words to choise
        for i in range(len(words_user)):
            aantal_keer_geselecteerd = sentence_user.count(words_user[i])
            hoeveelste_keer = words_user[:i].count(words_user[i])
            geel = hoeveelste_keer >= aantal_keer_geselecteerd
            if selected == i:
                if geel:
                    s_out('\x1b[7;49;33m' + str(i + 1) + '. ' + words_user[i] + '\x1b[0m', end = '')
                else:
                    s_out('\x1b[7m' + str(i + 1) + '. ' + words_user[i] + '\x1b[0m', end = '')

            else:
                if geel:
                    s_out('\x1b[1;49;33m' + str(i + 1) + '. ' + words_user[i] + '\x1b[0m', end = '')
                else:
                    s_out(str(i + 1) + '. ' + words_user[i], end = '')

            if i != (len(words_user) - 1):
                s_out('      ', end = '')

        s_out()
        s_out()
        s_out(str(len(sentence_user)) + ' / ' + str(len(words_user)))
        s_out()

        # ask input
        if settings[20]:
            inp = s_inp('Type a number, select with a/d or h/l and t to add or c to check.   > ', input = inp, enter_characters = ['a', 'd', 'h', 'l', 't', 'c', '\x1b[C', '\x1b[D', '\x1b[2~', '\t', '\x1d', '\x1b[E'])
        else:
            inp = s_inp('Type a number, word or the whole sentence, select with arrows, tab to add or enter to check.   > ', input = inp, enter_characters = ['\x1b[C', '\x1b[D', '\x1b[2~', '\t', '\x1d', '\x1b[E'])

        inp_without_spaces = inp
        try:
            while inp_without_spaces[0] == ' ':
                inp_without_spaces = inp_without_spaces[1:]
            while inp_without_spaces[-1] == ' ':
                inp_without_spaces = inp_without_spaces[:-1]
        except IndexError:
            inp_without_spaces = ''

        if type(inp) == tuple:
            key = inp[1]
            inp = inp[0]
            
            if key in ['a', 'h', '\x1b[D']:
                selected = selected - 1
                if selected < 0:
                    selected = len(words_user) - 1

            elif key in ['d', 'l', '\x1b[C']:
                selected = selected + 1
                if selected >= len(words_user):
                    selected = 0

            elif key in ['c', '\n', '\x1d']:
                check = True
                answer = ''
                for w in sentence_user:
                    answer = answer + ' ' + w

            elif key in ['t', '\x1b[2~', '\t', '\x1b[E']:
                if words_user[selected] not in sentence_user:
                    sentence_user.append(words_user[selected])
                elif words_user.count(words_user[selected]) > 1 and sentence_user.count(words_user[selected]) < words_user.count(words_user[selected]):
                    sentence_user.append(words_user[selected])
                elif words_user[selected] in sentence_user:
                    while words_user[selected] in sentence_user:
                        sentence_user.remove(words_user[selected])
                else:
                    s_out('\x1b[1;49;31mSomething went wrong.\x1b[0m')
                    wait(1.5)

        elif inp.isdigit():
            if 0 < int(inp) <= len(words_user) and inp in words_user:
                choice = s_inp('You have typed \'' + inp + '\', but it\'s a number and a word. Choice \x1b[4mN\x1b[0mumber or \x1b[4mW\x1b[0mord \'' + inp + '\'?   > ', enter_characters = ['n', 'w'], invalid_characters = ['\n'])[1]
                if choice == 'n':
                    if words_user[int(inp) - 1] not in sentence_user:
                        sentence_user.append(words_user[int(inp) - 1])
                    elif words_user.count(words_user[int(inp) - 1]) > 1 and sentence_user.count(words_user[int(inp) - 1]) < words_user.count(words_user[int(inp) - 1]):
                        sentence_user.append(words_user[int(inp) - 1])
                    elif words_user[int(inp) - 1] in sentence_user:
                        while words_user[int(inp) - 1] in sentence_user:
                            sentence_user.remove(words_user[int(inp) - 1])
                    else:
                        s_out('\x1b[1;49;31mSomething went wrong.\x1b[0m')
                        wait(1.5)

                if choice == 'w':
                    if inp not in sentence_user:
                        sentence_user.append(inp)
                    elif words_user.count(inp) > 1 and sentence_user.count(inp) < words_user.count(inp):
                        sentence_user.append(inp)
                    elif inp in sentence_user:
                        while inp in sentence_user:
                            sentence_user.remove(inp)
                    else:
                        s_out('\x1b[1;49;31mSomething went wrong.\x1b[0m')
                        wait(1.5)

            elif 0 < int(inp) <= len(words_user):
                if words_user[int(inp) - 1] not in sentence_user:
                    sentence_user.append(words_user[int(inp) - 1])
                elif words_user.count(words_user[int(inp) - 1]) > 1 and sentence_user.count(words_user[int(inp) - 1]) < words_user.count(words_user[int(inp) - 1]):
                    sentence_user.append(words_user[int(inp) - 1])
                elif words_user[int(inp) - 1] in sentence_user:
                    while words_user[int(inp) - 1] in sentence_user:
                        sentence_user.remove(words_user[int(inp) - 1])
                else:
                    s_out('\x1b[1;49;31mSomething went wrong.\x1b[0m')
                    wait(1.5)

            inp = ''

        elif inp in words_user:
            if inp not in sentence_user:
                sentence_user.append(inp)
            elif words_user.count(inp) > 1 and sentence_user.count(inp) < words_user.count(inp):
                sentence_user.append(inp)
            elif inp in sentence_user:
                while inp in sentence_user:
                    sentence_user.remove(inp)
            else:
                s_out('\x1b[1;49;31mSomething went wrong.\x1b[0m')
                wait(1.5)

            inp = ''

        elif inp_without_spaces in words_user:
            if inp_without_spaces not in sentence_user:
                sentence_user.append(inp_without_spaces)
            elif words_user.count(inp_without_spaces) > 1 and sentence_user.count(inp_without_spaces) < words_user.count(inp_without_spaces):
                sentence_user.append(inp_without_spaces)
            elif inp_without_spaces in sentence_user:
                while inp_without_spaces in sentence_user:
                    sentence_user.remove(inp_without_spaces)
            else:
                s_out('\x1b[1;49;31mSomething went wrong.\x1b[0m')
                wait(1.5)

            inp_without_spaces = ''
            inp = ''

        elif inp == '':
            check = True
            answer = ''
            for w in sentence_user:
                answer = answer + ' ' + w

        elif inp.count(' ') > 1:
            check = True
            answer = inp

        else:
            s_out('Something went wrong.')
            wait(1.5)

        if check:
            if answer.count(' ') == len(answer):
                s_out('\x1b[1;49;31mIt looks you don\'t have enter something. Try again.\x1b[0m')
                wait(1.5)
                check = False
                continue

            while answer[0] == ' ':
                answer = answer[1:]

            while answer[-1] == ' ':
                answer = answer[:-1]

            if check_answer(word[1], answer, settings):
                s_out('\x1b[1;49;32mThat\'s correct!!!\x1b[0m')
                wait(1.5)
                return True, answer

            else:
                s_out(answer)
                s_out('\x1b[1;49;31mThat\'s wrong.\x1b[0m')
                if settings[1]:
                    show_mistake(answer, word[1], list_words)
                if mode == 'review':
                    ch = s_inp('Press enter to continue or esc to save as correct. ', enter_characters = ['\x1b'])
                    if type(ch) == tuple:
                        return True, answer
                    else:
                        return False, answer
                else:
                    s_inp('Press enter to continue. ')
                    return False, answer

