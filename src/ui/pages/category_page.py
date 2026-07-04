"""CategoryPage —— 分类浏览页。
路由: /category/{slug}
无登录要求。

与 HomePage 共享相同的筛选区（sort / price slider / filter checkboxes）和分页结构。
当前阶段暂不提取 FilterSidebar 组件，等待第 3~4 个列表页出现后统一抽象。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer
from src.ui.components.product_card import ProductCard


class CategoryPage(BasePage):
    """Toolshop 分类浏览页，展示指定分类下的商品列表。"""

    BASE_URL = "https://practicesoftwaretesting.com/category"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation -------------------------------------------------------

    def goto(self, slug: str = "hand-tools") -> None:
        """导航到指定分类页并等待渲染。"""
        super().goto(f"{self.BASE_URL}/{slug}")
        self.wait_for_page("[data-test=nav-home]")

    # -- 分类标题（页面级，非组件）----------------------------------------

    @property
    def category_heading(self) -> Locator:
        return self._page.locator("h2")
    # 快照中可见 <h2>Category: {name}</h2>, 例 "Category: Hand Tools"

    # -- 排序 -------------------------------------------------------------

    @property
    def sort_select(self) -> Locator:
        return self._page.locator("[data-test=sort]")

    # -- 筛选区（与 HomePage 共享结构）-----------------------------------

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
        return self._page.locator("a[href*='/product/']")

    def product_card(self, index: int) -> ProductCard:
        return ProductCard(self.product_cards.nth(index))
