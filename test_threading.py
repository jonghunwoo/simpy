from random import random
import threading
import time

result = None
result_available = threading.Event()

def background_calculation():
    # here goes some long calculation
    time.sleep(5)

    # when the calculation is done, the result is stored in a global variable
    global result
    result = 42
    result_available.set()

    # do some more work before exiting the thread
    time.sleep(10)

def main():

    #thread = threading.Thread(target=background_calculation)
    #thread.start()

    # wait here for the result to be available before continuing
    result_available.wait()

    print('The result is', result)

if __name__ == '__main__':
    main()