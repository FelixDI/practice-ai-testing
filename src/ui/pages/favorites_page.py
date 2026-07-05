"""FavoritesPage —— 收藏夹页。
路由: /account/favorites
需要登录。

展示用户收藏的商品列表。新账号无收藏时为空页面。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class FavoritesPage(BasePage):
    """Toolshop 收藏夹页。"""

    BASE_URL = "https://practicesoftwaretesting.com/account/favorites"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """导航到收藏夹页（需已登录）。"""
        super().goto(self.BASE_URL)

    # -- 页面内容 -----------------------------------------------------------

    @property
    def page_title(self) -> Locator:
        return self._page.locator("[data-test=page-title]")
