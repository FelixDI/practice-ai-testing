"""HomePage —— 首页 / 商品列表。
路由: /
无登录要求。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage


class HomePage(BasePage):
    """Toolshop 首页，展示商品列表、分类导航、搜索框。"""

    URL = "https://practicesoftwaretesting.com/"

    # -- Navigation -------------------------------------------------------

    def goto(self) -> None:
        """导航到首页并等待关键元素渲染。"""
        super().goto(self.URL)
        self.wait_for_page("[data-test=nav-home]")

    # -- 搜索 -------------------------------------------------------------

    @property
    def search_input(self) -> Locator:
        return self._page.locator("[data-test=search-query]")

    def search(self, query: str) -> None:
        self.search_input.fill(query)
        self.search_input.press("Enter")

    # -- 导航栏 -----------------------------------------------------------

    @property
    def nav_home(self) -> Locator:
        return self._page.locator("[data-test=nav-home]")

    @property
    def nav_categories(self) -> Locator:
        return self._page.locator("[data-test=nav-categories]")

    @property
    def nav_sign_in(self) -> Locator:
        return self._page.locator("[data-test=nav-sign-in]")

    @property
    def nav_hand_tools(self) -> Locator:
        return self._page.locator("[data-test=nav-hand-tools]")

    def navigate_to_category(self, category: str) -> None:
        """展开 Categories 菜单并点击指定分类。"""
        self.nav_categories.click()
        self._page.locator(f"[data-test=nav-{category}]").click()

    # -- 排序 -------------------------------------------------------------

    @property
    def sort_select(self) -> Locator:
        return self._page.locator("[data-test=sort]")

    # -- 商品列表 ---------------------------------------------------------

    @property
    def product_cards(self) -> Locator:
        return self._page.locator("a[href*='/product/']")
