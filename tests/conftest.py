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
from src.api.client.contact_client import ContactClient
from src.api.client.favorite_client import FavoriteClient
from src.api.client.payment_client import PaymentClient
from src.api.client.product_spec_client import ProductSpecClient
from src.api.client.user_client import UserClient
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


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


@pytest.fixture
def favorite_client() -> Generator[FavoriteClient]:
    """未登录的 Favorite API 客户端。"""
    with FavoriteClient() as client:
        yield client


@pytest.fixture
def payment_client() -> Generator[PaymentClient]:
    """未登录的 Payment API 客户端。"""
    with PaymentClient() as client:
        yield client


@pytest.fixture
def contact_client() -> Generator[ContactClient]:
    """未登录的 Contact API 客户端。"""
    with ContactClient() as client:
        yield client


@pytest.fixture
def product_spec_client() -> Generator[ProductSpecClient]:
    """未登录的 Product Spec API 客户端。"""
    with ProductSpecClient() as client:
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


# ---------------------------------------------------------------------------
# module 级认证 Token（复用固定测试账号，减少注册请求量）
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def _mod_auth_token() -> Generator[str]:
    """module 级：使用固定测试账号登录，返回 access_token。

    适用于只读 / 不修改共享状态的操作。
    """
    with UserClient() as uc:
        result = uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        token: str = result["access_token"]
        yield token
        uc.logout()
