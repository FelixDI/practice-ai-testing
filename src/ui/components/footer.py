"""Footer —— 页脚组件。

跨所有页面复用。包含 Demo 声明、GitHub 链接、隐私政策、图片版权。
注意：Footer 链接无 data-test 属性，使用文本定位。
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator


class Footer:
    """Toolshop 页脚，含声明文本、外链、聊天按钮。"""

    def __init__(self, page: Page) -> None:
        self._page = page

    # -- 页脚文本段落 -------------------------------------------------------

    @property
    def container(self) -> Locator:
        """页脚段落（无 data-test，通过文本特征定位）。"""
        return self._page.locator("p:has-text('DEMO application')")

    # -- 链接（文本定位，无 data-test）--------------------------------------

    @property
    def github_link(self) -> Locator:
        return self._page.locator("a:has-text('GitHub repo')")

    @property
    def privacy_link(self) -> Locator:
        return self._page.locator("a:has-text('Privacy Policy')")

    @property
    def barn_images_link(self) -> Locator:
        return self._page.locator("a:has-text('Barn Images')")

    @property
    def unsplash_link(self) -> Locator:
        return self._page.locator("a:has-text('Unsplash')")

    # -- 聊天按钮（有 data-test）--------------------------------------------

    @property
    def chat_toggle(self) -> Locator:
        return self._page.locator("[data-test=chat-toggle]")
