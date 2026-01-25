import asyncio
import logging

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def example():
    # 创建一个playwright异步实例
    async with async_playwright() as playwright:
        # 连接到cdp获取浏览器的实例
        browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]

        # 获取当前上下文的第一个页面
        page = default_context.pages[0]
        logger.info(f"页面标题：{await page.title()}")
        logger.info(f"页面URL：{page.url}")

        # 新增页面并且跳转到imooc.com
        page = await default_context.new_page()
        await page.goto("https://imooc.com")

        # 在页面上执行JS代码并获取结果
        href = await page.evaluate('() => document.location.href')
        logger.info(f"js执行结果：{href}")

        # 截图
        await page.screenshot(path="resources/screenshot.png")
        await page.screenshot(path="resources/screenshot-full.png", full_page=True)

if __name__ == "__main__":
    asyncio.run(example())