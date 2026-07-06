"""项目级 pytest fixtures —— 仅跨测试类型共享的工具。

API 专用夹具见 tests/api/conftest.py
UI 专用夹具见 tests/ui/conftest.py
"""

from __future__ import annotations

import pytest

from src.common.data_factory import (
    generate_unique_email as _factory_unique_email,
    set_seed,
)


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """Seed Faker once per session so test data is reproducible across runs."""
    set_seed(0)


def generate_unique_email(prefix: str = "test", domain: str = "e2e.example") -> str:
    """生成唯一的测试邮箱（委托给 data_factory）。"""
    return _factory_unique_email(prefix=prefix, domain=domain)
