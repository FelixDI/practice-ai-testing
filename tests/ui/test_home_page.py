"""HomePage 模块 UI 测试。

蓝图：docs/test-cases/home_page.md —— 8 条用例。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.home_page import HomePage


@pytest.fixture
def home(page: Page) -> HomePage:
    hp = HomePage(page)
    hp.goto()
    page.wait_for_selector("[data-test=nav-home]", timeout=30000)
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
        home._page.wait_for_timeout(500)
        expect(home.notification_bar).to_be_visible()  # 页面不崩溃即可


class TestCategoryNavigation:
    # [UI_HOME_003] P0
    def test_navigate_to_hand_tools(self, home: HomePage) -> None:
        home.navigate_to_category("hand-tools")
        home._page.wait_for_timeout(1000)
        assert "/category/hand-tools" in home._page.url

    # [UI_HOME_007] P1
    def test_categories_menu_toggle(self, home: HomePage) -> None:
        home.nav_categories.click()
        home._page.wait_for_timeout(500)
        # 展开后 Hand Tools 应可见
        expect(home.nav_hand_tools).to_be_visible()


class TestProductDetail:
    # [UI_HOME_004] P0
    def test_click_product_card(self, home: HomePage) -> None:
        first_card = home.product_cards.first
        first_card.click()
        home._page.wait_for_timeout(1000)
        assert "/product/" in home._page.url


class TestSortAndNav:
    # [UI_HOME_006] P1
    def test_sort_select(self, home: HomePage) -> None:
        home.sort_select.select_option("price,asc")
        home._page.wait_for_timeout(1000)
        # 页面不崩溃即可

    # [UI_HOME_008] P1
    def test_sign_in_link(self, home: HomePage) -> None:
        home.nav_sign_in.click()
        home._page.wait_for_timeout(1000)
        assert "/auth/login" in home._page.url
