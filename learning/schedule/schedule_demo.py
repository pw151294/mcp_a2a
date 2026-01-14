import time

import schedule
from schedule import repeat

i = 0


def some_task():
    global i  # 修复变量作用域问题
    i += 1
    print(i)
    if i == 10:
        schedule.clear()  # 清除所有任务
        print('All jobs canceled')
        exit(0)


@repeat(schedule.every().second)
def repeat_job():
    print("I'm working...")


def job_that_executes_once():
    print("I'm working...")
    return schedule.CancelJob  # 确保任务只执行一次


def job():
    schedule.every(10).seconds.do(lambda: print("I'm working..."))
    schedule.every(10).minutes.do(lambda: print("I'm working..."))
    schedule.every().hour.do(lambda: print("I'm working..."))
    schedule.every().day.at('10:30').do(lambda: print("I'm working..."))
    schedule.every(5).to(10).minutes.do(lambda: print("I'm working..."))
    schedule.every().monday.do(lambda: print("I'm working..."))
    schedule.every().wednesday.at('13:15').do(lambda: print("I'm working)..."))
    schedule.every().minute.at(':17').do(lambda: print("I'm working..."))


if __name__ == '__main__':
    # job() 如果需要一次性添加多个任务，可以取消注释这一行
    pass

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # 取消任务
    # schedule.every().second.do(some_task)
    # 主循环
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # 只执行一次的任务
    schedule.every().minute.at(':30').do(job_that_executes_once)
    while True:
        schedule.run_pending()
        time.sleep(1)
