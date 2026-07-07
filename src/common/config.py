"""项目级配置常量。

所有 URL、超时、测试凭据等配置集中管理，禁止在用例或客户端中硬编码。
"""

import os

# API 基础地址
API_BASE_URL: str = os.getenv(
    "API_BASE_URL",
    "https://api.practicesoftwaretesting.com",
)

# UI 基础地址
UI_BASE_URL: str = os.getenv(
    "UI_BASE_URL",
    "https://practicesoftwaretesting.com",
)

# 请求超时（秒）
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

# 测试用户凭据（从环境变量读取，未设置时使用本地开发默认值）
# 多环境账号隔离：
#   本地开发  → config.py 默认值（test-local-*）
#   Jenkins   → Jenkinsfile 通过 env 覆盖为 jenkins-ci-*（独立账号，避免并发冲突）
#   GitHub CI → 只跑 API 测试，token 鉴权，不依赖此账号
TEST_USER_EMAIL: str = os.getenv(
    "TEST_USER_EMAIL",
    "test-local-b3dc3d0e@example.com",
)
TEST_USER_PASSWORD: str = os.getenv(
    "TEST_USER_PASSWORD",
    "KnCkAugd9AZUrd4x!L1",
)

# Jenkins 专用测试账号（独立于本地开发，避免并发登录/写入冲突）
# 供 Jenkinsfile 通过 `uv run python -c "from src.common.config import ..."` 读取
JENKINS_TEST_EMAIL = "jenkins-bvbrju-ebd2@e2e.example"
JENKINS_TEST_PASSWORD = "k*w86Yty0ibLpDFB"

# 管理员账号（报表等管理端接口）
ADMIN_EMAIL: str = os.getenv(
    "ADMIN_EMAIL",
    "admin@practicesoftwaretesting.com",
)
ADMIN_PASSWORD: str = os.getenv(
    "ADMIN_PASSWORD",
    "welcome01",
)

# 注册测试用户数据已迁移至 src/common/data_factory.py 的 new_user_data()
