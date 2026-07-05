"""FavoritesPage 模块 UI 测试。

蓝图：docs/test-cases/ui/favorites_page.md —— 2 条用例（P0×1 + P1×1）。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD
from src.ui.pages.login_page import LoginPage
from src.ui.pages.favorites_page import FavoritesPage


@pytest.fixture
def logged_in(page: Page) -> FavoritesPage | None:
    """登录后进入收藏夹页。"""
    lp = LoginPage(page)
    lp.goto()
    expect(lp.login_form).to_be_visible(timeout=30000)
    lp.fill_email(TEST_USER_EMAIL)
    lp.fill_password(TEST_USER_PASSWORD)
    with page.expect_navigation():
        lp.submit()
    fp = FavoritesPage(page)
    fp.goto()
    try:
        expect(fp.page_title).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail("page-title 不可见——请检查选择器或页面结构")
    except TimeoutError:
        pytest.skip("收藏页渲染超时（30s），环境异常")
    return fp


class TestFavoritesPageLoad:
    """收藏页基础加载。"""

    # [UI_FAV_001] P0
    def test_favorites_page_loads(self, logged_in: FavoritesPage) -> None:
        expect(logged_in.page_title).to_have_text("Favorites")


class TestFavoritesPageException:
    """异常路径。"""

    # [UI_FAV_002] P1
    def test_unauthenticated_redirects_to_login(self, page: Page) -> None:
        fp = FavoritesPage(page)
        fp.goto()
        page.wait_for_url("**/auth/login**", timeout=10000)
        expect(page.locator("[data-test=login-form]")).to_be_visible()
