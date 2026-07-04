"""Footer 组件 UI 测试。

蓝图：docs/test-cases/ui/footer_component.md —— 5 条用例（P0×2 + P1×2 + P2×1）。
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.ui.pages.home_page import HomePage


@pytest.fixture
def home(page: Page) -> HomePage:
    hp = HomePage(page)
    hp.goto()
    expect(hp.header.nav_home).to_be_visible(timeout=60000)
    return hp


class TestFooterContent:
    """页脚内容渲染。"""

    # [UI_FOOTER_001] P0
    def test_footer_contains_demo_text(self, home: HomePage) -> None:
        expect(home.footer.container).to_be_visible()
        expect(home.footer.container).to_contain_text("DEMO application")

    # [UI_FOOTER_002] P0
    def test_chat_toggle_visible(self, home: HomePage) -> None:
        expect(home.footer.chat_toggle).to_be_visible()


class TestFooterLinks:
    """页脚链接。"""

    # [UI_FOOTER_003] P1
    def test_github_link_points_to_correct_repo(self, home: HomePage) -> None:
        expect(home.footer.github_link).to_be_visible()
        expect(home.footer.github_link).to_have_attribute(
            "href", "https://github.com/testsmith-io/practice-software-testing"
        )

    # [UI_FOOTER_004] P1
    def test_privacy_link_navigates(self, home: HomePage) -> None:
        with home._page.expect_navigation():
            home.footer.privacy_link.click()
        expect(home._page).to_have_url(re.compile(r"/privacy"))

    # [UI_FOOTER_005] P2
    def test_all_footer_links_present(self, home: HomePage) -> None:
        expect(home.footer.github_link).to_be_visible()
        expect(home.footer.privacy_link).to_be_visible()
        expect(home.footer.barn_images_link).to_be_visible()
        expect(home.footer.unsplash_link).to_be_visible()
