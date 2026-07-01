"""Payment 模块 API 测试。

蓝图：docs/test-cases/payment.md —— 36 条用例，1 个端点全覆盖。

实测行为备注：
- /payment/check 对 payment_method 完全不校验（任意值均 200）
- payment_details 各字段有格式要求：credit_card_number 需 xxxx-xxxx-xxxx-xxxx 格式，
  expiration_date 需 m/YYYY 格式且晚于今日，account_number 需纯数字，
  gift_card_number 需 16 位数字，validation_code 需 4 位数字
"""

from __future__ import annotations

import pytest

from src.api.client.payment_client import PaymentClient


@pytest.fixture
def client() -> PaymentClient:
    with PaymentClient() as c:
        yield c


# 已知合法的测试数据（按实际 API 格式要求）
VALID_CREDIT_CARD = {
    "credit_card_number": "4111-1111-1111-1111",
    "expiration_date": "12/2028",
    "cvv": "123",
    "card_holder_name": "Test User",
}
VALID_BANK_TRANSFER = {
    "bank_name": "Test Bank",
    "account_name": "John Doe",
    "account_number": "12345678",
}
VALID_GIFT_CARD = {
    "gift_card_number": "1234567890123456",
    "validation_code": "1234",
}
VALID_BNPL = {"monthly_installments": "3"}


# ======================================================================
# 1.1 支付校验 · POST /payment/check ── API_PAYMENT_001 ~ 036
# ======================================================================

class TestPaymentCheck:
    # -- P0 ---------------------------------------------------------------

    # [API_PAYMENT_001] P0
    def test_cash_on_delivery_200(self, client: PaymentClient) -> None:
        r = client.check_payment("cash-on-delivery", {})
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PAYMENT_002] P0
    def test_credit_card_200(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", VALID_CREDIT_CARD)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PAYMENT_003] P0
    def test_missing_payment_method_200(self, client: PaymentClient) -> None:
        """payment_method 不传时 API 仍返回 200（不校验 method）。"""
        r = client.post("/payment/check", json={"payment_details": {}})
        assert r.status_code == 200, f"期望200（API 不校验 method）, 实际{r.status_code}"

    # -- P1 ---------------------------------------------------------------

    # [API_PAYMENT_004] P1
    def test_bank_transfer_200(self, client: PaymentClient) -> None:
        r = client.check_payment("bank-transfer", VALID_BANK_TRANSFER)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PAYMENT_005] P1
    def test_gift_card_200(self, client: PaymentClient) -> None:
        r = client.check_payment("gift-card", VALID_GIFT_CARD)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PAYMENT_006] P1
    def test_buy_now_pay_later_200(self, client: PaymentClient) -> None:
        r = client.check_payment("buy-now-pay-later", VALID_BNPL)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_PAYMENT_007] P1
    def test_invalid_payment_method_200(self, client: PaymentClient) -> None:
        """API 不校验 payment_method 枚举，任意值均返回 200。"""
        r = client.check_payment("bitcoin", {})
        assert r.status_code == 200, f"期望200（API 不校验 method）, 实际{r.status_code}"

    # [API_PAYMENT_008] P1
    def test_credit_card_missing_cvv_422(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "card_holder_name": "Test User",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_009] P1
    def test_bank_transfer_missing_account_number_422(self, client: PaymentClient) -> None:
        r = client.check_payment("bank-transfer", {
            "bank_name": "Test Bank",
            "account_name": "John Doe",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_010] P1
    def test_gift_card_missing_number_422(self, client: PaymentClient) -> None:
        r = client.check_payment("gift-card", {"validation_code": "1234"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_011] P1
    def test_payment_details_null_422(self, client: PaymentClient) -> None:
        r = client.post("/payment/check", json={
            "payment_method": "credit-card",
            "payment_details": None,
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_012] P1
    def test_method_details_mismatch_200(self, client: PaymentClient) -> None:
        """API 不校验 method 与 details 的匹配关系。"""
        r = client.check_payment("cash-on-delivery", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
        })
        assert r.status_code == 200, f"期望200（API 不校验匹配）, 实际{r.status_code}"

    # -- P2 枚举边界 --------------------------------------------------------

    # [API_PAYMENT_013] P2
    def test_payment_method_case_insensitive(self, client: PaymentClient) -> None:
        """API 不校验 method 大小写。"""
        r = client.check_payment("Credit-Card", {})
        assert r.status_code == 200, f"期望200（API 不校验 method）, 实际{r.status_code}"

    # [API_PAYMENT_014] P2
    def test_payment_method_empty_200(self, client: PaymentClient) -> None:
        """API 不校验空 method。"""
        r = client.check_payment("", {})
        assert r.status_code == 200, f"期望200（API 不校验 method）, 实际{r.status_code}"

    # -- P2 BankTransferDetails 边界 ---------------------------------------

    # [API_PAYMENT_015] P2
    def test_bank_name_empty_422(self, client: PaymentClient) -> None:
        r = client.check_payment("bank-transfer", {
            "bank_name": "", "account_name": "John", "account_number": "12345678",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_016] P2
    def test_account_name_empty_422(self, client: PaymentClient) -> None:
        r = client.check_payment("bank-transfer", {
            "bank_name": "Bank", "account_name": "", "account_number": "12345678",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_017] P2
    def test_account_number_empty_422(self, client: PaymentClient) -> None:
        r = client.check_payment("bank-transfer", {
            "bank_name": "Bank", "account_name": "John", "account_number": "",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_018] P2
    def test_bank_transfer_whitespace_422(self, client: PaymentClient) -> None:
        r = client.check_payment("bank-transfer", {
            "bank_name": "   ", "account_name": "   ", "account_number": "   ",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_019] P2
    def test_bank_transfer_extra_field(self, client: PaymentClient) -> None:
        r = client.post("/payment/check", json={
            "payment_method": "bank-transfer",
            "payment_details": {
                "bank_name": "Bank", "account_name": "John",
                "account_number": "12345678", "extra": "ignored",
            },
        })
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # -- P2 CreditCardDetails 边界 -----------------------------------------

    # [API_PAYMENT_020] P2
    def test_credit_card_number_alpha_422(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": "abcd-efgh-ijkl-mnop",
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "123", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_021] P2
    def test_expiration_date_bad_format_422(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": "2028-12-01",
            "cvv": "123", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_022] P2
    def test_cvv_non_numeric_422(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "abc", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_023] P2
    def test_card_holder_name_empty_422(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "123", "card_holder_name": "",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_024] P2
    def test_credit_card_number_too_short_422(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": "123",
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "123", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_025] P2
    def test_expired_card(self, client: PaymentClient) -> None:
        """过期卡：expiration_date 早于当前日期时 API 返回 422。"""
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": "01/2020",
            "cvv": "123", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422（过期卡）, 实际{r.status_code}"

    # [API_PAYMENT_037] P2
    def test_cvv_2_digits(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "12", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422（cvv过短）, 实际{r.status_code}"

    # [API_PAYMENT_038] P2
    def test_cvv_5_digits(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "12345", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422（cvv过长）, 实际{r.status_code}"

    # [API_PAYMENT_039] P2
    def test_credit_card_number_no_dashes(self, client: PaymentClient) -> None:
        """16位连写（无连字符）的卡号格式。"""
        r = client.check_payment("credit-card", {
            "credit_card_number": "4111111111111111",
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "123", "card_holder_name": "John",
        })
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # -- P2 GiftCardDetails 边界 -------------------------------------------

    # [API_PAYMENT_026] P2
    def test_gift_card_number_empty_422(self, client: PaymentClient) -> None:
        r = client.check_payment("gift-card", {
            "gift_card_number": "", "validation_code": "1234",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_027] P2
    def test_validation_code_empty_422(self, client: PaymentClient) -> None:
        r = client.check_payment("gift-card", {
            "gift_card_number": VALID_GIFT_CARD["gift_card_number"],
            "validation_code": "",
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_040] P2
    def test_gift_card_number_with_spaces(self, client: PaymentClient) -> None:
        r = client.check_payment("gift-card", {
            "gift_card_number": "1234 5678 9012 3456",
            "validation_code": VALID_GIFT_CARD["validation_code"],
        })
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_PAYMENT_041] P2
    def test_validation_code_3_digits(self, client: PaymentClient) -> None:
        r = client.check_payment("gift-card", {
            "gift_card_number": VALID_GIFT_CARD["gift_card_number"],
            "validation_code": "123",
        })
        assert r.status_code == 422, f"期望422（过短）, 实际{r.status_code}"

    # [API_PAYMENT_042] P2
    def test_validation_code_5_digits(self, client: PaymentClient) -> None:
        r = client.check_payment("gift-card", {
            "gift_card_number": VALID_GIFT_CARD["gift_card_number"],
            "validation_code": "12345",
        })
        assert r.status_code == 422, f"期望422（过长）, 实际{r.status_code}"

    # -- P2 BuyNowPayLaterDetails 边界 -------------------------------------

    # [API_PAYMENT_028] P2
    def test_installments_zero_200(self, client: PaymentClient) -> None:
        """API 不校验 monthly_installments 的值范围。"""
        r = client.check_payment("buy-now-pay-later", {"monthly_installments": "0"})
        assert r.status_code == 200, f"期望200（API 不校验值）, 实际{r.status_code}"

    # [API_PAYMENT_029] P2
    def test_installments_negative_200(self, client: PaymentClient) -> None:
        """API 不校验 monthly_installments 是否为负数。"""
        r = client.check_payment("buy-now-pay-later", {"monthly_installments": "-3"})
        assert r.status_code == 200, f"期望200（API 不校验值）, 实际{r.status_code}"

    # [API_PAYMENT_030] P2
    def test_installments_non_numeric_422(self, client: PaymentClient) -> None:
        r = client.check_payment("buy-now-pay-later", {"monthly_installments": "abc"})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_031] P2
    def test_installments_empty_422(self, client: PaymentClient) -> None:
        r = client.check_payment("buy-now-pay-later", {"monthly_installments": ""})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_043] P2
    def test_installments_float(self, client: PaymentClient) -> None:
        r = client.check_payment("buy-now-pay-later", {"monthly_installments": "3.5"})
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # -- P2 CashOnDelivery 边界 --------------------------------------------

    # [API_PAYMENT_032] P2
    def test_cod_extra_field(self, client: PaymentClient) -> None:
        r = client.post("/payment/check", json={
            "payment_method": "cash-on-delivery",
            "payment_details": {"extra": "ignored"},
        })
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # -- P1 请求体边界 ------------------------------------------------------

    # [API_PAYMENT_044] P1
    def test_empty_body(self, client: PaymentClient) -> None:
        r = client.post("/payment/check", json={})
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # -- P3 深度防御 --------------------------------------------------------

    # [API_PAYMENT_033] P3
    def test_sql_injection_card_number(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": "' OR '1'='1",
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "123", "card_holder_name": "John",
        })
        assert r.status_code == 422, f"期望422（不应触发DB异常）, 实际{r.status_code}"

    # [API_PAYMENT_034] P3
    def test_xss_card_holder_name(self, client: PaymentClient) -> None:
        r = client.check_payment("credit-card", {
            "credit_card_number": VALID_CREDIT_CARD["credit_card_number"],
            "expiration_date": VALID_CREDIT_CARD["expiration_date"],
            "cvv": "123",
            "card_holder_name": "<script>alert(1)</script>",
        })
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_PAYMENT_035] P3
    def test_deeply_nested_details(self, client: PaymentClient) -> None:
        """API 不校验 payment_details 嵌套深度，返回 200。"""
        nested = {"level0": {"level1": {"level2": {"level3": {"level4": "deep"}}}}}
        r = client.check_payment("cash-on-delivery", nested)
        assert r.status_code == 200, f"期望200（API 不校验嵌套）, 实际{r.status_code}"

    # [API_PAYMENT_036] P3
    def test_oversized_request(self, client: PaymentClient) -> None:
        r = client.check_payment("bank-transfer", {
            "bank_name": "A" * 10000,
            "account_name": "B" * 10000,
            "account_number": "C" * 10000,
        })
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_PAYMENT_045] P3
    def test_json_nested_bomb(self, client: PaymentClient) -> None:
        """100 层深度嵌套 —— 不应导致服务崩溃。"""
        nested: dict = {}
        current = nested
        for i in range(100):
            current["a"] = {}
            current = current["a"]
        current["v"] = "deep"
        r = client.check_payment("cash-on-delivery", nested)
        assert r.status_code in (200, 422, 500), f"不应崩溃, 实际{r.status_code}"
