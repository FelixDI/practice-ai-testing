"""Report 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class ReportClient(BaseClient):
    """Report（销售报表）API 客户端。"""

    def total_sales_per_country(self) -> Any:
        """各国销售总额。GET /reports/total-sales-per-country → 200"""
        return self.get("/reports/total-sales-per-country")

    def top10_purchased_products(self) -> Any:
        """热销商品 Top10。GET /reports/top10-purchased-products → 200"""
        return self.get("/reports/top10-purchased-products")

    def top10_best_selling_categories(self) -> Any:
        """热销分类 Top10。GET /reports/top10-best-selling-categories → 200"""
        return self.get("/reports/top10-best-selling-categories")

    def total_sales_of_years(self, years: list[str] | None = None) -> Any:
        """各年度销售总额。GET /reports/total-sales-of-years → 200"""
        params = {"years": years} if years else None
        return self.get("/reports/total-sales-of-years", params=params)

    def average_sales_per_month(self, year: int | None = None) -> Any:
        """月均销售额。GET /reports/average-sales-per-month → 200"""
        params = {"year": year} if year is not None else None
        return self.get("/reports/average-sales-per-month", params=params)

    def average_sales_per_week(self, year: int | None = None) -> Any:
        """周均销售额。GET /reports/average-sales-per-week → 200"""
        params = {"year": year} if year is not None else None
        return self.get("/reports/average-sales-per-week", params=params)

    def customers_by_country(self) -> Any:
        """各国客户分布。GET /reports/customers-by-country → 200"""
        return self.get("/reports/customers-by-country")
