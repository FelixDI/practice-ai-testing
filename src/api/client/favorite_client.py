"""Favorite 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class FavoriteClient(BaseClient):
    """Favorite 资源 API 客户端。"""

    def add_favorite(self, product_id: str) -> Any:
        """添加收藏。POST /favorites → 200"""
        return self.post("/favorites", json={"product_id": product_id})

    def get_favorites(self) -> Any:
        """获取收藏列表。GET /favorites → 200"""
        return self.get("/favorites")

    def get_favorite(self, favorite_id: str) -> Any:
        """获取指定收藏。GET /favorites/{favoriteId} → 200"""
        return self.get(f"/favorites/{favorite_id}")

    def delete_favorite(self, favorite_id: str) -> Any:
        """取消收藏。DELETE /favorites/{favoriteId} → 204"""
        return self.delete(f"/favorites/{favorite_id}")
