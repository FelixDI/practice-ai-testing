"""Payment 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class PaymentClient(BaseClient):
    """Payment 资源 API 客户端。"""

    def check_payment(self, payment_method: str, payment_details: dict[str, Any]) -> Any:
        """支付校验。POST /payment/check → 200"""
        return self.post("/payment/check", json={
            "payment_method": payment_method,
            "payment_details": payment_details,
        })
