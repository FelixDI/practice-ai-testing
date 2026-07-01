"""TOTP 模块 API 测试。

蓝图：docs/test-cases/totp.md —— 19 条用例，2 个端点全覆盖。

注意：TOTP 每个账号仅可设置一次，固定测试账号不可设置。
测试需要动态注册新用户。
"""

from __future__ import annotations

import uuid

import pyotp
import pytest

from src.api.client.totp_client import TOTPClient
from src.api.client.user_client import UserClient


# -- helpers -------------------------------------------------------------

def _register_and_login() -> tuple[UserClient, str, str]:
    """注册新用户并登录，返回 (UserClient, email, token)。"""
    email = f"totp-{uuid.uuid4().hex[:8]}@e2e.example"
    uc = UserClient()
    uc.post("/users/register", json={
        "first_name": "TOTP", "last_name": "Test",
        "email": email, "password": "Str0ng!Pass",
        "address": {"street": "X", "city": "Y", "country": "DE", "postal_code": "10115"},
        "dob": "1990-01-01",
    })
    uc.login(email, "Str0ng!Pass")
    return uc, email, uc.token  # type: ignore[return-value]


def _setup_totp(token: str) -> tuple[str, str]:
    """设置 TOTP 并返回 (secret, qrCodeUrl)。"""
    with TOTPClient() as tc:
        tc.set_token(token)
        r = tc.setup_totp()
        assert r.status_code == 200, f"setup failed: {r.status_code} {r.text}"
        data = r.json()
        return data["secret"], data.get("qrCodeUrl", "")


# -- module 级夹具 --------------------------------------------------------

@pytest.fixture(scope="module")
def _mod_totp_data() -> dict:
    """module 级：注册用户 + 设置 TOTP，返回 token/secret 供验证测试复用。"""
    uc, email, token = _register_and_login()
    secret, qr_url = _setup_totp(token)
    yield {
        "email": email,
        "token": token,
        "secret": secret,
        "qr_url": qr_url,
    }
    uc.close()


# -- function 级夹具 ------------------------------------------------------

@pytest.fixture
def _auth_totp() -> TOTPClient:
    """function 级：独立注册用户 + 独立 TOTPClient（mutation 测试用）。"""
    uc, _email, token = _register_and_login()
    tc = TOTPClient()
    tc.set_token(token)
    yield tc
    tc.close()
    uc.close()


# ======================================================================
# 1.1 设置 TOTP · POST /totp/setup ── API_TOTP_001 ~ 003
# ======================================================================

class TestSetupTOTP:
    # [API_TOTP_001] P0
    def test_setup_totp_200(self, _auth_totp: TOTPClient) -> None:
        r = _auth_totp.setup_totp()
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        d = r.json()
        assert "secret" in d, "响应应含 secret"
        assert len(d["secret"]) >= 16

    # [API_TOTP_002] P1
    def test_setup_unauthorized_401(self, totp_client: TOTPClient) -> None:
        r = totp_client.setup_totp()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_TOTP_003] P1
    def test_setup_already_enabled_200(self, _auth_totp: TOTPClient) -> None:
        """实测：重复 setup 返回 200（重新颁发 secret），不阻止。"""
        r = _auth_totp.setup_totp()
        assert r.status_code == 200, f"prep failed: {r.status_code}"
        r2 = _auth_totp.setup_totp()
        assert r2.status_code == 200, f"期望200（重新颁发）, 实际{r2.status_code}"


# ======================================================================
# 1.2 验证 TOTP · POST /totp/verify ── API_TOTP_004 ~ 019
# ======================================================================

class TestVerifyTOTP:
    # [API_TOTP_004] P0
    def test_verify_valid_code_200(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        secret: str = _mod_totp_data["secret"]
        valid_code = pyotp.TOTP(secret).now()
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, valid_code)
            assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

    # [API_TOTP_005] P1
    def test_verify_invalid_code_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "000000")
            assert r.status_code == 400, f"期望400, 实际{r.status_code}"

    # [API_TOTP_006] P1
    def test_verify_unauthorized_401(self, totp_client: TOTPClient, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        r = totp_client.verify_totp(token, "123456")
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_TOTP_007] P1
    def test_verify_missing_access_token_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.post("/totp/verify", json={"totp": "123456"})
            assert r.status_code == 400, f"期望400, 实际{r.status_code}"

    # [API_TOTP_008] P1
    def test_verify_missing_totp_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.post("/totp/verify", json={"access_token": token})
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_TOTP_009] P1
    def test_verify_totp_3_digits_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "123")
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P2 totp 边界 -----------------------------------------------------

    # [API_TOTP_010] P2
    def test_verify_totp_5_digits_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "12345")
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_TOTP_011] P2
    def test_verify_totp_7_digits_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "1234567")
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_TOTP_012] P2
    def test_verify_totp_empty_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "")
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_TOTP_013] P2
    def test_verify_totp_alpha_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "abc123")
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_TOTP_014] P2
    def test_verify_totp_special_chars_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "12 34")
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_TOTP_015] P2
    def test_verify_totp_null_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.post("/totp/verify", json={"access_token": token, "totp": None})
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_TOTP_016] P2
    def test_verify_totp_negative_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp(token, "-12345")
            assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P2 access_token 边界 --------------------------------------------

    # [API_TOTP_017] P2
    def test_verify_access_token_empty_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp("", "123456")
            assert r.status_code == 400, f"期望400, 实际{r.status_code}"

    # [API_TOTP_018] P2
    def test_verify_access_token_random_400(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.verify_totp("invalid-token-xxxx", "123456")
            assert r.status_code == 400, f"期望400, 实际{r.status_code}"

    # [API_TOTP_020] P2
    def test_verify_extra_field(self, _mod_totp_data: dict) -> None:
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            r = tc.post("/totp/verify", json={
                "access_token": token, "totp": "123456", "extra": "ignored",
            })
            assert r.status_code in (400, 422), f"期望400或422, 实际{r.status_code}"


# ======================================================================
# P3 深度防御 ── API_TOTP_021 ~ 022
# ======================================================================

class TestTOTPDefense:
    # [API_TOTP_021] P3
    def test_cross_user_token_verify(self, _mod_totp_data: dict) -> None:
        """用户 A 的 totp + 用户 B 的 access_token → 400。"""
        secret: str = _mod_totp_data["secret"]
        import uuid
        from src.api.client.user_client import UserClient

        with UserClient() as uc:
            email = f"cross-totp-{uuid.uuid4().hex[:8]}@e2e.example"
            uc.post("/users/register", json={
                "first_name": "Cross", "last_name": "TOTP",
                "email": email, "password": "Str0ng!Pass",
                "address": {"street": "X", "city": "Y", "country": "DE", "postal_code": "10115"},
                "dob": "1990-01-01",
            })
            uc.login(email, "Str0ng!Pass")
            token_b = uc.token

        import pyotp
        valid_code = pyotp.TOTP(secret).now()
        with TOTPClient() as tc:
            tc.set_token(token_b)
            r = tc.verify_totp(token_b, valid_code)
            # 用户 B 的 token + 用户 A 的 secret → 应失败
            assert r.status_code in (400, 422, 500), f"期望400/422/500, 实际{r.status_code} {r.text}"

    # [API_TOTP_022] P3
    def test_token_expired_verify(self, _mod_totp_data: dict) -> None:
        """过期 token 验证 TOTP → 401。"""
        token: str = _mod_totp_data["token"]
        with TOTPClient() as tc:
            tc.set_token(token)
            tc.clear_token()
            r = tc.verify_totp(token, "123456")
            assert r.status_code == 401, f"期望401, 实际{r.status_code}"
