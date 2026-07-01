"""Image 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class ImageClient(BaseClient):
    """Image（图片资源）API 客户端。"""

    def get_images(self) -> Any:
        """获取图片列表。GET /images → 200"""
        return self.get("/images")
