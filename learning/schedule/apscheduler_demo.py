import time
from datetime import date

from apscheduler.schedulers.blocking import BlockingScheduler


def job():
    print('current time: {}'.format(time.ctime()))


if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(job, 'interval', seconds=1)
    sched.add_job(job, 'date', run_date=date(2024, 6, 30), args=['text'])
    sched.add_job(job, 'date', run_date=date(2024, 7, 1), args=['text'])

    # 6-8,11-12月第三个周五 00:00, 01:00, 02:00, 03:00运行
    sched.add_job(job, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')
    # 每周一到周五运行 直到2024-05-30 00:00:00
    sched.add_job(job, 'cron', day_of_week='mon-fri', hour=5, minute=30, end_date='2024-05-30')
    sched.start()
