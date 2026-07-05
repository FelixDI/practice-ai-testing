"""AccountDashboard —— 账户概览页（登录落地页）。
路由: /account
需要登录。

登录后自动跳转，展示 H1 "My account" + 4 个功能入口按钮（Favorites/Profile/Invoices/Messages）。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class AccountDashboard(BasePage):
    """Toolshop 账户概览页（登录后自动跳转的落地页）。"""

    BASE_URL = "https://practicesoftwaretesting.com/account"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """直接访问账户页（未登录会重定向到 /auth/login）。"""
        super().goto(self.BASE_URL)

    # -- 页面内容 -----------------------------------------------------------

    @property
    def page_heading(self) -> Locator:
        return self._page.locator("h1")

    @property
    def favorites_button(self) -> Locator:
        return self._page.get_by_role("button", name="Favorites")

    @property
    def profile_button(self) -> Locator:
        return self._page.get_by_role("button", name="Profile")

    @property
    def invoices_button(self) -> Locator:
        return self._page.get_by_role("button", name="Invoices")

    @property
    def messages_button(self) -> Locator:
        return self._page.get_by_role("button", name="Messages")
