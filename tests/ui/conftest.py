"""UI 测试全局 fixture。"""

from __future__ import annotations

import pytest
from playwright.sync_api import BrowserContext, Page

from src.common.config import UI_BASE_URL


@pytest.fixture(scope="session")
def base_url() -> str:
    """Playwright base URL，从 config.py 读取。"""
    return UI_BASE_URL


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Playwright page（base_url 由 pytest-base-url 插件注入）。"""
    return context.new_page()
