"""项目级配置常量。

所有 URL、超时、测试凭据等配置集中管理，禁止在用例或客户端中硬编码。
"""

import os

# API 基础地址
API_BASE_URL: str = os.getenv(
    "API_BASE_URL",
    "https://api.practicesoftwaretesting.com",
)

# 请求超时（秒）
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

# 测试用户凭据（从环境变量读取，未设置时使用默认演示账号）
TEST_USER_EMAIL: str = os.getenv(
    "TEST_USER_EMAIL",
    "customer@practicesoftwaretesting.com",
)
TEST_USER_PASSWORD: str = os.getenv(
    "TEST_USER_PASSWORD",
    "welcome01",
)

# 注册测试用户（每次注册使用唯一邮箱避免冲突）
# 测试中通过 fixture 动态生成，此处仅作为格式参考
REGISTER_USER_DATA: dict = {
    "first_name": "Test",
    "last_name": "Runner",
    "email": "test.runner@example.com",
    "password": "Str0ng!Pass",
    "address": {
        "street": "Test Street",
        "house_number": "42",
        "city": "TestCity",
        "state": "TestState",
        "country": "DE",
        "postal_code": "12345",
    },
    "phone": "+49123456789",
    "dob": "1990-01-01",
}
