import logging
import datetime

class WordIndexError(Exception):
    def __init__(self, message = ''):
        super().__init__(message)
        self.message = message

class ClosedTerminalError(Exception):
    def __init__(self, message = ''):
        super().__init__(message)
        self.message = message

class ProcessKilledError(Exception):
    def __init__(self, message = ''):
        super().__init__(message)
        self.message = message

class NotInListError(Exception):
    def __init__(self, message = ''):
        super().__init__(message)
        self.message = message

logging.basicConfig(filename = <path_to_log>, level = logging.ERROR)

def log_error(data = ''):
    logging.exception(str(datetime.datetime.now()) + (':' if data else '') + data)

