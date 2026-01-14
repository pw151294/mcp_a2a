import sched
import time
import datetime


def time_printer():
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func time :', ts)
    loop_monitor()


def loop_monitor():
    s = sched.scheduler(time.time, time.sleep)
    s.enter(1, 1, time_printer, ())  # 安排一个事件来延迟delay个时间单位
    s.run()


if __name__ == '__main__':
    loop_monitor()