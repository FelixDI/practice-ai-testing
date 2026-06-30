"""Category 模块 API 客户端。

封装所有 /categories 相关接口：
列表 / 树形结构 / 创建 / 详情 / 更新 / 部分更新 / 删除 / 搜索。
"""

from __future__ import annotations

from typing import Any

from src.api.client.base import BaseClient


class CategoryClient(BaseClient):
    """Category 资源 API 客户端。"""

    def get_categories(self) -> Any:
        """获取分类列表。GET /categories → 200，返回 Category 列表"""
        response = self.get("/categories")
        return response.json()

    def get_category_tree(self, by_category_slug: str | None = None) -> Any:
        """获取分类树（含子分类）。GET /categories/tree?by_category_slug=<slug> → 200"""
        params = {}
        if by_category_slug:
            params["by_category_slug"] = by_category_slug
        response = self.get("/categories/tree", params=params)
        return response.json()

    def get_category_tree_by_id(self, category_id: str) -> Any:
        """获取指定分类树。GET /categories/tree/{categoryId} → 200"""
        response = self.get(f"/categories/tree/{category_id}")
        return response.json()

    def get_category(self, category_id: str) -> Any:
        """获取指定分类。GET /categories/{categoryId} → 200，返回单个 Category"""
        response = self.get(f"/categories/{category_id}")
        return response.json()

    def search_categories(self, query: str) -> Any:
        """搜索分类。GET /categories/search?q=<query> → 200"""
        response = self.get("/categories/search", params={"q": query})
        return response.json()

    def create_category(self, data: dict[str, Any]) -> Any:
        """创建分类。POST /categories → 201"""
        response = self.post("/categories", json=data)
        return response.json()

    def update_category(self, category_id: str, data: dict[str, Any]) -> Any:
        """全量更新分类。PUT /categories/{categoryId} → 200"""
        response = self.put(f"/categories/{category_id}", json=data)
        return response.json()

    def patch_category(self, category_id: str, data: dict[str, Any]) -> Any:
        """部分更新分类。PATCH /categories/{categoryId} → 200"""
        response = self.patch(f"/categories/{category_id}", json=data)
        return response.json()

    def delete_category(self, category_id: str) -> "requests.Response":
        """删除分类。DELETE /categories/{categoryId} → 204"""
        response = self.delete(f"/categories/{category_id}")
        return response
