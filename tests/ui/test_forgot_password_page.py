"""ForgotPasswordPage 模块 UI 测试。

蓝图：docs/test-cases/ui/forgot_password_page.md —— 4 条用例（P0×2 + P1×1 + P3×1）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.forgot_password_page import ForgotPasswordPage
from tests.ui.conftest import is_cloudflare


@pytest.fixture
def forgot(page: Page) -> ForgotPasswordPage | None:
    """加载忘记密码页。"""
    fp = ForgotPasswordPage(page)
    response = page.goto(ForgotPasswordPage.BASE_URL, wait_until="load", timeout=30000)
    if response and response.status == 403 and is_cloudflare(page):
        pytest.skip("Cloudflare 拦截忘记密码页，环境不可用")
    try:
        expect(fp.form).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail("forgot-password-form 不可见——请检查选择器或页面结构")
    except TimeoutError:
        pytest.skip("忘记密码页渲染超时（30s），环境异常")
    return fp


class TestForgotPasswordPageLoad:
    """忘记密码页基础加载。"""

    # [UI_FORGOT_001] P0
    def test_form_elements_visible(self, forgot: ForgotPasswordPage) -> None:
        expect(forgot.email_input).to_be_visible()
        expect(forgot.submit_button).to_be_visible()
        expect(forgot.form).to_be_visible()

    # [UI_FORGOT_002] P0
    def test_valid_email_shows_confirmation(
        self, forgot: ForgotPasswordPage
    ) -> None:
        forgot.submit("customer@practicesoftwaretesting.com")
        expect(forgot.confirmation_message).to_be_visible(timeout=10000)
        expect(forgot.confirmation_message).to_contain_text(
            "page.forgot-password.confirm"
        )


class TestForgotPasswordException:
    """异常路径。"""

    # [UI_FORGOT_003] P1
    def test_empty_email_does_not_crash(self, forgot: ForgotPasswordPage) -> None:
        forgot.submit("")
        # 页面不崩溃，Header 仍可见
        expect(forgot.header.nav_home).to_be_visible(timeout=5000)


class TestForgotPasswordSecurity:
    """深度防御。"""

    # [UI_FORGOT_004] P3
    def test_xss_injection_does_not_crash(self, page: Page) -> None:
        fp = ForgotPasswordPage(page)
        fp.goto()
        fp.submit("<script>alert(1)</script>")
        expect(fp.header.nav_home).to_be_visible(timeout=10000)
