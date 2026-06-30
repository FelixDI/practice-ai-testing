"""User 模块 API 客户端。

封装所有 /users 相关接口：
- 注册 / 登录 / 登出 / 刷新 Token
- 获取 / 更新 / 部分更新 / 删除用户
- 搜索用户 / 忘记密码 / 修改密码
"""

from __future__ import annotations

from typing import Any

from src.api.client.base import BaseClient


class UserClient(BaseClient):
    """User 资源 API 客户端。"""

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def register(self, data: dict[str, Any]) -> dict[str, Any]:
        """注册新用户。POST /users/register → 201"""
        response = self.post("/users/register", json=data)
        return response.json()

    def login(self, email: str, password: str) -> dict[str, Any]:
        """登录。POST /users/login → 200，返回 access_token / token_type / expires_in"""
        response = self.post("/users/login", json={"email": email, "password": password})
        data: dict[str, Any] = response.json()
        # 登录成功后自动设置 Token
        if "access_token" in data:
            self.set_token(data["access_token"])
        return data

    def login_and_get_token(self, email: str, password: str) -> str:
        """登录并返回 access_token。"""
        data = self.login(email, password)
        return data["access_token"]

    def logout(self) -> requests.Response:
        """登出。GET /users/logout"""
        response = self.get("/users/logout")
        self.clear_token()
        return response

    def refresh_token(self) -> dict[str, Any]:
        """刷新 Token。GET /users/refresh → 200"""
        response = self.get("/users/refresh")
        return response.json()

    # ------------------------------------------------------------------
    # Password management
    # ------------------------------------------------------------------

    def forgot_password(self, email: str) -> dict[str, Any]:
        """忘记密码。POST /users/forgot-password → 200"""
        response = self.post("/users/forgot-password", json={"email": email})
        return response.json()

    def change_password(
        self,
        current_password: str,
        new_password: str,
        new_password_confirmation: str,
    ) -> dict[str, Any]:
        """修改密码。POST /users/change-password → 200"""
        response = self.post("/users/change-password", json={
            "current_password": current_password,
            "new_password": new_password,
            "new_password_confirmation": new_password_confirmation,
        })
        return response.json()

    # ------------------------------------------------------------------
    # User CRUD
    # ------------------------------------------------------------------

    def get_me(self) -> dict[str, Any]:
        """获取当前登录用户信息。GET /users/me → 200"""
        response = self.get("/users/me")
        return response.json()

    def get_users(self, page: int = 1) -> dict[str, Any]:
        """获取用户列表。GET /users?page=<page> → 200"""
        response = self.get("/users", params={"page": page})
        return response.json()

    def get_user(self, user_id: str) -> dict[str, Any]:
        """获取指定用户。GET /users/{userId} → 200"""
        response = self.get(f"/users/{user_id}")
        return response.json()

    def update_user(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """全量更新用户。PUT /users/{userId} → 200"""
        response = self.put(f"/users/{user_id}", json=data)
        return response.json()

    def patch_user(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """部分更新用户。PATCH /users/{userId} → 200"""
        response = self.patch(f"/users/{user_id}", json=data)
        return response.json()

    def delete_user(self, user_id: str) -> requests.Response:
        """删除用户。DELETE /users/{userId} → 204 or 200"""
        response = self.delete(f"/users/{user_id}")
        return response

    def search_users(self, query: str, page: int = 1) -> dict[str, Any]:
        """搜索用户。GET /users/search?q=<query>&page=<page> → 200"""
        response = self.get("/users/search", params={"q": query, "page": page})
        return response.json()
