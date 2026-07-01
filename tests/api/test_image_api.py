"""Image 模块 API 测试。

蓝图：docs/test-cases/image.md —— 2 条用例，1 个端点全覆盖。
"""

from __future__ import annotations

import pytest

from src.api.client.image_client import ImageClient


@pytest.fixture
def client() -> ImageClient:
    with ImageClient() as c:
        yield c


class TestGetImages:
    # [API_IMAGE_001] P0
    def test_get_images_200(self, client: ImageClient) -> None:
        r = client.get_images()
        assert r.status_code == 200, f"期望200, 实际{r.status_code}"
        data = r.json()
        assert isinstance(data, list), f"期望list, 实际{type(data)}"
        if len(data) > 0:
            img = data[0]
            assert "id" in img and "file_name" in img

    # [API_IMAGE_002] P1
    def test_post_images_405(self, client: ImageClient) -> None:
        r = client.post("/images")
        assert r.status_code == 405, f"期望405, 实际{r.status_code}"
