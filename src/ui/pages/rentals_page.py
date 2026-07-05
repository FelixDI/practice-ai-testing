"""RentalsPage —— 租赁工具列表页。
路由: /rentals
无登录要求。

纯静态展示页，列出可租赁的重型工具（挖掘机/推土机/起重机）。
每张卡片含图片、名称、描述，无交互操作（不可点击、无加购）。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class RentalsPage(BasePage):
    """Toolshop 租赁工具列表页。"""

    BASE_URL = "https://practicesoftwaretesting.com/rentals"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """导航到租赁列表页并等待渲染。"""
        super().goto(self.BASE_URL)
        self.wait_for_page("[data-test=nav-home]")

    # -- 页面标题 -----------------------------------------------------------

    @property
    def page_title(self) -> Locator:
        return self._page.locator("[data-test=page-title]")

    # -- 租赁卡片列表 -------------------------------------------------------

    @property
    def rental_cards(self) -> Locator:
        """所有租赁卡片容器（data-test 以 product- 开头）。"""
        return self._page.locator('[data-test^="product-"]')

    def rental_card(self, index: int) -> Locator:
        """第 index 张租赁卡片。"""
        return self.rental_cards.nth(index)

    @property
    def first_card(self) -> Locator:
        return self.rental_cards.first

    def card_image(self, index: int) -> Locator:
        return self.rental_card(index).locator("img")

    def card_title(self, index: int) -> Locator:
        return self.rental_card(index).locator("h5.card-title")

    def card_description(self, index: int) -> Locator:
        return self.rental_card(index).locator("p.card-text")
