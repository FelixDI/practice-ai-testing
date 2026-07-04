"""ProductCard 组件 UI 测试。

蓝图：docs/test-cases/ui/product_card_component.md —— 4 条用例（P0×2 + P1×1 + P2×1）。
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
    expect(hp.header.nav_home).to_be_visible(timeout=60000)
    return hp


class TestProductCardRender:
    """卡片渲染。"""

    # [UI_CARD_001] P0
    def test_first_card_has_all_core_elements(self, home: HomePage) -> None:
        card = home.product_card(0)
        expect(card.container).to_be_visible()
        expect(card.product_name).to_be_visible()
        expect(card.product_name).not_to_be_empty()
        expect(card.price).to_be_visible()
        expect(card.co2_badge).to_be_visible()
        expect(card.compare_button).to_be_visible()

    # [UI_CARD_002] P0
    def test_click_card_navigates_to_detail(self, home: HomePage) -> None:
        card = home.product_card(0)
        with home._page.expect_navigation():
            card.click()
        expect(home._page).to_have_url(re.compile(r"/product/"))


class TestProductCardInteraction:
    """卡片交互。"""

    # [UI_CARD_003] P1
    def test_compare_button_toggles_state(self, home: HomePage) -> None:
        card = home.product_card(0)
        initial = card.compare_button.get_attribute("aria-pressed")
        card.toggle_compare()
        after = card.compare_button.get_attribute("aria-pressed")
        assert after != initial, f"aria-pressed 应翻转, 初始={initial}, 点击后={after}"

    # [UI_CARD_004] P2
    def test_out_of_stock_card_has_label(self, home: HomePage) -> None:
        """遍历所有卡片，找到有缺货标签的卡片并验证。"""
        total = home.product_cards.count()
        found = False
        for i in range(total):
            card = home.product_card(i)
            oos = card.out_of_stock_label
            if oos.is_visible():
                expect(oos).to_contain_text("Out of stock")
                found = True
                break
        # 如果当前页面没有缺货商品，跳过断言
        if not found:
            pytest.skip("当前页面没有缺货商品")
