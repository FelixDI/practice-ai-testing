"""项目级 pytest fixtures。

定义跨模块复用的 fixture，包括：
- API 客户端实例（未认证 / 已认证）
- 测试用户注册与清理
- 测试数据生成工具
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from typing import Any

import pytest

from src.api.client.brand_client import BrandClient
from src.api.client.category_client import CategoryClient
from src.api.client.user_client import UserClient


# ---------------------------------------------------------------------------
# 未认证客户端
# ---------------------------------------------------------------------------

@pytest.fixture
def user_client() -> Generator[UserClient]:
    """未登录的 User API 客户端。"""
    with UserClient() as client:
        yield client


@pytest.fixture
def brand_client() -> Generator[BrandClient]:
    """未登录的 Brand API 客户端。"""
    with BrandClient() as client:
        yield client


@pytest.fixture
def category_client() -> Generator[CategoryClient]:
    """未登录的 Category API 客户端。"""
    with CategoryClient() as client:
        yield client


# ---------------------------------------------------------------------------
# 已认证用户
# ---------------------------------------------------------------------------

@pytest.fixture
def registered_user(user_client: UserClient) -> Generator[dict[str, Any]]:
    """注册一个唯一的测试用户，返回用户元数据字典。

    返回字段：
        - email: 注册邮箱
        - password: 密码
        - user_id: 用户 ID
        - first_name / last_name
    """
    email = f"test-{uuid.uuid4().hex[:8]}@e2e.example"
    password = "Str0ng!Pass"
    payload: dict[str, Any] = {
        "first_name": "PyTest",
        "last_name": "Runner",
        "email": email,
        "password": password,
        "address": {
            "street": "Teststr.",
            "city": "Berlin",
            "country": "DE",
            "postal_code": "10115",
        },
        "dob": "1990-01-01",
    }
    response = user_client.post("/users/register", json=payload)
    assert response.status_code == 201, f"注册失败: {response.status_code} {response.text}"
    user = response.json()
    yield {
        "email": email,
        "password": password,
        "user_id": user["id"],
        "first_name": payload["first_name"],
        "last_name": payload["last_name"],
    }


@pytest.fixture
def authenticated_user(
    user_client: UserClient, registered_user: dict[str, Any]
) -> Generator[dict[str, Any]]:
    """注册用户并完成登录，返回带 Token 的 client 和用户数据。"""
    result = user_client.login(
        registered_user["email"],
        registered_user["password"],
    )
    assert "access_token" in result, f"登录失败: {result}"
    yield {
        "client": user_client,
        **registered_user,
    }
    user_client.logout()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_unique_email(prefix: str = "test") -> str:
    """生成唯一的测试邮箱。"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@e2e.example"
