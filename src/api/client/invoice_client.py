"""Invoice 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class InvoiceClient(BaseClient):
    """Invoice 资源 API 客户端。"""

    def get_invoices(self, **params: Any) -> Any:
        return self.get("/invoices", params=params)

    def create_invoice(self, data: dict[str, Any]) -> Any:
        return self.post("/invoices", json=data)

    def create_guest_invoice(self, data: dict[str, Any]) -> Any:
        return self.post("/invoices/guest", json=data)

    def get_invoice(self, invoice_id: str) -> Any:
        return self.get(f"/invoices/{invoice_id}")

    def update_invoice(self, invoice_id: str, data: dict[str, Any]) -> Any:
        return self.put(f"/invoices/{invoice_id}", json=data)

    def patch_invoice(self, invoice_id: str, data: dict[str, Any]) -> Any:
        return self.patch(f"/invoices/{invoice_id}", json=data)

    def update_status(self, invoice_id: str, status: str, message: str | None = None) -> Any:
        body: dict[str, Any] = {"status": status}
        if message:
            body["status_message"] = message
        return self.put(f"/invoices/{invoice_id}/status", json=body)

    def download_pdf(self, invoice_number: str) -> Any:
        return self.get(f"/invoices/{invoice_number}/download-pdf")

    def pdf_status(self, invoice_number: str) -> Any:
        return self.get(f"/invoices/{invoice_number}/download-pdf-status")

    def search_invoices(self, q: str | None = None) -> Any:
        params = {"q": q} if q else None
        return self.get("/invoices/search", params=params)
