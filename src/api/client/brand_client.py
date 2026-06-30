"""Brand 模块 API 客户端。

封装所有 /brands 相关接口：列表 / 创建 / 详情 / 更新 / 部分更新 / 删除 / 搜索。
"""

from __future__ import annotations

from typing import Any

from src.api.client.base import BaseClient


class BrandClient(BaseClient):
    """Brand 资源 API 客户端。"""

    def get_brands(self) -> Any:
        """获取品牌列表。GET /brands → 200，返回 Brand 列表"""
        response = self.get("/brands")
        return response.json()

    def get_brand(self, brand_id: str) -> Any:
        """获取指定品牌。GET /brands/{brandId} → 200，返回单个 Brand"""
        response = self.get(f"/brands/{brand_id}")
        return response.json()

    def search_brands(self, query: str) -> Any:
        """搜索品牌。GET /brands/search?q=<query> → 200，返回 Brand 列表"""
        response = self.get("/brands/search", params={"q": query})
        return response.json()

    def create_brand(self, data: dict[str, Any]) -> Any:
        """创建品牌。POST /brands → 201，返回新 Brand"""
        response = self.post("/brands", json=data)
        return response.json()

    def update_brand(self, brand_id: str, data: dict[str, Any]) -> Any:
        """全量更新品牌。PUT /brands/{brandId} → 200，返回更新后 Brand"""
        response = self.put(f"/brands/{brand_id}", json=data)
        return response.json()

    def patch_brand(self, brand_id: str, data: dict[str, Any]) -> Any:
        """部分更新品牌。PATCH /brands/{brandId} → 200，返回更新后 Brand"""
        response = self.patch(f"/brands/{brand_id}", json=data)
        return response.json()

    def delete_brand(self, brand_id: str) -> "requests.Response":
        """删除品牌。DELETE /brands/{brandId} → 204"""
        response = self.delete(f"/brands/{brand_id}")
        return response
