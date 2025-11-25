# import modules
from time import sleep as wait
import os

from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out, cls

from questions import retype, show_word

# set functions
# go through the words
def go_through(list_words, name, settings):
    cls()
    # ask wich session
    choice = s_inp('Do you want to view or type over the words? (v/o)   > ')
    options = ['v', 'o']
    while choice not in options:
        cls()
        # ask again
        choice = s_inp('Do you want to view or type over the words? (v/o)   > ')

    if choice == 'v':
        go_watch(list_words)
    else:
        go_retype(list_words)

# view words
def go_watch(words):
    for i in range(len(words)):
        try:
            cls()
            # show state
            s_out(str(i + 1) + '/' + str(len(words)))
            s_out()
            # view word
            show_word(words[i])
            s_out('Next.')
            if i != (len(words) - 1): wait(1.5)
        except KeyboardInterrupt:
            s_out()
            if s_inp('Do you want to quit? (yes/no)   > ') == 'yes':
                return ''
            else:
                continue

    # back to home
    s_out('You have had all words!!!')
    s_out('Back to home...')
    wait(1.5)

# retype words
def go_retype(words):
    for i in range(len(words)):
        try:
            cls()
            # show state
            s_out(str(i + 1) + '/' + str(len(words)))
            s_out()
            # ask question
            retype(words[i])
        except KeyboardInterrupt:
            s_out()
            if s_inp('Do you want to quit? (yes/no)   > ') == 'yes':
                return ''
            else:
                continue

    # back to home
    s_out('You have had all words!!!')
    s_out('Back to home...')
    wait(1.5)

