"""UI 测试全局 fixture 和共享工具。"""

from __future__ import annotations

import pytest
import requests
from playwright.sync_api import BrowserContext, Page

from src.common.config import API_BASE_URL, UI_BASE_URL


@pytest.fixture(scope="session")
def base_url() -> str:
    """Playwright base URL，从 config.py 读取。"""
    return UI_BASE_URL


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Playwright page（base_url 由 pytest-base-url 插件注入）。"""
    return context.new_page()


def fetch_valid_product_id() -> str:
    """从 API 获取第一个有效商品 ID。

    商品数据会被服务端周期性重建，硬编码 ID 迟早过期（已发生两次）。
    所有需要商品 ID 的 fixture 应通过此函数动态获取。
    """
    r = requests.get(f"{API_BASE_URL}/products?page=1", timeout=10)
    if r.status_code != 200:
        pytest.skip("商品 API 不可用，无法获取有效商品 ID")
    data: list[dict] = r.json().get("data", [])
    if not data:
        pytest.skip("商品 API 返回空列表，无可用商品")
    return data[0]["id"]
