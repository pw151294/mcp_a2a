import time

from timeloop import Timeloop
from asyncpg.pgproto.pgproto import timedelta

tl = Timeloop()

@tl.job(interval=timedelta(seconds=1))
def sample_job_every_1s():
    print('1s job current time: {}'.format(time.ctime()))

@tl.job(interval=timedelta(seconds=5))
def sample_job_every_5s():
    print('5s job current time: {}'.format(time.ctime()))

@tl.job(interval=timedelta(seconds=10))
def sample_job_every_10s():
    print('10s job current time: {}'.format(time.ctime()))

if __name__ == '__main__':
    # 启动 Timeloop 调度器
    tl.start(block=True)
