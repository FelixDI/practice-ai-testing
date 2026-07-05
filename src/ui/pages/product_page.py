"""ProductPage —— 商品详情页。
路由: /product/{id}
无登录要求。

含商品信息、数量控件、操作按钮（加购/收藏/对比）、规格表、相关推荐。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.common.config import UI_BASE_URL
from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class ProductPage(BasePage):
    """Toolshop 商品详情页。"""

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation -------------------------------------------------------

    def goto(self, product_id: str = "01KWQ4KN44EQERCR5GNWBE2QR9") -> None:
        """导航到指定商品详情页并等待导航栏就绪。"""
        super().goto(f"{UI_BASE_URL}/product/{product_id}")
        self.wait_for_page("[data-test=nav-home]")

    # -- 商品信息 ---------------------------------------------------------

    @property
    def product_name(self) -> Locator:
        return self._page.locator("[data-test=product-name]")

    @property
    def unit_price(self) -> Locator:
        return self._page.locator("[data-test=unit-price]")

    @property
    def product_description(self) -> Locator:
        return self._page.locator("[data-test=product-description]")

    @property
    def co2_badge(self) -> Locator:
        return self._page.locator("[data-test=co2-rating-badge]")

    # -- 数量控件 ---------------------------------------------------------

    @property
    def decrease_quantity(self) -> Locator:
        return self._page.locator("[data-test=decrease-quantity]")

    @property
    def quantity_input(self) -> Locator:
        return self._page.locator("[data-test=quantity]")

    @property
    def increase_quantity(self) -> Locator:
        return self._page.locator("[data-test=increase-quantity]")

    # -- 操作按钮 ---------------------------------------------------------

    @property
    def add_to_cart(self) -> Locator:
        return self._page.locator("[data-test=add-to-cart]")

    @property
    def add_to_favorites(self) -> Locator:
        return self._page.locator("[data-test=add-to-favorites]")

    @property
    def add_to_compare(self) -> Locator:
        return self._page.locator("[data-test=add-to-compare]")

    # -- 规格表 -----------------------------------------------------------

    @property
    def specs_title(self) -> Locator:
        return self._page.locator("[data-test=specs-title]")

    @property
    def specs_table(self) -> Locator:
        return self._page.locator("[data-test=product-specs]")

    @property
    def spec_rows(self) -> Locator:
        """所有规格行。"""
        return self._page.locator("[data-test=spec-row]")

    # -- 相关推荐 ---------------------------------------------------------

    @property
    def related_products(self) -> Locator:
        """底部相关商品列表（复用商品卡片链接）。"""
        return self._page.locator("a[href*='/product/']")

    # -- 操作方法 ---------------------------------------------------------

    def increase_qty(self) -> None:
        """点击 + 按钮增加数量。"""
        self.increase_quantity.click()

    def decrease_qty(self) -> None:
        """点击 - 按钮减少数量。"""
        self.decrease_quantity.click()

    def click_add_to_cart(self) -> None:
        """点击 Add to cart 按钮。"""
        self.add_to_cart.click()
