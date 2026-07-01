"""Contact 模块 API 客户端。"""

from __future__ import annotations
from typing import Any
from src.api.client.base import BaseClient


class ContactClient(BaseClient):
    """Contact（留言）资源 API 客户端。"""

    def send_message(self, data: dict[str, Any]) -> Any:
        """提交留言。POST /messages → 200"""
        return self.post("/messages", json=data)

    def get_messages(self, page: int | None = None) -> Any:
        """获取留言列表。GET /messages → 200"""
        params = {"page": page} if page is not None else None
        return self.get("/messages", params=params)

    def get_message(self, message_id: str) -> Any:
        """获取指定留言。GET /messages/{messageId} → 200"""
        return self.get(f"/messages/{message_id}")

    def reply_message(self, message_id: str, data: dict[str, Any]) -> Any:
        """回复留言。POST /messages/{messageId}/reply → 200"""
        return self.post(f"/messages/{message_id}/reply", json=data)

    def update_message_status(self, message_id: str, status: str) -> Any:
        """更新留言状态。PUT /messages/{messageId}/status → 200"""
        return self.put(f"/messages/{message_id}/status", json={"status": status})

    def attach_file(self, message_id: str, file_path: str) -> Any:
        """上传附件。POST /messages/{messageId}/attach-file → 200"""
        with open(file_path, "rb") as f:
            return self.post(
                f"/messages/{message_id}/attach-file",
                files={"file": f},
                headers={"Content-Type": None},  # let requests set multipart
            )
