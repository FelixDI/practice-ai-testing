"""ContactPage —— 留言表单页。
路由: /contact
无登录要求。

包含 7 个表单控件：first-name / last-name / email / subject / message / attachment / contact-submit。
表单为 Demo，提交无可见成功反馈，但字段校验正常工作。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class ContactPage(BasePage):
    """Toolshop 留言表单页。"""

    BASE_URL = "https://practicesoftwaretesting.com/contact"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """导航到留言表单页并等待渲染。"""
        super().goto(self.BASE_URL)
        self.wait_for_page("[data-test=nav-home]")

    # -- 表单控件 -----------------------------------------------------------

    @property
    def first_name(self) -> Locator:
        return self._page.locator("[data-test=first-name]")

    @property
    def last_name(self) -> Locator:
        return self._page.locator("[data-test=last-name]")

    @property
    def email(self) -> Locator:
        return self._page.locator("[data-test=email]")

    @property
    def subject(self) -> Locator:
        return self._page.locator("[data-test=subject]")

    @property
    def message(self) -> Locator:
        return self._page.locator("[data-test=message]")

    @property
    def attachment(self) -> Locator:
        return self._page.locator("[data-test=attachment]")

    @property
    def submit_button(self) -> Locator:
        return self._page.locator("[data-test=contact-submit]")

    # -- 所有表单控件 -------------------------------------------------------

    @property
    def all_form_elements(self) -> list[Locator]:
        return [
            self.first_name,
            self.last_name,
            self.email,
            self.subject,
            self.message,
            self.attachment,
            self.submit_button,
        ]

    # -- 校验错误 -----------------------------------------------------------

    @property
    def validation_errors(self) -> Locator:
        return self._page.locator("[role=alert]")

    def fill_form(
        self,
        first_name: str = "Test",
        last_name: str = "User",
        email: str = "test@example.com",
        subject: str = "Customer service",
        message: str = "A" * 50,
    ) -> None:
        """填充表单所有字段。"""
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.email.fill(email)
        self.subject.select_option(subject)
        self.message.fill(message)

    def submit(self) -> None:
        """点击 Send 按钮。"""
        self.submit_button.click()
