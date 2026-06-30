"""Brand 模块 API 测试。

对应文档：docs/test-cases/api-test-cases-v1.md（API_BRAND_001 ~ API_BRAND_008）

覆盖维度：正常功能 · 异常场景（404）· 数据结构校验 · 搜索边界
"""

from __future__ import annotations

import uuid

import pytest

from src.api.client.brand_client import BrandClient


@pytest.fixture
def client() -> BrandClient:
    with BrandClient() as c:
        yield c


# ======================================================================
# 获取品牌列表（GET /brands）── API_BRAND_001 ~ API_BRAND_002
# ======================================================================

class TestGetBrands:
    """获取品牌列表。"""

    # [API_BRAND_001] -------------------------------------------------
    def test_get_brands_returns_200(self, client: BrandClient) -> None:
        """获取品牌列表 → 200，返回非空数组，元素含 id/name/slug。"""
        response = client.get("/brands")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        brands = response.json()
        assert isinstance(brands, list), f"期望列表, 实际{type(brands)}"
        assert len(brands) > 0, "品牌列表不应为空"
        brand = brands[0]
        assert "id" in brand, "品牌对象应包含 id"
        assert "name" in brand, "品牌对象应包含 name"
        assert "slug" in brand, "品牌对象应包含 slug"

    # [API_BRAND_002] -------------------------------------------------
    def test_get_brands_returns_valid_data(self, client: BrandClient) -> None:
        """数据结构校验：前 5 个品牌的 id/name/slug 均为非空字符串。"""
        response = client.get("/brands")
        brands = response.json()
        for brand in brands[:5]:
            assert isinstance(brand["id"], str), f"id 应为字符串"
            assert isinstance(brand["name"], str), f"name 应为字符串"
            assert isinstance(brand["slug"], str), f"slug 应为字符串"
            assert len(brand["name"]) > 0, "name 不应为空"
            assert len(brand["slug"]) > 0, "slug 不应为空"


# ======================================================================
# 获取指定品牌（GET /brands/{brandId}）── API_BRAND_003 ~ API_BRAND_004
# ======================================================================

class TestGetBrand:
    """获取指定品牌。"""

    # [API_BRAND_003] -------------------------------------------------
    def test_get_brand_by_valid_id(self, client: BrandClient) -> None:
        """存在的品牌 ID → 200，响应体 id 与请求一致。"""
        brands = client.get("/brands").json()
        existing_id = brands[0]["id"]
        existing_slug = brands[0]["slug"]
        response = client.get(f"/brands/{existing_id}")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        brand = response.json()
        assert brand["id"] == existing_id
        assert brand["slug"] == existing_slug

    # [API_BRAND_004] -------------------------------------------------
    def test_get_brand_nonexistent_returns_404(self, client: BrandClient) -> None:
        """不存在的品牌 ID → 404。"""
        response = client.get("/brands/nonexistent-id-99999")
        assert response.status_code == 404, f"期望404, 实际{response.status_code}"


# ======================================================================
# 搜索品牌（GET /brands/search）── API_BRAND_005 ~ API_BRAND_007
# ======================================================================

class TestSearchBrands:
    """搜索品牌。"""

    # [API_BRAND_005] -------------------------------------------------
    def test_search_brands_with_match(self, client: BrandClient) -> None:
        """搜索 'for' → 200，返回匹配的品牌列表。"""
        response = client.get("/brands/search", params={"q": "for"})
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        results = response.json()
        assert isinstance(results, list), f"期望列表, 实际{type(results)}"

    # [API_BRAND_006] -------------------------------------------------
    def test_search_brands_no_match(self, client: BrandClient) -> None:
        """搜索不存在的关键词 → 200，返回空数组。"""
        response = client.get("/brands/search", params={"q": "xyznonexistent999"})
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        results = response.json()
        assert isinstance(results, list), f"期望列表, 实际{type(results)}"
        assert len(results) == 0, "无匹配时应返回空列表"

    # [API_BRAND_007] -------------------------------------------------
    def test_search_brands_no_query_returns_all(self, client: BrandClient) -> None:
        """不传 q 参数 → 200，返回全量（q 为可选参数）。"""
        response = client.get("/brands/search")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"


# ======================================================================
# 创建品牌（POST /brands）── API_BRAND_008
# ======================================================================

class TestCreateBrand:
    """创建品牌。"""

    # [API_BRAND_008] -------------------------------------------------
    def test_create_brand_returns_201(self, client: BrandClient) -> None:
        """创建品牌 → 201，响应含 id/name/slug（本环境公开创建）。"""
        slug = f"test-brand-{uuid.uuid4().hex[:8]}"
        response = client.post("/brands", json={
            "name": "E2E Test Brand",
            "slug": slug,
        })
        assert response.status_code == 201, f"期望201, 实际{response.status_code} {response.text}"
        data = response.json()
        assert data["name"] == "E2E Test Brand"
        assert data["slug"] == slug
        assert "id" in data

# AI-assisted
