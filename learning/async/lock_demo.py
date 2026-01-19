import asyncio
import threading

counter: int = 0

def increment_counter():
    global counter
    counter += 1

def increment_counters():
    threads = []
    for i in range(1000):
        thread = threading.Thread(target=increment_counter)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

async def async_increment_counter():
    global counter
    counter += 1
async def async_increment_counters():
    tasks = []
    for _ in range(10000):
        task = asyncio.create_task(async_increment_counter())
        tasks.append(task)
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(async_increment_counters())
    print(counter)