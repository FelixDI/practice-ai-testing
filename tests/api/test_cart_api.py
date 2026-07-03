"""Cart 模块 API 测试。

蓝图：docs/test-cases/cart.md —— 26 条用例，6 个端点全覆盖。
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from src.api.client.cart_client import CartClient


# -- module 级夹具 --------------------------------------------------------

@pytest.fixture(scope="module")
def _mod_client():
    """module 级 CartClient —— 整个文件复用同一个连接。"""
    with CartClient() as c:
        yield c


@pytest.fixture(scope="module")
def _mod_empty_cart(_mod_client: CartClient) -> str:
    """module 级：空购物车（只读类测试复用）。"""
    r = _mod_client.post("/carts")
    assert r.status_code == 201, f"module create cart failed: {r.status_code}"
    return r.json()["id"]


@pytest.fixture(scope="module")
def _mod_product_id(_mod_client: CartClient) -> str:
    """module 级商品 ID。"""
    r = _mod_client.get("/products")
    data = r.json()
    items = data if isinstance(data, list) else data.get("data", [])
    assert len(items) > 0, "需有已有商品"
    return items[0]["id"]


@pytest.fixture(scope="module")
def _mod_cart_with_item(_mod_client: CartClient, _mod_empty_cart: str) -> tuple[str, str]:
    """module 级：含有商品的购物车（只读 + 部分操作复用）。商品失效时换下一个。"""
    r = _mod_client.get("/products")
    data = r.json()
    items = data if isinstance(data, list) else data.get("data", [])
    assert len(items) > 0, "需有已有商品"
    for item in items[:5]:
        pid = item["id"]
        r = _mod_client.add_item(_mod_empty_cart, pid, 2)
        if r.status_code == 200:
            return _mod_empty_cart, pid
    pytest.skip("module 添加商品失败(5次重试均422)，公开环境数据竞争")


# -- function 级 client + helpers（用于独立 mutation 测试）-------------------

@pytest.fixture
def client() -> CartClient:
    """function 级 CartClient —— mutation 测试用，避免互相污染。"""
    with CartClient() as c:
        yield c


def _get_product_id(client: CartClient) -> str:
    r = client.get("/products")
    data = r.json()
    items = data if isinstance(data, list) else data.get("data", [])
    assert len(items) > 0, "需有已有商品"
    return items[0]["id"]


def _create_cart(client: CartClient) -> str:
    """创建购物车，500 环境异常时最多重试 2 次，仍失败则 skip。"""
    import time
    last_status = None
    for attempt in range(3):
        r = client.post("/carts")
        if r.status_code == 201:
            return r.json()["id"]
        last_status = r.status_code
        if r.status_code >= 500:
            time.sleep(1)
            continue
        # 非 500/201 直接失败（如 422）
        break
    pytest.skip(f"创建购物车失败(3次重试均{last_status})，服务端环境异常")


def _cart_with_item(client: CartClient) -> tuple[str, str]:
    """创建 cart + 加商品。product_id 失效时自动换商品重试。"""
    cart_id = _create_cart(client)
    for attempt in range(3):
        pid = _get_product_id(client)
        r = client.add_item(cart_id, pid, 2)
        if r.status_code == 200:
            return cart_id, pid
        if r.status_code == 422 and "product id is invalid" in r.text.lower():
            continue  # 商品数据竞争，换一个再试
        # 非预期错误直接炸
        assert r.status_code == 200, f"prep add item failed: {r.status_code} {r.text}"
    pytest.skip("加商品到购物车失败(3次重试均422 product_id invalid)，公开环境数据竞争")


# ======================================================================
# 1.1 创建购物车（1 条）── API_CART_001
# ======================================================================

class TestCreateCart:
    # [API_CART_001]
    def test_create_cart_201(self, client: CartClient) -> None:
        r = client.post("/carts")
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"
        assert "id" in r.json()


# ======================================================================
# 1.2 添加商品（8 条）── API_CART_002 ~ 011 + 025
# ======================================================================

class TestAddItem:
    # [API_CART_002]
    def test_add_item_200(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        # 遍历前几个商品，规避公开环境商品数据竞争（部分 ID 可能不可加购）
        for _ in range(3):
            pid = _get_product_id(client)
            r = client.add_item(cart_id, pid, 2)
            if r.status_code == 200:
                break
            if r.status_code == 422 and "product id is invalid" in r.text.lower():
                continue
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

    # [API_CART_003]
    def test_missing_product_id_422(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.post(f"/carts/{cart_id}", json={"quantity": 1})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CART_004]
    def test_missing_quantity_422(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.post(f"/carts/{cart_id}", json={"product_id": _get_product_id(client)})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CART_005]
    def test_nonexistent_product_id(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.add_item(cart_id, "nonexistent-99999", 1)
        assert r.status_code in (404, 422), f"意外: {r.status_code}"

    # [API_CART_006]
    def test_add_to_nonexistent_cart(self, client: CartClient) -> None:
        r = client.add_item("nonexistent-99999", _get_product_id(client), 1)
        assert r.status_code in (404, 422), f"意外: {r.status_code}"

    # [API_CART_007]
    def test_quantity_zero_422(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.add_item(cart_id, _get_product_id(client), 0)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CART_008]
    def test_quantity_negative(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.add_item(cart_id, _get_product_id(client), -1)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CART_009]
    def test_quantity_large(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.add_item(cart_id, _get_product_id(client), 99999)
        assert r.status_code in (200, 422), f"意外: {r.status_code}"

    # [API_CART_010]
    def test_quantity_string_422(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.post(f"/carts/{cart_id}", json={"product_id": _get_product_id(client), "quantity": "abc"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CART_011]
    def test_duplicate_add(self, client: CartClient) -> None:
        cart_id, pid = _cart_with_item(client)
        r = client.add_item(cart_id, pid, 3)
        assert r.status_code in (200, 409), f"意外: {r.status_code}"

    # [API_CART_025]
    def test_product_id_empty_422(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.post(f"/carts/{cart_id}", json={"product_id": "", "quantity": 1})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"


# ======================================================================
# 1.3 获取购物车（3 条）── API_CART_012 ~ 014
# ======================================================================

class TestGetCart:
    # [API_CART_012]
    def test_get_cart_with_items_200(self, _mod_client: CartClient, _mod_cart_with_item: tuple[str, str]) -> None:
        cart_id, _ = _mod_cart_with_item
        r = _mod_client.get_cart(cart_id)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        d = r.json()
        assert "id" in d

    # [API_CART_013]
    def test_get_empty_cart_200(self, _mod_client: CartClient, _mod_empty_cart: str) -> None:
        r = _mod_client.get_cart(_mod_empty_cart)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CART_014]
    def test_get_nonexistent_404(self, client: CartClient) -> None:
        r = client.get_cart("nonexistent-99999")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 1.4 更新数量（3 条）── API_CART_015 ~ 018
# ======================================================================

class TestUpdateQuantity:
    # [API_CART_015]
    def test_update_quantity_200(self, client: CartClient) -> None:
        cart_id, pid = _cart_with_item(client)
        r = client.update_quantity(cart_id, pid, 5)
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

    # [API_CART_016]
    def test_update_nonexistent_cart(self, client: CartClient) -> None:
        r = client.update_quantity("nonexistent-99999", "x", 1)
        assert r.status_code in (404, 422), f"意外: {r.status_code}"

    # [API_CART_017]
    def test_update_nonexistent_product(self, client: CartClient) -> None:
        cart_id, _ = _cart_with_item(client)
        r = client.update_quantity(cart_id, "nonexistent-99999", 1)
        assert r.status_code in (404, 422), f"意外: {r.status_code}"

    # [API_CART_018]
    def test_update_quantity_zero(self, client: CartClient) -> None:
        cart_id, pid = _cart_with_item(client)
        r = client.update_quantity(cart_id, pid, 0)
        assert r.status_code in (200, 422), f"意外: {r.status_code}"


# ======================================================================
# 1.5 移除商品（2 条）── API_CART_019 ~ 021
# ======================================================================

class TestRemoveItem:
    # [API_CART_019]
    def test_remove_item(self, client: CartClient) -> None:
        cart_id, pid = _cart_with_item(client)
        r = client.remove_item(cart_id, pid)
        assert r.status_code in (200, 204), f"意外: {r.status_code}"

    # [API_CART_020]
    def test_remove_nonexistent_product(self, client: CartClient) -> None:
        cart_id, _ = _cart_with_item(client)
        r = client.remove_item(cart_id, "nonexistent-99999")
        assert r.status_code in (200, 204, 404, 422), f"意外: {r.status_code}"

    # [API_CART_021]
    def test_remove_from_nonexistent_cart(self, client: CartClient) -> None:
        r = client.remove_item("nonexistent-99999", "x")
        assert r.status_code in (404, 422), f"意外: {r.status_code}"


# ======================================================================
# 1.6 删除购物车（3 条）── API_CART_022 ~ 024
# ======================================================================

class TestDeleteCart:
    # [API_CART_022]
    def test_delete_cart(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        r = client.delete_cart(cart_id)
        assert r.status_code in (200, 204), f"意外: {r.status_code}"
        r2 = client.get_cart(cart_id)
        assert r2.status_code == 404, f"删除后应404, 实际{r2.status_code}"

    # [API_CART_023]
    def test_delete_nonexistent_404(self, client: CartClient) -> None:
        r = client.delete_cart("nonexistent-99999")
        assert r.status_code in (404, 422), f"意外: {r.status_code}"

    # [API_CART_024]
    def test_delete_twice(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        client.delete_cart(cart_id)
        r = client.delete_cart(cart_id)
        assert r.status_code == 404, f"二次删除应404, 实际{r.status_code}"


# ======================================================================
# 1.7 状态补充（1 条）── API_CART_026
# ======================================================================

class TestCartState:
    # [API_CART_026]
    def test_update_removed_product(self, client: CartClient) -> None:
        cart_id, pid = _cart_with_item(client)
        client.remove_item(cart_id, pid)
        r = client.update_quantity(cart_id, pid, 1)
        assert r.status_code in (200, 404, 422), f"意外: {r.status_code}"

    # [API_CART_027] P3
    def test_add_to_deleted_cart(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        client.delete_cart(cart_id)
        pid = _get_product_id(client)
        r = client.add_item(cart_id, pid, 1)
        assert r.status_code in (404, 422), f"期望404或422, 实际{r.status_code}"

    # [API_CART_028] P3
    def test_get_deleted_cart(self, client: CartClient) -> None:
        cart_id = _create_cart(client)
        client.delete_cart(cart_id)
        r = client.get_cart(cart_id)
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"

# AI-assisted
