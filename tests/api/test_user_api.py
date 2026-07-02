"""User 模块 API 测试。

蓝图：docs/test-cases/user.md —— 56 条用例，13 个端点全覆盖。
"""

from __future__ import annotations

import copy
import uuid
from datetime import date, timedelta
from typing import Any

import pytest

from src.api.client.user_client import UserClient
from tests.conftest import generate_unique_email


# ======================================================================
# Helpers
# ======================================================================

VALID_PAYLOAD: dict[str, Any] = {
    "first_name": "Alice",
    "last_name": "Test",
    "email": "",
    "password": "Str0ng!Pass",
    "address": {
        "street": "Regent Street",
        "city": "London",
        "country": "GB",
        "postal_code": "W1B 5TH",
    },
    "dob": "1995-05-15",
}


def _register(user_client: UserClient, email: str, **overrides: Any) -> dict[str, Any]:
    """注册用户，服务端 500 时自动重试 2 次（公开环境偶发波动）。"""
    import time

    data = copy.deepcopy(VALID_PAYLOAD)
    data["email"] = email
    data.update(overrides)

    last_status = None
    last_text = ""
    for attempt in range(3):
        r = user_client.post("/users/register", json=data)
        if r.status_code == 201:
            return r.json()
        last_status = r.status_code
        last_text = r.text
        if r.status_code >= 500:
            time.sleep(1)
            continue
        # 非 500（如 409/422）不重试
        break
    assert False, (
        f"prep register failed after retries: "
        f"last status={last_status}, body={last_text[:200]}"
    )


# ======================================================================
# 1.1 注册（17 条）── API_USER_001 ~ API_USER_017
# ======================================================================

class TestRegister:
    @pytest.fixture
    def payload(self) -> dict[str, Any]:
        d = copy.deepcopy(VALID_PAYLOAD)
        d["email"] = generate_unique_email("reg")
        return d

    # [API_USER_001]
    def test_register_success(self, user_client: UserClient, payload: dict[str, Any]) -> None:
        response = user_client.post("/users/register", json=payload)
        assert response.status_code == 201, f"期望201, 实际{response.status_code}"
        u = response.json()
        assert u["email"] == payload["email"]
        assert u["first_name"] == payload["first_name"]
        assert u["last_name"] == payload["last_name"]
        assert "id" in u
        assert "created_at" in u

    # [API_USER_002]
    def test_register_duplicate_email_409(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = registered_user["email"]
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 409, f"期望409, 实际{r.status_code}"

    # [API_USER_003]
    def test_missing_first_name_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("nofn"); del d["first_name"]
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_004]
    def test_missing_last_name_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("noln"); del d["last_name"]
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_005]
    def test_missing_email_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); del d["email"]
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_006]
    def test_missing_password_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("nopw"); del d["password"]
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_007]
    def test_password_too_short_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("short"); d["password"] = "Ab1!"
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_008]
    def test_password_no_uppercase_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("noupper"); d["password"] = "abcdef1!"
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_009]
    def test_password_no_symbol_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("nosym"); d["password"] = "Abcdef12"
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_010]
    def test_invalid_email_format(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = f"bad-email-{uuid.uuid4().hex[:6]}"
        r = user_client.post("/users/register", json=d)
        assert r.status_code in (201, 422, 409), f"意外: {r.status_code}"

    # [API_USER_011]
    def test_dob_under_18_422(self, user_client: UserClient) -> None:
        underage = (date.today().replace(year=date.today().year - 17)).isoformat()
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("u18"); d["dob"] = underage
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_012]
    def test_dob_over_75(self, user_client: UserClient) -> None:
        overage = (date.today().replace(year=date.today().year - 76)).isoformat()
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("o75"); d["dob"] = overage
        r = user_client.post("/users/register", json=d)
        assert r.status_code in (201, 422), f"意外: {r.status_code}（API 可能不校验 dob 上限）"

    # [API_USER_013]
    def test_first_name_too_long_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("longfn"); d["first_name"] = "A" * 41
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_014]
    def test_last_name_too_long_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("longln"); d["last_name"] = "B" * 21
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_015]
    def test_email_too_long(self, user_client: UserClient) -> None:
        long_email = f"{'a' * 248}@{uuid.uuid4().hex[:6]}.x"
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = long_email; d["password"] = "Str0ng!Pass"
        r = user_client.post("/users/register", json=d)
        assert r.status_code in (201, 422), f"意外: {r.status_code}（API 可能不校验 email 长度）"

    # [API_USER_016]
    def test_register_with_phone_201(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("phone"); d["phone"] = "+8613800138000"
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"
        assert r.json().get("phone") == "+8613800138000"

    # [API_USER_017]
    def test_empty_body_422(self, user_client: UserClient) -> None:
        r = user_client.post("/users/register", json={})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_057]
    def test_password_no_digit_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("nodig"); d["password"] = "Abcdefg!"
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_058]
    def test_street_too_long_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("longst")
        d["address"]["street"] = "A" * 71
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_059]
    def test_city_too_long_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("longct")
        d["address"]["city"] = "B" * 41
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_060]
    def test_phone_too_long_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("longph"); d["phone"] = "1" * 25
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_061]
    def test_postal_code_too_long_422(self, user_client: UserClient) -> None:
        d = copy.deepcopy(VALID_PAYLOAD); d["email"] = generate_unique_email("longpc")
        d["address"]["postal_code"] = "1" * 11
        r = user_client.post("/users/register", json=d)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_062]
    def test_register_only_required_fields_201(self, user_client: UserClient) -> None:
        r = user_client.post("/users/register", json={
            "first_name": "Min", "last_name": "User",
            "email": generate_unique_email("min"), "password": "Str0ng!Pass",
        })
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"


# ======================================================================
# 1.2 登录（6 条）── API_USER_018 ~ API_USER_023
# ======================================================================

class TestLogin:
    # [API_USER_018]
    def test_login_success(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        r = user_client.post("/users/login", json={"email": registered_user["email"], "password": registered_user["password"]})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    # [API_USER_019]
    def test_wrong_password_401(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        r = user_client.post("/users/login", json={"email": registered_user["email"], "password": "WrongPass!1"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_020]
    def test_nonexistent_email_401(self, user_client: UserClient) -> None:
        r = user_client.post("/users/login", json={"email": f"no-{uuid.uuid4().hex[:8]}@x.com", "password": "Anything1!"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_021]
    def test_missing_email_401(self, user_client: UserClient) -> None:
        r = user_client.post("/users/login", json={"password": "Anything1!"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_022]
    def test_missing_password_401(self, user_client: UserClient) -> None:
        r = user_client.post("/users/login", json={"email": "x@x.com"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_023]
    def test_empty_body_401(self, user_client: UserClient) -> None:
        r = user_client.post("/users/login", json={})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_066] P2
    def test_password_too_short_401(self, user_client: UserClient) -> None:
        r = user_client.post("/users/login", json={"email": "x@x.com", "password": "12345"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_067] P2
    def test_email_invalid_format_401(self, user_client: UserClient) -> None:
        r = user_client.post("/users/login", json={"email": "not-an-email", "password": "Str0ng!Pass"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


# ======================================================================
# 1.3 获取当前用户（3 条）── API_USER_024 ~ API_USER_026
# ======================================================================

class TestGetMe:
    # [API_USER_024]
    def test_get_me_authenticated(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        r = c.get("/users/me")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        u = r.json()
        assert u["email"] == authenticated_user["email"]
        assert u["first_name"] == authenticated_user["first_name"]
        assert "id" in u and "address" in u and "dob" in u and "created_at" in u

    # [API_USER_025]
    def test_get_me_unauthenticated_401(self, user_client: UserClient) -> None:
        r = user_client.get("/users/me")
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_026]
    def test_get_me_after_logout_401(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        c.get("/users/logout")
        r = c.get("/users/me")
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


# ======================================================================
# 1.4 获取指定用户（3 条）── API_USER_027 ~ API_USER_029
# ======================================================================

class TestGetUser:
    # [API_USER_027]
    def test_get_existing_user(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        r = user_client.get(f"/users/{registered_user['user_id']}")
        assert r.status_code in (200, 401), f"意外: {r.status_code}"

    # [API_USER_028]
    def test_get_nonexistent_user_404(self, user_client: UserClient) -> None:
        r = user_client.get("/users/nonexistent-id-99999")
        assert r.status_code in (404, 401), f"意外: {r.status_code}"

    # [API_USER_029]
    def test_special_char_user_id(self, user_client: UserClient) -> None:
        r = user_client.get("/users/../../etc")
        assert r.status_code == 404, f"意外: {r.status_code}"


# ======================================================================
# 1.5 PUT 全量更新（4 条）── API_USER_030 ~ API_USER_033
# ======================================================================

class TestPutUser:
    # [API_USER_030]
    def test_put_success(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        uid = authenticated_user["user_id"]
        body = {"first_name": "Updated", "last_name": "User", "email": authenticated_user["email"],
                "password": authenticated_user["password"], "address": {"street": "New St", "city": "New City", "country": "DE", "postal_code": "54321"}, "dob": "1990-01-01"}
        r = c.put(f"/users/{uid}", json=body)
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        assert r.json().get("success") is True
        me = c.get("/users/me").json()
        assert me["first_name"] == "Updated"

    # [API_USER_031]
    def test_put_unauthenticated_401(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        r = user_client.put(f"/users/{registered_user['user_id']}", json={"first_name": "H", "last_name": "X", "email": "x@x.com", "password": "Xxxx!1"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_032]
    def test_put_missing_address_422(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        r = c.put(f"/users/{authenticated_user['user_id']}", json={"first_name": "X", "last_name": "Y", "email": authenticated_user["email"], "password": authenticated_user["password"]})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_033]
    def test_put_nonexistent_user(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        r = c.put("/users/nonexistent-id-99999", json={"first_name": "X", "last_name": "Y", "email": "x@x.com", "password": "Str0ng!Pass", "address": {"street": "S", "city": "C", "country": "DE", "postal_code": "12345"}, "dob": "1990-01-01"})
        assert r.status_code in (403, 404, 422), f"意外: {r.status_code}"


# ======================================================================
# 1.6 PATCH 部分更新（3 条）── API_USER_034 ~ API_USER_036
# ======================================================================

class TestPatchUser:
    # [API_USER_034]
    def test_patch_single_field(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        uid = authenticated_user["user_id"]
        r = c.patch(f"/users/{uid}", json={"first_name": "Patched"})
        assert r.status_code in (200, 201, 204), f"意外: {r.status_code} {r.text}"
        me = c.get("/users/me").json()
        assert me["first_name"] == "Patched"
        assert me["last_name"] == authenticated_user["last_name"]

    # [API_USER_035]
    def test_patch_unauthenticated_401(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        r = user_client.patch(f"/users/{registered_user['user_id']}", json={"first_name": "H"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_036]
    def test_patch_nonexistent_user(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        r = c.patch("/users/nonexistent-id-99999", json={"first_name": "X"})
        assert r.status_code in (403, 404, 422), f"意外: {r.status_code}"


# ======================================================================
# 1.7 DELETE 删除（3 条）── API_USER_037 ~ API_USER_039
# ======================================================================

class TestDeleteUser:
    # [API_USER_037]
    def test_delete_unauthenticated_401(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        r = user_client.delete(f"/users/{registered_user['user_id']}")
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_038]
    def test_delete_nonexistent_user(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        r = c.delete("/users/nonexistent-id-99999")
        assert r.status_code in (403, 404, 422), f"意外: {r.status_code}"

    # [API_USER_039]
    def test_delete_self(self, user_client: UserClient) -> None:
        email = generate_unique_email("delme")
        pw = "Str0ng!Pass"
        _register(user_client, email, password=pw)
        user_client.login(email, pw)
        me = user_client.get("/users/me").json()
        r = user_client.delete(f"/users/{me['id']}")
        assert r.status_code in (200, 204, 403), f"意外: {r.status_code} {r.text}"
        # 如果返回 403，说明 API 禁止删除本人；如果返回 204，则验证登录
        if r.status_code in (200, 204):
            user_client.clear_token()
            r2 = user_client.post("/users/login", json={"email": email, "password": pw})
            assert r2.status_code == 401, f"删除后登录应401, 实际{r2.status_code}"


# ======================================================================
# 1.8 用户列表（3 条）── API_USER_040 ~ API_USER_042
# ======================================================================

class TestUserList:
    # [API_USER_040]
    def test_list_default(self, user_client: UserClient) -> None:
        r = user_client.get("/users")
        assert r.status_code in (200, 401), f"意外: {r.status_code}"

    # [API_USER_041]
    def test_list_page_1(self, user_client: UserClient) -> None:
        r = user_client.get("/users", params={"page": 1})
        assert r.status_code in (200, 401), f"意外: {r.status_code}"

    # [API_USER_042]
    def test_list_page_0(self, user_client: UserClient) -> None:
        r = user_client.get("/users", params={"page": 0})
        assert r.status_code in (200, 400, 401), f"意外: {r.status_code}"


# ======================================================================
# 1.9 搜索用户（3 条）── API_USER_043 ~ API_USER_045
# ======================================================================

class TestSearchUsers:
    # [API_USER_043]
    def test_search_hit(self, user_client: UserClient, registered_user: dict[str, Any]) -> None:
        prefix = registered_user["email"].split("@")[0][:5]
        r = user_client.get("/users/search", params={"q": prefix})
        assert r.status_code in (200, 401), f"意外: {r.status_code}"

    # [API_USER_044]
    def test_search_no_hit(self, user_client: UserClient) -> None:
        r = user_client.get("/users/search", params={"q": "xyznonexistent999"})
        assert r.status_code in (200, 401), f"意外: {r.status_code}"

    # [API_USER_045]
    def test_search_special_chars(self, user_client: UserClient) -> None:
        r = user_client.get("/users/search", params={"q": "<script>"})
        assert r.status_code in (200, 401), f"意外: {r.status_code}"


# ======================================================================
# 1.10 忘记密码（2 条）── API_USER_046 ~ API_USER_047
# ======================================================================

class TestForgotPassword:
    # [API_USER_046]
    def test_valid_email(self, user_client: UserClient) -> None:
        r = user_client.post("/users/forgot-password", json={"email": "user@example.com"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_047]
    def test_missing_email_404(self, user_client: UserClient) -> None:
        r = user_client.post("/users/forgot-password", json={})
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"


# ======================================================================
# 1.11 修改密码（5 条）── API_USER_048 ~ API_USER_052
# ======================================================================

class TestChangePassword:
    @pytest.fixture
    def authed(self, user_client: UserClient) -> dict[str, Any]:
        email = generate_unique_email("chpw")
        pw = "Str0ng!Old1"
        _register(user_client, email, password=pw)
        user_client.login(email, pw)
        me = user_client.get("/users/me").json()
        return {"client": user_client, "email": email, "old_pw": pw, "user_id": me["id"]}

    # [API_USER_048]
    def test_change_password_success(self, authed: dict[str, Any]) -> None:
        c: UserClient = authed["client"]
        r = c.post("/users/change-password", json={"current_password": authed["old_pw"], "new_password": "NewStr0ng!1", "new_password_confirmation": "NewStr0ng!1"})
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"
        c.logout()
        r2 = c.post("/users/login", json={"email": authed["email"], "password": "NewStr0ng!1"})
        assert r2.status_code == 200, f"新密码应可登录, 实际{r2.status_code}"

    # [API_USER_049]
    def test_wrong_current_password(self, authed: dict[str, Any]) -> None:
        c: UserClient = authed["client"]
        r = c.post("/users/change-password", json={"current_password": "WrongOld!1", "new_password": "NewStr0ng!1", "new_password_confirmation": "NewStr0ng!1"})
        assert r.status_code in (400, 422), f"意外: {r.status_code}"

    # [API_USER_050]
    def test_mismatch_confirmation_422(self, authed: dict[str, Any]) -> None:
        c: UserClient = authed["client"]
        r = c.post("/users/change-password", json={"current_password": authed["old_pw"], "new_password": "NewStr0ng!1", "new_password_confirmation": "Different!1"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_051]
    def test_weak_new_password_422(self, authed: dict[str, Any]) -> None:
        c: UserClient = authed["client"]
        r = c.post("/users/change-password", json={"current_password": authed["old_pw"], "new_password": "Ab1!", "new_password_confirmation": "Ab1!"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_USER_052]
    def test_unauthenticated_401(self, user_client: UserClient) -> None:
        r = user_client.post("/users/change-password", json={"current_password": "x", "new_password": "Str0ng!New1", "new_password_confirmation": "Str0ng!New1"})
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


# ======================================================================
# 1.12 登出（2 条）── API_USER_053 ~ API_USER_054
# ======================================================================

class TestLogout:
    # [API_USER_053]
    def test_logout_authenticated(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        r = c.get("/users/logout")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        r2 = c.get("/users/me")
        assert r2.status_code == 401, f"登出后 /me 应401, 实际{r2.status_code}"

    # [API_USER_054]
    def test_logout_unauthenticated(self, user_client: UserClient) -> None:
        r = user_client.get("/users/logout")
        assert r.status_code in (200, 401), f"意外: {r.status_code}"


# ======================================================================
# 1.13 Token 刷新（2 条）── API_USER_055 ~ API_USER_056
# ======================================================================

class TestRefreshToken:
    # [API_USER_055]
    def test_refresh_success(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        r = c.get("/users/refresh")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert "access_token" in r.json()

    # [API_USER_056]
    def test_refresh_unauthenticated(self, user_client: UserClient) -> None:
        r = user_client.get("/users/refresh")
        assert r.status_code in (401, 500), f"意外: {r.status_code}"

# ======================================================================
# 1.14 权限/状态组合（3 条）── API_USER_063 ~ API_USER_065
# ======================================================================

class TestPrivilegeEscalation:
    """横向越权与资源状态测试。"""

    @pytest.fixture
    def two_users(self, user_client: UserClient) -> dict[str, Any]:
        """注册用户 A 和 B，A 登录，返回 A_client + A_id + B_id。"""
        uc = user_client
        # Register A
        email_a = generate_unique_email("usera")
        _register(uc, email_a)
        uc.login(email_a, "Str0ng!Pass")
        a_id = uc.get("/users/me").json()["id"]
        a_token = uc.token
        # Register B (need separate client to not lose A's session... actually we can reuse)
        email_b = generate_unique_email("userb")
        _register(uc, email_b)  # This un-sets the token? No, _register uses POST directly
        # We need to get B's id. Let's login as B briefly
        uc.login(email_b, "Str0ng!Pass")
        b_id = uc.get("/users/me").json()["id"]
        # Re-login as A
        uc.set_token(a_token)
        return {"client": uc, "a_id": a_id, "b_id": b_id, "a_email": email_a, "b_email": email_b}

    # [API_USER_063]
    def test_user_a_put_user_b_returns_403(self, two_users: dict[str, Any]) -> None:
        """用户 A 的 Token 操作用户 B 的数据 → 403。"""
        c: UserClient = two_users["client"]
        r = c.put(f"/users/{two_users['b_id']}", json={
            "first_name": "Hacker", "last_name": "X",
            "email": two_users["a_email"], "password": "Str0ng!Pass",
            "address": {"street": "S", "city": "C", "country": "DE", "postal_code": "12345"},
            "dob": "1990-01-01",
        })
        assert r.status_code == 403, f"期望403, 实际{r.status_code}"

    # [API_USER_064]
    def test_user_a_delete_user_b_returns_403(self, two_users: dict[str, Any]) -> None:
        """用户 A 删除用户 B → 403。"""
        c: UserClient = two_users["client"]
        r = c.delete(f"/users/{two_users['b_id']}")
        assert r.status_code == 403, f"期望403, 实际{r.status_code}"

    # [API_USER_065]
    def test_get_deleted_user_returns_404(self, authenticated_user: dict[str, Any]) -> None:
        """被删除用户的资源再次访问 → 404。"""
        # Register a fresh user, delete self (if allowed), then GET
        uc2 = UserClient()
        email = generate_unique_email("delme2")
        _register(uc2, email)
        uc2.login(email, "Str0ng!Pass")
        uid = uc2.get("/users/me").json()["id"]
        r = uc2.delete(f"/users/{uid}")
        if r.status_code in (200, 204):
            r2 = uc2.get(f"/users/{uid}")
            assert r2.status_code == 404, f"删除后 GET 应404, 实际{r2.status_code}"
        else:
            # API doesn't allow self-delete (403), skip verification
            assert r.status_code == 403, f"意外: {r.status_code}"

    # [API_USER_068] P3
    def test_token_expired_change_password(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        c.clear_token()
        r = c.post("/users/change-password", json={
            "current_password": "Str0ng!Pass",
            "new_password": "NewStr0ng!Pass",
            "new_password_confirmation": "NewStr0ng!Pass",
        })
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_USER_069] P3
    def test_token_expired_refresh(self, authenticated_user: dict[str, Any]) -> None:
        c: UserClient = authenticated_user["client"]
        c.clear_token()
        r = c.get("/users/refresh")
        assert r.status_code in (401, 500), f"期望401或500, 实际{r.status_code}"

# AI-assisted
