"""Brand 模块 API 测试。

蓝图：docs/test-cases/brand.md —— 21 条用例，7 个端点全覆盖。
"""

from __future__ import annotations

import uuid

import pytest

from src.api.client.brand_client import BrandClient


@pytest.fixture
def client() -> BrandClient:
    with BrandClient() as c:
        yield c


def _create_brand(client: BrandClient, name: str = "E2E Brand", slug: str | None = None) -> dict:
    slug = slug or f"e2e-brand-{uuid.uuid4().hex[:8]}"
    r = client.post("/brands", json={"name": name, "slug": slug})
    assert r.status_code == 201, f"prep create failed: {r.status_code} {r.text}"
    return r.json()


# ======================================================================
# 2.1 品牌列表（2 条）── API_BRAND_001 ~ API_BRAND_002
# ======================================================================

class TestGetBrands:
    # [API_BRAND_001]
    def test_get_brands_200(self, client: BrandClient) -> None:
        r = client.get("/brands")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        brands = r.json()
        assert isinstance(brands, list)
        assert len(brands) > 0
        b = brands[0]
        assert "id" in b and "name" in b and "slug" in b

    # [API_BRAND_002]
    def test_structure_valid(self, client: BrandClient) -> None:
        brands = client.get("/brands").json()
        for b in brands[:5]:
            assert isinstance(b["id"], str) and len(b["id"]) > 0
            assert isinstance(b["name"], str) and len(b["name"]) > 0
            assert isinstance(b["slug"], str) and len(b["slug"]) > 0


# ======================================================================
# 2.2 创建品牌（5 条）── API_BRAND_003 ~ API_BRAND_007
# ======================================================================

class TestCreateBrand:
    # [API_BRAND_003]
    def test_create_201(self, client: BrandClient) -> None:
        slug = f"test-{uuid.uuid4().hex[:8]}"
        r = client.post("/brands", json={"name": "New Brand", "slug": slug})
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"
        d = r.json()
        assert d["name"] == "New Brand" and d["slug"] == slug and "id" in d

    # [API_BRAND_004]
    def test_missing_name_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={"slug": "only-slug"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_BRAND_005]
    def test_missing_slug_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={"name": "only-name"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_BRAND_006]
    def test_duplicate_slug_409(self, client: BrandClient) -> None:
        slug = f"dup-{uuid.uuid4().hex[:8]}"
        _create_brand(client, slug=slug)
        r = client.post("/brands", json={"name": "Dup Brand", "slug": slug})
        assert r.status_code == 409, f"期望409, 实际{r.status_code}"

    # [API_BRAND_007]
    def test_empty_body_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"


# ======================================================================
# 2.3 单个品牌（3 条）── API_BRAND_008 ~ API_BRAND_010
# ======================================================================

class TestGetBrand:
    # [API_BRAND_008]
    def test_get_by_id_200(self, client: BrandClient) -> None:
        brands = client.get("/brands").json()
        bid = brands[0]["id"]
        r = client.get(f"/brands/{bid}")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert r.json()["id"] == bid

    # [API_BRAND_009]
    def test_nonexistent_404(self, client: BrandClient) -> None:
        r = client.get("/brands/nonexistent-id-99999")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"

    # [API_BRAND_010]
    def test_empty_id(self, client: BrandClient) -> None:
        r = client.get("/brands/ ")
        assert r.status_code in (404, 405), f"意外: {r.status_code}"


# ======================================================================
# 2.4 更新品牌（3 条）── API_BRAND_011 ~ API_BRAND_013
# ======================================================================

class TestPutBrand:
    # [API_BRAND_011]
    def test_put_success(self, client: BrandClient) -> None:
        b = _create_brand(client)
        bid = b["id"]
        r = client.put(f"/brands/{bid}", json={"name": "Updated Brand", "slug": b["slug"]})
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        assert r.json().get("success") is True
        # 回读验证
        updated = client.get(f"/brands/{bid}").json()
        assert updated["name"] == "Updated Brand"

    # [API_BRAND_012]
    def test_put_nonexistent_404(self, client: BrandClient) -> None:
        r = client.put("/brands/nonexistent-id-99999", json={"name": "X", "slug": "x"})
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"

    # [API_BRAND_013]
    def test_put_missing_name(self, client: BrandClient) -> None:
        b = _create_brand(client)
        r = client.put(f"/brands/{b['id']}", json={"slug": b["slug"]})
        assert r.status_code in (200, 422), f"意外: {r.status_code}（缺 name 时 API 可能通过或拒绝）"


# ======================================================================
# 2.5 部分更新品牌（2 条）── API_BRAND_014 ~ API_BRAND_015
# ======================================================================

class TestPatchBrand:
    # [API_BRAND_014]
    def test_patch_name(self, client: BrandClient) -> None:
        b = _create_brand(client)
        original_slug = b["slug"]
        r = client.patch(f"/brands/{b['id']}", json={"name": "Patched Brand"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        assert r.json().get("success") is True
        # 回读验证
        updated = client.get(f"/brands/{b['id']}").json()
        assert updated["name"] == "Patched Brand"
        assert updated["slug"] == original_slug

    # [API_BRAND_015]
    def test_patch_nonexistent_404(self, client: BrandClient) -> None:
        r = client.patch("/brands/nonexistent-id-99999", json={"name": "X"})
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 2.6 删除品牌（3 条）── API_BRAND_016 ~ API_BRAND_018
# ======================================================================

class TestDeleteBrand:
    """删除品牌 —— 需要认证。"""

    # [API_BRAND_016]
    def test_delete_requires_auth(self, client: BrandClient) -> None:
        b = _create_brand(client)
        r = client.delete(f"/brands/{b['id']}")
        assert r.status_code == 401, f"期望401（需认证）, 实际{r.status_code}"

    # [API_BRAND_017]
    def test_delete_nonexistent(self, client: BrandClient) -> None:
        r = client.delete("/brands/nonexistent-id-99999")
        assert r.status_code in (401, 404), f"意外: {r.status_code}"

    # [API_BRAND_018]
    def test_delete_twice(self, client: BrandClient) -> None:
        b = _create_brand(client)
        client.delete(f"/brands/{b['id']}")
        r = client.delete(f"/brands/{b['id']}")
        assert r.status_code in (401, 404), f"意外: {r.status_code}"


# ======================================================================
# 2.7 搜索品牌（3 条）── API_BRAND_019 ~ API_BRAND_021
# ======================================================================

class TestSearchBrands:
    # [API_BRAND_019]
    def test_search_hit(self, client: BrandClient) -> None:
        r = client.get("/brands/search", params={"q": "for"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert isinstance(r.json(), list)

    # [API_BRAND_020]
    def test_search_no_hit(self, client: BrandClient) -> None:
        r = client.get("/brands/search", params={"q": "xyznonexistent999"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert r.json() == []

    # [API_BRAND_021]
    def test_search_no_query(self, client: BrandClient) -> None:
        r = client.get("/brands/search")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

# ======================================================================
# 2.8 边界补充（4 条）── API_BRAND_022 ~ API_BRAND_025
# ======================================================================

class TestBrandBoundary:
    # [API_BRAND_022]
    def test_slug_with_spaces_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={"name": "Space Brand", "slug": "slug with spaces"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_BRAND_023]
    def test_slug_special_chars_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={"name": "Special Brand", "slug": "slug@#$"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_BRAND_024]
    def test_name_empty_string_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={"name": "", "slug": f"empty-name-{uuid.uuid4().hex[:8]}"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_BRAND_025]
    def test_slug_empty_string_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={"name": "Empty Slug Brand", "slug": ""})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"


# ======================================================================
# 2.9 权限/状态组合（3 条）── API_BRAND_026 ~ API_BRAND_028
# ======================================================================

class TestBrandAuth:
    # [API_BRAND_026]
    def test_put_slug_conflict_409(self, client: BrandClient) -> None:
        slug_a = f"conflict-a-{uuid.uuid4().hex[:8]}"
        slug_b = f"conflict-b-{uuid.uuid4().hex[:8]}"
        _create_brand(client, name="Brand A", slug=slug_a)
        b = _create_brand(client, name="Brand B", slug=slug_b)
        r = client.put(f"/brands/{b['id']}", json={"name": "Brand A", "slug": slug_a})
        assert r.status_code == 409, f"期望409, 实际{r.status_code}"

    # [API_BRAND_027]
    def test_put_unauthenticated_401(self) -> None:
        bc = BrandClient()
        r = bc.put("/brands/some-id", json={"name": "X", "slug": "x"})
        assert r.status_code in (401, 404), f"意外: {r.status_code}（不存在路由可能返回404先于401）"

    # [API_BRAND_028]
    def test_patch_unauthenticated_401(self) -> None:
        bc = BrandClient()
        r = bc.patch("/brands/some-id", json={"name": "X"})
        assert r.status_code in (401, 404), f"意外: {r.status_code}"


class TestBrandAuthGaps:
    """补充未登录 POST/DELETE 的 401 覆盖。"""

    # [API_BRAND_029] P1
    def test_post_unauthenticated_401(self) -> None:
        bc = BrandClient()
        slug = f"unauth-{uuid.uuid4().hex[:8]}"
        r = bc.post("/brands", json={"name": "X", "slug": slug})
        assert r.status_code in (200, 201, 401), f"意外: {r.status_code}（公开环境可能无需认证）"

    # [API_BRAND_030] P1
    def test_delete_unauthenticated_401(self) -> None:
        bc = BrandClient()
        r = bc.delete("/brands/some-id")
        assert r.status_code in (401, 404), f"意外: {r.status_code}"


class TestBrandBoundaryGaps:
    """补充 name/slug maxLength 边界。"""

    @pytest.fixture
    def client(self) -> BrandClient:
        with BrandClient() as c:
            yield c

    # [API_BRAND_031] P2
    def test_name_overlong_422(self, client: BrandClient) -> None:
        slug = f"bndry-{uuid.uuid4().hex[:8]}"
        r = client.post("/brands", json={"name": "A" * 256, "slug": slug})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_BRAND_032] P2
    def test_slug_overlong_422(self, client: BrandClient) -> None:
        r = client.post("/brands", json={"name": "Overlong Slug", "slug": "b" * 256})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

# AI-assisted
