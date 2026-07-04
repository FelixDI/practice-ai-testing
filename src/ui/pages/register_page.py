"""RegisterPage —— 注册页。
路由: /auth/register
无登录要求。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class RegisterPage(BasePage):
    """Toolshop 注册页，提供完整用户注册表单。"""

    URL = "https://practicesoftwaretesting.com/auth/register"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation -------------------------------------------------------

    def goto(self) -> None:
        """导航到注册页并等待表单渲染。"""
        super().goto(self.URL)
        self.wait_for_page("[data-test=register-form]")

    # -- 表单元素 ---------------------------------------------------------

    @property
    def register_form(self) -> Locator:
        return self._page.locator("[data-test=register-form]")

    @property
    def first_name_input(self) -> Locator:
        return self._page.locator("[data-test=first-name]")

    @property
    def last_name_input(self) -> Locator:
        return self._page.locator("[data-test=last-name]")

    @property
    def dob_input(self) -> Locator:
        return self._page.locator("[data-test=dob]")

    @property
    def country_select(self) -> Locator:
        return self._page.locator("[data-test=country]")

    @property
    def postal_code_input(self) -> Locator:
        return self._page.locator("[data-test=postal_code]")

    @property
    def house_number_input(self) -> Locator:
        return self._page.locator("[data-test=house_number]")

    @property
    def street_input(self) -> Locator:
        return self._page.locator("[data-test=street]")

    @property
    def city_input(self) -> Locator:
        return self._page.locator("[data-test=city]")

    @property
    def state_input(self) -> Locator:
        return self._page.locator("[data-test=state]")

    @property
    def phone_input(self) -> Locator:
        return self._page.locator("[data-test=phone]")

    @property
    def email_input(self) -> Locator:
        return self._page.locator("[data-test=email]")

    @property
    def password_input(self) -> Locator:
        return self._page.locator("[data-test=password]")

    @property
    def submit_button(self) -> Locator:
        return self._page.locator("[data-test=register-submit]")

    # -- 密码可见性 -------------------------------------------------------

    @property
    def password_toggle(self) -> Locator:
        """密码框旁的 eye icon 按钮（无 data-test，用 CSS 定位）。"""
        return self._page.locator("[data-test=password] ~ div button")

    # -- 错误消息 ---------------------------------------------------------

    @property
    def register_error(self) -> Locator:
        return self._page.locator("[data-test=register-error]")

    def field_error(self, field: str) -> Locator:
        """获取字段级错误消息，如 first-name-error、email-error 等。"""
        return self._page.locator(f"[data-test={field}-error]")

    # -- 操作方法 ---------------------------------------------------------

    def fill_basic_info(self, first_name: str, last_name: str, dob: str) -> None:
        """填写基本个人信息。"""
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.dob_input.fill(dob)

    def fill_address(self, country: str, postal_code: str, house_number: str,
                     street: str, city: str, state: str) -> None:
        """填写地址信息（选择国家后等待邮编查询完成）。"""
        self.country_select.select_option(country)
        self._page.wait_for_timeout(500)  # 等待邮编查询 JS 就绪
        self.postal_code_input.fill(postal_code)
        self.house_number_input.fill(house_number)
        self._page.wait_for_timeout(1000)  # 等待街道/城市/州自动填充
        # 覆盖自动填充的值，确保准确性
        self.street_input.fill(street)
        self.city_input.fill(city)
        self.state_input.fill(state)

    def fill_contact(self, phone: str, email: str, password: str) -> None:
        """填写联系方式与密码。"""
        self.phone_input.fill(phone)
        self.email_input.fill(email)
        self.password_input.fill(password)

    def submit(self) -> None:
        """点击 Register 提交按钮。"""
        self.submit_button.click()
