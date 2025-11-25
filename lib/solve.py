# import modules
from time import sleep as wait

from extern.save_input import save_input as s_inp
from extern.save_output import save_output as s_out

from errors import WordIndexError
from functions import get_scores
from manage_files import create_list

def solve(pad_bestand):
    try:
        file = open(pad_bestand)
        data = file.read()
        file.close()
    except UnicodeDecodeError:
        solve_decodeerror(pad_bestand)
    except:
        s_out('Unknown error.')
        wait(1.5)
    else:
        try:
            lijst = create_list(data)
        except ValueError:
            solve_valueerror(pad_bestand)
        except:
            s_out('Unknown error.')
            wait(1.5)
        else:
            try:
                scores = get_scores(lijst)
            except WordIndexError:
                solve_wordindexerror(pad_bestand)
            else:
                s_out('Nothing wrong. Going back.')
                wait(1.5)

def solve_decodeerror(pad_bestand):
    file = open(pad_bestand, 'br')
    data = file.read()
    file.close()

    while True:
        try:
            nieuwe_data = data.decode()
            file = open(pad_bestand, mode = 'w')
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
            file = open(pad_bestand, mode = 'bw')
            file.write(data)
            file.close()
            s_inp('A error is solved.   > ')
            return ''
        
        foute_karakter = str(error)[34:36]
        s_out(eval('b\'\\x' + foute_karakter + '\''), b'\\' + foute_karakter.encode())
        data = data.replace(eval('b\'\\x' + foute_karakter + '\''), b'\\' + foute_karakter.encode())

def solve_valueerror(pad_bestand):
    file = open(pad_bestand)
    data = file.read()
    file.close()

    while True:
        lijst_data = data.split('\n')
        for regel in lijst_data:
            try:
                create_list(regel)
            except ValueError:
                s_out('This line can\'t be readed by the computer: ' + regel)
                data = data.replace(regel, s_inp('Type what it must be.   > ', input = regel))
        try:
            create_list(data)
        except ValueError:
            continue
        else:
            break

    file = open(pad_bestand, mode = 'w')
    file.write(data)
    file.close()
    
def solve_wordindexerror(pad_bestand):
    file = open(pad_bestand)
    data = file.read()
    file.close()

    while True:
        gedaan = False
        lijst_data = data.split('\n')
        for regel in lijst_data:
            try:
                if regel != '': get_scores([regel])
            except WordIndexError:
                s_out('This line can\'t be processed by the computer. The word index is invalid. [str, str, int, int, int, int]: ' + regel)
                data = data.replace(regel, s_inp('Type what it must be.   > ', input = regel))
                gedaan = True
        try:
            get_scores(data)
        except WordIndexError:
            continue
        else:
            break

        if not gedaan:
            break

    file = open(pad_bestand, mode = 'w')
    file.write(data)
    file.close()

