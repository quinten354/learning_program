# import modules
from extern.save_output import save_output as s_out

from menu import main_menu
from errors import log_error
from users import login, logout

# set main function
def main():
    while True:
        name, userinfo = login()
        try:
            output = main_menu(name, userinfo)
            if output:
                if not userinfo[4]:
                    logout(name, userinfo)
                continue
        except SystemExit:
            if not userinfo[4]:
                logout(name, userinfo)
            exit()
        except Exception as error:
            log_error()
            s_out('Something went wrong.')
        if not userinfo[4]:
            logout(name, userinfo)
        exit()

if __name__ == '__main__':
    main()

