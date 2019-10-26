import time
def handle(req):
    time.sleep(1)
    return {
        'msg': "Ok, slept for 1 secs"
    }

