import os

if os.name == 'nt':
    def timeout(functie, tijd = 1, *args):
        return functie(*args)
    
else:
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError

    def timeout(functie, tijd = 1, *args):
        if os.name == 'nt':
            timer = threading.Timer(tijd, timeout_handler)
            timer.start()
        else:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(tijd)

        output = None

        try:
            output = functie(*args)
        finally:
            if os.name == 'nt':
                timer.cancel()
            else:
                signal.alarm(0)

        return output
