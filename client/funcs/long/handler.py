import time
def handle(req):
    to_sleep = 10
    time.sleep(to_sleep)
    return "Slept %d seconds" % to_sleep

