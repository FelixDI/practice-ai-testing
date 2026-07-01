"""TOTP 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class TOTPClient(BaseClient):
    """TOTP（两步验证）API 客户端。"""

    def setup_totp(self) -> Any:
        """设置 TOTP。POST /totp/setup → 200"""
        return self.post("/totp/setup")

    def verify_totp(self, access_token: str, totp: str) -> Any:
        """验证 TOTP 码。POST /totp/verify → 200"""
        return self.post("/totp/verify", json={
            "access_token": access_token,
            "totp": totp,
        })
