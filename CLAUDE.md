# practice-ai-testing 项目开发规范

## 项目概述
- 定位：Toolshop 电商系统全流程 AI 辅助自动化测试项目
- 被测对象：Practice Software Testing（Toolshop），一个手工具电商演示系统
  - UI 地址：https://practicesoftwaretesting.com
  - Swagger接口文档：https://api.practicesoftwaretesting.com/api/documentation
  - API 地址：https://api.practicesoftwaretesting.com
  - API 文档：OpenAPI 3.0（`docs/practice_software_testing_api.json`）
- 核心目标：基于 Claude Code + DeepSeek V4 Pro 完整跑通 AI 协作开发流程，建立可复制的自动化测试体系

## 技术栈
- Python 3.12 | Pytest | Playwright（UI）| Requests（API）
- 包管理：uv，虚拟环境 `.venv`，依赖写入 `pyproject.toml`，禁止手动修改 `uv.lock`
- 报告：Allure

## 目录结构（src-layout，严格遵守）
```
src/
  ui/pages/          # UI 页面对象（POM）
  api/client/        # 接口客户端封装（API Object Pattern），按资源模块拆分
  common/            # 配置、日志、通用工具
tests/
  ui/                # UI 测试脚本
  api/               # 接口测试脚本
  integration/       # 全链路集成测试脚本
  conftest.py        # 全局 fixture，子模块可按需新增层级 conftest
docs/
  test-cases/        # 业务测试用例设计文档（按模块拆分，与测试脚本一一对应）
```
- 禁止在项目根目录创建业务代码或测试文件，新增模块仅在 `src/` 和 `tests/` 内扩展
- 本项目不需要 `src/db/`（被测系统为远程 API，无直接数据库访问权限）
- 本项目暂不设 `tests/security/`（安全测试留给 Juice Shop 阶段）

## AI 协作开发流程（强制执行顺序）
1. 需求分析 → 了解被测模块的业务逻辑和 API 能力
2. 测试用例设计 → 输出 MD 文档至 `docs/test-cases/`
3. 测试脚本生成 → 基于用例编写 Pytest 代码
4. 执行校验 → `pytest` 运行，分析失败原因
5. 缺陷修复 → 定位是测试代码问题还是理解偏差，修正后重新验证
6. 确认用例覆盖完整后，再进入下一模块

## 文档与脚本对应
- `docs/test-cases/{module}.md` ↔ `tests/ui/test_{module}.py` / `tests/api/test_{module}.py`
- 文件命名：与业务模块名一致，全小写，单词间用下划线（如 `brands.md`、`shopping_cart.md`）

## 测试用例文档规范
- 单条用例结构：**用例编号**（模块缩写-序号）→ **用例名称** → **前置条件** → **操作步骤** → **预期结果**
- 每个模块必须覆盖：
  - **正常功能场景**：核心业务流程的 Happy Path
  - **异常边界场景**：参数校验、空值、超长、不存在资源等
  - **权限场景**：未登录访问、无权限操作等

## UI 自动化规范
- 严格遵循 POM：页面元素定位与操作全部封装在页面对象中，用例不直接编写定位逻辑
- 元素定位优先级：`data-test` > `get_by_role` 语义化定位 > `get_by_text`，禁止绝对 XPath 与脆弱 CSS 选择器
- 等待机制：禁止 `time.sleep()`，依赖 Playwright 内置自动等待或 `expect` 条件等待
- 断言统一使用 Playwright 内置 `expect`
- 页面对象按功能区域拆分，如 `HomePage`、`ProductPage`、`CartPage`、`CheckoutPage`、`LoginPage` 等

## 接口自动化规范
- 严格遵循 API Object Pattern：按资源模块（Brand、Product、Cart、Invoice、User 等）封装独立客户端类
- 每个客户端类对应 API 文档中的一个 Tag（资源组）
- 请求头、鉴权、异常处理统一封装在基类中，用例层仅关注业务场景与断言
- 接口基础地址统一从配置读取（`src/common/config.py`），禁止硬编码完整 URL
- 核心业务场景做请求-响应完整性校验（状态码、响应体结构、关键字段）

## API 资源模块速览（Toolshop API v5.0.0，14 个模块）

按业务依赖关系与用户操作链路排序，AI 生成代码时严格按此顺序执行：

| 序号 | 模块 | 主要操作 | 依赖 | 优先级 |
|:--:|------|---------|------|:--:|
| 1 | User | 注册/登录/密码管理/用户信息 | 无 | 🔴 高 |
| 2 | Brand | CRUD + 搜索 | 无（读操作公开） | 🔴 高 |
| 3 | Category | CRUD + 树形结构 + 搜索 | 无（读操作公开） | 🔴 高 |
| 4 | Product | CRUD + 搜索 + 关联产品 | Brand、Category | 🔴 高 |
| 5 | Cart | 创建/管理购物车、修改数量 | User、Product | 🔴 高 |
| 6 | Invoice | 订单生成/查询/状态管理/PDF | User、Cart | 🔴 高 |
| 7 | Favorite | 收藏管理 | User、Product | 🟡 中 |
| 8 | Payment | 支付校验 | Invoice | 🟡 中 |
| 9 | Contact | 留言/回复/附件 | 无 | 🟡 中 |
| 10 | Product Spec | 产品规格管理 | Product | 🟡 中 |
| 11 | TOTP | 两步验证 | User | 🟢 低 |
| 12 | Report | 销售报表（6 个维度） | Invoice | 🟢 低 |
| 13 | Image | 图片资源 | Product | 🟢 低 |
| 14 | Postcode | 邮编查询 | 无 | 🟢 低 |

> 排序逻辑：先跑通不依赖其他模块的（1-3），再按电商用户操作链路（4-6），最后补充非核心模块（7-14）。

## 通用编码规范
- 测试文件：`test_{module}.py`，测试函数：`test_{场景描述}`，测试类：`Test{模块名}`
- 公共能力优先封装到 `src/`，避免用例中重复逻辑
- 遵循 PEP8，命名语义化
- 依赖管理：`uv add 包名`，禁止 `pip install`
- pytest 配置集中在 `pyproject.toml` 的 `[tool.pytest.ini_options]` 中
- 运行测试：项目根目录执行 `pytest`
