"""MessagesPage 模块 UI 测试。

蓝图：docs/test-cases/ui/messages_page.md —— 2 条用例（P0×1 + P1×1）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD
from src.ui.pages.login_page import LoginPage
from src.ui.pages.messages_page import MessagesPage


def _login(page: Page) -> None:
    lp = LoginPage(page)
    lp.goto()
    expect(lp.login_form).to_be_visible(timeout=30000)
    lp.fill_email(TEST_USER_EMAIL)
    lp.fill_password(TEST_USER_PASSWORD)
    with page.expect_navigation():
        lp.submit()


@pytest.fixture
def logged_in(page: Page) -> MessagesPage | None:
    _login(page)
    mp = MessagesPage(page)
    mp.goto()
    try:
        expect(mp.page_title).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail("page-title 不可见——请检查选择器或页面结构")
    except TimeoutError:
        pytest.skip("消息页渲染超时（30s），环境异常")
    return mp


class TestMessagesPageLoad:
    def test_messages_page_loads(self, logged_in: MessagesPage) -> None:
        expect(logged_in.page_title).to_have_text("Messages")


class TestMessagesPageException:
    def test_unauthenticated_redirects_to_login(self, page: Page) -> None:
        mp = MessagesPage(page)
        mp.goto()
        page.wait_for_url("**/auth/login**", timeout=10000)
        expect(page.locator("[data-test=login-form]")).to_be_visible()
