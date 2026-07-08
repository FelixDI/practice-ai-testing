# practice-ai-testing

> **AI 协作自动化测试工程 —— Toolshop 电商系统全栈测试**
>
> 以 Claude Code 为 AI 引擎，从零构建覆盖 14 个 API 模块 + 14 个 UI 页面的自动化测试体系（646 条用例，通过率 97%+），
> 完整跑通「需求分析 → 用例设计 → 脚本生成 → MCP 验证 → CI/CD 发布报告」的 AI 驱动闭环。

## 简历项目描述

### AI-Driven Test Automation Framework（Toolshop 电商系统）

**技术栈**：Python 3.12 · Pytest · Playwright · Requests · Allure · GitHub Actions · Jenkins · uv · Faker

**项目概述**

为 Practice Software Testing 电商平台构建全栈自动化测试框架，覆盖 API（14 模块 / 15 Client 类）与 UI（14 Page Object + 3 Component）共 **646 条用例**（通过率 97%+，22 skip 均为 Cloudflare/Angular zone.js/地址校验等不可控环境因素），打通从需求分析到 Allure 报告自动发布 GitHub Pages 的完整链路。核心目标是验证 **AI 协作开发的工程化落地**——通过规则约束、上下文管理、MCP 工具链与 CI/CD 集成，将 AI 从"辅助写代码"提升为"可控的工程生产力"。

**AI Engineering 体系**

```
AI Engineering Stack
├── Prompt Engineering
│   └── 3 条 Slash Commands（/generate-test-cases /generate-test-scripts /audit-module）
│       将多步提示词工程压缩为单一指令，消除人为偏差
│
├── Context Engineering
│   ├── CLAUDE.md（800+ 行）—— 四维覆盖模型、pytest.skip 强制约束、Fixture 作用域分层
│   ├── OpenAPI 文档按需分段读取（禁止全量解析），token 消耗从 ~200K 降至 ~30K
│   └── 已保存 MCP 快照复用、API 文档 ↔ 代码 ↔ 用例文档三向映射
│
├── MCP 工具链（恰好覆盖全流程）
│   ├── Playwright MCP —— 浏览器 DOM 快照 + 选择器批量校验
│   ├── pytest-runner MCP（自研 FastMCP）—— AI 会话内直接跑测试、重跑失败、按模块回归
│   └── GitHub MCP —— PR/Issue 管理全在对话流中完成
│   └── 覆盖「浏览器验证 → 测试执行 → 代码发布」三个关键节点
│
├── Hooks 自动化
│   └── PostToolUse Hook：每次 Write/Edit 测试文件后自动 uv run pytest，失败即时反馈
│       杜绝"写完就忘、攒 10 个文件一起炸"的 AI 协作顽疾
│
├── Skills 编排
│   └── python-automation-test-standard Skill（全局复用）+ loop / code-review / verify 等内置 Skill
│
└── CI/CD 双流水线
    ├── GitHub Actions：Git Push → API ∥ UI → Allure HTML → GitHub Pages
    └── Jenkins：同流程 + Skip Docs-Only + 归档 Playwright trace + gh-pages 推送重试
```

**工程可靠性保障**

```
src-layout 工程结构 + uv 依赖管理（pyproject.toml + uv.lock）
        │
        ▼ 保证本地 / CI / Jenkins 三环境一致
        │
        ├── API 可靠性 ────────────────────────────────────
        │   OpenAPI 3.0 文档驱动 → Schema 约束 → 状态码 + 业务字段双校验
        │   逐字段边界遍历（maxLength / minLength / format / range / enum）
        │
        └── UI 可靠性 ─────────────────────────────────────
            Playwright MCP 实测 DOM 快照 → data-test 选择器批量校验
            禁止提交含不存在选择器的代码
```

- **API 可靠性**：基于 OpenAPI 3.0 文档驱动开发——按 Schema 逐字段生成 P2 边界用例，`assert status_code + 核心业务字段` 双重断言
- **UI 可靠性**：Playwright MCP 浏览器实测 DOM 快照 → 批量 `browser_evaluate` 验证选择器 → 保存 `.playwright-mcp/` 供复用，禁止硬编码脆弱选择器
- **测试稳定性（三层防护）**：
  - **数据复用优先**：module 级夹具复用用户/购物车/订单，避免高频创建压垮公开测试环境
  - **自动重试**：`pytest-rerunfailures`（`--reruns 2 --reruns-delay 1`），仅触发服务端 5xx 和网络异常，业务断言失败不重试
  - **Fixture/Helper 容错 skip**：夹具 setup 阶段连续重试全部失败后 `pytest.skip` 兜底——区分 Cloudflare 拦截、页面超时、API 数据竞争三类场景
- **数据工厂**：`Faker + seed(0) + .unique` 集中管理测试数据生成，47 处散落 `uuid` 全部收敛至 `data_factory.py`，语义化（`generate_unique_slug("e2e-cat")` → `e2e-cat-forest`）且跨环境可复刻
- **破坏性测试隔离**：`@pytest.mark.destructive` 标记 + `destructive_user` 牺牲品账号（每次新注册），错误密码/锁定/删除不连累共享 `TEST_USER_*`
- **skip 准入规则**：7 条硬约束（禁止 P0/P1 无理由 skip、禁止裸 `except Exception`、禁止同文件 skip 超 50%），从工程层面杜绝 AI 用 skip 掩盖 Bug

**CI/CD 双流水线**

- `uv` 统一本地/CI 依赖管理（`uv.lock` 锁定 + `astral-sh/setup-uv@v7` 缓存），`uv run pytest` 替代硬编码 venv 路径，跨平台一套命令
- **测试前置检查**：
  - UI：`check_site_reachability.py`（Playwright 实测渲染，非 curl）自动跳过 Cloudflare 拦截
  - 账号：`pytest_configure` 启动时验证托管账号可用性，靶场数据重建后自动重新注册，避免大面积 401 skip
- **Jenkins 专项优化**：`Skip Docs-Only` 阶段 / `archiveArtifacts` 归档 Playwright trace / gh-pages 推送含 3 次重试
- 多环境账号隔离（本地 / Jenkins / GitHub Actions 各用独立账号，凭据统一在 `config.py` 维护，CI 动态注入）

**项目规模**

| 维度 | 数据 |
|------|------|
| 测试用例总数 | **646**（通过率 97%+，22 skip 均为不可控环境因素） |
| API 模块 / Client 类 | 14 / 15 |
| UI Page Object / Component | 14 / 3 |
| 自定义 MCP Server | 1（pytest-runner，FastMCP） |
| 自定义 Slash Command | 3 |
| 自定义 Hook | 1（PostToolUse 自动测试） |
| Data Factory 函数 | 6（`generate_unique_email/slug/product_name/password` + `new_user_data` + `unique_id`） |
| CI 流水线 | 2 条（GitHub Actions + Jenkins） |
| 测试用例文档 | 31 篇（API 14 + UI 14 Page + 3 Component） |

**个人职责（全部独立完成）**

| AI Engineering 层 | 具体实践 |
|------|------|
| **Prompt Engineering** | 设计 3 条 Slash Commands，将用例设计/脚本生成/覆盖审计的多步提示词固化为可复用指令 |
| **Context Engineering** | 编写 800+ 行 CLAUDE.md（四维覆盖模型 P0-P3、skip 准入 7 条、Fixture 分层、异常分类路径）；OpenAPI 按需分段读取策略 |
| **MCP 工具链** | 自研 pytest-runner MCP（FastMCP），实现 AI 会话内测试执行闭环；集成 Playwright MCP + GitHub MCP 覆盖全流程 |
| **Hooks 自动化** | PostToolUse Hook —— Write/Edit 后自动 `uv run pytest`，失败即时反馈 |
| **工程基础** | src-layout 工程结构 + uv 包管理 + pyproject.toml 配置；Data Factory 集中管理测试数据 |
| **CI/CD** | GitHub Actions + Jenkins 双流水线，Allure 报告自动发布 GitHub Pages；多环境账号隔离（config.py 统一凭据，CI 动态注入） |
| **测试架构** | 14 模块 API Client + 14 Page Object + 3 Component；测试稳定性三层防护 + 数据工厂 + 破坏性测试隔离 + skip 准入规则 |

---

## 被测对象

- UI：`https://practicesoftwaretesting.com`
- API：`https://api.practicesoftwaretesting.com`（OpenAPI 3.0 文档：`docs/practice_software_testing_api.json`）

## 目录结构

<!-- PROJECT_STRUCTURE_START -->
```
practice-ai-testing/
├── docs/
│   ├── test-cases/
│   │   ├── api/
│   │   │   ├── brand.md
│   │   │   ├── cart.md
│   │   │   ├── category.md
│   │   │   ├── contact.md
│   │   │   ├── favorite.md
│   │   │   ├── image.md
│   │   │   ├── invoice.md
│   │   │   ├── payment.md
│   │   │   ├── postcode.md
│   │   │   ├── product-spec.md
│   │   │   ├── product.md
│   │   │   ├── report.md
│   │   │   ├── totp.md
│   │   │   └── user.md
│   │   └── ui/
│   │       ├── account_dashboard.md
│   │       ├── category_page.md
│   │       ├── checkout_page.md
│   │       ├── contact_page.md
│   │       ├── favorites_page.md
│   │       ├── footer_component.md
│   │       ├── forgot_password_page.md
│   │       ├── header_component.md
│   │       ├── home_page.md
│   │       ├── invoices_page.md
│   │       ├── login_page.md
│   │       ├── messages_page.md
│   │       ├── product_card_component.md
│   │       ├── product_page.md
│   │       ├── profile_page.md
│   │       ├── register_page.md
│   │       └── rentals_page.md
│   ├── AI 辅助自动化测试开发 全阶段踩坑.md
│   └── practice_software_testing_api.json
├── scripts/
│   └── check_site_reachability.py
├── src/
│   ├── api/
│   │   ├── client/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── brand_client.py
│   │   │   ├── cart_client.py
│   │   │   ├── category_client.py
│   │   │   ├── contact_client.py
│   │   │   ├── favorite_client.py
│   │   │   ├── image_client.py
│   │   │   ├── invoice_client.py
│   │   │   ├── payment_client.py
│   │   │   ├── postcode_client.py
│   │   │   ├── product_client.py
│   │   │   ├── product_spec_client.py
│   │   │   ├── report_client.py
│   │   │   ├── totp_client.py
│   │   │   └── user_client.py
│   │   └── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── data_factory.py
│   │   └── pytest_mcp_server.py
│   ├── ui/
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── footer.py
│   │   │   ├── header.py
│   │   │   └── product_card.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── account_dashboard.py
│   │   │   ├── base_page.py
│   │   │   ├── category_page.py
│   │   │   ├── checkout_page.py
│   │   │   ├── contact_page.py
│   │   │   ├── favorites_page.py
│   │   │   ├── forgot_password_page.py
│   │   │   ├── home_page.py
│   │   │   ├── invoices_page.py
│   │   │   ├── login_page.py
│   │   │   ├── messages_page.py
│   │   │   ├── product_page.py
│   │   │   ├── profile_page.py
│   │   │   ├── register_page.py
│   │   │   └── rentals_page.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_brand_api.py
│   │   ├── test_cart_api.py
│   │   ├── test_category_api.py
│   │   ├── test_contact_api.py
│   │   ├── test_favorite_api.py
│   │   ├── test_image_api.py
│   │   ├── test_invoice_api.py
│   │   ├── test_payment_api.py
│   │   ├── test_postcode_api.py
│   │   ├── test_product_api.py
│   │   ├── test_product_spec_api.py
│   │   ├── test_report_api.py
│   │   ├── test_totp_api.py
│   │   └── test_user_api.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_account_dashboard.py
│   │   ├── test_category_page.py
│   │   ├── test_checkout_page.py
│   │   ├── test_contact_page.py
│   │   ├── test_favorites_page.py
│   │   ├── test_footer_component.py
│   │   ├── test_forgot_password_page.py
│   │   ├── test_header_component.py
│   │   ├── test_home_page.py
│   │   ├── test_invoices_page.py
│   │   ├── test_login_page.py
│   │   ├── test_messages_page.py
│   │   ├── test_product_card_component.py
│   │   ├── test_product_page.py
│   │   ├── test_profile_page.py
│   │   ├── test_register_page.py
│   │   └── test_rentals_page.py
│   ├── __init__.py
│   └── conftest.py
├── CLAUDE.md
├── Jenkinsfile
├── README.md
├── main.py
├── pyproject.toml
├── update_tree.py
└── uv.lock

16 directories, 121 files
```
<!-- PROJECT_STRUCTURE_END -->



#### API test:
[Allure测试报告](https://felixdi.github.io/practice-ai-testing/api-allure-report/)



#### UI test:
[Allure测试报告](https://felixdi.github.io/practice-ai-testing/ui-allure-report/)