"""Product Spec 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class ProductSpecClient(BaseClient):
    """Product Spec 资源 API 客户端。"""

    def get_specs(self, product_id: str) -> Any:
        """获取产品规格列表。GET /products/{productId}/specs → 200"""
        return self.get(f"/products/{product_id}/specs")

    def add_spec(self, product_id: str, data: dict[str, Any]) -> Any:
        """添加产品规格。POST /products/{productId}/specs → 201"""
        return self.post(f"/products/{product_id}/specs", json=data)

    def get_spec(self, product_id: str, spec_id: str) -> Any:
        """获取指定规格。GET /products/{productId}/specs/{specId} → 200"""
        return self.get(f"/products/{product_id}/specs/{spec_id}")

    def update_spec(self, product_id: str, spec_id: str, data: dict[str, Any]) -> Any:
        """更新产品规格。PUT /products/{productId}/specs/{specId} → 200"""
        return self.put(f"/products/{product_id}/specs/{spec_id}", json=data)

    def delete_spec(self, product_id: str, spec_id: str) -> Any:
        """删除产品规格。DELETE /products/{productId}/specs/{specId} → 204"""
        return self.delete(f"/products/{product_id}/specs/{spec_id}")

    def get_spec_names(self) -> Any:
        """获取所有规格名称。GET /product-specs/names → 200"""
        return self.get("/product-specs/names")
