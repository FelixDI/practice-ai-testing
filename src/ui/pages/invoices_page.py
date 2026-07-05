"""InvoicesPage —— 订单列表页。
路由: /account/invoices
需要登录。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class InvoicesPage(BasePage):
    """Toolshop 订单列表页。"""

    BASE_URL = "https://practicesoftwaretesting.com/account/invoices"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    def goto(self) -> None:
        super().goto(self.BASE_URL)

    @property
    def page_title(self) -> Locator:
        return self._page.locator("[data-test=page-title]")
