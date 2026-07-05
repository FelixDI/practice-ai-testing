"""RentalsPage 模块 UI 测试。

蓝图：docs/test-cases/ui/rentals_page.md —— 4 条用例（P0×2 + P1×1 + P2×1）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.rentals_page import RentalsPage
from tests.ui.conftest import is_cloudflare


@pytest.fixture
def rentals(page: Page) -> RentalsPage | None:
    """加载租赁列表页。"""
    rp = RentalsPage(page)
    response = page.goto(RentalsPage.BASE_URL, wait_until="load", timeout=30000)
    if response and response.status == 403 and is_cloudflare(page):
        pytest.skip("Cloudflare 拦截租赁页，环境不可用")
    try:
        expect(rp.page_title).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail("page-title 不可见——请检查选择器或页面结构")
    except TimeoutError:
        pytest.skip("租赁页渲染超时（30s），环境异常")
    return rp


class TestRentalsPageLoad:
    """租赁列表页基础加载。"""

    # [UI_RENT_001] P0
    def test_rentals_page_loads(self, rentals: RentalsPage) -> None:
        expect(rentals.page_title).to_be_visible()
        expect(rentals.page_title).to_have_text("Rentals")

    # [UI_RENT_002] P0
    def test_at_least_one_rental(self, rentals: RentalsPage) -> None:
        expect(rentals.rental_cards.first).to_be_visible(timeout=10000)


class TestRentalsCardStructure:
    """卡片结构校验。"""

    # [UI_RENT_003] P1
    def test_card_has_image_title_description(self, rentals: RentalsPage) -> None:
        card = rentals.first_card
        expect(card.locator("img")).to_be_visible()
        expect(card.locator("h5.card-title")).to_be_visible()
        expect(card.locator("p.card-text")).to_be_visible()


class TestRentalsBoundary:
    """边界覆盖。"""

    # [UI_RENT_004] P2
    def test_rental_count_is_three(self, rentals: RentalsPage) -> None:
        expect(rentals.rental_cards).to_have_count(3)
