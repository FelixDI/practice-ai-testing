"""ProductPage 模块 UI 测试。

蓝图：docs/test-cases/ui/product_page.md —— 9 条用例（P0×3 + P1×3 + P2×2 + P3×1）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.common.config import UI_BASE_URL
from src.ui.pages.product_page import ProductPage
from tests.ui.conftest import fetch_valid_product_id


def _is_cloudflare(page: Page) -> bool:
    """检查当前页面是否被 Cloudflare 拦截。"""
    try:
        body = page.content()
        return "cloudflare" in body.lower() or "checking your browser" in body.lower()
    except Exception:
        return False


@pytest.fixture
def product(page: Page) -> ProductPage | None:
    """从 API 动态获取有效商品 ID，加载详情页。"""
    valid_id = fetch_valid_product_id()
    pp = ProductPage(page)
    response = page.goto(
        f"{UI_BASE_URL}/product/{valid_id}",
        wait_until="load",
        timeout=30000,
    )
    # 1. 检查 Cloudflare 拦截（response 403 + 页面特征）
    if response and response.status == 403 and _is_cloudflare(page):
        pytest.skip(f"Cloudflare 拦截商品页 ({valid_id})，环境不可用")
    # 2. 检查页面是否渲染正常
    try:
        expect(pp.product_name).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail(
            "product-name 不可见——页面已加载但元素未找到，请检查选择器或页面结构"
        )
    except TimeoutError:
        pytest.skip("商品页渲染超时（30s），环境异常")
    return pp


class TestProductPageLoad:
    """商品详情页基础加载。"""

    # [UI_PROD_001] P0
    def test_product_page_loads(self, product: ProductPage) -> None:
        expect(product.product_name).to_be_visible()
        expect(product.unit_price).to_be_visible()
        expect(product.product_description).to_be_visible()

    # [UI_PROD_002] P0
    def test_add_to_cart_button_works(self, product: ProductPage) -> None:
        product.click_add_to_cart()
        expect(product.header.cart_quantity).to_be_visible(timeout=5000)

    # [UI_PROD_003] P0
    def test_increase_quantity(self, product: ProductPage) -> None:
        product.increase_qty()
        expect(product.quantity_input).to_have_value("2")


class TestProductExceptions:
    """异常路径。"""

    # [UI_PROD_004] P1
    def test_invalid_product_id(self, page: Page) -> None:
        pp = ProductPage(page)
        pp.goto("invalid-id")
        expect(pp.header.nav_home).to_be_visible(timeout=10000)

    # [UI_PROD_005] P1
    def test_quantity_not_below_one(self, product: ProductPage) -> None:
        expect(product.quantity_input).to_have_value("1")
        product.decrease_qty()
        # 最小值为 1，减少后仍为 1
        expect(product.quantity_input).to_have_value("1")

    # [UI_PROD_006] P1
    def test_specs_table_renders(self, product: ProductPage) -> None:
        expect(product.specs_title).to_be_visible()
        expect(product.specs_table).to_be_visible()
        assert product.spec_rows.count() > 0, "应至少有一条规格"


class TestProductBoundary:
    """边界覆盖。"""

    # [UI_PROD_007] P2
    def test_favorites_button_exists(self, product: ProductPage) -> None:
        expect(product.add_to_favorites).to_be_visible()
        expect(product.add_to_favorites).to_contain_text("Add to favourites")

    # [UI_PROD_008] P2
    def test_related_products_exist(self, product: ProductPage) -> None:
        expect(product.related_products.first).to_be_visible(timeout=5000)


class TestProductSecurity:
    """深度防御。"""

    # [UI_PROD_009] P3
    def test_xss_in_product_id(self, page: Page) -> None:
        pp = ProductPage(page)
        pp.goto("<script>alert(1)</script>")
        expect(pp.header.nav_home).to_be_visible(timeout=10000)
