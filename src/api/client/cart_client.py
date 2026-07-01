"""Cart 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class CartClient(BaseClient):
    """Cart 资源 API 客户端。"""

    def create_cart(self) -> Any:
        return self.post("/carts")

    def add_item(self, cart_id: str, product_id: str, quantity: int) -> Any:
        return self.post(f"/carts/{cart_id}", json={"product_id": product_id, "quantity": quantity})

    def get_cart(self, cart_id: str) -> Any:
        return self.get(f"/carts/{cart_id}")

    def update_quantity(self, cart_id: str, product_id: str, quantity: int) -> Any:
        return self.put(f"/carts/{cart_id}/product/quantity", json={"product_id": product_id, "quantity": quantity})

    def remove_item(self, cart_id: str, product_id: str) -> Any:
        return self.delete(f"/carts/{cart_id}/product/{product_id}")

    def delete_cart(self, cart_id: str) -> Any:
        return self.delete(f"/carts/{cart_id}")
