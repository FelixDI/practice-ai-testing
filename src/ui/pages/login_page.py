"""LoginPage —— 登录页。
路由: /auth/login
无登录要求。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class LoginPage(BasePage):
    """Toolshop 登录页，提供邮箱+密码表单登录。"""

    URL = "https://practicesoftwaretesting.com/auth/login"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation -------------------------------------------------------

    def goto(self) -> None:
        """导航到登录页并等待表单渲染。"""
        super().goto(self.URL)
        self.wait_for_page("[data-test=login-form]")

    # -- 表单元素 ---------------------------------------------------------

    @property
    def login_form(self) -> Locator:
        return self._page.locator("[data-test=login-form]")

    @property
    def email_input(self) -> Locator:
        return self._page.locator("[data-test=email]")

    @property
    def password_input(self) -> Locator:
        return self._page.locator("[data-test=password]")

    @property
    def submit_button(self) -> Locator:
        return self._page.locator("[data-test=login-submit]")

    @property
    def login_error(self) -> Locator:
        return self._page.locator("[data-test=login-error]")

    # -- 密码可见性 -------------------------------------------------------

    @property
    def password_toggle(self) -> Locator:
        """密码框旁的 eye icon 按钮（无 data-test，用 CSS 定位）。"""
        return self._page.locator("[data-test=password] ~ div button")

    # -- 导航链接 ---------------------------------------------------------

    @property
    def register_link(self) -> Locator:
        return self._page.locator("[data-test=register-link]")

    @property
    def forgot_password_link(self) -> Locator:
        return self._page.locator("[data-test=forgot-password-link]")

    # -- 操作方法 ---------------------------------------------------------

    def fill_email(self, email: str) -> None:
        """填写邮箱。"""
        self.email_input.fill(email)

    def fill_password(self, password: str) -> None:
        """填写密码。"""
        self.password_input.fill(password)

    def submit(self) -> None:
        """点击 Login 提交按钮。"""
        self.submit_button.click()

    def login(self, email: str, password: str) -> None:
        """完整的登录流程：填写表单并提交。"""
        self.fill_email(email)
        self.fill_password(password)
        self.submit()
