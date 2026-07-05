"""ContactPage 模块 UI 测试。

蓝图：docs/test-cases/ui/contact_page.md —— 6 条用例（P0×2 + P1×2 + P2×1 + P3×1）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.contact_page import ContactPage


def _is_cloudflare(page: Page) -> bool:
    """检查当前页面是否被 Cloudflare 拦截。"""
    try:
        body = page.content()
        return "cloudflare" in body.lower() or "checking your browser" in body.lower()
    except Exception:
        return False


@pytest.fixture
def contact(page: Page) -> ContactPage | None:
    """加载留言表单页。"""
    cp = ContactPage(page)
    response = page.goto(ContactPage.BASE_URL, wait_until="load", timeout=30000)
    if response and response.status == 403 and _is_cloudflare(page):
        pytest.skip("Cloudflare 拦截留言页，环境不可用")
    try:
        expect(cp.first_name).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail("first-name 不可见——请检查选择器或页面结构")
    except TimeoutError:
        pytest.skip("留言页渲染超时（30s），环境异常")
    return cp


class TestContactPageLoad:
    """留言表单页基础加载。"""

    # [UI_CONTACT_001] P0
    def test_form_elements_visible(self, contact: ContactPage) -> None:
        for el in contact.all_form_elements:
            expect(el).to_be_visible()

    # [UI_CONTACT_002] P0
    def test_empty_form_shows_validation_errors(self, contact: ContactPage) -> None:
        contact.submit()
        expect(contact.validation_errors).to_have_count(5)
        expect(contact.validation_errors.first).to_contain_text("is required")


class TestContactValidation:
    """表单字段校验。"""

    # [UI_CONTACT_003] P1
    def test_invalid_email_format(self, contact: ContactPage) -> None:
        contact.fill_form(email="not-an-email")
        contact.submit()
        expect(contact.validation_errors).to_contain_text("Email format is invalid")

    # [UI_CONTACT_004] P1
    def test_message_min_50_chars(self, contact: ContactPage) -> None:
        contact.fill_form(message="too short")
        contact.submit()
        expect(contact.validation_errors).to_contain_text(
            "Message must be minimal 50 characters"
        )


class TestContactBoundary:
    """边界覆盖。"""

    # [UI_CONTACT_005] P2
    def test_subject_has_seven_options_including_placeholder(
        self, contact: ContactPage
    ) -> None:
        options = contact.subject.locator("option")
        expect(options).to_have_count(7)
        expected = [
            "Select a subject *",
            "Customer service",
            "Webmaster",
            "Return",
            "Payments",
            "Warranty",
            "Status of my order",
        ]
        actual = options.all_text_contents()
        assert actual == expected, f"选项不匹配: {actual}"


class TestContactSecurity:
    """深度防御。"""

    # [UI_CONTACT_006] P3
    def test_xss_in_fields_does_not_crash(self, page: Page) -> None:
        cp = ContactPage(page)
        cp.goto()
        xss = '<script>alert(1)</script>'
        cp.first_name.fill(xss)
        cp.last_name.fill(xss)
        cp.email.fill("xss@example.com")
        cp.message.fill(xss * 2)  # xss * 2 > 50 chars
        cp.submit()
        # 页面不崩溃，Header 仍可见
        expect(cp.header.nav_home).to_be_visible(timeout=10000)
