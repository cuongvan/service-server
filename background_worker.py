import threading
import time
from queue import Queue
import traceback

#Routine that processes whatever you want as background

_task_queue = Queue()

SUCCESS = 'TASK_SUCCEEDED'

def run_forever():
    while True:
        try:
            func = _task_queue.get()
            try:
                ret = func()
                will_retry = (ret != SUCCESS)
            except Exception as e:
                will_retry = True
                traceback.print_exc(limit=5)

            if will_retry:
                _task_queue.put(func)
            time.sleep(1)
        except KeyboardInterrupt:
            return
        except Exception as e:
            traceback.print_exc(limit=10)
            pass


def start_worker():
    t1 = threading.Thread(target=run_forever)
    t1.setDaemon(True)
    t1.start()
    del t1

def submit_task(task, *args, **kargs):
    _task_queue.put(lambda : task(*args, **kargs))
