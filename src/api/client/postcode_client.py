"""Postcode 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class PostcodeClient(BaseClient):
    """Postcode（邮编查询）API 客户端。"""

    def lookup(self, country: str, postcode: str, house_number: str | None = None) -> Any:
        """邮编查地址。GET /postcode-lookup → 200"""
        params: dict[str, str] = {"country": country, "postcode": postcode}
        if house_number is not None:
            params["house_number"] = house_number
        return self.get("/postcode-lookup", params=params)
