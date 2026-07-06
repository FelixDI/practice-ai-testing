"""UI 测试全局 fixture 和共享工具。"""

from __future__ import annotations

from typing import Any

import pytest
import requests
from playwright.sync_api import BrowserContext, Page

from src.common.config import API_BASE_URL, UI_BASE_URL
from src.common.data_factory import new_user_data


@pytest.fixture(scope="session")
def base_url() -> str:
    """Playwright base URL，从 config.py 读取。"""
    return UI_BASE_URL


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Playwright page（base_url 由 pytest-base-url 插件注入）。"""
    return context.new_page()


def is_cloudflare(page: Page) -> bool:
    """检查当前页面是否被 Cloudflare 拦截。

    供各 UI fixture 复用，避免每个测试文件重复定义。
    """
    try:
        body = page.content()
        return "cloudflare" in body.lower() or "checking your browser" in body.lower()
    except Exception:
        return False


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


@pytest.fixture
def destructive_user() -> dict[str, Any]:
    """注册一个"牺牲品"用户，供 UI 破坏性测试使用。

    通过 API 注册（非 UI 流程），返回 email/password/user_id。
    测试可以随意错误密码、触发锁定，不影响 TEST_USER_* 固定账号。
    """
    payload = new_user_data()
    r = requests.post(
        f"{API_BASE_URL}/users/register",
        json=payload,
        timeout=30,
    )
    assert r.status_code == 201, f"destructive_user 注册失败: {r.status_code} {r.text}"
    user: dict[str, Any] = r.json()
    return {
        "email": payload["email"],
        "password": payload["password"],
        "user_id": user["id"],
    }
