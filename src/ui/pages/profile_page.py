"""ProfilePage —— 个人资料页。
路由: /account/profile
需要登录。

3 个功能区：个人信息编辑、密码修改、TOTP 两步验证设置。
"""

from __future__ import annotations

from playwright.sync_api import Locator

from src.ui.pages.base_page import BasePage
from src.ui.components.header import Header
from src.ui.components.footer import Footer


class ProfilePage(BasePage):
    """Toolshop 个人资料编辑页。"""

    BASE_URL = "https://practicesoftwaretesting.com/account/profile"

    def __init__(self, page):  # type: ignore[no-untyped-def]
        super().__init__(page)
        self.header = Header(page)
        self.footer = Footer(page)

    # -- Navigation ---------------------------------------------------------

    def goto(self) -> None:
        """导航到个人资料页（需已登录）。"""
        super().goto(self.BASE_URL)
        self.wait_for_page("[data-test=nav-home]")

    # -- 页面标题 -----------------------------------------------------------

    @property
    def page_title(self) -> Locator:
        return self._page.locator("[data-test=page-title]")

    # -- 个人信息 -----------------------------------------------------------

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
    def phone(self) -> Locator:
        return self._page.locator("[data-test=phone]")

    @property
    def street(self) -> Locator:
        return self._page.locator("[data-test=street]")

    @property
    def postal_code(self) -> Locator:
        return self._page.locator("[data-test=postal_code]")

    @property
    def city(self) -> Locator:
        return self._page.locator("[data-test=city]")

    @property
    def state(self) -> Locator:
        return self._page.locator("[data-test=state]")

    @property
    def country(self) -> Locator:
        return self._page.locator("[data-test=country]")

    @property
    def update_profile_button(self) -> Locator:
        return self._page.locator("[data-test=update-profile-submit]")

    # -- 密码修改 -----------------------------------------------------------

    @property
    def current_password(self) -> Locator:
        return self._page.locator("[data-test=current-password]")

    @property
    def new_password(self) -> Locator:
        return self._page.locator("[data-test=new-password]")

    @property
    def new_password_confirm(self) -> Locator:
        return self._page.locator("[data-test=new-password-confirm]")

    @property
    def change_password_button(self) -> Locator:
        return self._page.locator("[data-test=change-password-submit]")

    # -- TOTP ---------------------------------------------------------------

    @property
    def totp_secret(self) -> Locator:
        return self._page.locator("[data-test=totp-secret]")

    @property
    def totp_code(self) -> Locator:
        return self._page.locator("[data-test=totp-code]")

    @property
    def verify_totp_button(self) -> Locator:
        return self._page.locator("[data-test=verify-totp]")

    # -- 操作 ---------------------------------------------------------------

    def change_password(
        self, current: str = "", new: str = "", confirm: str = ""
    ) -> None:
        if current:
            self.current_password.fill(current)
        if new:
            self.new_password.fill(new)
        if confirm:
            self.new_password_confirm.fill(confirm)
        self.change_password_button.click()
