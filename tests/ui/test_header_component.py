"""Header 组件 UI 测试。

蓝图：docs/test-cases/ui/header_component.md —— 9 条用例（P0×3 + P1×4 + P2×2）。
说明：搜索、分类跳转、sign-in 跳转已在 test_home_page.py 覆盖，此处只补充缺口。
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.home_page import HomePage
from src.ui.pages.login_page import LoginPage


# -- Fixtures ---------------------------------------------------------------

@pytest.fixture
def home(page: Page) -> HomePage:
    hp = HomePage(page)
    hp.goto()
    expect(hp.header.nav_home).to_be_visible(timeout=60000)
    return hp


@pytest.fixture
def logged_in_home(page: Page) -> HomePage:
    """登录后回到首页，返回 HomePage 实例。"""
    from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD

    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    page.wait_for_url("**/account**", timeout=10000)

    hp = HomePage(page)
    hp.goto()
    expect(hp.header.nav_home).to_be_visible(timeout=60000)
    return hp


# -- P0 核心链路 ------------------------------------------------------------

class TestHeaderNavigation:
    """导航链接跳转。"""

    # [UI_HEADER_001] P0
    def test_contact_link_navigates(self, home: HomePage) -> None:
        with home._page.expect_navigation():
            home.header.nav_contact.click()
        expect(home._page).to_have_url(re.compile(r"/contact"))

    # [UI_HEADER_002] P0
    def test_rentals_link_has_correct_href(self, home: HomePage) -> None:
        expect(home.header.nav_rentals).to_have_attribute("href", "/rentals")

    # [UI_HEADER_003] P0
    def test_categories_dropdown_contains_all(self, home: HomePage) -> None:
        home.header.nav_categories.click()
        expect(home.header.nav_hand_tools).to_be_visible()
        expect(home.header.nav_power_tools).to_be_visible()
        expect(home.header.nav_other).to_be_visible()
        expect(home.header.nav_special_tools).to_be_visible()


# -- P1 关键异常 ------------------------------------------------------------

class TestHeaderElements:
    """导航元素存在性。"""

    # [UI_HEADER_004] P1
    def test_main_nav_elements_visible(self, home: HomePage) -> None:
        """主菜单栏元素可见（Home/Categories/Contact/Sign in）。
        nav-rentals 在 DOM 中存在但不在主菜单栏，属于响应式折叠区。
        """
        header = home.header
        expect(header.nav_home).to_be_visible()
        expect(header.nav_categories).to_be_visible()
        expect(header.nav_contact).to_be_visible()
        expect(header.nav_sign_in).to_be_visible()


class TestLanguageSwitch:
    """语言切换。"""

    # [UI_HEADER_005] P1
    def test_language_menu_expands(self, home: HomePage) -> None:
        home.header.language_select.click()
        expect(home.header.language_option("de")).to_be_visible()
        expect(home.header.language_option("en")).to_be_visible()
        expect(home.header.language_option("es")).to_be_visible()
        expect(home.header.language_option("fr")).to_be_visible()
        expect(home.header.language_option("nl")).to_be_visible()
        expect(home.header.language_option("tr")).to_be_visible()


class TestLoggedInNav:
    """登录态导航。"""

    # [UI_HEADER_006] P1
    def test_user_menu_contains_all_items(self, logged_in_home: HomePage) -> None:
        logged_in_home.header.open_user_menu()
        expect(logged_in_home.header.nav_my_account).to_be_visible(timeout=5000)
        expect(logged_in_home.header.nav_my_favorites).to_be_visible()
        expect(logged_in_home.header.nav_my_profile).to_be_visible()
        expect(logged_in_home.header.nav_my_invoices).to_be_visible()
        expect(logged_in_home.header.nav_my_messages).to_be_visible()
        expect(logged_in_home.header.nav_sign_out).to_be_visible()

    # [UI_HEADER_007] P1
    def test_sign_out_returns_to_public_nav(self, logged_in_home: HomePage) -> None:
        logged_in_home.header.sign_out()
        expect(logged_in_home.header.nav_sign_in).to_be_visible(timeout=5000)
        expect(logged_in_home.header.nav_menu).not_to_be_visible()


# -- P2 边界覆盖 ------------------------------------------------------------

class TestHeaderBoundary:
    """边界操作。"""

    # [UI_HEADER_008] P2
    def test_navigate_to_power_tools(self, home: HomePage) -> None:
        home.header.navigate_to_category("power-tools")
        expect(home._page).to_have_url(re.compile(r"/category/power-tools"))

    # [UI_HEADER_009] P2
    def test_search_buttons_exist(self, home: HomePage) -> None:
        expect(home.header.search_reset).to_be_visible()
        expect(home.header.search_submit).to_be_visible()
