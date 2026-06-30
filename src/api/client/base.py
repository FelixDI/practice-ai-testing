"""API 客户端基类。

封装请求头、鉴权、异常处理与通用 HTTP 方法，
子类仅关注业务接口调用与数据组装。
"""

from __future__ import annotations

from typing import Any

import requests

from src.common.config import API_BASE_URL, REQUEST_TIMEOUT


class BaseClient:
    """API 客户端基类。

    提供：
    - Session 复用（连接池）
    - Bearer Token 鉴权管理
    - 通用 GET / POST / PUT / PATCH / DELETE 方法
    - 统一超时与基础错误处理
    """

    def __init__(self, base_url: str | None = None, timeout: int | None = None) -> None:
        self._base_url: str = (base_url or API_BASE_URL).rstrip("/")
        self._timeout: int = timeout if timeout is not None else REQUEST_TIMEOUT
        self._session: requests.Session = requests.Session()
        self._token: str | None = None
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    @property
    def token(self) -> str | None:
        return self._token

    def set_token(self, token: str) -> None:
        """设置 Bearer Token，后续请求自动携带 Authorization 头。"""
        self._token = token
        self._session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        """清除 Token。"""
        self._token = None
        self._session.headers.pop("Authorization", None)

    # ------------------------------------------------------------------
    # HTTP methods
    # ------------------------------------------------------------------

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self._base_url}{path}"
        kwargs.setdefault("timeout", self._timeout)
        return self._session.get(url, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self._base_url}{path}"
        kwargs.setdefault("timeout", self._timeout)
        return self._session.post(url, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self._base_url}{path}"
        kwargs.setdefault("timeout", self._timeout)
        return self._session.put(url, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self._base_url}{path}"
        kwargs.setdefault("timeout", self._timeout)
        return self._session.patch(url, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self._base_url}{path}"
        kwargs.setdefault("timeout", self._timeout)
        return self._session.delete(url, **kwargs)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "BaseClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
