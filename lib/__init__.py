# Learning program: learn words, sentences and grammer
# Autor:   Quinten Taminiau
# Date:    25-11-2025
# Version: 3.1
# Python:  3.11

import os
import sys
import signal

from errors import log_error, ProcessKilledError, ClosedTerminalError

def show_users(show_info):
    from manage_files import ch_path, get_list

    if show_info:
        from extra_functions import ch_time, get_user_size, ch_size
        from time import time
        
    users = os.listdir(ch_path('~/'))
    for user in users:
        print(user, end = '')
        if show_info:
            print(' ' * ((os.get_terminal_size().columns - len(users)) - 14), end = '')
            last_time_learned = get_list(user, 'userinfo')[1]
            print(ch_time(time() - last_time_learned)[0], end = ' ')
            print(ch_size(get_user_size(user)), end = '')

    print()
    if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

# TODO: add run command

def run_cmd(command, username):
    pass

# set signals
def keyboardinterrupt(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, keyboardinterrupt)

def processkilled(signum, frame):
    raise ProcessKilledError

signal.signal(signal.SIGTERM, processkilled)

def closedterminal(signum, frame):
    raise ClosedTerminalError

if os.name != 'nt':
    signal.signal(signal.SIGHUP, closedterminal)

# parameters
args = sys.argv

if len(args) > 1:
    if args[1][0] == '-':
        if len(args[1]) > 1:
            if args[1][1] != '-':
                string = args[1][1:]
                del args[1]
                for count in range(len(string)):
                    args.insert(count + 1, '-' + string[count])

extra_information = False
quiet = False

if '-q' in args:
    quiet = True
    args.remove('-q')

if '-e' in args:
    extra_information = True
    args.remove('-e')

if '-i' in args:
    extra_information = True
    args.remove('-i')

# setup program
if len(args) == 1:
    from main import login
    try:
        login() 
        exit()
    except Exception as exception:
        if type(exception) != SystemExit:
            print('\nProgram ended with exit-code 1.')
            log_error()
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
            exit(1)
        else:
            exit()

# commands
if 'users' in args:
    show_users(extra_information)
    args.remove('users')

if '--users' in args:
    show_users(extra_information)
    args.remove('--users')

if '-u' in args:
    show_users(extra_information)
    args.remove('-u')

if 'create' in args:
    from manage_files import create
    try:
        create(args[args.index('create') + 1])
        del args[args.index('create') + 1]
        args.remove('create')
    except IndexError:
        print('Missing username (create).')
        args.remove('create')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('create')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '--create' in args:
    from manage_files import create
    try:
        create(args[args.index('--create') + 1])
        del args[args.index('--create') + 1]
        args.remove('--create')
    except IndexError:
        print('Missing username (create).')
        args.remove('--create')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('--create')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '-c' in args:
    from manage_files import create
    try:
        create(args[args.index('-c') + 1])
        del args[args.index('-c') + 1]
        args.remove('-c')
    except IndexError:
        print('Missing username (create).')
        args.remove('-c')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('-c')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if 'delete' in args:
    from manage_files import delete
    try:
        if (input('Are you sure to delete \'' + args[args.index('-d') + 1] + '\'? (y/n)   > ') == 'y' if not quiet else True):
            delete(args[args.index('delete') + 1])
            del args[args.index('delete') + 1]
            args.remove('delete')
    except IndexError:
        print('Missing username (delete).')
        args.remove('delete')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('delete')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '--delete' in args:
    from manage_files import delete
    try:
        if (input('Are you sure to delete \'' + args[args.index('-d') + 1] + '\'? (y/n)   > ') == 'y' if not quiet else True):
            delete(args[args.index('--delete') + 1])
            del args[args.index('--delete') + 1]
            args.remove('--delete')
    except IndexError:
        print('Missing username (delete).')
        args.remove('--delete')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('--delete')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '-d' in args:
    from manage_files import delete
    try:
        if (input('Are you sure to delete \'' + args[args.index('-d') + 1] + '\'? (y/n)   > ') == 'y' if not quiet else True):
            delete(args[args.index('-d') + 1])
            del args[args.index('-d') + 1]
            args.remove('-d')
    except IndexError:
        print('Missing username (delete).')
        args.remove('-d')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('-d')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if 'login' in args:
    from main import login
    try:
        login(args[args.index('login') + 1])
        del args[args.index('login') + 1]
        args.remove('login')
    except IndexError:
        print('Missing username (login).')
        args.remove('login')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('login')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '--login' in args:
    from main import login
    try:
        login(args[args.index('--login') + 1])
        del args[args.index('--login') + 1]
        args.remove('--login')
    except IndexError:
        print('Missing username (login).')
        args.remove('--login')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('--login')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '-l' in args:
    from main import login
    try:
        login(args[args.index('-l') + 1])
        del args[args.index('-l') + 1]
        args.remove('-l')
    except IndexError:
        print('Missing username (login).')
        args.remove('-l')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        args.remove('-l')
        if type(error) != SystemExit:
            log_error()
            print(error)
            if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if 'log' in args:
    try:
        if args[args.index('log') + 1] == 'clear':
            file = open(<path_to_log>, mode = 'w')
            file.write('')
            file.close()
            args.remove('clear')
        else:
            file = open(<path_to_log>)
            print(file.read())
            file.close()
            if os.name == 'nt' and not quiet: input('\n\n\n\n\nPress enter to close the program. ')

    except:
        file = open(<path_to_log>)
        print(file.read())
        file.close()
        if os.name == 'nt' and not quiet: input('\n\n\n\n\nPress enter to close the program. ')

    args.remove('log')

if '--log' in args:
    try:
        if args[args.index('--log') + 1] == 'clear':
            file = open(<path_to_log>, mode = 'w')
            file.write('')
            file.close()
            args.remove('clear')
        else:
            file = open(<path_to_log>)
            print(file.read())
            file.close()
            if os.name == 'nt' and not quiet: input('\n\n\n\n\nPress enter to close the program. ')

    except:
        file = open(<path_to_log>)
        print(file.read())
        file.close()
        if os.name == 'nt' and not quiet: input('\n\n\n\n\nPress enter to close the program. ')

    args.remove('--log')

if '-L' in args:
    try:
        if args[args.index('-L') + 1] == 'clear':
            file = open(<path_to_log>, mode = 'w')
            file.write('')
            file.close()
            args.remove('clear')
        else:
            file = open(<path_to_log>)
            print(file.read())
            file.close()
            if os.name == 'nt' and not quiet: input('\n\n\n\n\nPress enter to close the program. ')

    except:
        file = open(<path_to_log>)
        print(file.read())
        file.close()
        if os.name == 'nt' and not quiet: input('\n\n\n\n\nPress enter to close the program. ')

    args.remove('-L')

if 'logpath' in args:
    print(<path_to_log>)
    args.remove('logpath')

if '--logpath' in args:
    print(<path_to_log>)
    args.remove('--logpath')

if 'update' in args:
    from update import update
    update(<path_to_info>)
    args.remove('update')

if '--update' in args:
    from update import update
    update(<path_to_info>)
    args.remove('--update')

if '-U' in args:
    from update import update
    update(<path_to_info>)
    args.remove('-U')

if 'name' in args:
    try:
        username_run = args[args.index('name') + 1]
        del args[args.index('name') + 1]
    except:
        print('Missing username.')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

    args.remove('name')

if '--name' in args:
    try:
        username_run = args[args.index('--name') + 1]
        del args[args.index('--name') + 1]
    except:
        print('Missing username.')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

    args.remove('--name')

if '-n' in args:
    try:
        username_run = args[args.index('-n') + 1]
        del args[args.index('-n') + 1]
    except:
        print('Missing username.')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

    args.remove('-n')

if 'run' in args:
    try:
        run_cmd(args[1:], username_run)
    except NameError:
        print('Error: No username given, type \'-n <username>\' before the run command.')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        log_error()
        print(error)
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '--run' in args:
    try:
        run_cmd(args[1:], username_run)
    except NameError:
        print('Error: No username given, type \'-n <username>\' before the run command.')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        log_error()
        print(error)
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if '-r' in args:
    try:
        run_cmd(args[1:], username_run)
    except NameError:
        print('Error: No username given, type \'-n <username>\' before the run command.')
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')
    except Exception as error:
        log_error()
        print(error)
        if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

if len(args) > 1:
    print('Unknown command(s).')
    print(str(args[1:])[1:][:-1])
    if os.name == 'nt' and not quiet: input('Press enter to close the program. ')

