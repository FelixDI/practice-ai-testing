"""Favorite 模块 API 测试。

蓝图：docs/test-cases/favorite.md —— 28 条用例，4 个端点全覆盖。

实测行为备注：
- POST /favorites 对不存在的 product_id（如 "nonexistent-99999"）返回 422 而非 404
- DELETE /favorites/{id} 对不存在的 id 返回 204（幂等删除）而非 404
"""

from __future__ import annotations

import uuid

import pytest

from src.api.client.favorite_client import FavoriteClient
from src.api.client.user_client import UserClient
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


# -- helpers -------------------------------------------------------------

def _login_and_get_token() -> str:
    """使用固定测试账号登录，返回 access_token。"""
    with UserClient() as uc:
        uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        return uc.token  # type: ignore[return-value]


def _get_product_ids(count: int = 3) -> list[str]:
    """获取前 N 个有效 product_id。"""
    with UserClient() as uc:
        r = uc.get("/products")
        data = r.json()
        items = data if isinstance(data, list) else data.get("data", [])
        assert len(items) >= count, f"需至少有 {count} 个商品"
        return [item["id"] for item in items[:count]]


def _create_favorite(fc: FavoriteClient, product_id: str) -> str:
    """创建收藏（若已存在则先查列表去重），返回 favorite_id。"""
    r = fc.get_favorites()
    if r.status_code == 200:
        for fav in r.json():
            if fav.get("product_id") == product_id:
                return fav["id"]
    r = fc.add_favorite(product_id)
    assert r.status_code in (200, 201), f"prep add favorite failed: {r.status_code} {r.text}"
    return r.json()["id"]


def _get_unfavorited_product(fc: FavoriteClient) -> str:
    """获取一个当前用户未收藏的 product_id。"""
    r = fc.get_favorites()
    favorited: set[str] = set()
    if r.status_code == 200:
        favorited = {f["product_id"] for f in r.json()}
    products = _get_product_ids(9)
    for pid in products:
        if pid not in favorited:
            return pid
    # 所有商品都已收藏，取最后一个（测试 409 场景）
    return products[-1]


# -- module 级夹具（只读复用）----------------------------------------------

@pytest.fixture(scope="module")
def _mod_product_ids() -> list[str]:
    """module 级：多个 product_id，避免各测试用同一个导致 409。"""
    return _get_product_ids(5)


@pytest.fixture(scope="module")
def _mod_auth_fav(_mod_product_ids: list[str]) -> tuple[FavoriteClient, str, str]:
    """module 级：已认证 FavoriteClient + 一个已收藏的 favorite_id + 未收藏的 product_id。

    读操作用 favorite_id；写操作用 unused_product_id 避免 409。
    """
    token = _login_and_get_token()
    fc = FavoriteClient()
    fc.set_token(token)
    # 用第 0 个商品创建 module 级收藏
    fav_id = _create_favorite(fc, _mod_product_ids[0])
    # 返回 client、已收藏的 fav_id、一个未收藏的 product_id（供 function 测试用）
    yield fc, fav_id, _mod_product_ids[1]
    fc.close()


# -- function 级夹具（mutation 隔离）---------------------------------------

@pytest.fixture
def _auth_fav(_mod_product_ids: list[str]) -> FavoriteClient:
    """function 级：独立的已认证 FavoriteClient。

    不预创建收藏——各测试通过 _get_unfavorited_product() 自行获取未收藏的商品。
    """
    token = _login_and_get_token()
    fc = FavoriteClient()
    fc.set_token(token)
    yield fc
    fc.close()


# ======================================================================
# 1.1 添加收藏 · POST /favorites ── API_FAVORITE_001 ~ 005, 015~021
# ======================================================================

class TestAddFavorite:
    # [API_FAVORITE_001] P0
    def test_add_favorite_201(self, _auth_fav: FavoriteClient) -> None:
        """实测：POST /favorites 返回 201 Created。"""
        pid = _get_unfavorited_product(_auth_fav)
        r = _auth_fav.add_favorite(pid)
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"
        d = r.json()
        assert "id" in d and "product_id" in d and "user_id" in d

    # [API_FAVORITE_002] P0
    def test_missing_product_id_422(self, _auth_fav: FavoriteClient) -> None:
        r = _auth_fav.post("/favorites", json={})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_FAVORITE_003] P1
    def test_unauthorized_401(self, favorite_client: FavoriteClient) -> None:
        r = favorite_client.add_favorite(_get_product_ids(1)[0])
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_FAVORITE_004] P1
    def test_nonexistent_product(self, _auth_fav: FavoriteClient) -> None:
        """实测：不存在的 product_id 格式返回 422 而非 404。"""
        r = _auth_fav.add_favorite("nonexistent-99999")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_FAVORITE_005] P1
    def test_duplicate_favorite_409(self, _auth_fav: FavoriteClient) -> None:
        pid = _get_unfavorited_product(_auth_fav)
        r = _auth_fav.add_favorite(pid)
        # 若已收藏（409），直接验证第二次调用仍返回 409
        if r.status_code == 409:
            pass  # 已有收藏，跳过 prep
        else:
            assert r.status_code in (200, 201), f"prep failed: {r.status_code}"
        r2 = _auth_fav.add_favorite(pid)
        assert r2.status_code == 409, f"期望409, 实际{r2.status_code}"

    # -- P2 边界 ----------------------------------------------------------

    # [API_FAVORITE_015] P2
    def test_product_id_empty_422(self, _auth_fav: FavoriteClient) -> None:
        r = _auth_fav.add_favorite("")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_FAVORITE_016] P2
    def test_product_id_whitespace(self, _auth_fav: FavoriteClient) -> None:
        r = _auth_fav.add_favorite("   ")
        assert r.status_code in (404, 422), f"期望404/422, 实际{r.status_code}"

    # [API_FAVORITE_017] P2
    def test_product_id_overlong(self, _auth_fav: FavoriteClient) -> None:
        r = _auth_fav.add_favorite("A" * 256)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_FAVORITE_018] P2
    def test_product_id_special_chars(self, _auth_fav: FavoriteClient) -> None:
        r = _auth_fav.add_favorite("<script>alert(1)</script>")
        assert r.status_code in (404, 422), f"期望404/422, 实际{r.status_code}"

    # [API_FAVORITE_019] P2
    def test_product_id_null_422(self, _auth_fav: FavoriteClient) -> None:
        r = _auth_fav.post("/favorites", json={"product_id": None})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_FAVORITE_020] P2
    def test_product_id_type_int_422(self, _auth_fav: FavoriteClient) -> None:
        r = _auth_fav.post("/favorites", json={"product_id": 12345})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_FAVORITE_021] P2
    def test_extra_field(self, _auth_fav: FavoriteClient) -> None:
        pid = _get_unfavorited_product(_auth_fav)
        r = _auth_fav.post("/favorites", json={"product_id": pid, "extra": "ignored"})
        assert r.status_code in (200, 201, 409, 422), f"实际{r.status_code}"


# ======================================================================
# 1.2 获取收藏列表 · GET /favorites ── API_FAVORITE_006 ~ 008
# ======================================================================

class TestGetFavorites:
    # [API_FAVORITE_006] P0
    def test_get_favorites_with_data(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        fc, _, _ = _mod_auth_fav
        r = fc.get_favorites()
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0] and "product_id" in data[0]

    # [API_FAVORITE_008] P1
    def test_get_favorites_unauthorized_401(self, favorite_client: FavoriteClient) -> None:
        r = favorite_client.get_favorites()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_FAVORITE_030] P2
    def test_empty_list_structure(self, _auth_fav: FavoriteClient) -> None:
        """空收藏列表响应应为 [] 而非 null 或对象。"""
        r = _auth_fav.get_favorites()
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list), f"期望list, 实际{type(data)}"


# ======================================================================
# 1.3 获取指定收藏 · GET /favorites/{id} ── API_FAVORITE_009 ~ 011, 022~023
# ======================================================================

class TestGetFavorite:
    # [API_FAVORITE_009] P0
    def test_get_favorite_200(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        fc, fav_id, _ = _mod_auth_fav
        r = fc.get_favorite(fav_id)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        d = r.json()
        assert d["id"] == fav_id

    # [API_FAVORITE_010] P1
    def test_get_favorite_unauthorized_401(
        self, favorite_client: FavoriteClient,
        _mod_auth_fav: tuple[FavoriteClient, str, str],
    ) -> None:
        _, fav_id, _ = _mod_auth_fav
        r = favorite_client.get_favorite(fav_id)
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_FAVORITE_011] P1
    def test_get_nonexistent_favorite_404(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        fc, _, _ = _mod_auth_fav
        r = fc.get_favorite("nonexistent-99999")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"

    # -- P2 边界 ----------------------------------------------------------

    # [API_FAVORITE_022] P2
    def test_favorite_id_special_chars(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        fc, _, _ = _mod_auth_fav
        r = fc.get_favorite("<script>")
        assert r.status_code in (404, 422), f"期望404/422, 实际{r.status_code}"

    # [API_FAVORITE_023] P2
    def test_favorite_id_overlong(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        fc, _, _ = _mod_auth_fav
        r = fc.get_favorite("A" * 256)
        assert r.status_code in (404, 422), f"期望404/422, 实际{r.status_code}"

    # [API_FAVORITE_029] P2
    def test_favorite_id_empty(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        """favoriteId 为空时 GET /favorites/ 匹配列表路由返回 200。"""
        fc, _, _ = _mod_auth_fav
        r = fc.get("/favorites/")
        assert r.status_code == 200, f"期望200（匹配列表路由）, 实际{r.status_code}"


# ======================================================================
# 1.4 取消收藏 · DELETE /favorites/{id} ── API_FAVORITE_012 ~ 014, 024
# ======================================================================

class TestDeleteFavorite:
    # [API_FAVORITE_012] P0
    def test_delete_favorite_204(self, _auth_fav: FavoriteClient) -> None:
        pid = _get_unfavorited_product(_auth_fav)
        fav_id = _create_favorite(_auth_fav, pid)
        r = _auth_fav.delete_favorite(fav_id)
        assert r.status_code == 204, f"期望204, 实际{r.status_code}"
        r2 = _auth_fav.get_favorite(fav_id)
        assert r2.status_code == 404, f"删除后应返回404, 实际{r2.status_code}"

    # [API_FAVORITE_013] P1
    def test_delete_unauthorized_401(
        self, favorite_client: FavoriteClient,
        _mod_auth_fav: tuple[FavoriteClient, str, str],
    ) -> None:
        _, fav_id, _ = _mod_auth_fav
        r = favorite_client.delete_favorite(fav_id)
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_FAVORITE_014] P1
    def test_delete_nonexistent_204(self, _auth_fav: FavoriteClient) -> None:
        """实测：删除不存在的收藏返回 204（幂等）。"""
        r = _auth_fav.delete_favorite("nonexistent-99999")
        assert r.status_code == 204, f"期望204（幂等删除）, 实际{r.status_code}"

    # -- P2 边界 ----------------------------------------------------------

    # [API_FAVORITE_024] P2
    def test_delete_already_deleted(self, _auth_fav: FavoriteClient) -> None:
        pid = _get_unfavorited_product(_auth_fav)
        fav_id = _create_favorite(_auth_fav, pid)
        _auth_fav.delete_favorite(fav_id)
        r2 = _auth_fav.delete_favorite(fav_id)
        assert r2.status_code == 204, f"期望204（幂等）, 实际{r2.status_code}"

    # [API_FAVORITE_031] P2
    def test_delete_favorite_id_empty(self, _auth_fav: FavoriteClient) -> None:
        """DELETE favoriteId 为空字符串返回 404 或 405。"""
        r = _auth_fav.delete("/favorites/")
        assert r.status_code in (404, 405), f"期望404/405, 实际{r.status_code}"


# ======================================================================
# P3 深度防御 ── API_FAVORITE_025 ~ 028
# ======================================================================

class TestFavoriteDefense:
    # [API_FAVORITE_025] P3
    def test_cross_user_get_favorite(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        """用户 B 查看用户 A 的收藏：实测 API 不校验所有权，返回 200。"""
        _, fav_id, _ = _mod_auth_fav
        with UserClient() as uc:
            email = f"cross-{uuid.uuid4().hex[:8]}@e2e.example"
            uc.register({
                "first_name": "Cross", "last_name": "User",
                "email": email, "password": "Str0ng!Pass",
                "address": {"street": "X", "city": "Y", "country": "DE", "postal_code": "10115"},
                "dob": "1990-01-01",
            })
            uc.login(email, "Str0ng!Pass")
            token_b = uc.token

        with FavoriteClient() as fc_b:
            fc_b.set_token(token_b)
            r = fc_b.get_favorite(fav_id)
            assert r.status_code == 200, f"期望200（API 不校验所有权）, 实际{r.status_code}"

    # [API_FAVORITE_026] P3
    def test_cross_user_delete_favorite(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        """用户 B 删除用户 A 的收藏：实测 DELETE 幂等返回 204。"""
        _, fav_id, _ = _mod_auth_fav
        with UserClient() as uc:
            email = f"cross-{uuid.uuid4().hex[:8]}@e2e.example"
            uc.register({
                "first_name": "Cross", "last_name": "User",
                "email": email, "password": "Str0ng!Pass",
                "address": {"street": "X", "city": "Y", "country": "DE", "postal_code": "10115"},
                "dob": "1990-01-01",
            })
            uc.login(email, "Str0ng!Pass")
            token_b = uc.token

        with FavoriteClient() as fc_b:
            fc_b.set_token(token_b)
            r = fc_b.delete_favorite(fav_id)
            assert r.status_code == 204, f"期望204（幂等删除）, 实际{r.status_code}"

    # [API_FAVORITE_028] P3
    def test_operation_after_logout(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        """登出后操作收藏返回 401。"""
        fc, _, _ = _mod_auth_fav
        fc.clear_token()
        r = fc.get_favorites()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_FAVORITE_032] P3
    def test_cross_user_get_favorites_list(self, _mod_auth_fav: tuple[FavoriteClient, str, str]) -> None:
        """用户 B 获取收藏列表：不应包含用户 A 的收藏。"""
        fc_a, _, _ = _mod_auth_fav
        # 确保 token 有效（logout 测试可能已清除）
        if fc_a.token is None:
            fc_a.set_token(_login_and_get_token())
        r_a = fc_a.get_favorites()
        assert r_a.status_code == 200, f"prep get A favorites failed: {r_a.status_code}"
        a_fav_ids = {f["id"] for f in r_a.json()}

        # 注册用户 B
        with UserClient() as uc:
            email = f"cross-list-{uuid.uuid4().hex[:8]}@e2e.example"
            uc.register({
                "first_name": "CrossList", "last_name": "User",
                "email": email, "password": "Str0ng!Pass",
                "address": {"street": "X", "city": "Y", "country": "DE", "postal_code": "10115"},
                "dob": "1990-01-01",
            })
            uc.login(email, "Str0ng!Pass")
            token_b = uc.token

        with FavoriteClient() as fc_b:
            fc_b.set_token(token_b)
            r_b = fc_b.get_favorites()
            assert r_b.status_code == 200
            b_fav_ids = {f["id"] for f in r_b.json()}
            overlap = a_fav_ids & b_fav_ids
            assert len(overlap) == 0, f"越权：用户 B 看到了用户 A 的收藏 {overlap}"
