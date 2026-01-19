import multiprocessing

from learning.decorators import timer
from multi_thread_demo import urls, download_site


@timer
def multi_processing_demo():
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.map(download_site, urls)
    print(results)

if __name__ == '__main__':
    multi_processing_demo()

