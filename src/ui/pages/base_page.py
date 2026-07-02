"""BasePage —— 所有页面对象的基类。

封装公共页面操作：
- goto / 等待渲染
- 页面标题
- 通知栏（跨页面存在）
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator


class BasePage:
    """页面对象基类。"""

    def __init__(self, page: Page) -> None:
        self._page = page

    # -- Navigation -------------------------------------------------------

    def goto(self, url: str) -> None:
        """导航到指定 URL（domcontentloaded + 手动等待元素更可靠）。"""
        self._page.goto(url, wait_until="domcontentloaded")

    def wait_for_page(self, selector: str, timeout: int = 15000) -> None:
        """等待关键元素出现，确认页面渲染完成。"""
        self._page.wait_for_selector(selector, timeout=timeout)

    @property
    def title(self) -> str:
        return self._page.title()

    # -- 公共元素 ---------------------------------------------------------

    @property
    def notification_bar(self) -> Locator:
        return self._page.locator("[data-test=notification-bar]")
