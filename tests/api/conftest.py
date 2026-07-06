"""API 测试专用夹具。

所有 API Client 实例、用户注册/登录、Token 管理均在此定义，
仅供 tests/api/ 下的测试使用，UI 和集成测试不会加载。
"""

from __future__ import annotations

import pytest

from src.api.client.brand_client import BrandClient
from src.api.client.category_client import CategoryClient
from src.api.client.contact_client import ContactClient
from src.api.client.favorite_client import FavoriteClient
from src.api.client.image_client import ImageClient
from src.api.client.payment_client import PaymentClient
from src.api.client.postcode_client import PostcodeClient
from src.api.client.product_spec_client import ProductSpecClient
from src.api.client.report_client import ReportClient
from src.api.client.totp_client import TOTPClient
from src.api.client.user_client import UserClient
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD
from src.common.data_factory import generate_unique_email, new_user_data


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


@pytest.fixture
def totp_client() -> Generator[TOTPClient]:
    """未登录的 TOTP API 客户端。"""
    with TOTPClient() as client:
        yield client


@pytest.fixture
def report_client() -> Generator[ReportClient]:
    """未登录的 Report API 客户端。"""
    with ReportClient() as client:
        yield client


@pytest.fixture
def image_client() -> Generator[ImageClient]:
    """未登录的 Image API 客户端。"""
    with ImageClient() as client:
        yield client


@pytest.fixture
def postcode_client() -> Generator[PostcodeClient]:
    """未登录的 Postcode API 客户端。"""
    with PostcodeClient() as client:
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
    payload = new_user_data(address_city="Berlin")
    response = user_client.post("/users/register", json=payload)
    assert response.status_code == 201, f"注册失败: {response.status_code} {response.text}"
    user = response.json()
    yield {
        "email": payload["email"],
        "password": payload["password"],
        "user_id": user["id"],
        "first_name": payload["first_name"],
        "last_name": payload["last_name"],
    }


@pytest.fixture
def destructive_user(user_client: UserClient) -> Generator[dict[str, Any]]:
    """注册一个"牺牲品"用户，供破坏性测试使用。

    与 registered_user 的区别：此 fixture 语义明确为"这个账号会被玩坏"——
    测试可以随意错误密码、触发锁定、删除账号，不影响正常共享账号。
    每次 function 级新注册，用完即弃。
    """
    payload = new_user_data()
    r = user_client.post("/users/register", json=payload)
    assert r.status_code == 201, f"destructive_user 注册失败: {r.status_code} {r.text}"
    user = r.json()
    yield {
        "email": payload["email"],
        "password": payload["password"],
        "user_id": user["id"],
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
# module 级认证 Token
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
