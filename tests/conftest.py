"""项目级 pytest fixtures —— 仅跨测试类型共享的工具。

API 专用夹具见 tests/api/conftest.py
UI 专用夹具见 tests/ui/conftest.py
"""

from __future__ import annotations

import pytest
import requests

from src.common.config import (
    API_BASE_URL,
    JENKINS_TEST_EMAIL,
    JENKINS_TEST_PASSWORD,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)
from src.common.data_factory import (
    generate_unique_email as _factory_unique_email,
    set_seed,
)


# ---------------------------------------------------------------------------
# 账号健康检查（靶场周期性重建会清空所有用户）
# ---------------------------------------------------------------------------

_MANAGED_ACCOUNTS: list[tuple[str, str, str]] = [
    ("local", TEST_USER_EMAIL, TEST_USER_PASSWORD),
    ("jenkins", JENKINS_TEST_EMAIL, JENKINS_TEST_PASSWORD),
]


def _ensure_account(label: str, email: str, password: str) -> str:
    """验证并修复单个测试账号。返回状态：ok / registered / error。"""
    r = requests.post(
        f"{API_BASE_URL}/users/login",
        json={"email": email, "password": password},
        timeout=15,
    )
    if r.status_code == 200:
        return "ok"

    # 401 → 账号不存在或被删，重新注册
    rr = requests.post(
        f"{API_BASE_URL}/users/register",
        json={
            "first_name": "Test",
            "last_name": label.capitalize(),
            "email": email,
            "password": password,
            "address": {
                "street": "Teststr.",
                "city": "Berlin",
                "country": "DE",
                "postal_code": "10115",
            },
            "dob": "1990-01-01",
        },
        timeout=15,
    )
    if rr.status_code in (200, 201):
        return "registered"
    return f"error({rr.status_code})"


def _verify_test_accounts() -> None:
    """确保所有托管测试账号可用（靶场重建后自动恢复）。"""
    issues: list[str] = []
    for label, email, _password in _MANAGED_ACCOUNTS:
        status = _ensure_account(label, email, _password)
        if status == "registered":
            issues.append(f"🔧 {label} 账号已重建")
        elif status != "ok":
            issues.append(f"❌ {label} 账号异常: {status}")

    if issues:
        header = "⚠️  靶场账号健康检查:"
        print(f"\n{header}\n" + "\n".join(f"   {i}" for i in issues) + "\n")


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """Session 初始化：Faker 种子 + 账号健康检查。"""
    set_seed(0)
    _verify_test_accounts()


# ---------------------------------------------------------------------------
# 共享工具
# ---------------------------------------------------------------------------


def generate_unique_email(prefix: str = "test", domain: str = "e2e.example") -> str:
    """生成唯一的测试邮箱（委托给 data_factory）。"""
    return _factory_unique_email(prefix=prefix, domain=domain)
