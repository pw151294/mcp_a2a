import threading

import requests

from learning.decorators import timer

urls = [
    "https://www.python.org",
    "https://www.baidu.com/",
    "https://goproxy.cn/"]


def download_site(url: str):
    """模拟io密集型任务"""
    response = requests.get(url)
    print(f"Read {len(response.content)} bytes from {url}")


@timer
def download_sites():
    threads = []
    for url in urls:
        thread = threading.Thread(target=download_site, args=(url,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    download_sites()
