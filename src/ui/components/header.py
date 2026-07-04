"""Header —— 顶部导航栏组件。

跨所有页面复用，含三区：
- 公共导航：11 个 nav-* 链接（含 nav-cart）+ 语言切换
- 登录态导航：7 个 nav-* 链接（用户菜单）
- 搜索：仅列表页（HomePage / CategoryPage）出现
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator


class Header:
    """Toolshop 顶部导航栏，封装导航链接、购物车、搜索、语言切换。"""

    def __init__(self, page: Page) -> None:
        self._page = page

    # -- 公共导航 -------------------------------------------------------------

    @property
    def nav_home(self) -> Locator:
        return self._page.locator("[data-test=nav-home]")

    @property
    def nav_categories(self) -> Locator:
        return self._page.locator("[data-test=nav-categories]")

    @property
    def nav_hand_tools(self) -> Locator:
        return self._page.locator("[data-test=nav-hand-tools]")

    @property
    def nav_power_tools(self) -> Locator:
        return self._page.locator("[data-test=nav-power-tools]")

    @property
    def nav_other(self) -> Locator:
        return self._page.locator("[data-test=nav-other]")

    @property
    def nav_special_tools(self) -> Locator:
        return self._page.locator("[data-test=nav-special-tools]")

    @property
    def nav_rentals(self) -> Locator:
        return self._page.locator("[data-test=nav-rentals]")

    @property
    def nav_contact(self) -> Locator:
        return self._page.locator("[data-test=nav-contact]")

    @property
    def nav_sign_in(self) -> Locator:
        return self._page.locator("[data-test=nav-sign-in]")

    # -- 购物车（始终可见）--------------------------------------------------

    @property
    def nav_cart(self) -> Locator:
        """购物车按钮，点击跳转到 /checkout。"""
        return self._page.locator("[data-test=nav-cart]")

    @property
    def cart_quantity(self) -> Locator:
        """购物车角标，显示商品数量。"""
        return self._page.locator("[data-test=cart-quantity]")

    # -- 登录态导航 ---------------------------------------------------------

    @property
    def nav_menu(self) -> Locator:
        """登录后出现在导航栏的用户菜单按钮（汉堡图标）。"""
        return self._page.locator("[data-test=nav-menu]")

    @property
    def nav_my_account(self) -> Locator:
        return self._page.locator("[data-test=nav-my-account]")

    @property
    def nav_my_favorites(self) -> Locator:
        return self._page.locator("[data-test=nav-my-favorites]")

    @property
    def nav_my_profile(self) -> Locator:
        return self._page.locator("[data-test=nav-my-profile]")

    @property
    def nav_my_invoices(self) -> Locator:
        return self._page.locator("[data-test=nav-my-invoices]")

    @property
    def nav_my_messages(self) -> Locator:
        return self._page.locator("[data-test=nav-my-messages]")

    @property
    def nav_sign_out(self) -> Locator:
        return self._page.locator("[data-test=nav-sign-out]")

    # -- 搜索（仅列表页存在）-----------------------------------------------

    @property
    def search_input(self) -> Locator:
        return self._page.locator("[data-test=search-query]")

    @property
    def search_reset(self) -> Locator:
        return self._page.locator("[data-test=search-reset]")

    @property
    def search_submit(self) -> Locator:
        return self._page.locator("[data-test=search-submit]")

    # -- 语言切换 -----------------------------------------------------------

    @property
    def language_select(self) -> Locator:
        return self._page.locator("[data-test=language-select]")

    def language_option(self, lang: str) -> Locator:
        """获取语言选项，如 lang='de' → [data-test=lang-de]。"""
        return self._page.locator(f"[data-test=lang-{lang}]")

    # -- 操作方法 -----------------------------------------------------------

    def search(self, query: str) -> None:
        """在搜索框中输入并回车提交。"""
        self.search_input.fill(query)
        self.search_input.press("Enter")

    def navigate_to_category(self, category: str) -> None:
        """展开 Categories 下拉并点击指定分类。
        category 为 data-test 后缀，如 'hand-tools'、'power-tools'。
        """
        self.nav_categories.click()
        self._page.locator(f"[data-test=nav-{category}]").click()

    def open_user_menu(self) -> None:
        """点击用户菜单按钮（登录态）。"""
        self.nav_menu.click()

    def sign_out(self) -> None:
        """登出：打开用户菜单 → 点击 Sign out。"""
        self.open_user_menu()
        self.nav_sign_out.click()
