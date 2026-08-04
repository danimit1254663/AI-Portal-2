import queue
import time
import queue


audio_queue = queue.Queue()


microphone_enabled = True

assistant_running = True
hud_visible = True

audio_queue = queue.Queue()


active_until = 0



def activate(seconds=10):

    global active_until

    active_until = (
        time.time()
        +
        seconds
    )



def is_active():

    return time.time() < active_until