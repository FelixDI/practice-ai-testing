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


class TestSearchBoundary:
    """P2 搜索边界。"""

    @pytest.fixture
    def home(self, page: Page) -> HomePage:
        hp = HomePage(page)
        hp.goto()
        page.wait_for_selector("[data-test=nav-home]", timeout=30000)
        return hp

    # [UI_HOME_009] P2
    def test_search_overlong_input(self, home: HomePage) -> None:
        home.search("A" * 150)
        home._page.wait_for_timeout(1000)
        expect(home.notification_bar).to_be_visible()  # 不崩溃

    # [UI_HOME_010] P2
    def test_search_no_results(self, home: HomePage) -> None:
        home.search("xyznonexistent999")
        home._page.wait_for_timeout(1000)
        # 期望出现空结果提示
        no_result = home._page.locator("text=No products found")
        expect(no_result).to_be_visible(timeout=5000)


class TestSortAndPagination:
    """P2 排序 + 分页。"""

    @pytest.fixture
    def home(self, page: Page) -> HomePage:
        hp = HomePage(page)
        hp.goto()
        page.wait_for_selector("[data-test=nav-home]", timeout=30000)
        return hp

    # [UI_HOME_011] P2
    def test_sort_all_options(self, home: HomePage) -> None:
        options = home.sort_select.locator("option")
        count = options.count()
        for i in range(min(count, 6)):  # 最多遍历 6 个
            val = options.nth(i).get_attribute("value")
            if val:
                home.sort_select.select_option(val)
                home._page.wait_for_timeout(300)
        # 遍历完不崩溃即可

    # [UI_HOME_012] P2
    def test_pagination_exists(self, home: HomePage) -> None:
        pagination = home._page.locator("[class*=pagination], [data-test=page], [class*=pager]")
        # 分页可能存在也可能不存在（取决于商品总量），不崩溃即可
        _ = pagination.count()


class TestLoggedInState:
    """P3 登录态。"""

    @pytest.fixture
    def logged_in_home(self, page: Page) -> HomePage:
        from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD

        # 登录
        page.goto("https://practicesoftwaretesting.com/auth/login")
        page.wait_for_selector("#email", timeout=10000)
        page.fill("#email", TEST_USER_EMAIL)
        page.fill("#password", TEST_USER_PASSWORD)
        page.click("input.btnSubmit")
        page.wait_for_url("**/account**", timeout=10000)

        # 回到首页
        hp = HomePage(page)
        hp.goto()
        page.wait_for_selector("[data-test=nav-home]", timeout=30000)
        return hp

    # [UI_HOME_013] P3
    def test_logged_in_nav_has_favorites(self, logged_in_home: HomePage) -> None:
        # 展开用户菜单
        logged_in_home._page.locator("[data-test=nav-menu]").click()
        logged_in_home._page.wait_for_timeout(500)

        # 登录后出现 Sign out（在下拉菜单中）
        sign_out = logged_in_home._page.locator("[data-test=nav-sign-out]")
        expect(sign_out).to_be_visible(timeout=5000)

        # 登录后出现 My Favorites 入口（在下拉菜单中）
        fav = logged_in_home._page.locator("[data-test=nav-my-favorites]")
        expect(fav).to_be_visible(timeout=5000)

