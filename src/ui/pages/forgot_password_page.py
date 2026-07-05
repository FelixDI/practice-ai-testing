"""ForgotPasswordPage —— 忘记密码页。
路由: /auth/forgot-password
无登录要求。

仅一个 email 输入框 + 提交按钮。提交后显示确认消息，无格式校验。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class ForgotPasswordPage(BasePage):
    """Toolshop 忘记密码页。"""

    BASE_URL = "https://practicesoftwaretesting.com/auth/forgot-password"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """导航到忘记密码页并等待渲染。"""
        super().goto(self.BASE_URL)
        self.wait_for_page("[data-test=nav-home]")

    # -- 表单控件 -----------------------------------------------------------

    @property
    def email_input(self) -> Locator:
        return self._page.locator("[data-test=email]")

    @property
    def submit_button(self) -> Locator:
        return self._page.locator("[data-test=forgot-password-submit]")

    @property
    def form(self) -> Locator:
        return self._page.locator("[data-test=forgot-password-form]")

    @property
    def confirmation_message(self) -> Locator:
        """提交后的确认消息（role=alert）。"""
        return self._page.locator("[role=alert]")

    # -- 操作 ---------------------------------------------------------------

    def submit(self, email: str = "") -> None:
        """输入邮箱并提交。"""
        if email:
            self.email_input.fill(email)
        self.submit_button.click()
