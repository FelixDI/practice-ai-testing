"""ProductCard —— 商品卡片组件。

跨列表页复用：HomePage / CategoryPage / SearchPage。
每张卡片包含图片、名称、CO₂ 评级、价格、对比按钮，缺货时显示缺货标签。

初始化方式：
    ProductCard(page.locator("a[href*='/product/']").first)
    ProductCard(page.locator("[data-test=product-{id}]"))
"""

from __future__ import annotations

from playwright.sync_api import Locator


class ProductCard:
    """商品卡片，表示商品列表中的单个商品。"""

    def __init__(self, locator: Locator) -> None:
        self._base = locator

    # -- 卡片根元素 ---------------------------------------------------------

    @property
    def container(self) -> Locator:
        return self._base

    # -- 内部元素 -----------------------------------------------------------

    @property
    def compare_button(self) -> Locator:
        return self._base.locator("[data-test=compare-btn]")

    @property
    def product_name(self) -> Locator:
        return self._base.locator("[data-test=product-name]")

    @property
    def co2_badge(self) -> Locator:
        return self._base.locator("[data-test=co2-rating-badge]")

    @property
    def price(self) -> Locator:
        return self._base.locator("[data-test=product-price]")

    @property
    def out_of_stock_label(self) -> Locator:
        return self._base.locator("[data-test=out-of-stock]")

    # -- 操作方法 -----------------------------------------------------------

    def click(self) -> None:
        """点击卡片跳转到商品详情页。"""
        self._base.click()

    def toggle_compare(self) -> None:
        """切换对比状态。"""
        self.compare_button.click()
