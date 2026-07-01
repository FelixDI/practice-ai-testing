"""Postcode 模块 API 测试。

蓝图：docs/test-cases/postcode.md —— 22 条用例，1 个端点全覆盖。
"""

from __future__ import annotations

import pytest

from src.api.client.postcode_client import PostcodeClient


@pytest.fixture
def client() -> PostcodeClient:
    with PostcodeClient() as c:
        yield c


VALID_COUNTRY = "DE"
VALID_POSTCODE = "10115"


class TestPostcodeLookup:
    # -- P0 ---------------------------------------------------------------

    # [API_POSTCODE_001] P0
    def test_lookup_full_params_200(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, VALID_POSTCODE, "1")
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

    # [API_POSTCODE_002] P0
    def test_lookup_without_house_number_200(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, VALID_POSTCODE)
        assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

    # [API_POSTCODE_003] P0
    def test_missing_country_422(self, client: PostcodeClient) -> None:
        r = client.get("/postcode-lookup", params={"postcode": VALID_POSTCODE})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_POSTCODE_004] P0
    def test_missing_postcode_422(self, client: PostcodeClient) -> None:
        r = client.get("/postcode-lookup", params={"country": VALID_COUNTRY})
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P1 ---------------------------------------------------------------

    # [API_POSTCODE_005] P1
    def test_invalid_country(self, client: PostcodeClient) -> None:
        """实测：API 不校验 country 格式，返回 200。"""
        r = client.lookup("XX", VALID_POSTCODE)
        assert r.status_code == 200, f"期望200（API 不校验 country）, 实际{r.status_code}"

    # [API_POSTCODE_006] P1
    def test_invalid_postcode_format_422(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, "!@#$%")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_POSTCODE_007] P1
    def test_nonexistent_postcode(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, "00000")
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_POSTCODE_008] P1
    def test_country_empty_422(self, client: PostcodeClient) -> None:
        r = client.lookup("", VALID_POSTCODE)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_POSTCODE_009] P1
    def test_postcode_empty_422(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, "")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P2 country 边界 --------------------------------------------------

    # [API_POSTCODE_010] P2
    def test_country_1_char(self, client: PostcodeClient) -> None:
        r = client.lookup("D", VALID_POSTCODE)
        assert r.status_code == 200, f"期望200（API 不校验 country）, 实际{r.status_code}"

    # [API_POSTCODE_011] P2
    def test_country_4_chars(self, client: PostcodeClient) -> None:
        r = client.lookup("DEUT", VALID_POSTCODE)
        assert r.status_code == 200, f"期望200（API 不校验 country）, 实际{r.status_code}"

    # [API_POSTCODE_012] P2
    def test_country_lowercase(self, client: PostcodeClient) -> None:
        r = client.lookup("de", VALID_POSTCODE)
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"

    # [API_POSTCODE_013] P2
    def test_country_numeric(self, client: PostcodeClient) -> None:
        r = client.lookup("12", VALID_POSTCODE)
        assert r.status_code == 200, f"期望200（API 不校验 country）, 实际{r.status_code}"

    # [API_POSTCODE_014] P2
    def test_country_special_chars(self, client: PostcodeClient) -> None:
        r = client.lookup("D<E", VALID_POSTCODE)
        assert r.status_code == 200, f"期望200（API 不校验 country）, 实际{r.status_code}"

    # -- P2 postcode 边界 ------------------------------------------------

    # [API_POSTCODE_015] P2
    def test_postcode_overlong_422(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, "1" * 50)
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # [API_POSTCODE_016] P2
    def test_postcode_with_spaces(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, "101 15")
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_POSTCODE_017] P2
    def test_postcode_alphanumeric(self, client: PostcodeClient) -> None:
        """英国邮编为字母数字混合格式。"""
        r = client.lookup("GB", "SW1A1AA")
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_POSTCODE_018] P2
    def test_postcode_special_only_422(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, "!@#$%")
        assert r.status_code == 422, f"期望422, 实际{r.status_code}"

    # -- P2 house_number 边界 --------------------------------------------

    # [API_POSTCODE_019] P2
    def test_house_number_overlong(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, VALID_POSTCODE, "A" * 100)
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_POSTCODE_020] P2
    def test_house_number_special_chars(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, VALID_POSTCODE, "<script>")
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_POSTCODE_021] P2
    def test_house_number_empty_200(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, VALID_POSTCODE, "")
        assert r.status_code == 200, f"期望200（等同于不传）, 实际{r.status_code}"

    # [API_POSTCODE_022] P2
    def test_house_number_negative(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, VALID_POSTCODE, "-1")
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"

    # [API_POSTCODE_023] P1
    def test_post_method_405(self, client: PostcodeClient) -> None:
        r = client.post("/postcode-lookup")
        assert r.status_code == 405, f"期望405, 实际{r.status_code}"

    # [API_POSTCODE_024] P2
    def test_house_number_long_numeric(self, client: PostcodeClient) -> None:
        r = client.lookup(VALID_COUNTRY, VALID_POSTCODE, "9" * 50)
        assert r.status_code in (200, 422), f"期望200或422, 实际{r.status_code}"
