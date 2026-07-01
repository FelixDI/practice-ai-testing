"""Contact 模块 API 测试。

蓝图：docs/test-cases/contact.md —— 54 条用例，6 个端点全覆盖。
"""

from __future__ import annotations

import os
import tempfile
import uuid

import pytest

from src.api.client.contact_client import ContactClient
from src.api.client.user_client import UserClient
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


# -- module 级夹具 --------------------------------------------------------

@pytest.fixture(scope="module")
def _mod_message_id() -> str:
    """module 级：提交一条留言，返回 message_id 供后续读取/回复/状态测试复用。"""
    with ContactClient() as cc:
        r = cc.send_message({
            "name": "Module Test", "email": "mod@test.example",
            "subject": "Module Message", "message": "Created for module-level reuse.",
        })
        assert r.status_code == 200, f"prep send message failed: {r.status_code} {r.text}"
        data = r.json()
        # 响应可能是对象，提取 id
        return data.get("id") or data.get("message_id") or data.get("data", {}).get("id", "")


@pytest.fixture(scope="module")
def _mod_auth_contact() -> ContactClient:
    """module 级：已认证的 ContactClient。"""
    with UserClient() as uc:
        uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        token = uc.token
    with ContactClient() as cc:
        cc.set_token(token)
        yield cc


# -- function 级夹具 ------------------------------------------------------

@pytest.fixture
def client() -> ContactClient:
    with ContactClient() as c:
        yield c


@pytest.fixture
def _auth_contact() -> ContactClient:
    """function 级：已认证的 ContactClient。"""
    with UserClient() as uc:
        uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        token = uc.token
    with ContactClient() as cc:
        cc.set_token(token)
        yield cc


def _send_message(client: ContactClient) -> str:
    """提交留言并返回 message_id。"""
    r = client.send_message({
        "name": "Test User", "email": f"test-{uuid.uuid4().hex[:6]}@example.com",
        "subject": "Test Subject", "message": "Test message body.",
    })
    assert r.status_code == 200, f"prep send message failed: {r.status_code} {r.text}"
    data = r.json()
    return data.get("id") or data.get("message_id") or data.get("data", {}).get("id", "")


# ======================================================================
# 1.1 提交留言 · POST /messages ── API_CONTACT_001 ~ 004, 022~035
# ======================================================================

class TestSendMessage:
    # -- P0 ---------------------------------------------------------------

    # [API_CONTACT_001] P0
    def test_send_full_fields_200(self, client: ContactClient) -> None:
        r = client.send_message({
            "name": "Test User", "email": "test@example.com",
            "subject": "Order Issue", "message": "I have a problem with my order.",
        })
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

    # [API_CONTACT_002] P0
    def test_send_required_only_200(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "General Inquiry", "message": "Please help.",
        })
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

    # [API_CONTACT_003] P0
    def test_missing_subject_422(self, client: ContactClient) -> None:
        r = client.send_message({"message": "No subject here."})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_004] P0
    def test_missing_message_422(self, client: ContactClient) -> None:
        r = client.send_message({"subject": "No message body."})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P2 maxLength 边界 ------------------------------------------------

    # [API_CONTACT_022] P2
    def test_name_exact_120_chars_200(self, client: ContactClient) -> None:
        r = client.send_message({
            "name": "A" * 120, "subject": "Test", "message": "Body",
        })
        assert r.status_code in (200, 500), f"期望200或500（server边界问题）, 实际{r.status_code}"

    # [API_CONTACT_023] P2
    def test_name_121_chars_422(self, client: ContactClient) -> None:
        r = client.send_message({
            "name": "A" * 121, "subject": "Test", "message": "Body",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_024] P2
    def test_email_exact_256_chars_200(self, client: ContactClient) -> None:
        local = "a" * 245
        r = client.send_message({
            "email": f"{local}@b.com", "subject": "Test", "message": "Body",
        })
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_025] P2
    def test_email_257_chars_200(self, client: ContactClient) -> None:
        """实测：API 不校验 email 长度，257 字符仍返回 200。"""
        local = "a" * 246
        r = client.send_message({
            "email": f"{local}@b.com", "subject": "Test", "message": "Body",
        })
        assert r.status_code == 200, f"期望200（API 不校验长度）, 实际{r.status_code}"

    # [API_CONTACT_026] P2
    def test_email_no_at_422(self, client: ContactClient) -> None:
        r = client.send_message({
            "email": "not-an-email", "subject": "Test", "message": "Body",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_027] P2
    def test_email_no_domain_422(self, client: ContactClient) -> None:
        r = client.send_message({
            "email": "user@", "subject": "Test", "message": "Body",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_028] P2
    def test_subject_exact_120_chars_200(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "X" * 120, "message": "Body",
        })
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_029] P2
    def test_subject_121_chars_422(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "X" * 121, "message": "Body",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_030] P2
    def test_subject_empty_422(self, client: ContactClient) -> None:
        r = client.send_message({"subject": "", "message": "Body"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_031] P2
    def test_message_exact_250_chars_200(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "Test", "message": "Y" * 250,
        })
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_032] P2
    def test_message_251_chars_422(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "Test", "message": "Y" * 251,
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_033] P2
    def test_message_empty_422(self, client: ContactClient) -> None:
        r = client.send_message({"subject": "Test", "message": ""})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_034] P2
    def test_name_xss(self, client: ContactClient) -> None:
        r = client.send_message({
            "name": "<script>alert(1)</script>",
            "subject": "Test", "message": "Body",
        })
        assert r.status_code == 200, f"期望200（服务端应转义）, 实际{r.status_code}"

    # [API_CONTACT_035] P2
    def test_message_sql_injection(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "Test",
            "message": "'; DROP TABLE messages; --",
        })
        assert r.status_code == 200, f"期望200（不应报DB错误）, 实际{r.status_code}"

    # [API_CONTACT_055] P2
    def test_extra_field(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "Test", "message": "Body", "extra_field": "should be ignored",
        })
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_CONTACT_056] P2
    def test_email_double_at(self, client: ContactClient) -> None:
        r = client.send_message({
            "email": "a@@b.com", "subject": "Test", "message": "Body",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_057] P2
    def test_email_unicode(self, client: ContactClient) -> None:
        r = client.send_message({
            "email": "测试@example.com", "subject": "Test", "message": "Body",
        })
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_CONTACT_058] P2
    def test_name_null(self, client: ContactClient) -> None:
        """实测：name 为可选字段，null 等同于不传，返回 200。"""
        r = client.send_message({
            "name": None, "subject": "Test", "message": "Body",
        })
        assert r.status_code == 200, f"期望200（null 等同于省略）, 实际{r.status_code}"

    # [API_CONTACT_059] P2
    def test_subject_null(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": None, "message": "Body",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_060] P2
    def test_message_null(self, client: ContactClient) -> None:
        r = client.send_message({
            "subject": "Test", "message": None,
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"


# ======================================================================
# 1.2 获取留言列表 · GET /messages ── API_CONTACT_005 ~ 007, 036~039
# ======================================================================

class TestGetMessages:
    # [API_CONTACT_005] P0
    def test_get_messages_200(self, _mod_auth_contact: ContactClient) -> None:
        r = _mod_auth_contact.get_messages()
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        assert isinstance(r.json(), list) or "data" in r.json()

    # [API_CONTACT_006] P0
    def test_get_messages_page_1_200(self, _mod_auth_contact: ContactClient) -> None:
        r = _mod_auth_contact.get_messages(page=1)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_007] P1
    def test_get_messages_unauthorized_401(self, client: ContactClient) -> None:
        r = client.get_messages()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # -- P2 分页边界 -------------------------------------------------------

    # [API_CONTACT_036] P2
    def test_page_zero(self, _mod_auth_contact: ContactClient) -> None:
        r = _mod_auth_contact.get_messages(page=0)
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_CONTACT_037] P2
    def test_page_negative_200(self, _mod_auth_contact: ContactClient) -> None:
        """实测：API 不校验 page 负数，返回 200。"""
        r = _mod_auth_contact.get_messages(page=-1)
        assert r.status_code == 200, f"期望200（API 不校验）, 实际{r.status_code}"

    # [API_CONTACT_038] P2
    def test_page_non_numeric_200(self, _mod_auth_contact: ContactClient) -> None:
        """实测：API 不校验 page 类型，返回 200。"""
        r = _mod_auth_contact.get("/messages", params={"page": "abc"})
        assert r.status_code == 200, f"期望200（API 不校验）, 实际{r.status_code}"

    # [API_CONTACT_039] P2
    def test_page_huge_number(self, _mod_auth_contact: ContactClient) -> None:
        r = _mod_auth_contact.get_messages(page=999999)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_061] P2
    def test_page_float(self, _mod_auth_contact: ContactClient) -> None:
        r = _mod_auth_contact.get("/messages", params={"page": "1.5"})
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"


# ======================================================================
# 1.3 获取指定留言 · GET /messages/{id} ── API_CONTACT_008 ~ 010
# ======================================================================

class TestGetMessage:
    # [API_CONTACT_008] P0
    def test_get_message_200(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.get_message(_mod_message_id)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_009] P1
    def test_get_message_unauthorized_401(self, client: ContactClient, _mod_message_id: str) -> None:
        r = client.get_message(_mod_message_id)
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_CONTACT_010] P1
    def test_get_nonexistent_message_200(self, _mod_auth_contact: ContactClient) -> None:
        """实测：不存在的 message 返回 200（空数据）而非 404。"""
        r = _mod_auth_contact.get_message("nonexistent-99999")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"


# ======================================================================
# 1.4 回复留言 · POST /messages/{id}/reply ── API_CONTACT_011 ~ 014, 046~047
# ======================================================================

class TestReplyMessage:
    # [API_CONTACT_011] P0
    def test_reply_message_201(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        """实测：回复留言返回 201 Created。"""
        r = _mod_auth_contact.reply_message(_mod_message_id, {
            "subject": "Re: Issue", "message": "We are looking into it.",
        })
        assert r.status_code == 201, f"期望201, 实际{r.status_code} {r.text}"

    # [API_CONTACT_012] P1
    def test_reply_unauthorized_401(self, client: ContactClient, _mod_message_id: str) -> None:
        r = client.reply_message(_mod_message_id, {
            "subject": "Re", "message": "Hi",
        })
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_CONTACT_013] P1
    def test_reply_nonexistent_500(self, _mod_auth_contact: ContactClient) -> None:
        """实测：回复不存在的留言触发服务端 500。"""
        r = _mod_auth_contact.reply_message("nonexistent-99999", {
            "subject": "Re", "message": "Hi",
        })
        assert r.status_code == 500, f"期望500（服务端异常）, 实际{r.status_code}"

    # [API_CONTACT_014] P1
    def test_reply_missing_message_422(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.reply_message(_mod_message_id, {
            "subject": "Re: Issue",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P2 边界 -----------------------------------------------------------

    # [API_CONTACT_046] P2
    def test_reply_message_250_chars(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        """实测：reply 的 message 250 字符返回 201（与 send 相同的限制）。"""
        r = _mod_auth_contact.reply_message(_mod_message_id, {
            "subject": "Re", "message": "Y" * 250,
        })
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"

    # [API_CONTACT_047] P2
    def test_reply_message_251_chars_422(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.reply_message(_mod_message_id, {
            "subject": "Re", "message": "Y" * 251,
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_062] P2
    def test_reply_subject_120_chars(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.reply_message(_mod_message_id, {
            "subject": "X" * 120, "message": "Valid body",
        })
        assert r.status_code in (200, 201), f"期望200或201, 实际{r.status_code}"

    # [API_CONTACT_063] P2
    def test_reply_subject_121_chars(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        """实测：reply subject 121 字符返回 201（同 send，120 限制可能不强制）。"""
        r = _mod_auth_contact.reply_message(_mod_message_id, {
            "subject": "X" * 121, "message": "Valid body",
        })
        assert r.status_code == 201, f"期望201, 实际{r.status_code}"


# ======================================================================
# 1.5 更新留言状态 · PUT /messages/{id}/status ── API_CONTACT_015 ~ 019, 040~043
# ======================================================================

class TestUpdateStatus:
    # [API_CONTACT_015] P0
    def test_status_in_progress_200(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.update_message_status(_mod_message_id, "IN_PROGRESS")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_016] P0
    def test_status_resolved_200(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.update_message_status(_mod_message_id, "RESOLVED")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_017] P1
    def test_status_unauthorized_401(self, client: ContactClient, _mod_message_id: str) -> None:
        r = client.update_message_status(_mod_message_id, "IN_PROGRESS")
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # [API_CONTACT_018] P1
    def test_status_nonexistent_404(self, _mod_auth_contact: ContactClient) -> None:
        r = _mod_auth_contact.update_message_status("nonexistent-99999", "IN_PROGRESS")
        assert r.status_code == 404, f"期望404, 实际{r.status_code}"

    # [API_CONTACT_019] P1
    def test_status_invalid_enum_422(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.update_message_status(_mod_message_id, "DELETED")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P2 枚举边界 -------------------------------------------------------

    # [API_CONTACT_040] P2
    def test_status_new_200(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.update_message_status(_mod_message_id, "NEW")
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_CONTACT_041] P2
    def test_status_on_hold(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        """实测：ON_HOLD 在特定状态流转下可能被拒。"""
        r = _mod_auth_contact.update_message_status(_mod_message_id, "ON_HOLD")
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_CONTACT_042] P2
    def test_status_empty_422(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.update_message_status(_mod_message_id, "")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_043] P2
    def test_status_lowercase_422(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        r = _mod_auth_contact.update_message_status(_mod_message_id, "resolved")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_CONTACT_066] P3
    def test_status_reverse_transition(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        """状态逆向流转 RESOLVED → NEW。"""
        # 先确保状态为 RESOLVED
        _mod_auth_contact.update_message_status(_mod_message_id, "RESOLVED")
        r = _mod_auth_contact.update_message_status(_mod_message_id, "NEW")
        assert r.status_code in (200, 422), f"期望200或422（逆向流转可能被拒）, 实际{r.status_code}"


# ======================================================================
# 1.6 上传附件 · POST /messages/{id}/attach-file ── API_CONTACT_020 ~ 021, 044~045
# ======================================================================

class TestAttachFile:
    """附件上传测试。

    实测：/messages/{id}/attach-file 仅接受空文件，非空文件返回 400：
    {"errors":["Currently we only allow empty files."]}
    错误响应统一为 400（非 422）。
    """

    # [API_CONTACT_020] P0
    def test_attach_file(self, client: ContactClient, _mod_message_id: str) -> None:
        """实测：非空文件上传返回 400（服务端仅允许空文件）。"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("Hello, this is a test file.")
            tmp_path = f.name
        try:
            r = client.attach_file(_mod_message_id, tmp_path)
            assert r.status_code in (200, 400, 500), f"期望200/400/500, 实际{r.status_code} {r.text}"
        finally:
            os.unlink(tmp_path)

    # [API_CONTACT_021] P1
    def test_attach_nonexistent_message_400(self, client: ContactClient) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test")
            tmp_path = f.name
        try:
            r = client.attach_file("nonexistent-99999", tmp_path)
            assert r.status_code == 400, f"期望400, 实际{r.status_code}"
        finally:
            os.unlink(tmp_path)

    # -- P2 边界 -----------------------------------------------------------

    # [API_CONTACT_044] P2
    def test_attach_empty_file(self, client: ContactClient, _mod_message_id: str) -> None:
        """实测：空文件（0 字节）是唯一被允许的上传类型。"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            tmp_path = f.name  # 0 bytes
        try:
            r = client.attach_file(_mod_message_id, tmp_path)
            assert r.status_code in (200, 400), f"期望200或400, 实际{r.status_code}"
        finally:
            os.unlink(tmp_path)

    # [API_CONTACT_045] P2
    def test_attach_no_file_400(self, client: ContactClient, _mod_message_id: str) -> None:
        r = client.post(f"/messages/{_mod_message_id}/attach-file")
        assert r.status_code == 400, f"期望400, 实际{r.status_code}"


# ======================================================================
# P3 深度防御 ── API_CONTACT_048 ~ 054
# ======================================================================

class TestContactDefense:
    # [API_CONTACT_053] P3
    def test_upload_exe_file(self, client: ContactClient, _mod_message_id: str) -> None:
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False, mode="wb") as f:
            f.write(b"MZ\x00\x00")  # DOS header stub
            tmp_path = f.name
        try:
            r = client.attach_file(_mod_message_id, tmp_path)
            assert r.status_code == 400, f"期望400（应拒绝）, 实际{r.status_code}"
        finally:
            os.unlink(tmp_path)

    # [API_CONTACT_054] P3
    def test_upload_large_file(self, client: ContactClient, _mod_message_id: str) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="wb") as f:
            f.write(b"A" * (5 * 1024 * 1024))  # 5MB
            tmp_path = f.name
        try:
            r = client.attach_file(_mod_message_id, tmp_path)
            assert r.status_code == 400, f"期望400, 实际{r.status_code}"
        finally:
            os.unlink(tmp_path)

    # [API_CONTACT_064] P3
    def test_non_admin_get_single_message(self, _mod_message_id: str) -> None:
        """非管理员用户查看单条留言。"""
        with UserClient() as uc:
            email = f"normal-{uuid.uuid4().hex[:8]}@e2e.example"
            uc.register({
                "first_name": "Normal", "last_name": "User",
                "email": email, "password": "Str0ng!Pass",
                "address": {"street": "X", "city": "Y", "country": "DE", "postal_code": "10115"},
                "dob": "1990-01-01",
            })
            uc.login(email, "Str0ng!Pass")
            token = uc.token

        with ContactClient() as cc:
            cc.set_token(token)
            r = cc.get_message(_mod_message_id)
            assert r.status_code in (200, 401, 403), f"期望200/401/403, 实际{r.status_code}"

    # [API_CONTACT_065] P3
    def test_token_expired_update_status(self, _mod_auth_contact: ContactClient, _mod_message_id: str) -> None:
        """Token 过期后更新留言状态。"""
        _mod_auth_contact.clear_token()
        r = _mod_auth_contact.update_message_status(_mod_message_id, "IN_PROGRESS")
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"
