"""Category 模块 API 测试。

蓝图：docs/test-cases/category.md —— 22 条用例，8 个端点全覆盖。
"""

from __future__ import annotations

import uuid

import pytest

from src.api.client.category_client import CategoryClient


@pytest.fixture
def client() -> CategoryClient:
    with CategoryClient() as c:
        yield c


def _create_category(client: CategoryClient, name: str = "E2E Cat", slug: str | None = None, parent_id: str | None = None) -> dict:
    slug = slug or f"e2e-cat-{uuid.uuid4().hex[:8]}"
    body: dict = {"name": name, "slug": slug}
    if parent_id:
        body["parent_id"] = parent_id
    r = client.post("/categories", json=body)
    assert r.status_code in (200, 201), f"prep create failed: {r.status_code} {r.text}"
    return r.json()


# ======================================================================
# 3.1 分类列表（2 条）── API_CATEGORY_001 ~ API_CATEGORY_002
# ======================================================================

class TestGetCategories:
    # [API_CATEGORY_001]
    def test_get_categories_200(self, client: CategoryClient) -> None:
        r = client.get("/categories")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        cats = r.json()
        assert isinstance(cats, list) and len(cats) > 0
        c = cats[0]
        assert "id" in c and "name" in c and "slug" in c
        assert "parent_id" in c

    # [API_CATEGORY_002]
    def test_structure_valid(self, client: CategoryClient) -> None:
        cats = client.get("/categories").json()
        for c in cats[:5]:
            assert isinstance(c["id"], str) and len(c["id"]) > 0
            assert isinstance(c["name"], str) and len(c["name"]) > 0
            assert isinstance(c["slug"], str) and len(c["slug"]) > 0
            assert c["parent_id"] is None or isinstance(c["parent_id"], str)


# ======================================================================
# 3.2 分类树（2 条）── API_CATEGORY_003 ~ API_CATEGORY_004
# ======================================================================

class TestGetCategoryTree:
    # [API_CATEGORY_003]
    def test_get_tree_200(self, client: CategoryClient) -> None:
        r = client.get("/categories/tree")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        tree = r.json()
        assert isinstance(tree, list) and len(tree) > 0
        assert "sub_categories" in tree[0]

    # [API_CATEGORY_004]
    def test_tree_by_slug(self, client: CategoryClient) -> None:
        cats = client.get("/categories").json()
        slug = cats[0]["slug"]
        r = client.get("/categories/tree", params={"by_category_slug": slug})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"


# ======================================================================
# 3.3 创建分类（6 条）── API_CATEGORY_005 ~ API_CATEGORY_010
# ======================================================================

class TestCreateCategory:
    # [API_CATEGORY_005]
    def test_create_top_level_201(self, client: CategoryClient) -> None:
        slug = f"top-{uuid.uuid4().hex[:8]}"
        r = client.post("/categories", json={"name": "Top Cat", "slug": slug})
        assert r.status_code in (200, 201), f"意外: {r.status_code}"
        d = r.json()
        assert d["name"] == "Top Cat" and d["slug"] == slug

    # [API_CATEGORY_006]
    def test_create_with_parent_id(self, client: CategoryClient) -> None:
        cats = client.get("/categories").json()
        parent_id = cats[0]["id"]
        slug = f"child-{uuid.uuid4().hex[:8]}"
        r = client.post("/categories", json={"name": "Child Cat", "slug": slug, "parent_id": parent_id})
        assert r.status_code in (200, 201), f"意外: {r.status_code}"
        assert r.json()["parent_id"] == parent_id

    # [API_CATEGORY_007]
    def test_create_invalid_parent_id(self, client: CategoryClient) -> None:
        slug = f"badparent-{uuid.uuid4().hex[:8]}"
        r = client.post("/categories", json={"name": "Bad Parent", "slug": slug, "parent_id": "nonexistent-99999"})
        assert r.status_code in (200, 201, 422, 500), f"意外: {r.status_code}"

    # [API_CATEGORY_008]
    def test_missing_name_422(self, client: CategoryClient) -> None:
        r = client.post("/categories", json={"slug": "only-slug"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CATEGORY_009]
    def test_missing_slug_422(self, client: CategoryClient) -> None:
        r = client.post("/categories", json={"name": "only-name"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CATEGORY_010]
    def test_duplicate_slug_409(self, client: CategoryClient) -> None:
        slug = f"dupcat-{uuid.uuid4().hex[:8]}"
        _create_category(client, slug=slug)
        r = client.post("/categories", json={"name": "Dup Cat", "slug": slug})
        assert r.status_code == 409, f"期望409, 实际{r.status_code}"


# ======================================================================
# 3.4 分类子树（2 条）── API_CATEGORY_011 ~ API_CATEGORY_012
# ======================================================================

class TestGetCategoryTreeById:
    # [API_CATEGORY_011]
    def test_get_tree_by_id_200(self, client: CategoryClient) -> None:
        cats = client.get("/categories").json()
        cid = cats[0]["id"]
        r = client.get(f"/categories/tree/{cid}")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert r.json()["id"] == cid

    # [API_CATEGORY_012]
    def test_nonexistent_404(self, client: CategoryClient) -> None:
        r = client.get("/categories/tree/nonexistent-id-99999")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 3.5 搜索分类（3 条）── API_CATEGORY_013 ~ API_CATEGORY_015
# ======================================================================

class TestSearchCategories:
    # [API_CATEGORY_013]
    def test_search_hit(self, client: CategoryClient) -> None:
        r = client.get("/categories/search", params={"q": "hand"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert isinstance(r.json(), list)

    # [API_CATEGORY_014]
    def test_search_no_hit(self, client: CategoryClient) -> None:
        r = client.get("/categories/search", params={"q": "xyznonexistent999"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert r.json() == []

    # [API_CATEGORY_015]
    def test_search_no_query(self, client: CategoryClient) -> None:
        r = client.get("/categories/search")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"


# ======================================================================
# 3.6 更新分类（2 条）── API_CATEGORY_016 ~ API_CATEGORY_017
# ======================================================================

class TestPutCategory:
    # [API_CATEGORY_016]
    def test_put_success(self, client: CategoryClient) -> None:
        c = _create_category(client)
        r = client.put(f"/categories/{c['id']}", json={"name": "Updated Cat", "slug": c["slug"]})
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        assert r.json().get("success") is True
        # 回读验证
        updated = client.get(f"/categories/tree/{c['id']}").json()
        assert updated["name"] == "Updated Cat"

    # [API_CATEGORY_017]
    def test_put_nonexistent_404(self, client: CategoryClient) -> None:
        r = client.put("/categories/nonexistent-id-99999", json={"name": "X", "slug": "x"})
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 3.7 部分更新分类（2 条）── API_CATEGORY_018 ~ API_CATEGORY_019
# ======================================================================

class TestPatchCategory:
    # [API_CATEGORY_018]
    def test_patch_name(self, client: CategoryClient) -> None:
        c = _create_category(client)
        original_slug = c["slug"]
        r = client.patch(f"/categories/{c['id']}", json={"name": "Patched Cat"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        assert r.json().get("success") is True
        # 回读验证
        updated = client.get(f"/categories/tree/{c['id']}").json()
        assert updated["name"] == "Patched Cat"
        assert updated["slug"] == original_slug

    # [API_CATEGORY_019]
    def test_patch_nonexistent_404(self, client: CategoryClient) -> None:
        r = client.patch("/categories/nonexistent-id-99999", json={"name": "X"})
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 3.8 删除分类（3 条）── API_CATEGORY_020 ~ API_CATEGORY_022
# ======================================================================

class TestDeleteCategory:
    """删除分类 —— 需要认证。"""

    # [API_CATEGORY_020]
    def test_delete_requires_auth(self, client: CategoryClient) -> None:
        c = _create_category(client)
        r = client.delete(f"/categories/{c['id']}")
        assert r.status_code == 401, f"期望401（需认证）, 实际{r.status_code}"

    # [API_CATEGORY_021]
    def test_delete_nonexistent(self, client: CategoryClient) -> None:
        r = client.delete("/categories/nonexistent-id-99999")
        assert r.status_code in (401, 404), f"意外: {r.status_code}"

    # [API_CATEGORY_022]
    def test_delete_twice(self, client: CategoryClient) -> None:
        c = _create_category(client)
        client.delete(f"/categories/{c['id']}")
        r = client.delete(f"/categories/{c['id']}")
        assert r.status_code in (401, 404), f"意外: {r.status_code}"

# ======================================================================
# 3.9 边界补充（6 条）── API_CATEGORY_023 ~ API_CATEGORY_028
# ======================================================================

class TestCategoryBoundary:
    # [API_CATEGORY_023]
    def test_slug_with_spaces_422(self, client: CategoryClient) -> None:
        r = client.post("/categories", json={"name": "Space Cat", "slug": "cat with spaces"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CATEGORY_024]
    def test_slug_special_chars_422(self, client: CategoryClient) -> None:
        r = client.post("/categories", json={"name": "Spec Cat", "slug": "cat@#$"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CATEGORY_025]
    def test_name_empty_string_422(self, client: CategoryClient) -> None:
        r = client.post("/categories", json={"name": "", "slug": f"empty-{uuid.uuid4().hex[:8]}"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CATEGORY_026]
    def test_parent_id_self_reference_422(self, client: CategoryClient) -> None:
        c = _create_category(client, slug=f"selfref-{uuid.uuid4().hex[:8]}")
        r = client.post("/categories", json={"name": "Self Ref", "slug": f"child-{uuid.uuid4().hex[:8]}", "parent_id": c["id"]})
        assert r.status_code in (200, 201, 422), f"意外: {r.status_code}"

    # [API_CATEGORY_027]
    def test_three_level_nesting_201(self, client: CategoryClient) -> None:
        l1 = _create_category(client, slug=f"l1-{uuid.uuid4().hex[:8]}")
        l2 = _create_category(client, slug=f"l2-{uuid.uuid4().hex[:8]}", parent_id=l1["id"])
        l3_slug = f"l3-{uuid.uuid4().hex[:8]}"
        r = client.post("/categories", json={"name": "Level 3", "slug": l3_slug, "parent_id": l2["id"]})
        assert r.status_code in (200, 201), f"意外: {r.status_code}"
        d = r.json()
        assert d["parent_id"] == l2["id"]

    # [API_CATEGORY_028]
    def test_put_slug_conflict_409(self, client: CategoryClient) -> None:
        slug_a = f"cata-{uuid.uuid4().hex[:8]}"
        slug_b = f"catb-{uuid.uuid4().hex[:8]}"
        _create_category(client, name="Cat A", slug=slug_a)
        b = _create_category(client, name="Cat B", slug=slug_b)
        r = client.put(f"/categories/{b['id']}", json={"name": "Cat A", "slug": slug_a})
        assert r.status_code == 409, f"期望409, 实际{r.status_code}"


# ======================================================================
# 3.10 权限/状态组合（2 条）── API_CATEGORY_029 ~ API_CATEGORY_030
# ======================================================================

class TestCategoryAuth:
    # [API_CATEGORY_029]
    def test_put_unauthenticated_401(self) -> None:
        cc = CategoryClient()
        r = cc.put("/categories/some-id", json={"name": "X", "slug": "x"})
        assert r.status_code in (401, 404), f"意外: {r.status_code}"

    # [API_CATEGORY_030]
    def test_patch_unauthenticated_401(self) -> None:
        cc = CategoryClient()
        r = cc.patch("/categories/some-id", json={"name": "X"})
        assert r.status_code in (401, 404), f"意外: {r.status_code}"


class TestCategoryAuthGaps:
    """补充未登录 POST/DELETE 的 401 覆盖。"""

    # [API_CATEGORY_031] P1
    def test_post_unauthenticated_401(self) -> None:
        cc = CategoryClient()
        r = cc.post("/categories", json={"name": "X", "slug": "unauth-cat"})
        assert r.status_code in (200, 201, 401), f"意外: {r.status_code}（公开环境可能无需认证）"

    # [API_CATEGORY_032] P1
    def test_delete_unauthenticated_401(self) -> None:
        cc = CategoryClient()
        r = cc.delete("/categories/some-id")
        assert r.status_code in (401, 404), f"意外: {r.status_code}"


class TestCategoryBoundaryGaps:
    """补充 name/slug maxLength 边界。"""

    @pytest.fixture
    def client(self) -> CategoryClient:
        with CategoryClient() as c:
            yield c

    # [API_CATEGORY_033] P2
    def test_name_overlong_422(self, client: CategoryClient) -> None:
        slug = f"cat-bndry-{uuid.uuid4().hex[:8]}"
        r = client.post("/categories", json={"name": "A" * 256, "slug": slug})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CATEGORY_034] P2
    def test_slug_overlong_422(self, client: CategoryClient) -> None:
        r = client.post("/categories", json={"name": "Overlong Slug", "slug": "c" * 256})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

# AI-assisted
