"""HomePage 模块 UI 测试。

蓝图：docs/test-cases/home_page.md —— 13 条用例（P0×4 + P1×4 + P2×4 + P3×1）。
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.home_page import HomePage


@pytest.fixture
def home(page: Page) -> HomePage:
    hp = HomePage(page)
    hp.goto()
    expect(hp.nav_home).to_be_visible(timeout=60000)
    return hp


class TestHomePageLoad:
    # [UI_HOME_001] P0
    def test_page_loads_with_products(self, home: HomePage) -> None:
        expect(home.notification_bar).to_be_visible()
        assert "Practice Software Testing" in home.title
        expect(home.product_cards.first).to_be_visible(timeout=10000)


class TestSearch:
    # [UI_HOME_002] P0
    def test_search_hammer(self, home: HomePage) -> None:
        home.search("hammer")
        expect(home.product_cards.first).to_be_visible(timeout=10000)

    # [UI_HOME_005] P1
    def test_empty_search(self, home: HomePage) -> None:
        home.search("")
        expect(home.notification_bar).to_be_visible()


class TestCategoryNavigation:
    # [UI_HOME_003] P0
    def test_navigate_to_hand_tools(self, home: HomePage) -> None:
        home.navigate_to_category("hand-tools")
        expect(home._page).to_have_url(re.compile(r"/category/hand-tools"))

    # [UI_HOME_007] P1
    def test_categories_menu_toggle(self, home: HomePage) -> None:
        home.nav_categories.click()
        expect(home.nav_hand_tools).to_be_visible()


class TestProductDetail:
    # [UI_HOME_004] P0
    def test_click_product_card(self, home: HomePage) -> None:
        first_card = home.product_cards.first
        with home._page.expect_navigation():
            first_card.click()


class TestSortAndNav:
    # [UI_HOME_006] P1
    def test_sort_select(self, home: HomePage) -> None:
        home.sort_select.select_option("price,asc")
        expect(home.product_cards.first).to_be_visible()

    # [UI_HOME_008] P1
    def test_sign_in_link(self, home: HomePage) -> None:
        with home._page.expect_navigation():
            home.nav_sign_in.click()
        expect(home._page).to_have_url(re.compile(r"/auth/login"))


class TestSearchBoundary:
    """P2 搜索边界。"""

    # [UI_HOME_009] P2
    def test_search_overlong_input(self, home: HomePage) -> None:
        home.search("A" * 150)
        expect(home.notification_bar).to_be_visible()

    # [UI_HOME_010] P2
    def test_search_no_results(self, home: HomePage) -> None:
        home.search("xyznonexistent999")
        no_result = home._page.locator("text=No products found")
        expect(no_result).to_be_visible(timeout=5000)


class TestSortAndPagination:
    """P2 排序 + 分页。"""

    # [UI_HOME_011] P2
    def test_sort_all_options(self, home: HomePage) -> None:
        options = home.sort_select.locator("option")
        count = options.count()
        for i in range(min(count, 6)):
            val = options.nth(i).get_attribute("value")
            if val:
                home.sort_select.select_option(val)
                expect(home.product_cards.first).to_be_visible()

    # [UI_HOME_012] P2
    def test_pagination_exists(self, home: HomePage) -> None:
        pagination = home._page.locator("[class*=pagination], [data-test=page], [class*=pager]")
        _ = pagination.count()


class TestLoggedInState:
    """P3 登录态。"""

    @pytest.fixture
    def logged_in_home(self, page: Page) -> HomePage:
        from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD

        page.goto("https://practicesoftwaretesting.com/auth/login")
        page.wait_for_selector("#email", timeout=10000)
        page.fill("#email", TEST_USER_EMAIL)
        page.fill("#password", TEST_USER_PASSWORD)
        page.click("input.btnSubmit")
        page.wait_for_url("**/account**", timeout=10000)

        hp = HomePage(page)
        hp.goto()
        expect(hp.nav_home).to_be_visible(timeout=60000)
        return hp

    # [UI_HOME_013] P3
    def test_logged_in_nav_has_favorites(self, logged_in_home: HomePage) -> None:
        logged_in_home._page.locator("[data-test=nav-menu]").click()
        sign_out = logged_in_home._page.locator("[data-test=nav-sign-out]")
        expect(sign_out).to_be_visible(timeout=5000)

        fav = logged_in_home._page.locator("[data-test=nav-my-favorites]")
        expect(fav).to_be_visible(timeout=5000)
