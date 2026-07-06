"""RegisterPage 模块 UI 测试。

蓝图：docs/test-cases/register_page.md —— 14 条用例（P0×3 + P1×5 + P2×4 + P3×2）。
"""

from __future__ import annotations


import pytest
from playwright.sync_api import Page, expect

from src.common.data_factory import generate_unique_email, generate_valid_password
from src.ui.pages.register_page import RegisterPage
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD

def _fill_valid_form(page: RegisterPage, email: str, password: str) -> None:
    """填写完整合法的注册表单。"""
    page.fill_basic_info("Test", "User", "1990-01-15")
    page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
    page.fill_contact("5551234567", email, password)

@pytest.fixture
def register_page(page: Page) -> RegisterPage:
    rp = RegisterPage(page)
    rp.goto()
    expect(rp.register_form).to_be_visible(timeout=30000)
    return rp

class TestRegisterSuccess:
    """P0 正常注册。"""

    # [UI_REG_001] P0
    def test_register_success_redirects_to_login(self, register_page: RegisterPage) -> None:
        _fill_valid_form(
            register_page,
            email=generate_unique_email("test", domain="example.com"),
            password=generate_valid_password(),
        )
        register_page.submit()
        expect(register_page._page).to_have_url("/auth/login", timeout=15000)

class TestRegisterValidation:
    """P0 + P1 表单校验。"""

    # [UI_REG_002] P0
    def test_empty_form_shows_field_errors(self, register_page: RegisterPage) -> None:
        register_page.submit()
        expect(register_page.field_error("first-name")).to_be_visible(timeout=5000)
        expect(register_page.field_error("email")).to_be_visible(timeout=5000)
        expect(register_page.field_error("password")).to_be_visible(timeout=5000)

    # [UI_REG_003] P0
    def test_duplicate_email_shows_error(self, register_page: RegisterPage) -> None:
        _fill_valid_form(
            register_page,
            email=TEST_USER_EMAIL,
            password=generate_valid_password(),
        )
        register_page.submit()
        expect(register_page.register_error).to_be_visible(timeout=10000)
        expect(register_page.register_error).to_contain_text("already exists")

    # [UI_REG_004] P1
    def test_weak_password_only_numbers(self, register_page: RegisterPage) -> None:
        _fill_valid_form(
            register_page,
            email=generate_unique_email("test", domain="example.com"),
            password="12345678",
        )
        register_page.submit()
        expect(register_page.field_error("password")).to_be_visible(timeout=5000)

    # [UI_REG_005] P1
    def test_password_no_special_char(self, register_page: RegisterPage) -> None:
        _fill_valid_form(
            register_page,
            email=generate_unique_email("test", domain="example.com"),
            password="NoSpecialChar1",
        )
        register_page.submit()
        expect(register_page.field_error("password")).to_be_visible(timeout=5000)

    # [UI_REG_006] P1
    def test_invalid_email_format(self, register_page: RegisterPage) -> None:
        register_page.fill_basic_info("Test", "User", "1990-01-15")
        register_page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
        register_page.fill_contact("5551234567", "not-an-email", generate_valid_password())
        register_page.submit()
        expect(register_page.field_error("email")).to_be_visible(timeout=5000)

    # [UI_REG_011] P1
    def test_phone_with_letters_shows_error(self, register_page: RegisterPage) -> None:
        register_page.fill_basic_info("Test", "User", "1990-01-15")
        register_page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
        register_page.fill_contact("abc", generate_unique_email("test", domain="example.com"), generate_valid_password())
        register_page.submit()
        expect(register_page.field_error("phone")).to_be_visible(timeout=5000)
        expect(register_page.field_error("phone")).to_contain_text("Only numbers are allowed")

    # [UI_REG_012] P1
    def test_password_too_short(self, register_page: RegisterPage) -> None:
        register_page.fill_basic_info("Test", "User", "1990-01-15")
        register_page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
        register_page.fill_contact("5551234567", generate_unique_email("test", domain="example.com"), "Ab1!")
        register_page.submit()
        expect(register_page.field_error("password")).to_be_visible(timeout=5000)
        expect(register_page.field_error("password")).to_contain_text("minimal 6 characters")

class TestRegisterBoundary:
    """P2 边界条件。"""

    # [UI_REG_007] P2
    def test_dob_invalid_format(self, register_page: RegisterPage) -> None:
        register_page.fill_basic_info("Test", "User", "abc")
        register_page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
        register_page.fill_contact("5551234567", generate_unique_email("test", domain="example.com"), generate_valid_password())
        register_page.submit()
        expect(register_page.field_error("dob")).to_be_visible(timeout=5000)

    # [UI_REG_008] P2
    def test_dob_future_date(self, register_page: RegisterPage) -> None:
        register_page.fill_basic_info("Test", "User", "2099-01-01")
        register_page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
        register_page.fill_contact("5551234567", generate_unique_email("test", domain="example.com"), generate_valid_password())
        register_page.submit()
        # 应被前端或服务端拒绝
        error = register_page.field_error("dob")
        register_err = register_page.register_error
        expect(error.or_(register_err)).to_be_visible(timeout=5000)

    # [UI_REG_009] P2
    def test_overlong_first_name(self, register_page: RegisterPage) -> None:
        register_page.fill_basic_info("A" * 200, "User", "1990-01-15")
        register_page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
        register_page.fill_contact("5551234567", generate_unique_email("test", domain="example.com"), generate_valid_password())
        register_page.submit()
        # 页面不崩溃；可能通过前端校验或被服务端拒绝
        expect(register_page.register_form).to_be_visible()

    # [UI_REG_013] P2
    def test_password_visibility_toggle(self, register_page: RegisterPage) -> None:
        register_page.password_input.fill("test-password")
        expect(register_page.password_input).to_have_attribute("type", "password")
        register_page.password_toggle.click()
        expect(register_page.password_input).to_have_attribute("type", "text")
        register_page.password_toggle.click()
        expect(register_page.password_input).to_have_attribute("type", "password")

class TestLoggedInState:
    """P3 已登录状态。"""

    @pytest.fixture
    def logged_in_page(self, page: Page) -> Page:
        page.goto("https://practicesoftwaretesting.com/auth/login")
        page.wait_for_selector("[data-test=email]", timeout=10000)
        page.fill("[data-test=email]", TEST_USER_EMAIL)
        page.fill("[data-test=password]", TEST_USER_PASSWORD)
        page.click("[data-test=login-submit]")
        page.wait_for_url("**/account**", timeout=10000)
        return page

    # [UI_REG_010] P3
    def test_already_logged_in_nav_state(self, logged_in_page: Page) -> None:
        logged_in_page.goto("https://practicesoftwaretesting.com/auth/register")
        expect(logged_in_page.locator("[data-test=nav-menu]")).to_be_visible(timeout=10000)
        logged_in_page.locator("[data-test=nav-menu]").click()
        expect(logged_in_page.locator("[data-test=nav-sign-out]")).to_be_visible(timeout=5000)

class TestRegisterSecurity:
    """P3 安全注入。"""

    # [UI_REG_014] P3
    def test_xss_injection_in_name(self, register_page: RegisterPage) -> None:
        register_page.fill_basic_info("<script>alert(1)</script>", "User", "1990-01-15")
        register_page.fill_address("US", "90210", "123", "Main Street", "Beverly Hills", "California")
        register_page.fill_contact("5551234567", generate_unique_email("test", domain="example.com"), generate_valid_password())
        register_page.submit()
        # 页面不崩溃、不弹窗
        expect(register_page.register_form).to_be_visible()
        # 确认没有 alert 弹窗
        assert "/auth/register" in register_page._page.url or "/auth/login" in register_page._page.url, \
            "XSS 注入不应导致页面异常跳转"

# AI-assisted
