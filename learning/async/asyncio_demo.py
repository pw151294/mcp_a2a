import asyncio
import time


async def make_coffer_async(consumer: str) -> str:
    print(f"开始为 {consumer} 制作咖啡...")
    await asyncio.sleep(5)
    print(f"{consumer} 的咖啡制作完成！")
    return f"{consumer} 的咖啡"


async def main_async():
   start_time = time.time()

   task = [
       make_coffer_async("Alice"),
       make_coffer_async("Bob"),
   ]
   results = await asyncio.gather(*task)
   print(results)

   end_time = time.time()
   print(f"总耗时: {end_time - start_time:.2f} 秒")

if __name__ == '__main__':
    asyncio.run(main_async())