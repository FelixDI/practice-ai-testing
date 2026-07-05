"""AccountDashboard 模块 UI 测试。

蓝图：docs/test-cases/ui/account_dashboard.md —— 2 条用例（P0×1 + P1×1）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD
from src.ui.pages.login_page import LoginPage
from src.ui.pages.account_dashboard import AccountDashboard


@pytest.fixture
def logged_in(page: Page) -> AccountDashboard | None:
    """登录后进入账户概览页。"""
    lp = LoginPage(page)
    lp.goto()
    expect(lp.login_form).to_be_visible(timeout=30000)
    lp.fill_email(TEST_USER_EMAIL)
    lp.fill_password(TEST_USER_PASSWORD)
    with page.expect_navigation():
        lp.submit()
    ad = AccountDashboard(page)
    return ad


class TestAccountDashboardLoad:
    """账户概览页基础加载。"""

    # [UI_ACCT_001] P0
    def test_logged_in_nav_items_visible(
        self, logged_in: AccountDashboard
    ) -> None:
        assert "/account" in logged_in._page.url, (
            f"期望跳转到 /account，实际 {logged_in._page.url}"
        )
        # 登录态导航（下拉项 nav-my-*/nav-sign-out 默认隐藏，仅在展开时可见）
        expect(logged_in.header.nav_menu).to_be_visible()
        # 页面核心内容
        expect(logged_in.page_heading).to_be_visible()
        expect(logged_in.page_heading).to_have_text("My account")
        # 4 个功能入口按钮
        expect(logged_in.favorites_button).to_be_visible()
        expect(logged_in.profile_button).to_be_visible()
        expect(logged_in.invoices_button).to_be_visible()
        expect(logged_in.messages_button).to_be_visible()


class TestAccountDashboardException:
    """异常路径。"""

    # [UI_ACCT_002] P1
    def test_unauthenticated_redirects_to_login(self, page: Page) -> None:
        ad = AccountDashboard(page)
        ad.goto()
        page.wait_for_url("**/auth/login**", timeout=10000)
        expect(page.locator("[data-test=login-form]")).to_be_visible()
