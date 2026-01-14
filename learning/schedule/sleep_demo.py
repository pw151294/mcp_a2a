import datetime
import time

def time_printer():
    now = datetime.datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    print(ts)

def loop_monitor():
    while True:
        time_printer()
        time.sleep(3)

if __name__ == "__main__":
    loop_monitor()
