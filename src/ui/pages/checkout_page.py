"""CheckoutPage —— 购物车与结账页（4 步流程）。

路由: /checkout
需要登录。未登录时自动重定向到 /auth/login。

4 步流程：Cart (1) → Sign in (2) → Billing Address (3) → Payment (4)
每个步骤对应一个 proceed-N 按钮，同时存在于 DOM 但仅当前步骤可见。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class CheckoutPage(BasePage):
    """Toolshop 结账页。"""

    BASE_URL = "https://practicesoftwaretesting.com/checkout"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """导航到结账页（需已登录）。"""
        super().goto(self.BASE_URL)
        self.wait_for_page("[data-test=nav-cart]")

    # -- 步骤指示器 ---------------------------------------------------------

    # 步骤指示器中的列表项无 data-test；通过文本定位

    # -- Cart 步骤 (Step 1) -------------------------------------------------

    @property
    def cart_quantity(self) -> Locator:
        """购物车徽章数量。"""
        return self._page.locator("[data-test=cart-quantity]")

    @property
    def cart_total(self) -> Locator:
        """购物车总价。"""
        return self._page.locator("[data-test=cart-total]")

    @property
    def proceed_1(self) -> Locator:
        """Step 1 → Step 2：Cart → Sign in confirmation（可见于购物车步骤）。"""
        return self._page.locator("[data-test=proceed-1]")

    # -- Sign in 步骤 (Step 2) ----------------------------------------------

    @property
    def proceed_2(self) -> Locator:
        """Step 2 → Step 3：Sign in → Billing Address。"""
        return self._page.locator("[data-test=proceed-2]")

    # -- Billing Address 步骤 (Step 3) --------------------------------------

    @property
    def country(self) -> Locator:
        """国家下拉。"""
        return self._page.locator("[data-test=country]")

    @property
    def postal_code(self) -> Locator:
        return self._page.locator("[data-test=postal_code]")

    @property
    def house_number(self) -> Locator:
        return self._page.locator("[data-test=house_number]")

    @property
    def street(self) -> Locator:
        return self._page.locator("[data-test=street]")

    @property
    def city(self) -> Locator:
        return self._page.locator("[data-test=city]")

    @property
    def state(self) -> Locator:
        return self._page.locator("[data-test=state]")

    @property
    def proceed_3(self) -> Locator:
        """Step 3 → Step 4：Billing Address → Payment。"""
        return self._page.locator("[data-test=proceed-3]")

    # -- Payment 步骤 (Step 4) ----------------------------------------------

    @property
    def payment_method(self) -> Locator:
        """支付方式下拉。"""
        return self._page.locator("[data-test=payment-method]")

    @property
    def finish_button(self) -> Locator:
        """Confirm 按钮（确认下单）。"""
        return self._page.locator("[data-test=finish]")

    # -- 操作 ----------------------------------------------------------------

    def fill_billing_address(
        self,
        postal: str = "10115",
        house: str = "42",
        street: str = "Teststr.",
        city: str = "Berlin",
        state: str = "Berlin",
    ) -> None:
        """填写 Billing Address 表单（Step 3）。"""
        self.postal_code.fill(postal)
        self.postal_code.press("Tab")  # 触发地址自动查找
        self.house_number.fill(house)
        self.street.fill(street)
        self.city.fill(city)
        self.state.fill(state)

    def wait_for_address_lookup(self, timeout: int = 15000) -> None:
        """等待地址自动填充完成（proceed-3 变为 enabled）。"""
        from playwright.sync_api import expect
        expect(self.proceed_3).to_be_enabled(timeout=timeout)

    def select_payment_method(self, method: str = "Cash on Delivery") -> None:
        """选择支付方式（Step 4）。"""
        self.payment_method.select_option(label=method)

    def complete_checkout(
        self,
        payment: str = "Cash on Delivery",
    ) -> None:
        """执行完整购买流程（从 Cart 到 Confirm）。

        调用方需确保已在 checkout 页面且购物车非空。
        """
        # Step 1 → 2
        self.proceed_1.click()
        # Step 2 → 3
        self.proceed_2.click()
        # Step 3: fill billing
        self.fill_billing_address()
        self.proceed_3.click()
        # Step 4: payment
        self.select_payment_method(payment)
        self.finish_button.click()
