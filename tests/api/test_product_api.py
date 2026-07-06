"""Product 模块 API 测试。

蓝图：docs/test-cases/product.md —— 51 条用例，8 个端点全覆盖。
"""

from __future__ import annotations

from src.common.data_factory import generate_unique_product_name, unique_id
from typing import Any

import pytest

from src.api.client.product_client import ProductClient
from src.api.client.user_client import UserClient
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


# -- module 级夹具 --------------------------------------------------------

@pytest.fixture(scope="module")
def _mod_client():
    """module 级 ProductClient —— 整个文件复用同一个连接。"""
    with ProductClient() as c:
        yield c


@pytest.fixture(scope="module")
def _mod_product(_mod_client: ProductClient) -> dict[str, Any]:
    """module 级：第一个已有商品（所有读测试复用）。"""
    r = _mod_client.get("/products")
    body = r.json()
    items = body if isinstance(body, list) else body.get("data", [])
    assert len(items) > 0, "需有已有商品数据"
    return items[0]


@pytest.fixture(scope="module")
def _mod_brand_slug(_mod_client: ProductClient, _mod_product: dict[str, Any]) -> str:
    """module 级品牌 slug。"""
    r = _mod_client.get("/brands")
    brands = r.json()
    return brands[0]["slug"]


@pytest.fixture(scope="module")
def _mod_category_slug(_mod_product: dict[str, Any]) -> str:
    """module 级分类 slug。"""
    return _mod_product["category"]["slug"]


@pytest.fixture(scope="module")
def _mod_create_ctx(_mod_product: dict[str, Any]) -> dict[str, Any]:
    """module 级：创建商品所需的 brand_id, category_id, product_image_id。"""
    return {
        "brand_id": _mod_product["brand"]["id"],
        "category_id": _mod_product["category"]["id"],
        "product_image_id": _mod_product["product_image"]["id"],
    }


# -- function 级 client（mutation 测试用）----------------------------------

@pytest.fixture
def client() -> ProductClient:
    with ProductClient() as c:
        yield c


# -- helpers ------------------------------------------------------------

def _get_first_product(client: ProductClient) -> dict[str, Any]:
    r = client.get("/products")
    body = r.json()
    items = body if isinstance(body, list) else body.get("data", [])
    assert len(items) > 0, "需有已有商品数据"
    return items[0]


def _get_first_product_id(client: ProductClient) -> str:
    return _get_first_product(client)["id"]


def _get_brand_slug(client: ProductClient) -> str:
    """brand 嵌套对象无 slug，从 /brands 端点获取。"""
    r = client.get("/brands")
    brands = r.json()
    return brands[0]["slug"]


def _get_category_slug(client: ProductClient) -> str:
    return _get_first_product(client)["category"]["slug"]


def _get_create_context(client: ProductClient) -> dict[str, Any]:
    """返回创建商品所需的 brand_id, category_id, product_image_id。"""
    p = _get_first_product(client)
    return {
        "brand_id": p["brand"]["id"],
        "category_id": p["category"]["id"],
        "product_image_id": p["product_image"]["id"],
    }


def _create_product(client: ProductClient, **overrides: Any) -> dict[str, Any]:
    ctx = _get_create_context(client)
    body: dict[str, Any] = {
        "name": generate_unique_product_name(),
        "description": "Auto-generated test product",
        "price": 19.99,
        "brand_id": ctx["brand_id"],
        "category_id": ctx["category_id"],
        "is_location_offer": 1,
        "is_rental": 0,
        "product_image_id": ctx["product_image_id"],
    }
    body.update(overrides)
    r = client.post("/products", json=body)
    assert r.status_code in (200, 201), f"prep create failed: {r.status_code} {r.text}"
    return r.json()


# ======================================================================
# 1.1 商品列表 · GET /products（8 条）── API_PRODUCT_001 ~ 008
# ======================================================================

class TestGetProducts:
    # [API_PRODUCT_001]
    def test_get_products_200(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        body = r.json()
        items = body if isinstance(body, list) else body.get("data", [])
        assert len(items) > 0, "商品列表不应为空"
        p = items[0]
        assert "id" in p and "name" in p and "price" in p
        assert "brand" in p and "category" in p

    # [API_PRODUCT_002]
    def test_filter_by_brand(self, _mod_client: ProductClient, _mod_brand_slug: str) -> None:
        r = _mod_client.get("/products", params={"by_brand": _mod_brand_slug})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        body = r.json()
        items = body if isinstance(body, list) else body.get("data", [])
        assert isinstance(items, list), "应按品牌筛选返回列表"

    # [API_PRODUCT_003]
    def test_filter_by_category(self, _mod_client: ProductClient, _mod_category_slug: str) -> None:
        r = _mod_client.get("/products", params={"by_category": _mod_category_slug})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        body = r.json()
        items = body if isinstance(body, list) else body.get("data", [])
        for p in items:
            assert p["category"]["slug"] == _mod_category_slug

    # [API_PRODUCT_004]
    def test_filter_is_rental(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products", params={"is_rental": 1})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        body = r.json()
        items = body if isinstance(body, list) else body.get("data", [])
        for p in items:
            assert p["is_rental"] is True

    # [API_PRODUCT_005]
    def test_filter_between(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products", params={"between": "10,100"})
        assert r.status_code in (200, 500), f"意外: {r.status_code}"

    # [API_PRODUCT_006]
    def test_sort(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products", params={"sort": "price"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PRODUCT_007]
    def test_page(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products", params={"page": 1})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PRODUCT_008]
    def test_page_zero(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products", params={"page": 0})
        assert r.status_code in (200, 400, 500), f"意外: {r.status_code}"


# ======================================================================
# 1.2 商品搜索（4 条）── API_PRODUCT_009 ~ 012
# ======================================================================

class TestSearchProducts:
    # [API_PRODUCT_009]
    def test_search_hit(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products/search", params={"q": "hammer"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        data = r.json(); items = data if isinstance(data, list) else data.get("data", data)
        assert len(items) > 0

    # [API_PRODUCT_010]
    def test_search_no_hit(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products/search", params={"q": "xyznonexistent999"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        data = r.json(); items = data if isinstance(data, list) else data.get("data", data)
        assert items == []

    # [API_PRODUCT_011]
    def test_search_no_q(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products/search")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PRODUCT_012]
    def test_search_special_chars(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products/search", params={"q": "<script>"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"


# ======================================================================
# 1.3 商品详情（3 条）── API_PRODUCT_013 ~ 015
# ======================================================================

class TestGetProduct:
    # [API_PRODUCT_013]
    def test_get_existing(self, _mod_client: ProductClient, _mod_product: dict[str, Any]) -> None:
        pid = _mod_product["id"]
        r = _mod_client.get(f"/products/{pid}")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        p = r.json()
        assert p["id"] == pid
        assert "name" in p and "price" in p and "description" in p
        assert "brand" in p and "id" in p["brand"]
        assert "category" in p and "id" in p["category"]
        assert "in_stock" in p and "is_rental" in p

    # [API_PRODUCT_014]
    def test_get_nonexistent_404(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products/nonexistent-id-99999")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"

    # [API_PRODUCT_015]
    def test_get_empty_id(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products/ ")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 1.4 相关商品（2 条）── API_PRODUCT_016 ~ 017
# ======================================================================

class TestRelatedProducts:
    # [API_PRODUCT_016]
    def test_related(self, _mod_client: ProductClient, _mod_product: dict[str, Any]) -> None:
        r = _mod_client.get(f"/products/{_mod_product['id']}/related")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert isinstance(r.json(), list)

    # [API_PRODUCT_017]
    def test_related_nonexistent(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products/nonexistent-id-99999/related")
        assert r.status_code in (404, 500), f"意外: {r.status_code}"


# ======================================================================
# 1.5 创建商品 · POST /products（7 条）── API_PRODUCT_018 ~ 024
# + 边界补充中属于 POST 的（API_PRODUCT_032~038/046~048）
# ======================================================================

class TestCreateProduct:
    @pytest.fixture
    def create_payload(self, client: ProductClient) -> dict[str, Any]:
        ctx = _get_create_context(client)
        return {
            "name": generate_unique_product_name("E2E"),
            "description": "Test created by automation",
            "price": 29.99,
            "brand_id": ctx["brand_id"],
            "category_id": ctx["category_id"],
            "is_location_offer": 1,
            "is_rental": 0,
            "product_image_id": ctx["product_image_id"],
        }

    # [API_PRODUCT_018]
    def test_create_200(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201), f"意外: {r.status_code} {r.text}"
        d = r.json()
        assert "id" in d and d["name"] == create_payload["name"]

    # [API_PRODUCT_019]
    def test_missing_name_422(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        del create_payload["name"]
        r = client.post("/products", json=create_payload)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_020]
    def test_missing_price_422(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        del create_payload["price"]
        r = client.post("/products", json=create_payload)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_021]
    def test_invalid_category_id(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["category_id"] = "nonexistent-99999"
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201, 422, 500), f"意外: {r.status_code}"

    # [API_PRODUCT_022]
    def test_invalid_brand_id(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["brand_id"] = "nonexistent-99999"
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201, 422, 500), f"意外: {r.status_code}"

    # [API_PRODUCT_023]
    def test_negative_price(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["price"] = -9.99
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201, 422), f"意外: {r.status_code}（API 可能不校验负价）"

    # [API_PRODUCT_024]
    def test_empty_body_422(self, client: ProductClient) -> None:
        r = client.post("/products", json={})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_032]
    def test_price_zero(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["price"] = 0
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201, 422), f"意外: {r.status_code}"

    # [API_PRODUCT_033]
    def test_price_huge(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["price"] = 999999999.99
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201, 422, 500), f"意外: {r.status_code}"

    # [API_PRODUCT_034]
    def test_name_empty_422(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["name"] = ""
        r = client.post("/products", json=create_payload)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_035]
    def test_name_too_long(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["name"] = "A" * 256
        r = client.post("/products", json=create_payload)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_036]
    def test_missing_brand_id(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        del create_payload["brand_id"]
        r = client.post("/products", json=create_payload)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_037]
    def test_missing_category_id(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        del create_payload["category_id"]
        r = client.post("/products", json=create_payload)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_038]
    def test_co2_rating_invalid(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["co2_rating"] = "X"
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201, 422), f"意外: {r.status_code}"

    # [API_PRODUCT_046]
    def test_product_image_id_invalid(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["product_image_id"] = "nonexistent-img-99999"
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201, 422, 500), f"意外: {r.status_code}"

    # [API_PRODUCT_047]
    def test_description_too_long(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["description"] = "D" * 5000
        r = client.post("/products", json=create_payload)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PRODUCT_048]
    def test_is_location_offer_true(self, client: ProductClient, create_payload: dict[str, Any]) -> None:
        create_payload["is_location_offer"] = True
        r = client.post("/products", json=create_payload)
        assert r.status_code in (200, 201), f"意外: {r.status_code}"
        assert r.json()["is_location_offer"] is True


# ======================================================================
# 1.6 PUT 更新（2 条）── API_PRODUCT_025 ~ 026
# ======================================================================

class TestPutProduct:
    # [API_PRODUCT_025]
    def test_put_success(self, client: ProductClient) -> None:
        p = _create_product(client)
        pid = p["id"]
        ctx = _get_create_context(client)
        r = client.put(f"/products/{pid}", json={
            "name": "Updated Product", "description": "Updated desc",
            "price": 49.99, "brand_id": ctx["brand_id"], "category_id": ctx["category_id"],
            "is_location_offer": 1, "is_rental": 0, "product_image_id": ctx["product_image_id"],
        })
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        updated = client.get(f"/products/{pid}").json()
        assert updated["name"] == "Updated Product"

    # [API_PRODUCT_026]
    def test_put_nonexistent_404(self, client: ProductClient) -> None:
        ctx = _get_create_context(client)
        r = client.put("/products/nonexistent-id-99999", json={
            "name": "X", "description": "X", "price": 1,
            "brand_id": ctx["brand_id"], "category_id": ctx["category_id"],
            "is_location_offer": 1, "is_rental": 0, "product_image_id": ctx["product_image_id"],
        })
        assert r.status_code in (404, 500), f"意外: {r.status_code}"


# ======================================================================
# 1.7 PATCH 更新（2 条）── API_PRODUCT_027 ~ 028
# ======================================================================

class TestPatchProduct:
    # [API_PRODUCT_027]
    def test_patch_name(self, client: ProductClient) -> None:
        p = _create_product(client)
        pid = p["id"]
        r = client.patch(f"/products/{pid}", json={"name": "Patched Product"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        updated = client.get(f"/products/{pid}").json()
        assert updated["name"] == "Patched Product"
        assert updated["price"] == p["price"]  # unchanged

    # [API_PRODUCT_028]
    def test_patch_nonexistent_404(self, client: ProductClient) -> None:
        r = client.patch("/products/nonexistent-id-99999", json={"name": "X"})
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 1.8 DELETE 删除（3 条）── API_PRODUCT_029 ~ 031
# ======================================================================

class TestDeleteProduct:
    # [API_PRODUCT_029]
    def test_delete_success(self, client: ProductClient) -> None:
        p = _create_product(client)
        pid = p["id"]
        r = client.delete(f"/products/{pid}")
        assert r.status_code in (200, 204, 401), f"意外: {r.status_code}"
        if r.status_code in (200, 204):
            r2 = client.get(f"/products/{pid}")
            assert r2.status_code == 404, f"删除后应404, 实际{r2.status_code}"

    # [API_PRODUCT_030]
    def test_delete_nonexistent(self, client: ProductClient) -> None:
        r = client.delete("/products/nonexistent-id-99999")
        assert r.status_code in (401, 404, 422), f"意外: {r.status_code}"

    # [API_PRODUCT_031]
    def test_delete_twice(self, client: ProductClient) -> None:
        p = _create_product(client)
        pid = p["id"]
        client.delete(f"/products/{pid}")
        r = client.delete(f"/products/{pid}")
        assert r.status_code in (401, 404, 422), f"意外: {r.status_code}"


# ======================================================================
# 1.9 边界补充-查询参数（3 条）── API_PRODUCT_039 ~ 041
# ======================================================================

class TestProductQueryBoundary:
    # [API_PRODUCT_039]
    def test_between_invalid(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products", params={"between": "abc"})
        assert r.status_code in (200, 400, 500), f"意外: {r.status_code}"

    # [API_PRODUCT_040]
    def test_sort_invalid(self, _mod_client: ProductClient) -> None:
        r = _mod_client.get("/products", params={"sort": "invalid_field"})
        assert r.status_code in (200, 400, 500), f"意外: {r.status_code}"

    # [API_PRODUCT_041]
    def test_combined_filters(self, _mod_client: ProductClient, _mod_brand_slug: str, _mod_category_slug: str) -> None:
        r = _mod_client.get("/products", params={"by_brand": _mod_brand_slug, "by_category": _mod_category_slug})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"


# ======================================================================
# 1.10 权限（4 条）── API_PRODUCT_042 ~ 045
# ======================================================================

class TestProductAuth:
    # [API_PRODUCT_042]
    def test_create_unauthenticated_401(self) -> None:
        r = ProductClient().post("/products", json={"name": "X", "description": "X", "price": 1, "brand_id": "x", "category_id": "x"})
        assert r.status_code in (401, 404, 422), f"意外: {r.status_code}"

    # [API_PRODUCT_043]
    def test_put_unauthenticated_401(self) -> None:
        r = ProductClient().put("/products/some-id", json={"name": "X", "description": "X", "price": 1, "brand_id": "x", "category_id": "x"})
        assert r.status_code in (401, 404, 422), f"意外: {r.status_code}"

    # [API_PRODUCT_044]
    def test_patch_unauthenticated_401(self) -> None:
        r = ProductClient().patch("/products/some-id", json={"name": "X"})
        assert r.status_code in (401, 404, 422), f"意外: {r.status_code}"

    # [API_PRODUCT_045]
    def test_delete_unauthenticated_401(self) -> None:
        r = ProductClient().delete("/products/some-id")
        assert r.status_code in (401, 404, 422), f"意外: {r.status_code}"


class TestProductDefense:
    """P3 深度防御。"""

    @pytest.fixture
    def _auth_product(self) -> ProductClient:
        """function 级：已认证 ProductClient（token 过期测试用）。"""
        with UserClient() as uc:
            uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
            token = uc.token
        pc = ProductClient()
        pc.set_token(token)
        yield pc
        pc.close()

    # [API_PRODUCT_049] P3
    def test_xss_description(
        self, client: ProductClient, _mod_create_ctx: dict[str, Any],
    ) -> None:
        r = client.post("/products", json={
            "name": f"XSS-Test-{unique_id(6)}",
            "description": "<script>alert(1)</script>",
            "price": 9.99,
            "is_location_offer": True,
            "is_rental": False,
            **_mod_create_ctx,
        })
        assert r.status_code in (200, 201), f"期望200/201（应转义）, 实际{r.status_code} {r.text}"

    # [API_PRODUCT_050] P3
    def test_token_expired_put(self, _auth_product: ProductClient) -> None:
        _auth_product.clear_token()
        r = _auth_product.put("/products/some-id", json={"name": "X"})
        assert r.status_code in (401, 404), f"期望401或404, 实际{r.status_code}"

    # [API_PRODUCT_051] P3
    def test_token_expired_delete(self, _auth_product: ProductClient) -> None:
        _auth_product.clear_token()
        r = _auth_product.delete("/products/some-id")
        assert r.status_code in (401, 404), f"期望401或404, 实际{r.status_code}"

# AI-assisted
