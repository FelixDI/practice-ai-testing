"""HomePage —— 首页 / 商品列表。
路由: /
无登录要求。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer
from src.ui.components.product_card import ProductCard


class HomePage(BasePage):
    """Toolshop 首页，展示商品列表、筛选区、分页。"""

    URL = "https://practicesoftwaretesting.com/"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation -------------------------------------------------------

    def goto(self) -> None:
        """导航到首页并等待关键元素渲染。"""
        super().goto(self.URL)
        self.wait_for_page("[data-test=nav-home]")

    # -- 排序 -------------------------------------------------------------

    @property
    def sort_select(self) -> Locator:
        return self._page.locator("[data-test=sort]")

    # -- 筛选区（页面级，非组件）------------------------------------------

    @property
    def price_slider(self) -> Locator:
        return self._page.locator(".ngx-slider")

    @property
    def eco_filter(self) -> Locator:
        return self._page.locator("[data-test=eco-friendly-filter]")

    def category_filter(self, label: str) -> Locator:
        """通过 label 文本定位分类筛选 checkbox。"""
        return self._page.locator("input[type=checkbox]", has=self._page.locator(f"text={label}"))

    def brand_filter(self, label: str) -> Locator:
        """通过 label 文本定位品牌筛选 checkbox。"""
        return self._page.locator("input[type=checkbox]", has=self._page.locator(f"text={label}"))

    # -- 分页 -------------------------------------------------------------

    @property
    def pagination_prev(self) -> Locator:
        return self._page.locator("[data-test=pagination-prev]")

    @property
    def pagination_next(self) -> Locator:
        return self._page.locator("[data-test=pagination-next]")

    def page_button(self, page_num: int) -> Locator:
        return self._page.locator(f"[aria-label=Page-{page_num}]")

    # -- 商品列表 ---------------------------------------------------------

    @property
    def product_cards(self) -> Locator:
        """当前页所有商品卡片链接（Locator，供 .count() / .first / .nth() 查询）。"""
        return self._page.locator("a[href*='/product/']")

    def product_card(self, index: int) -> ProductCard:
        """按列表索引获取单张卡片的组件实例（0-based）。"""
        return ProductCard(self.product_cards.nth(index))

    def get_product_card(self, product_id: str) -> ProductCard:
        """通过商品 data-test ID 获取单张卡片组件实例。"""
        return ProductCard(self._page.locator(f"[data-test=product-{product_id}]"))
