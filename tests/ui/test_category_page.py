"""CategoryPage 模块 UI 测试。

蓝图：docs/test-cases/ui/category_page.md —— 12 条用例（P0×4 + P1×4 + P2×3 + P3×1）。
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.category_page import CategoryPage


@pytest.fixture
def cat_hand(page: Page) -> CategoryPage:
    cp = CategoryPage(page)
    cp.goto("hand-tools")
    expect(cp.product_cards.first).to_be_visible(timeout=60000)
    return cp


@pytest.fixture
def cat_power(page: Page) -> CategoryPage:
    cp = CategoryPage(page)
    cp.goto("power-tools")
    expect(cp.product_cards.first).to_be_visible(timeout=60000)
    return cp


class TestCategoryPageLoad:
    """分类页基础渲染。"""

    # [UI_CAT_001] P0
    def test_hand_tools_page_loads(self, cat_hand: CategoryPage) -> None:
        expect(cat_hand._page).to_have_url(re.compile(r"/category/hand-tools"))
        assert "Practice Software Testing" in cat_hand.title
        expect(cat_hand.product_cards.first).to_be_visible(timeout=10000)

    # [UI_CAT_002] P0
    def test_power_tools_page_loads(self, cat_power: CategoryPage) -> None:
        expect(cat_power._page).to_have_url(re.compile(r"/category/power-tools"))
        expect(cat_power.product_cards.first).to_be_visible(timeout=10000)

    # [UI_CAT_009] P0
    def test_category_heading_shows_correct_name(self, cat_hand: CategoryPage) -> None:
        expect(cat_hand.category_heading).to_be_visible()
        expect(cat_hand.category_heading).to_contain_text("Hand Tools")


class TestProductNavigation:
    """商品导航。"""

    # [UI_CAT_003] P0
    def test_click_product_navigates_to_detail(self, cat_hand: CategoryPage) -> None:
        first_card = cat_hand.product_cards.first
        with cat_hand._page.expect_navigation():
            first_card.click()
        expect(cat_hand._page).to_have_url(re.compile(r"/product/"))


class TestSortAndSearch:
    """排序与搜索。"""

    # [UI_CAT_004] P1
    def test_sort_on_category_page(self, cat_hand: CategoryPage) -> None:
        cat_hand.sort_select.select_option("price,asc")
        expect(cat_hand.product_cards.first).to_be_visible()

    # [UI_CAT_005] P1
    def test_search_on_category_page(self, cat_hand: CategoryPage) -> None:
        """分类页搜索框可能仅在首页存在，优先通过 Header 搜索组件验证。"""
        search_input = cat_hand.header.search_input
        if not search_input.is_visible():
            pytest.skip("当前分类页不包含搜索框")
        cat_hand.header.search("pliers")
        expect(cat_hand.product_cards.first).to_be_visible(timeout=10000)


class TestFilterSection:
    """筛选区交互。"""

    # [UI_CAT_010] P1
    def test_brand_filter_can_be_checked(self, cat_hand: CategoryPage) -> None:
        brand_cb = cat_hand.brand_filter("ForgeFlex Tools")
        brand_cb.check()
        expect(brand_cb).to_be_checked()
        # 筛选后商品列表重新渲染
        expect(cat_hand.product_cards.first).to_be_visible(timeout=10000)

    # [UI_CAT_011] P2
    def test_subcategory_filter_on_power_tools(self, cat_power: CategoryPage) -> None:
        sub_cb = cat_power.category_filter("Drill")
        sub_cb.check()
        expect(sub_cb).to_be_checked()
        expect(cat_power.product_cards.first).to_be_visible(timeout=10000)


class TestNonExistentCategory:
    """不存在分类。"""

    # [UI_CAT_006] P1
    def test_nonexistent_category_handles_gracefully(self, page: Page) -> None:
        cp = CategoryPage(page)
        cp.goto("nonexistent")
        # 页面应正常加载（可能为空列表或提示）
        expect(cp._page).to_have_url(re.compile(r"/category/nonexistent"))
        expect(cp.header.nav_home).to_be_visible()


class TestAllCategories:
    """所有分类路由。"""

    # [UI_CAT_007] P2
    def test_all_category_routes_accessible(self, page: Page) -> None:
        slugs = ["hand-tools", "power-tools", "other"]
        for slug in slugs:
            cp = CategoryPage(page)
            cp.goto(slug)
            expect(cp._page).to_have_url(re.compile(rf"/category/{slug}"))
            expect(cp.product_cards.first).to_be_visible(timeout=15000)


class TestSecurity:
    """深度防御。"""

    # [UI_CAT_012] P3
    def test_xss_in_slug_does_not_crash(self, page: Page) -> None:
        """XSS 注入被 Angular 路由安全处理，跳回首页而非崩溃。"""
        cp = CategoryPage(page)
        cp.goto("<script>alert(1)</script>")
        # 页面应正常加载，Header 可见（不崩溃、不执行脚本）
        expect(cp.header.nav_home).to_be_visible(timeout=10000)


class TestPagination:
    """分页。"""

    # [UI_CAT_008] P2
    def test_pagination_exists(self, cat_hand: CategoryPage) -> None:
        expect(cat_hand.pagination_prev).to_be_visible()
        expect(cat_hand.pagination_next).to_be_visible()
