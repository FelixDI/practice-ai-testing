"""Product 模块 API 客户端。

封装所有 /products 相关接口。
"""

from __future__ import annotations

from typing import Any

from src.api.client.base import BaseClient


class ProductClient(BaseClient):
    """Product 资源 API 客户端。"""

    # -- 查询 ------------------------------------------------------------

    def get_products(self, **params: Any) -> Any:
        """GET /products → 200，支持 by_brand/by_category/is_rental/between/sort/page"""
        r = self.get("/products", params=params)
        return r

    def get_product(self, product_id: str) -> Any:
        """GET /products/{productId} → 200"""
        return self.get(f"/products/{product_id}")

    def get_related(self, product_id: str) -> Any:
        """GET /products/{productId}/related → 200"""
        return self.get(f"/products/{product_id}/related")

    def search_products(self, q: str | None = None, **params: Any) -> Any:
        """GET /products/search → 200"""
        p: dict[str, Any] = dict(params)
        if q is not None:
            p["q"] = q
        return self.get("/products/search", params=p if p else None)

    # -- 增删改 ----------------------------------------------------------

    def create_product(self, data: dict[str, Any]) -> Any:
        """POST /products → 200/201"""
        return self.post("/products", json=data)

    def update_product(self, product_id: str, data: dict[str, Any]) -> Any:
        """PUT /products/{productId} → 200"""
        return self.put(f"/products/{product_id}", json=data)

    def patch_product(self, product_id: str, data: dict[str, Any]) -> Any:
        """PATCH /products/{productId} → 200"""
        return self.patch(f"/products/{product_id}", json=data)

    def delete_product(self, product_id: str) -> Any:
        """DELETE /products/{productId} → 204/401"""
        return self.delete(f"/products/{product_id}")
