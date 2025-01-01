import time
import os
from flask_socketio import SocketIO

socketio = SocketIO(message_queue='redis://')

def watch_css(directory):
    css_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.css')]
    last_modified_times = {f: os.path.getmtime(f) for f in css_files}

    while True:
        time.sleep(1)
        for f in css_files:
            if os.path.getmtime(f) != last_modified_times[f]:
                last_modified_times[f] = os.path.getmtime(f)
                socketio.emit('reload')
                print(f'{f} changed, reloading...')

if __name__ == "__main__":
    watch_css('/c:/Users/d.blom/Projecten/Rekening daan/rekening-daan/static')
