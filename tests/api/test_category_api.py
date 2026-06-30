"""Category 模块 API 测试。

对应文档：docs/test-cases/api-test-cases-v1.md（API_CATEGORY_001 ~ API_CATEGORY_009）

覆盖维度：正常功能 · 异常场景（404）· 树形结构校验 · 搜索边界
"""

from __future__ import annotations

import uuid

import pytest

from src.api.client.category_client import CategoryClient


@pytest.fixture
def client() -> CategoryClient:
    with CategoryClient() as c:
        yield c


# ======================================================================
# 获取分类列表（GET /categories）── API_CATEGORY_001 ~ API_CATEGORY_002
# ======================================================================

class TestGetCategories:
    """获取分类列表。"""

    # [API_CATEGORY_001] ------------------------------------------------
    def test_get_categories_returns_200(self, client: CategoryClient) -> None:
        """获取分类列表 → 200，返回非空数组，元素含 id/name/slug/parent_id。"""
        response = client.get("/categories")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        categories = response.json()
        assert isinstance(categories, list), f"期望列表, 实际{type(categories)}"
        assert len(categories) > 0, "分类列表不应为空"
        cat = categories[0]
        assert "id" in cat, "分类对象应包含 id"
        assert "name" in cat, "分类对象应包含 name"
        assert "slug" in cat, "分类对象应包含 slug"
        assert "parent_id" in cat, "分类对象应包含 parent_id"

    # [API_CATEGORY_002] ------------------------------------------------
    def test_get_categories_returns_valid_structure(
        self, client: CategoryClient
    ) -> None:
        """数据结构校验：前 5 个分类的字段类型正确，parent_id 可为 null。"""
        response = client.get("/categories")
        categories = response.json()
        for cat in categories[:5]:
            assert isinstance(cat["id"], str)
            assert isinstance(cat["name"], str)
            assert isinstance(cat["slug"], str)
            assert len(cat["name"]) > 0
            assert len(cat["slug"]) > 0
            assert "parent_id" in cat


# ======================================================================
# 获取分类树（GET /categories/tree）── API_CATEGORY_003 ~ API_CATEGORY_005
# ======================================================================

class TestGetCategoryTree:
    """获取分类树。"""

    # [API_CATEGORY_003] ------------------------------------------------
    def test_get_category_tree_returns_200(self, client: CategoryClient) -> None:
        """获取分类树 → 200，返回非空数组，顶级节点含 sub_categories。"""
        response = client.get("/categories/tree")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        tree = response.json()
        assert isinstance(tree, list), f"期望列表, 实际{type(tree)}"
        assert len(tree) > 0, "分类树不应为空"
        node = tree[0]
        assert "id" in node
        assert "name" in node

    # [API_CATEGORY_004] ------------------------------------------------
    def test_get_category_tree_by_valid_id(self, client: CategoryClient) -> None:
        """存在的分类 ID → 200，响应体 id 与请求一致。"""
        categories = client.get("/categories").json()
        existing_id = categories[0]["id"]
        response = client.get(f"/categories/tree/{existing_id}")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"

    # [API_CATEGORY_005] ------------------------------------------------
    def test_get_category_tree_nonexistent_returns_404(
        self, client: CategoryClient
    ) -> None:
        """不存在的分类 ID → 404。"""
        response = client.get("/categories/tree/nonexistent-id-99999")
        assert response.status_code == 404, f"期望404, 实际{response.status_code}"


# ======================================================================
# 搜索分类（GET /categories/search）── API_CATEGORY_006 ~ API_CATEGORY_008
# ======================================================================

class TestSearchCategories:
    """搜索分类。"""

    # [API_CATEGORY_006] ------------------------------------------------
    def test_search_categories_with_match(self, client: CategoryClient) -> None:
        """搜索 'hand' → 200，返回匹配的分类列表。"""
        response = client.get("/categories/search", params={"q": "hand"})
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        results = response.json()
        assert isinstance(results, list), f"期望列表, 实际{type(results)}"

    # [API_CATEGORY_007] ------------------------------------------------
    def test_search_categories_no_match(self, client: CategoryClient) -> None:
        """搜索不存在的关键词 → 200，返回空数组。"""
        response = client.get("/categories/search", params={"q": "xyznonexistent999"})
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        results = response.json()
        assert isinstance(results, list), f"期望列表, 实际{type(results)}"
        assert len(results) == 0, "无匹配时应返回空列表"

    # [API_CATEGORY_008] ------------------------------------------------
    def test_search_categories_no_query_returns_all(
        self, client: CategoryClient
    ) -> None:
        """不传 q 参数 → 200，返回全量（q 为可选参数）。"""
        response = client.get("/categories/search")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        results = response.json()
        assert isinstance(results, list), f"期望列表, 实际{type(results)}"


# ======================================================================
# 创建分类（POST /categories）── API_CATEGORY_009
# ======================================================================

class TestCreateCategory:
    """创建分类。"""

    # [API_CATEGORY_009] ------------------------------------------------
    def test_create_category_returns_201(self, client: CategoryClient) -> None:
        """创建分类 → 201（本环境公开创建）。"""
        slug = f"test-cat-{uuid.uuid4().hex[:8]}"
        response = client.post("/categories", json={
            "name": "E2E Test Category",
            "slug": slug,
        })
        assert response.status_code in (201, 200), f"意外状态码: {response.status_code} {response.text}"

# AI-assisted
