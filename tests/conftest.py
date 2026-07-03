"""项目级 pytest fixtures —— 仅跨测试类型共享的工具。

API 专用夹具见 tests/api/conftest.py
UI 专用夹具见 tests/ui/conftest.py
"""

from __future__ import annotations

import uuid


def generate_unique_email(prefix: str = "test") -> str:
    """生成唯一的测试邮箱。"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@e2e.example"
