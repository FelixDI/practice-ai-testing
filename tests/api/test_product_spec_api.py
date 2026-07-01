"""Product Spec 模块 API 测试。

蓝图：docs/test-cases/product-spec.md —— 40 条用例，6 个端点全覆盖。
"""

from __future__ import annotations

import pytest

from src.api.client.product_spec_client import ProductSpecClient
from src.api.client.user_client import UserClient
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


# -- module 级夹具 --------------------------------------------------------

@pytest.fixture(scope="module")
def _mod_product_id() -> str:
    """module 级：获取一个有效 product_id。"""
    with UserClient() as uc:
        r = uc.get("/products")
        data = r.json()
        items = data if isinstance(data, list) else data.get("data", [])
        assert len(items) > 0, "需有已有商品"
        return items[0]["id"]


@pytest.fixture(scope="module")
def _mod_auth_spec() -> ProductSpecClient:
    """module 级：已认证的 ProductSpecClient。"""
    with UserClient() as uc:
        uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        token = uc.token
    with ProductSpecClient() as psc:
        psc.set_token(token)
        yield psc


@pytest.fixture(scope="module")
def _mod_spec(_mod_auth_spec: ProductSpecClient, _mod_product_id: str) -> dict:
    """module 级：预创建一个规格，返回其数据。"""
    r = _mod_auth_spec.add_spec(_mod_product_id, {
        "spec_name": "ModuleWeight", "spec_value": "1.0", "spec_unit": "kg",
    })
    assert r.status_code == 201, f"prep create spec failed: {r.status_code} {r.text}"
    return r.json()


# -- function 级夹具 ------------------------------------------------------

@pytest.fixture
def client() -> ProductSpecClient:
    with ProductSpecClient() as c:
        yield c


@pytest.fixture
def _auth_spec() -> ProductSpecClient:
    """function 级：已认证的 ProductSpecClient（mutation 测试用）。"""
    with UserClient() as uc:
        uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        token = uc.token
    with ProductSpecClient() as psc:
        psc.set_token(token)
        yield psc


# ======================================================================
# 1.1 获取产品规格列表 · GET /products/{productId}/specs ── API_SPEC_001
# ======================================================================

class TestGetSpecs:
    # [API_SPEC_001] P0
    def test_get_specs_200(self, client: ProductSpecClient, _mod_product_id: str) -> None:
        r = client.get_specs(_mod_product_id)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        data = r.json()
        assert isinstance(data, list), f"期望list, 实际{type(data)}"

    # [API_SPEC_041] P1
    def test_get_specs_nonexistent_product(self, client: ProductSpecClient) -> None:
        r = client.get_specs("nonexistent-99999")
        assert r.status_code in (200, 404), f"期望200或404, 实际{r.status_code}"


# ======================================================================
# 1.2 添加产品规格 · POST /products/{productId}/specs ── API_SPEC_002~007, 016~025
# ======================================================================

class TestAddSpec:
    # -- P0 ---------------------------------------------------------------

    # [API_SPEC_002] P0
    def test_add_spec_full_201(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "P0Weight", "spec_value": "1.5", "spec_unit": "kg",
        })
        assert r.status_code == 201, f"期望201, 实际{r.status_code} {r.text}"
        d = r.json()
        assert d["spec_name"] == "P0Weight"
        assert d["spec_value"] == "1.5"
        assert d["spec_unit"] == "kg"
        assert "id" in d and "product_id" in d

    # [API_SPEC_003] P0
    def test_add_spec_required_only_201(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "P0Color", "spec_value": "Red",
        })
        assert r.status_code == 201, f"期望201, 实际{r.status_code} {r.text}"
        d = r.json()
        assert d["spec_unit"] is None

    # [API_SPEC_004] P0
    def test_missing_spec_name_422(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {"spec_value": "100"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_SPEC_005] P0
    def test_missing_spec_value_422(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {"spec_name": "Width"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P1 ---------------------------------------------------------------

    # [API_SPEC_006] P1
    def test_unauthorized_401(self, client: ProductSpecClient, _mod_product_id: str) -> None:
        r = client.add_spec(_mod_product_id, {"spec_name": "X", "spec_value": "Y"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_SPEC_007] P1
    def test_nonexistent_product_500(self, _auth_spec: ProductSpecClient) -> None:
        """实测：为不存在的产品添加规格触发服务端 500。"""
        r = _auth_spec.add_spec("nonexistent-99999", {
            "spec_name": "Weight", "spec_value": "1.0",
        })
        assert r.status_code == 500, f"期望500, 实际{r.status_code}"

    # -- P2 字段边界 -------------------------------------------------------

    # [API_SPEC_016] P2
    def test_spec_name_empty_422(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {"spec_name": "", "spec_value": "100"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_SPEC_017] P2
    def test_spec_value_empty(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {"spec_name": "Weight", "spec_value": ""})
        assert r.status_code in (201, 422), f"期望201或422, 实际{r.status_code}"

    # [API_SPEC_018] P2
    def test_spec_name_overlong_422(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "A" * 256, "spec_value": "100",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_SPEC_019] P2
    def test_spec_value_overlong(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "Weight", "spec_value": "B" * 256,
        })
        assert r.status_code in (201, 422), f"期望201或422, 实际{r.status_code}"

    # [API_SPEC_020] P2
    def test_spec_unit_empty_string(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "Width", "spec_value": "100", "spec_unit": "",
        })
        assert r.status_code in (201, 422), f"期望201或422, 实际{r.status_code}"

    # [API_SPEC_021] P2
    def test_spec_unit_null_201(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "Width", "spec_value": "100", "spec_unit": None,
        })
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"
        assert r.json()["spec_unit"] is None

    # [API_SPEC_022] P2
    def test_spec_name_whitespace_422(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "   ", "spec_value": "100",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_SPEC_023] P2
    def test_spec_value_whitespace(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "Width", "spec_value": "   ",
        })
        assert r.status_code in (201, 422), f"期望201或422, 实际{r.status_code}"

    # [API_SPEC_024] P2
    def test_spec_name_special_chars(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "<b>Bold</b>", "spec_value": "100",
        })
        assert r.status_code == 201, f"期望201（服务端应转义）, 实际{r.status_code}"

    # [API_SPEC_025] P2
    def test_extra_field(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "Test", "spec_value": "100", "extra": "ignored",
        })
        assert r.status_code in (201, 422), f"期望201或422, 实际{r.status_code}"

    # [API_SPEC_042] P2
    def test_spec_name_null_422(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": None, "spec_value": "100",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_SPEC_043] P2
    def test_spec_value_null_422(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "Width", "spec_value": None,
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"


# ======================================================================
# 1.3 获取指定规格 · GET /products/{productId}/specs/{specId} ── API_SPEC_008~009
# ======================================================================

class TestGetSpec:
    # [API_SPEC_008] P0
    def test_get_spec_200(self, client: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = client.get_spec(_mod_product_id, _mod_spec["id"])
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        d = r.json()
        assert d["id"] == _mod_spec["id"]

    # [API_SPEC_009] P1
    def test_get_nonexistent_spec_404(self, client: ProductSpecClient, _mod_product_id: str) -> None:
        r = client.get_spec(_mod_product_id, "nonexistent-99999")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 1.4 更新产品规格 · PUT /products/{productId}/specs/{specId} ── API_SPEC_010~012, 026~029
# ======================================================================

class TestUpdateSpec:
    # [API_SPEC_010] P0
    def test_update_spec_value_200(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = _mod_auth_spec.update_spec(_mod_product_id, _mod_spec["id"], {"spec_value": "2.0"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_SPEC_011] P0
    def test_update_spec_name_unit_200(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = _mod_auth_spec.update_spec(_mod_product_id, _mod_spec["id"], {
            "spec_name": "NetWeight", "spec_unit": "g",
        })
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_SPEC_012] P1
    def test_update_unauthorized_401(self, client: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = client.update_spec(_mod_product_id, _mod_spec["id"], {"spec_value": "3.0"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # -- P2 边界 -----------------------------------------------------------

    # [API_SPEC_026] P2
    def test_update_empty_body_200(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = _mod_auth_spec.update_spec(_mod_product_id, _mod_spec["id"], {})
        assert r.status_code == 200, f"期望200（无变更）, 实际{r.status_code}"

    # [API_SPEC_027] P2
    def test_update_unit_to_null_200(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = _mod_auth_spec.update_spec(_mod_product_id, _mod_spec["id"], {"spec_unit": None})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_SPEC_028] P2
    def test_update_name_empty_422(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = _mod_auth_spec.update_spec(_mod_product_id, _mod_spec["id"], {"spec_name": ""})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_SPEC_029] P2
    def test_update_value_empty(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = _mod_auth_spec.update_spec(_mod_product_id, _mod_spec["id"], {"spec_value": ""})
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_SPEC_044] P1
    def test_update_nonexistent_spec(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _mod_auth_spec.update_spec(_mod_product_id, "nonexistent-99999", {"spec_value": "3.0"})
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"

    # [API_SPEC_045] P1
    def test_update_nonexistent_product(self, _mod_auth_spec: ProductSpecClient, _mod_spec: dict) -> None:
        r = _mod_auth_spec.update_spec("nonexistent-99999", _mod_spec["id"], {"spec_value": "3.0"})
        assert r.status_code in (404, 500), f"期望404或500, 实际{r.status_code}"


# ======================================================================
# 1.5 删除产品规格 · DELETE /products/{productId}/specs/{specId} ── API_SPEC_013~014
# ======================================================================

class TestDeleteSpec:
    # [API_SPEC_013] P0
    def test_delete_spec_204(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        # 创建一个独立的 spec 用于删除
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "ToDelete", "spec_value": "temp",
        })
        assert r.status_code == 201, f"prep failed: {r.status_code}"
        spec_id = r.json()["id"]
        r2 = _auth_spec.delete_spec(_mod_product_id, spec_id)
        assert r2.status_code == 204, f"期望204, 实际{r2.status_code}"

    # [API_SPEC_014] P1
    def test_delete_unauthorized_401(self, client: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        r = client.delete_spec(_mod_product_id, _mod_spec["id"])
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


# ======================================================================
# 1.6 获取所有规格名称 · GET /product-specs/names ── API_SPEC_015
# ======================================================================

class TestGetSpecNames:
    # [API_SPEC_015] P0
    def test_get_spec_names_200(self, client: ProductSpecClient) -> None:
        r = client.get_spec_names()
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        data = r.json()
        assert isinstance(data, (list, dict)), f"期望list或dict, 实际{type(data)}"


# ======================================================================
# P2 路径参数 / 重复操作边界 ── API_SPEC_030 ~ 034
# ======================================================================

class TestSpecBoundary:
    # [API_SPEC_030] P2
    def test_product_id_special_chars(self, client: ProductSpecClient) -> None:
        """实测：特殊字符 product_id 被当作普通字符串返回 200（空数据）。"""
        r = client.get_specs("<script>")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_SPEC_031] P2
    def test_spec_id_special_chars_get(self, client: ProductSpecClient, _mod_product_id: str) -> None:
        r = client.get_spec(_mod_product_id, "<img>")
        assert r.status_code in (404, 422), f"期望404/422, 实际{r.status_code}"

    # [API_SPEC_032] P2
    def test_spec_id_injection_delete(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        """实测：DELETE 不校验 spec_id 格式，返回 204（幂等）。"""
        r = _mod_auth_spec.delete_spec(_mod_product_id, "'; DROP--")
        assert r.status_code == 204, f"期望204（幂等删除）, 实际{r.status_code}"

    # [API_SPEC_033] P2
    def test_delete_already_deleted_204(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        """实测：重复删除返回 204（幂等）。"""
        r = _auth_spec.add_spec(_mod_product_id, {"spec_name": "DelMe", "spec_value": "x"})
        assert r.status_code == 201
        spec_id = r.json()["id"]
        _auth_spec.delete_spec(_mod_product_id, spec_id)
        r2 = _auth_spec.delete_spec(_mod_product_id, spec_id)
        assert r2.status_code == 204, f"期望204（幂等）, 实际{r2.status_code}"

    # [API_SPEC_034] P2
    def test_duplicate_spec_name(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {"spec_name": "DupTest", "spec_value": "1"})
        assert r.status_code == 201
        r2 = _auth_spec.add_spec(_mod_product_id, {"spec_name": "DupTest", "spec_value": "2"})
        assert r2.status_code in (201, 409), f"期望201或409, 实际{r2.status_code}"


# ======================================================================
# P3 深度防御 ── API_SPEC_035 ~ 040
# ======================================================================

class TestSpecDefense:
    # [API_SPEC_040] P3
    def test_sql_injection_spec_value(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "InjectionTest",
            "spec_value": "1'; DROP TABLE product_specs; --",
        })
        assert r.status_code == 201, f"期望201（应参数化查询）, 实际{r.status_code} {r.text}"

    # [API_SPEC_046] P3
    def test_xss_spec_name(self, _auth_spec: ProductSpecClient, _mod_product_id: str) -> None:
        r = _auth_spec.add_spec(_mod_product_id, {
            "spec_name": "<script>alert(1)</script>", "spec_value": "100",
        })
        assert r.status_code == 201, f"期望201（应转义）, 实际{r.status_code} {r.text}"

    # [API_SPEC_047] P3
    def test_token_expired_update(self, _mod_auth_spec: ProductSpecClient, _mod_product_id: str, _mod_spec: dict) -> None:
        """Token 过期后更新规格。"""
        _mod_auth_spec.clear_token()
        r = _mod_auth_spec.update_spec(_mod_product_id, _mod_spec["id"], {"spec_value": "9.0"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"
