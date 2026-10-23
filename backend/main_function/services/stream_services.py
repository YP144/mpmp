import time
import threading
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from services.db_services import get_machine_data

data_cache = []

def stream_data():
    global data_cache
    while True:
        data_cache = get_machine_data()
        time.sleep(2)

def start_stream():
    thread = threading.Thread(target=stream_data)
    thread.start()

if __name__ == "__main__":
    start_stream()
    time.sleep(2)
    print (data_cache)