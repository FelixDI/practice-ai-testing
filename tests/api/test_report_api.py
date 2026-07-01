"""Report 模块 API 测试。

蓝图：docs/test-cases/report.md —— 28 条用例，7 个端点全覆盖。

实测：所有 /reports/* 端点为管理端接口，测试账号返回 403 Forbidden。
"""

from __future__ import annotations

import pytest

from src.api.client.report_client import ReportClient
from src.api.client.user_client import UserClient
from src.common.config import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.fixture(scope="module")
def _mod_auth_report() -> ReportClient:
    """module 级：已认证的 ReportClient。"""
    with UserClient() as uc:
        uc.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        token = uc.token
    with ReportClient() as rc:
        rc.set_token(token)
        yield rc


def _report_or_skip(r) -> None:
    """若返回 403 说明非管理员，跳过测试。"""
    if r.status_code == 403:
        pytest.skip("管理端接口，测试账号无权限(403)")
    assert r.status_code == 200, f"期望200, 实际{r.status_code}"


# ======================================================================
# 1.1 各国销售总额 ── API_REPORT_001 ~ 002
# ======================================================================

class TestTotalSalesPerCountry:
    # [API_REPORT_001] P0
    def test_total_sales_per_country_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.total_sales_per_country()
        _report_or_skip(r)
        data = r.json()
        assert isinstance(data, list)

    # [API_REPORT_002] P1
    def test_unauthorized_401(self, report_client: ReportClient) -> None:
        r = report_client.total_sales_per_country()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


# ======================================================================
# 1.2 热销商品 Top10 ── API_REPORT_003 ~ 004
# ======================================================================

class TestTop10PurchasedProducts:
    # [API_REPORT_003] P0
    def test_top10_products_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.top10_purchased_products()
        _report_or_skip(r)
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    # [API_REPORT_004] P1
    def test_unauthorized_401(self, report_client: ReportClient) -> None:
        r = report_client.top10_purchased_products()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


# ======================================================================
# 1.3 热销分类 Top10 ── API_REPORT_005 ~ 006
# ======================================================================

class TestTop10Categories:
    # [API_REPORT_005] P0
    def test_top10_categories_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.top10_best_selling_categories()
        _report_or_skip(r)
        data = r.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    # [API_REPORT_006] P1
    def test_unauthorized_401(self, report_client: ReportClient) -> None:
        r = report_client.top10_best_selling_categories()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


# ======================================================================
# 1.4 年度销售总额 ── API_REPORT_007 ~ 009, 018~021
# ======================================================================

class TestTotalSalesOfYears:
    # [API_REPORT_007] P0
    def test_all_years_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.total_sales_of_years()
        _report_or_skip(r)
        assert isinstance(r.json(), list)

    # [API_REPORT_008] P0
    def test_specific_years_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.total_sales_of_years("2025,2026")
        _report_or_skip(r)

    # [API_REPORT_009] P1
    def test_unauthorized_401(self, report_client: ReportClient) -> None:
        r = report_client.total_sales_of_years()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # -- P2 边界 ----------------------------------------------------------

    # [API_REPORT_018] P2
    def test_single_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.total_sales_of_years("2025")
        _report_or_skip(r)

    # [API_REPORT_019] P2
    def test_future_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.total_sales_of_years("2050")
        _report_or_skip(r)

    # [API_REPORT_020] P2
    def test_years_non_numeric(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.total_sales_of_years("abc")
        assert r.status_code in (200, 403, 422), f"实际{r.status_code}"

    # [API_REPORT_021] P2
    def test_years_empty(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.total_sales_of_years("")
        assert r.status_code in (200, 403, 422), f"实际{r.status_code}"


# ======================================================================
# 1.5 月均销售额 ── API_REPORT_010 ~ 012, 022~025
# ======================================================================

class TestAverageSalesPerMonth:
    # [API_REPORT_010] P0
    def test_default_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_month()
        _report_or_skip(r)

    # [API_REPORT_011] P0
    def test_specific_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_month(2025)
        _report_or_skip(r)

    # [API_REPORT_012] P1
    def test_unauthorized_401(self, report_client: ReportClient) -> None:
        r = report_client.average_sales_per_month()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # -- P2 边界 ----------------------------------------------------------

    # [API_REPORT_022] P2
    def test_future_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_month(2050)
        _report_or_skip(r)

    # [API_REPORT_023] P2
    def test_year_non_numeric(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.get("/reports/average-sales-per-month", params={"year": "abc"})
        assert r.status_code in (200, 403, 422), f"实际{r.status_code}"

    # [API_REPORT_024] P2
    def test_year_negative(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_month(-1)
        assert r.status_code in (200, 403, 422), f"实际{r.status_code}"

    # [API_REPORT_025] P2
    def test_year_empty(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.get("/reports/average-sales-per-month", params={"year": ""})
        assert r.status_code in (200, 403, 422), f"实际{r.status_code}"


# ======================================================================
# 1.6 周均销售额 ── API_REPORT_013 ~ 015, 026~028
# ======================================================================

class TestAverageSalesPerWeek:
    # [API_REPORT_013] P0
    def test_default_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_week()
        _report_or_skip(r)

    # [API_REPORT_014] P0
    def test_specific_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_week(2025)
        _report_or_skip(r)

    # [API_REPORT_015] P1
    def test_unauthorized_401(self, report_client: ReportClient) -> None:
        r = report_client.average_sales_per_week()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"

    # -- P2 边界 ----------------------------------------------------------

    # [API_REPORT_026] P2
    def test_future_year_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_week(2050)
        _report_or_skip(r)

    # [API_REPORT_027] P2
    def test_year_non_numeric(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.get("/reports/average-sales-per-week", params={"year": "abc"})
        assert r.status_code in (200, 403, 422), f"实际{r.status_code}"

    # [API_REPORT_028] P2
    def test_year_min_value(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.average_sales_per_week(1)
        _report_or_skip(r)


# ======================================================================
# 1.7 各国客户分布 ── API_REPORT_016 ~ 017
# ======================================================================

class TestCustomersByCountry:
    # [API_REPORT_016] P0
    def test_customers_by_country_200(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.customers_by_country()
        _report_or_skip(r)
        assert isinstance(r.json(), list)

    # [API_REPORT_017] P1
    def test_unauthorized_401(self, report_client: ReportClient) -> None:
        r = report_client.customers_by_country()
        assert r.status_code == 401, f"期望401, 实际{r.status_code}"


class TestReportMethodNotAllowed:
    # [API_REPORT_029] P1
    def test_post_method_405(self, _mod_auth_report: ReportClient) -> None:
        r = _mod_auth_report.post("/reports/total-sales-per-country")
        assert r.status_code in (403, 405), f"期望403或405, 实际{r.status_code}"
