# import modules
from time import sleep as wait

from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out

from errors import WordIndexError
from functions import get_scores
from manage_files import create_list

def solve(path_file):
    try:
        file = open(path_file)
        data = file.read()
        file.close()
    except UnicodeDecodeError:
        solve_decodeerror(path_file)
    except:
        s_out('Unknown error.')
        wait(1.5)
    else:
        try:
            created_list = create_list(data)
        except ValueError:
            solve_valueerror(path_file)
        except:
            s_out('Unknown error.')
            wait(1.5)
        else:
            try:
                scores = get_scores(created_list)
            except WordIndexError:
                solve_wordindexerror(path_file)
            else:
                s_out('Nothing wrong. Going back.')
                wait(1.5)

def solve_decodeerror(path_file):
    file = open(path_file, 'br')
    data = file.read()
    file.close()

    while True:
        try:
            nieuwe_data = data.decode()
            file = open(path_file, mode = 'w')
            file.write(nieuwe_data)
            file.close()
            s_inp('A error is solved.   > ')
            return ''
        
        except UnicodeDecodeError as decodeerror:
            error = decodeerror
            
        except:
            s_inp('Unknown error. Press enter to continue.   > ')
            return ''
            
        else:
            file = open(path_file, mode = 'bw')
            file.write(data)
            file.close()
            s_inp('A error is solved.   > ')
            return ''
        
        foute_karakter = str(error)[34:36]
        s_out(eval('b\'\\x' + foute_karakter + '\''), b'\\' + foute_karakter.encode())
        data = data.replace(eval('b\'\\x' + foute_karakter + '\''), b'\\' + foute_karakter.encode())

def solve_valueerror(path_file):
    file = open(path_file)
    data = file.read()
    file.close()

    while True:
        list_data = data.split('\n')
        for line in list_data:
            try:
                create_list(line)
            except ValueError:
                s_out('This line can\'t be readed by the computer: ' + line)
                data = data.replace(line, s_inp('Type what it must be.   > ', input = line))
        try:
            create_list(data)
        except ValueError:
            continue
        else:
            break

    file = open(path_file, mode = 'w')
    file.write(data)
    file.close()
    
def solve_wordindexerror(path_file):
    file = open(path_file)
    data = file.read()
    file.close()

    while True:
        gedaan = False
        list_data = data.split('\n')
        for line in list_data:
            try:
                if line != '': get_scores([line])
            except WordIndexError:
                s_out('This line can\'t be processed by the computer. The word index is invalid. [str, str, int, int, int, int]: ' + line)
                data = data.replace(line, s_inp('Type what it must be.   > ', input = line))
                gedaan = True
        try:
            get_scores(data)
        except WordIndexError:
            continue
        else:
            break

        if not gedaan:
            break

    file = open(path_file, mode = 'w')
    file.write(data)
    file.close()

