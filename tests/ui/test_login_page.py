"""LoginPage 模块 UI 测试。

蓝图：docs/test-cases/login_page.md —— 12 条用例（P0×3 + P1×3 + P2×4 + P3×2）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.login_page import LoginPage
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD
from src.common.data_factory import generate_unique_email


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.goto()
    expect(lp.login_form).to_be_visible(timeout=30000)
    return lp


class TestLoginSuccess:
    """P0 正常登录。"""

    # [UI_LOGIN_001] P0
    def test_login_success_redirects_to_account(self, login_page: LoginPage) -> None:
        login_page.fill_email(TEST_USER_EMAIL)
        login_page.fill_password(TEST_USER_PASSWORD)
        with login_page._page.expect_navigation():
            login_page.submit()
        assert "/account" in login_page._page.url, f"期望跳转到 /account，实际 {login_page._page.url}"


class TestLoginFailure:
    """P0 + P1 登录失败场景。"""

    # [UI_LOGIN_002] P0
    def test_wrong_password_shows_error(self, login_page: LoginPage) -> None:
        login_page.fill_email(TEST_USER_EMAIL)
        login_page.fill_password("wrong-password-123")
        login_page.submit()
        expect(login_page.login_error).to_be_visible(timeout=5000)
        expect(login_page.login_error).to_contain_text("Invalid email or password")

    # [UI_LOGIN_003] P0
    def test_empty_form_validation(self, login_page: LoginPage) -> None:
        login_page.submit()
        # HTML5 required validation keeps user on the login page
        expect(login_page.login_form).to_be_visible()
        assert "/auth/login" in login_page._page.url, "空表单提交不应离开登录页"

    # [UI_LOGIN_004] P1
    def test_nonexistent_email_shows_error(self, login_page: LoginPage) -> None:
        random_email = generate_unique_email("no-such-user", domain="example.com")
        login_page.fill_email(random_email)
        login_page.fill_password("some-password-123")
        login_page.submit()
        expect(login_page.login_error).to_be_visible(timeout=5000)
        expect(login_page.login_error).to_contain_text("Invalid email or password")


class TestLoginNavigation:
    """P1 登录页内导航链接。"""

    # [UI_LOGIN_005] P1
    def test_register_link_redirects(self, login_page: LoginPage) -> None:
        with login_page._page.expect_navigation():
            login_page.register_link.click()
        expect(login_page._page).to_have_url("/auth/register")

    # [UI_LOGIN_006] P1
    def test_forgot_password_link_redirects(self, login_page: LoginPage) -> None:
        with login_page._page.expect_navigation():
            login_page.forgot_password_link.click()
        expect(login_page._page).to_have_url("/auth/forgot-password")


class TestLoginBoundary:
    """P2 边界条件。"""

    # [UI_LOGIN_007] P2
    def test_overlong_email(self, login_page: LoginPage) -> None:
        long_email = "A" * 200 + "@example.com"
        login_page.fill_email(long_email)
        login_page.fill_password("any-password")
        login_page.submit()
        # 前端 HTML5 校验拦截，显示 "Email format is invalid"，不会提交到服务端
        expect(login_page.email_input).to_have_attribute("aria-invalid", "true", timeout=5000)
        assert "/auth/login" in login_page._page.url, "校验失败不应离开登录页"

    # [UI_LOGIN_008] P2
    def test_overlong_password(self, login_page: LoginPage) -> None:
        login_page.fill_email(TEST_USER_EMAIL)
        login_page.fill_password("X" * 300)
        login_page.submit()
        # 前端校验拦截超长密码，显示 "Password length is invalid"
        expect(login_page._page.locator("text=Password length is invalid")).to_be_visible(timeout=5000)
        assert "/auth/login" in login_page._page.url

    # [UI_LOGIN_009] P2
    def test_sql_injection_in_email(self, login_page: LoginPage) -> None:
        login_page.fill_email("' OR '1'='1")
        login_page.fill_password("' OR '1'='1")
        login_page.submit()
        # 前端校验拦截非法邮箱格式；页面不崩溃、不报 500
        expect(login_page.email_input).to_have_attribute("aria-invalid", "true", timeout=5000)
        assert "/auth/login" in login_page._page.url

    # [UI_LOGIN_011] P2
    def test_password_visibility_toggle(self, login_page: LoginPage) -> None:
        login_page.fill_password("test-password")
        # 默认隐藏
        expect(login_page.password_input).to_have_attribute("type", "password")
        # 点击 eye icon 切换为明文
        login_page.password_toggle.click()
        expect(login_page.password_input).to_have_attribute("type", "text")
        # 再次点击切回密文
        login_page.password_toggle.click()
        expect(login_page.password_input).to_have_attribute("type", "password")


class TestLoggedInRedirect:
    """P3 已登录状态。"""

    @pytest.fixture
    def logged_in_page(self, page: Page) -> Page:
        """登录后返回 page，用于访问 /auth/login 测试自动跳转。"""
        page.goto("https://practicesoftwaretesting.com/auth/login")
        page.wait_for_selector("[data-test=email]", timeout=10000)
        page.fill("[data-test=email]", TEST_USER_EMAIL)
        page.fill("[data-test=password]", TEST_USER_PASSWORD)
        page.click("[data-test=login-submit]")
        page.wait_for_url("**/account**", timeout=10000)
        return page

    # [UI_LOGIN_010] P3
    def test_already_logged_in_nav_state(self, logged_in_page: Page) -> None:
        logged_in_page.goto("https://practicesoftwaretesting.com/auth/login")
        # Toolshop 不会自动跳转，但导航栏应显示已登录状态
        expect(logged_in_page.locator("[data-test=nav-menu]")).to_be_visible(timeout=10000)
        logged_in_page.locator("[data-test=nav-menu]").click()
        expect(logged_in_page.locator("[data-test=nav-sign-out]")).to_be_visible(timeout=5000)

class TestLoginSecurity:
    """P3 安全注入。"""

    # [UI_LOGIN_012] P3
    def test_xss_injection_in_email(self, login_page: LoginPage) -> None:
        login_page.fill_email("<script>alert(1)</script>")
        login_page.fill_password("any-password-123")
        login_page.submit()
        # 前端校验拦截非法邮箱格式；页面不崩溃、不弹窗
        expect(login_page.email_input).to_have_attribute("aria-invalid", "true", timeout=5000)
        assert "/auth/login" in login_page._page.url, "XSS 注入不应离开登录页"
        expect(login_page.login_form).to_be_visible()

# AI-assisted
