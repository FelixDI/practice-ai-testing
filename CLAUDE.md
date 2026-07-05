# practice-ai-testing 项目开发规范

## 项目概述

- **定位**：AI-Driven Test Automation Framework
- **被测对象**：Practice Software Testing（Toolshop），手工具电商演示系统
  - UI：`https://practicesoftwaretesting.com`
  - Swagger 接口文档：`https://api.practicesoftwaretesting.com/api/documentation`
  - API：`https://api.practicesoftwaretesting.com`
  - API 文档：OpenAPI 3.0（`docs/practice_software_testing_api.json`）
- **核心目标**：基于 Claude Code 完整跑通 AI 协作开发流程，建立可复制的自动化测试体系

## 技术栈

- Python 3.12 | Pytest | Playwright（UI）| Requests（API）
- 包管理：uv，虚拟环境 `.venv`，依赖写入 `pyproject.toml`，**禁止手动修改 `uv.lock`**
- 报告：Allure（pytest 产出原始数据 → CI 生成 HTML → GitHub Pages 发布）

## 目录结构（src-layout，严格遵守）

```
src/
  ui/pages/          # UI 页面对象（Page Object —— 每个路由一个 Page）
  ui/components/     # UI 组件对象（跨页面复用的 UI 片段：Header/Footer/ProductCard 等）
  api/client/        # API 客户端封装（API Object Pattern），按资源模块拆分
  common/            # 配置、日志、通用工具
tests/
  ui/                # UI 测试
  api/               # API 测试（含 conftest.py，夹具仅供 API 层使用）
  integration/       # 全链路集成测试
  conftest.py        # 跨测试类型共享的工具（仅 generate_unique_email）
docs/
  test-cases/
    api/             # API 测试用例设计文档
    ui/              # UI 测试用例设计文档
    integration/     # 集成测试用例设计文档
  practice_software_testing_api.json
```

- 禁止在项目根目录创建业务代码或测试文件，新增模块仅在 `src/` 和 `tests/` 内扩展
- 本项目不需要 `src/db/`（被测系统为远程 API，无直接数据库访问权限）
- 本项目暂不设 `tests/security/`（安全测试留给 Juice Shop 阶段）

## AI 协作开发流程（强制执行）

```
需求分析 → 测试用例设计 → 测试脚本生成 → MCP 浏览器验证 → pytest 验证 → 缺陷修复 → 覆盖完整 → 下一模块
```

1. 需求分析——了解业务逻辑和 API 能力
2. 测试用例设计——输出 MD 至 `docs/test-cases/api/`、`docs/test-cases/ui/` 或 `docs/test-cases/integration/`
3. 测试脚本生成——基于用例编写 Pytest
4. **测试前置校验**——写新模块的 fixture 和测试用例前，先做以下 4 项校验（详见 [测试前置校验清单](#测试前置校验清单)）
5. **MCP 浏览器验证**——使用 Playwright MCP 打开目标页面，`browser_snapshot` + `browser_evaluate` 批量验证所有 `data-test` 选择器是否存在，禁止提交含不存在选择器的代码（详见 [Playwright MCP 浏览器验证](#playwright-mcp-浏览器验证强制执行)）
6. 执行校验——`pytest` 运行，分析失败
7. 缺陷修复——区分测试 Bug 还是环境问题
8. 当前层级（P0+P1 / P2 / P3）用例全部生成且 pytest 全绿后，按 Git 提交规范推送

## 测试前置校验清单（新模块强制执行）

> 开发新 UI Page 或 API Client 时，**在写 pytest 测试代码之前**，先完成以下 4 项校验。
> 这 4 步能在进入 pytest 之前暴露"数据过期"、"账号权限不足"、"选择器丢失"等最常被 skip 掩盖的问题。

### ① 测试数据有效性校验（UI + API 通用）

**为什么**：ProductPage 硬编码的商品 ID 过期后，fixture 加载不到商品页，旧代码用 `except Exception` 掩盖成"Cloudflare 拦截"。

| 检查项 | 方法 | 通过标准 |
|--------|------|---------|
| 硬编码 ID（产品/SKU/分类 slug）当前有效 | 用 `curl` 或 `requests` 调用 API 确认返回 200 | 返回期望数据，不返回 404/500 |
| 被测试的页面/路由当前可访问 | 浏览器打开或 API HEAD 请求返回 2xx | 页面正常渲染，非空白/500 |
| 所使用的测试账号对目标端点有正确权限 | 用该账号调用目标 API | 返回 200（非 401/403） |

> **特别约束：商品 ID 禁止硬编码。** 商品数据会被服务端周期性重建，ID 全部变化（已实际发生过两次：`01KWQ4...` → `01KWR3...` → `01KWRR...`）。任何需要商品 ID 的 fixture 必须从 API 动态获取首个有效 ID，不得硬编码：
>
> ```python
> # ✅ fixture 中动态获取商品 ID
> def _fetch_valid_product_id() -> str:
>     r = requests.get(f"{API_BASE_URL}/products?page=1", timeout=10)
>     return r.json()["data"][0]["id"]
>
> # ❌ VALID_ID = "01KWR3GEF7T1HCXQXC111YATDY"  # 迟早过期
> ```

### ② 账号权限预检（API 测试专用）

**为什么**：Report API 使用 `customer@...`（非管理员）写全套测试 → 15 条全部因 403 skip，写了等于没写。

```python
# ✅ 在写测试代码之前，先验证账号权限
r = client.get("/reports/total-sales-per-country")
if r.status_code == 403:
    print("❌ 当前账号无权限！需更换为管理员账号")
    # 查找或确认管理员账号存在后再继续
```

| 检查项 | 方法 | 通过标准 |
|--------|------|---------|
| 确认模块所需权限级别（public / user / admin） | 读 OpenAPI spec 或实测 | 明确知道需要什么角色 |
| fixture 使用的账号具备该权限 | 先发一个 P0 请求 | 返回 200（非 401/403） |

### ③ Fixture 正确性校验（UI 测试专用）

**为什么**：ProductPage fixture 用 `except Exception` 隐藏了 ID 过期；CategoryPage fixture 确认了 `product_cards.first` 可见，就提前发现 slug 错误。

```python
# ❌ 禁止 —— fixture 从不报错，把问题留给用例
@pytest.fixture
def product(page):
    pp = ProductPage(page)
    pp.goto(VALID_ID)
    try:
        expect(pp.product_name).to_be_visible()
        return pp
    except Exception:          # 什么都接
        pytest.skip("随便理由")  # 什么都跳过

# ✅ 正确 —— fixture 明确告知错误类型
@pytest.fixture
def product(page):
    pp = ProductPage(page)
    page.goto(f"{URL}/{VALID_ID}")
    # 1. 先检查环境拦截
    if response.status == 403 and "cloudflare" in page.content().lower():
        pytest.skip("Cloudflare 拦截")
    # 2. 再判断页面渲染
    try:
        expect(pp.product_name).to_be_visible(timeout=N)
    except AssertionError:
        pytest.fail("元素不存在——测试数据或选择器错误")  # 忽略 Bug，必报
    return pp
```

| 检查项 | 方法 | 通过标准 |
|--------|------|---------|
| fixture 不包含裸 `except Exception` | 肉眼检查 | 区分了 `AssertionError`、`TimeoutError`、其他 |
| fixture 单独的测试（无效 ID、XSS）独立定义 `page` fixture | 测试参数只传 `page`，不传业务 fixture | 不依赖页面数据加载 |

### ④ skip 必要性验证（写任何一个 `pytest.skip` 之前执行）

**为什么**：31 条 skip 中有 15 条（Report API）通过简单预检就能避免；7 条（ProductPage）通过拆异常类型就能暴露真实错误。

```python
# 在写 pytest.skip() 之前，先问自己 3 个问题：
# 1. 这个 skip 是永远发生，还是有时发生？→ 永远发生 = 设计缺陷，不应 skip
# 2. 被跳过的是测试 Bug 还是环境问题？  → 测试 Bug 不应 skip
# 3. 有没有办法提前发现这个问题？      → 有 → 加到前置校验清单
```

| 检查项 | 通过标准 |
|--------|---------|
| 该 skip 基于显式条件（`if`），非异常捕获 | ✅ 允许继续 |
| skip reason 包含具体根因（非"环境问题"） | ✅ 允许继续 |
| 预期该 skip 最终会消失（服务恢复/数据补回后） | ✅ 允许继续 |
| 该 skip **永远会发生**（如账号权限不够、功能不存在） | ❌ 禁止 —— 是设计缺陷，不是环境问题，必须改 |

---

## Git 提交规范

### Commit Message 格式

```
<type>: <中文简述>

- 具体变更 1
- 具体变更 2

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

### Type 定义

| Type | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能、新模块 | `feat: Favorite 模块 API 测试全覆盖` |
| `fix` | Bug 修复 | `fix: CI 409冲突 - 未登录POST 改用动态唯一slug` |
| `docs` | 文档变更 | `docs: CLAUDE.md 全面优化` |
| `chore` | 依赖、配置 | `chore: add pyotp` |
| `refactor` | 重构（不改变行为） | `refactor: 夹具作用域分层决策` |

### 规则

- **小步提交**：每个独立功能/修复完成后立即提交，禁止攒一堆再推
- **首行 ≤72 字符**：中文按 2 字符=1 英文折算
- 每行 `-` 开头的项目列表具体说明变更内容
- **禁止** `WIP`、`tmp`、`fix bug` 等模糊描述
- **禁止** 提交包含 `pytest.skip` 的临时规避代码（除非已按夹具容错规范走完重试流程）
- 所有 AI 生成的 commit 必须带尾缀

## 文档与脚本对应

- `docs/test-cases/api/{module}.md` ↔ `tests/api/test_{module}_api.py` + `src/api/client/{module}_client.py`
- `docs/test-cases/ui/{page}.md` ↔ `tests/ui/test_{page}.py` + `src/ui/pages/{page}.py`
- `docs/test-cases/integration/{flow}.md` ↔ `tests/integration/test_{flow}.py`
- 命名：全小写，下划线分隔（`brand.md`、`home_page.md`）

---

## 测试用例文档规范

- 单条结构：**用例编号（模块缩写-序号）→ 用例名称 → 优先级 → 前置条件 → 操作步骤 → 预期结果**
- 用例编号格式：`API_{MODULE}_{序号}`（如 `API_BRAND_001`）
- 每条必须标注 P0/P1/P2/P3

### 优先级定义

| 级别 | 定义 | 覆盖内容 | 每端点数量 | 交付约束 |
|:--:|------|------|:--:|------|
| **P0** | 冒烟 / 核心链路 | 每个端点的 Happy Path（200/201/204）；关键必填字段校验缺失（422）；登录成功/失败（200/401） | 2~3 | 必须首批交付，P0 不通过则不做 P1 |
| **P1** | 关键异常 / 高频边界 | 每个端点涉及权限的状态码（401/403）；不存在资源（404）；重复创建（409）；关键 Schema 约束（password 强度、dob 范围） | 1~3 | P0 全部通过后交付 |
| **P2** | 边界覆盖 | 按 Schema 逐字段的 maxLength/minLength/format/range/enum 边界值；分页边界（page=0）；组合筛选 | 按字段数 | P1 全部通过后交付 |
| **P3** | 深度防御 | 横向越权（A 操作 B 数据）；Token 过期/登出后操作；资源删除后再次操作；特殊字符注入（XSS/SQL）；三级嵌套；自引用；极端并发场景 | 按需 0~5 | 仅在安全测试或上线前审计时要求 |

### 四维覆盖模型

| 维度 | 优先级 | 说明 |
|------|:--:|------|
| ① 核心链路（完整 Happy Path） | **P0** | 不通过 = 系统不可用 |
| ② 边界条件（逐字段约束遍历） | **P2** | 体力活，批量做 |
| ③ 异常路径（逐状态码覆盖） | **P1** | 401/404/409/422 是高频 Bug 来源 |
| ④ 权限/状态组合 | **P1+P3** | 未登录=P1；横向越权/Token 过期=P3 |

### 分批交付

```
P0+P1（首批）→ 脚本全绿 → 推 Git → P2（二批）→ 全绿 → 推 Git → P3（按需审计）
```

---

## API 资源模块速览（14 个模块，严格按此顺序开发）

| # | 模块 | 端点 | 主要操作 | 依赖 | 优先级 |
|:--:|------|:--:|------|------|:--:|
| 1 | User | 13 | 注册/登录/密码管理/用户信息 | 无 | 🔴 |
| 2 | Brand | 7 | CRUD + 搜索 | 无 | 🔴 |
| 3 | Category | 8 | CRUD + 树形 + 搜索 | 无 | 🔴 |
| 4 | Product | 8 | CRUD + 搜索 + 关联 | Brand, Category | 🔴 |
| 5 | Cart | 6 | 创建/管理/修改数量 | User, Product | 🔴 |
| 6 | Invoice | 10 | 订单生成/查询/状态/PDF | User, Cart | 🔴 |
| 7 | Favorite | 4 | 收藏管理 | User, Product | 🟡 |
| 8 | Payment | 1 | 支付校验 | Invoice | 🟡 |
| 9 | Contact | 6 | 留言/回复/附件 | 无 | 🟡 |
| 10 | Product Spec | 6 | 规格管理 | Product | 🟡 |
| 11 | TOTP | 2 | 两步验证 | User | 🟢 |
| 12 | Report | 7 | 6 维度销售报表 | Invoice | 🟢 |
| 13 | Image | 1 | 图片资源 | Product | 🟢 |
| 14 | Postcode | 1 | 邮编查询 | 无 | 🟢 |

---

## OpenAPI 文档使用原则

**优先复用 CLAUDE.md**，避免每次重新解析 OpenAPI 浪费 token。

```
需要接口细节？
├── 否 → 复用 CLAUDE.md / 已有代码 / 记忆
└── 是 → 按需读取 docs/practice_software_testing_api.json
         └── 只读当前模块的 paths + components/schemas
```

| 必须读 | 无需读 |
|------|------|
| 设计新模块用例 | 修改已有测试代码 |
| 编写 API Client | 修复断言/Fixture |
| 校验 Schema/状态码 | 调整 CI/CD/conftest |
| 文档更新后同步 | 补充 P2/P3 用例 |

---

## API 自动化规范

### API Object Pattern

- 按资源模块封装独立 Client 类，继承 `BaseClient`
- 每个 Client 对应 API 文档一个 Tag，方法名与业务语义对齐
- 请求头、鉴权、异常处理统一在 `BaseClient` 中

```python
# src/api/client/{module}_client.py
class BrandClient(BaseClient):
    def get_brands(self) -> Any:
        return self.get("/brands")
```

- API 基础地址统一从 `src/common/config.py` 读取，禁止硬编码
- 固定测试账号在 `config.py` 中维护，优先复用
- **断言双校验原则**：标准做法为「响应状态码 + 数据库双校验」。Toolshop 为远程 API 无数据库直连权限，**退而求其次**——必须同时校验响应状态码 + 核心业务字段（至少 2 项），仅断言状态码视为不合格

### 测试结构模式

```python
# tests/api/test_{module}_api.py
class TestGetBrands:
    def test_get_brands_200(self, client): ...      # P0
    def test_unauthorized_401(self, client): ...      # P1

class TestCreateBrand:
    def test_create_201(self, client): ...            # P0
    def test_missing_name_422(self, client): ...      # P0
    def test_duplicate_slug_409(self, client): ...    # P1
```

---

## UI 自动化规范

### 架构：Page + Component 双层封装

```
src/ui/
├── pages/           # 页面对象 —— 每个路由一个 Page
│   ├── home_page.py
│   ├── product_page.py
│   └── ...
└── components/      # 组件对象 —— 跨页面复用的 UI 组件
    ├── header.py        # 顶部导航栏（分类菜单、搜索框、购物车图标）
    ├── footer.py        # 页脚
    ├── product_card.py  # 商品卡片（首页列表、分类页、搜索页共用）
    └── login_form.py    # 登录表单（LoginPage、弹窗共用）
```

- **Page**：对应一个路由，负责页面级操作（`goto`、等待加载完成）
- **Component**：跨页面复用的 UI 片段，Page 通过组合引入 Component，禁止在 Page 中重复实现 Component 已有的逻辑
- **组件抽象时机**：写完 3~4 个页面后，哪些是真正跨页面复用的组件就清楚了，此时抽象最自然。前期过早抽组件容易过度设计，全部写完再抽重构成本高
- **MCP 辅助 Component 提取**：决定提取组件前，用 Playwright MCP 打开至少 2 个使用该组件的页面，对比 DOM 确认复用范围。验证通过后再创建 `src/ui/components/{name}.py`，将 Page 中的选择器迁移到 Component，Page 改为组合引用

### 定位与等待

- 定位优先级：`data-test` > `get_by_role` > `get_by_text`
- **禁止** 绝对 XPath、脆弱 CSS 选择器
- **禁止** `time.sleep()`，用 Playwright 自动等待或 `expect` 条件等待
- **禁止** `page.wait_for_timeout()` 固定等待（本地碰巧够，CI 全炸）。必须使用 `expect()`、`wait_for_url()`、`expect_navigation()`、`wait_for_selector()` 等显式等待
- 断言统一使用 `expect`

### Playwright MCP 浏览器验证（强制执行）

Playwright MCP 是 UI 测试开发的**实时纠错手段**——让 AI 直接操作浏览器验证选择器和交互逻辑，而非盲写代码等 pytest 报错。

**触发时机**：
- 新建或修改 Page Object → 必须用 MCP 打开页面验证所有 `data-test` 选择器
- 新建或修改 Component → 必须用 MCP 打开至少 2 个使用该组件的页面验证
- 提取 Component 前 → 用 MCP 浏览多个页面确认复用范围
- 调试 UI 测试失败 → 用 MCP 复原操作步骤、截图对比

**验证清单**：

| 步骤 | 工具 | 目的 |
|------|------|------|
| 1. 打开目标页面 | `browser_navigate` | 加载页面 |
| 2. 获取 DOM 快照 | `browser_snapshot` | 了解页面结构、语义角色、层级 |
| 3. 批量检查选择器 | `browser_evaluate` | 验证所有 `data-test` 是否存在 |
| 4. 截图确认（可选） | `browser_take_screenshot` | 视觉对比、布局确认 |
| 5. 交互验证（可选） | `browser_click` / `browser_type` | 验证点击、输入后状态变化 |

**`browser_evaluate` 验证模板**：

```js
() => {
  const selectors = ['nav-home', 'nav-categories', 'search-query', /* ... */];
  const results = {};
  for (const s of selectors) {
    const el = document.querySelector(`[data-test="${s}"]`);
    results[s] = el ? el.tagName : 'MISSING';
  }
  return results;
}
```

**通过标准**：
- 所有 Page Object 中引用的 `data-test` 选择器必须返回非 `MISSING`
- 登录态专属选择器必须在登录后单独验证
- 发现 `MISSING` → 立即修复选择器，**禁止提交含不存在选择器的代码**

**Component 抽取决策**（MCP 辅助）：

| 组件 | 验证方法 | 判定标准 |
|------|------|------|
| `Header` | 分别打开 HomePage + LoginPage，执行 `querySelectorAll('[data-test^="nav-"]')` | 两个页面返回的 `data-test` 列表一致 |
| `Footer` | 同上，检查页脚链接 | 跨页面一致 |
| `ProductCard` | 打开 HomePage + CategoryPage，检查 `.card` 或 `a[href*="/product/"]` 结构 | DOM 子树结构一致 |

#### MCP 配置维护

**Playwright MCP 不可用时的排查顺序**：
1. 确认两个配置文件都正确维护：
   - **CLI（Claude Code）** → 用 `claude mcp add` 写入 `~/.claude.json`，`command` 使用绝对路径二进制
   - **VSCode 插件** → 写入 `~/.claude/mcp.json`，Playwright 需用 shell 包装（VSCode 沙箱限制）
2. `command` **禁止使用 `npx`** —— `npx` 是 Node.js shebang 脚本，Claude Code 的 MCP 进程启动器无法解析，必须展开为绝对路径：`/opt/homebrew/bin/node /opt/homebrew/lib/node_modules/@playwright/mcp/cli.js`
3. 配置生效后需**重启整个会话**，仅重载配置文件不会生效
4. 启动后如果工具列表仍不出现，检查缓存目录下是否存在 `mcp-logs-playwright/`——不存在说明 Claude Code 根本没尝试启动（已知 bug #27373），使用 `claude mcp add` 重配

```json
// CLI（~/.claude.json，通过 claude mcp add 自动生成）
{
  "playwright": {
    "type": "stdio",
    "command": "/opt/homebrew/bin/node",
    "args": ["/opt/homebrew/lib/node_modules/@playwright/mcp/cli.js"]
  }
}

// VSCode 插件（~/.claude/mcp.json，需 shell 包装绕过沙箱）
{
  "playwright": {
    "command": "/bin/sh",
    "args": ["-c", "/opt/homebrew/bin/node /opt/homebrew/lib/node_modules/@playwright/mcp/cli.js"]
  }
}
```

注意：macOS 路径可能因 Node.js 安装方式不同而不同（Homebrew / nvm / fnm），根据本机实测路径配置。

### 页面对象清单（基于 MCP 浏览器实测 DOM 导航）

| # | 页面对象 | 路由 | 需登录 | 验证方式 |
|:--:|------|------|:--:|------|
| 1 | `HomePage` | `/` | — | nav-home ✅ |
| 2 | `CategoryPage` | `/category/{slug}` | — | nav-{tool} href 确认 ✅ |
| 3 | `ProductPage` | `/product/{id}` | — | product card click 确认 ✅ |
| 4 | `RentalsPage` | `/rentals` | — | nav-rentals href="/rentals" ✅ |
| 5 | `ContactPage` | `/contact` | — | nav-contact click 确认 ✅ |
| 6 | `LoginPage` | `/auth/login` | — | nav-sign-in + login-form ✅ |
| 7 | `RegisterPage` | `/auth/register` | — | register-link 确认 ✅ |
| 8 | `ForgotPasswordPage` | `/auth/forgot-password` | — | LoginPage 底部链接 ✅ |
| 9 | `CheckoutPage` | `/checkout` | ✅ | nav-cart href="/checkout"（购物车与结账合一） |
| 10 | `AccountDashboard` | `/account` | ✅ | 登录后自动跳转 |
| 11 | `ProfilePage` | `/account/profile` | ✅ | nav-my-profile（登录态菜单）|
| 12 | `FavoritesPage` | `/account/favorites` | ✅ | nav-my-favorites |
| 13 | `InvoicesPage` | `/account/invoices` | ✅ | nav-my-invoices |
| 14 | `MessagesPage` | `/account/messages` | ✅ | nav-my-messages |
| — | ~~`CartPage`~~ | ~~侧边栏/弹窗~~ | — | ❌ 实测不存在。`nav-cart` 直接链到 `/checkout`，无独立购物车页面 |
| — | `PrivacyPage` | `/privacy` | — | Footer 链接，仅供静态内容，无需 Page Object |

#### 页面对象关系图

```
Public flow（无需登录）:
  HomePage → CategoryPage → ProductPage → CheckoutPage（需登录）
  LoginPage ↔ RegisterPage ↔ ForgotPasswordPage
  RentalsPage / ContactPage

Authenticated flow（需登录）:
  AccountDashboard → ProfilePage / FavoritesPage / InvoicesPage / MessagesPage
  CheckoutPage（购物车+结账合一）
```

#### 关键校核结论

1. **`/cart` 路由不存在** —— 购物车是 header 上的 `nav-cart` 按钮，点击直接进入 `/checkout`
2. **`/checkout` 路由需登录** —— `routerlink="/checkout"`，但未登录时点击会跳转到登录页
3. **登录后跳转 `/account`** —— 非 `/account/profile`，存在一个 Dashboard 概览页
4. **`/privacy` 路由** —— Footer 链接，静态内容，无需 Page Object
5. **`/auth/forgot-password` 路由** —— LoginPage 底部链接，后续可扩展

---

## Fixture 管理规范

### 作用域分层决策（禁止一刀切）

| 优先级 | 场景 | 作用域 |
|:--:|------|:--:|
| 1 | 修改共享状态（改密码、登出、删除用户） | `function` |
| 2 | 只读 / 创建但不修改共享状态 | `module` |
| 3 | 全局不变配置（base_url、测试账号） | `session` |

### 高频创建控制

- **必须** 优先复用 `config.py` 固定测试账号
- **禁止** 同文件内每用例重复注册用户 / 创建购物车 / 创建发票
- **必须** 将注册、创建购物车等封装为 `module` 级夹具
- **必须** 在夹具 `yield` 后清理数据（容错静默放行）

### 夹具容错

- **API 夹具**：setup 阶段遇到 500/超时 → 自动重试 2 次 → 仍失败 `pytest.skip`（含具体 reason）
- **UI 夹具**：不得使用裸 `except Exception`，必须按异常类型分派 —— `AssertionError → pytest.fail()`（测试/选择器 Bug）、`TimeoutError → skip`（环境问题），详见 [UI fixture 编码规范](#ui-fixture-编码规范)
- 后置清理遇到 500/409 → 静默放行，不抛断言

---

## 接口测试稳定性总纲

> **核心背景**：被测站点 `practicesoftwaretesting.com` 为公开练习环境，服务端资源与并发承载能力有限。高频调用写接口（用户注册、购物车创建、发票创建）极易触发 500，属于**环境波动而非测试代码逻辑问题**。

**防护三层机制（执行优先级从高到低）**：

```
数据复用（减少请求量） > 自动重试 > 夹具容错 skip > 手动跳过用例
```

---

### 🚨 pytest.skip 强制约束（AI 必须遵守）

#### 禁止行为

- **禁止** 为"让测试通过"而使用 `pytest.skip` —— 跳过不是通过
- **禁止** 在 P0/P1 核心业务用例中使用 `pytest.skip`，除非被测服务整体不可用（502/503/连接超时）
- **禁止** 无 `reason` 参数或使用 "skip this test" 等模糊描述
- **禁止** 在业务断言失败、测试代码逻辑错误场景使用 `pytest.skip` 掩盖问题
- **禁止** 在 fixture 中使用裸 `except Exception` 接住所有异常后 skip —— 必须按异常类型分派（详见 [UI fixture 编码规范](#ui-fixture-编码规范) 中的异常分类参考，API夹具同理）

#### 生效前置规则

1. 必须先触发自动重试机制，连续重试全部失败后，再判断是否符合 skip 条件
2. 仅夹具 setup 阶段的环境类错误允许 skip；用例执行阶段的业务断言失败禁止 skip
3. 单次偶发 500 不得直接 skip，必须满足「连续 2 次重试失败」阈值

#### 允许 skip 的场景（仅限以下，`reason` 必须具体）

| 场景 | 示例 |
|------|------|
| 被测服务整体不可用 | `reason="服务返回 503，环境不可用"` |
| 依赖数据被删除且无法重建 | `reason="指定 SKU 已下架，无法复现加购场景"` |
| 运行环境不满足前置条件 | `reason="仅 Linux 环境支持该校验逻辑"` |
| 夹具前置操作连续重试 2 次仍失败的服务端环境异常 | `reason="创建购物车连续2次返回500，服务端环境异常"` |

---

### 遇到测试失败时的修复优先级（强制执行）

```
1. 修测试代码 —— 断言是否正确？参数是否匹配接口文档？路径是否拼写正确？
2. 修被测环境/数据 —— 服务是否正常？测试数据是否有效？是否触发了环境限流？
3. 最后才跳过 —— 仅限外部不可控因素，且必须说明具体原因
```

### AI 必须报告（不得自行处理）

以下情况必须向我报告，等待确认后再操作：
- 同一接口连续 3 次返回 500
- 接口文档与实际返回不一致（字段缺失、状态码不符、结构差异等）
- **任何** 需要新增 `pytest.skip` 的情况（含完整原因分析）

---

### 失败自动重试规范

**插件配置**：`pyproject.toml` 已配 `addopts = "--reruns 2 --reruns-delay 1"`

**重试触发边界（严格限定）**：

| 允许触发重试 | 禁止触发重试 |
|------|------|
| 服务端 500/502/503/504 | 业务断言失败（预期 422 实际 200） |
| 连接超时、网络断开、DNS 解析失败 | 非幂等写接口（注册重复 → 409） |
| — | 权限校验（401/403）、资源不存在（404）、参数校验失败（422） |

**与 skip 机制联动**：自动重试 2 次全部失败，且属于环境类异常时，夹具层可执行 `pytest.skip` 兜底。业务逻辑类失败不触发重试、不允许跳过，必须定位根因并修复。

---

## UI 测试稳定性总纲

> **核心背景**：被测站点 `practicesoftwaretesting.com` 使用了 Cloudflare 反爬保护，Chromium headless 模式下可能出现 403 拦截或 Challenge 页面，属于环境波动而非测试代码逻辑问题。

**防护三层机制（执行优先级从高到低）**：

```
选择器 MCP 提前验证 > 显式等待（expect/auto-waiting） > 环境异常跳过（低频）
```

---

### 🚨 UI 测试 pytest.skip 强制约束（AI 必须遵守）

UI 测试 **同样适用** API 章节 [pytest.skip 强制约束](#-pytestskip-强制约束ai-必须遵守) 的全部基础规则：
- 禁止为"让测试通过"而 skip
- 禁止 P0/P1 无理由 skip
- 禁止无 `reason` 参数
- 禁止对业务断言失败使用 skip 掩盖
- AI 必须报告任何新增的 skip

#### UI 附加禁止行为

- **禁止** fixture 中使用裸 `except Exception` 捕获所有异常后 skip——必须区分异常类型
- **禁止** 页面元素不存在就自动 skip——先检查选择器是否正确（MCP 验证），确认是环境问题再考虑 skip
- **禁止** fixture skip 导致独立测试被连带跳过——不依赖 fixture 的测试（无效 ID、XSS 等）必须独立执行，不受 fixture 加载失败影响
- **禁止** 同一文件 skip 比例超过 50%（P0+P1 中超过 30%），超过必须排查根因

#### 允许 skip 的场景（UI 专属）

| 场景 | 判断方法 | 示例 reason |
|------|------|------|
| Cloudflare/反爬拦截 | `page.content()` 含 `cloudflare` 或 `Checking your browser`；或 `response.status == 403` | `"Cloudflare 拦截({url})，环境不可用"` |
| 登录页自动重定向非测试目标 | 当前 URL 跳转到 `/auth/login` | `"CheckoutPage 需登录，非测试范围"` |
| 依赖功能数据为空（0 商品分类） | 页面加载正常但主要列表容器为空 | `"special-tools 分类无商品，跳过"` |
| 视口/设备不兼容 | 已知响应式断点 | `"该功能仅桌面视口支持"` |

#### UI fixture 编码规范

1. **区分异常类型**：`except Exception` 禁止。至少分三路：
   - `AssertionError`（expect 失败）→ `pytest.fail()`（测试/选择器问题）
   - `TimeoutError` → 可考虑 skip（环境慢/拦截）
   - `其他` → 记录后 skip（需要报告）
2. **检查 Cloudflare 特征**：不要只靠超时判断，显式检查页面内容是否含 Cloudflare 关键字
3. ** fixture 职责单一**：仅负责页面加载就绪，不承载业务断言

```python
# ✅ fixture 正确做法
@pytest.fixture
def product(page: Page) -> ProductPage | None:
    pp = ProductPage(page)
    response = page.goto(f"{ProductPage.BASE_URL}/{VALID_ID}", wait_until="load", timeout=30000)
    # 1. 检查 Cloudflare 拦截
    if response and response.status == 403:
        body = page.content()  # type: ignore[no-untyped-call]
        if "cloudflare" in body.lower():
            pytest.skip("Cloudflare 拦截商品页，环境不可用")
    # 2. 判断页面加载
    try:
        expect(pp.product_name).to_be_visible(timeout=30000)
    except AssertionError:
        pytest.fail("product-name 不可见，请检查选择器或页面结构")  # 测试代码问题
    except TimeoutError:
        pytest.skip("商品页超时，环境异常")
    return pp

# ❌ 禁止
@pytest.fixture
def product(page):
    pp = ProductPage(page)
    pp.goto(VALID_ID)
    try:
        ...
        return pp
    except Exception:                    # 裸捕获——无法区分错误类型
        pytest.skip("随便一个理由")      # 掩盖了测试代码 Bug
```

#### 异常分类参考（Playwright）

| 异常类型 | 含义 | 处理 |
|------|------|------|
| `TimeoutError` | 显式等待超时 | 环境问题 → 允许 skip |
| `AssertionError` | `expect` 断言失败 | 测试/选择器 Bug → `pytest.fail()` |
| `Error` (Playwright) | 页面操作异常（元素 detached、navigation 失败） | 视具体场景判断 |
| 其他异常 | 网络断开、浏览器崩溃 | 报告后 skip |

---

## CI/CD 规范

### Workflow 触发条件

| Workflow | 触发 | 作用 |
|------|------|------|
| **Tests** | push/PR 到 main（`src/` `tests/` `pyproject.toml` `uv.lock` 变更） | API + UI 并行测试 |
| **Deploy Allure** | Tests 完成（仅 success） | 生成 API/UI Allure HTML → 发布 GitHub Pages |

> **已知限制**：`practicesoftwaretesting.com` 启用了 Cloudflare 反爬保护，GitHub Actions Runner 可能被拦截（返回 403 或 Cloudflare 挑战页）。CI 已配置 `Check site reachability` 步骤自动检测并跳过 UI 测试。UI 测试以本地执行为准。

### CI 失败处理

**🚨 本地通过 + CI 失败 = 先排查环境，再怀疑代码。**

| 优先级 | 检查项 | 常见 CI 环境问题 |
|:--:|------|------|
| 1 | CI log 完整报错 | 不要只看测试名，看具体错误信息 |
| 2 | 网络可达性 | CI runner 能否访问被测站点 |
| 3 | 系统依赖 | Playwright 是否 `--with-deps`、浏览器是否安装 |
| 4 | 超时/等待策略 | `networkidle` 永远等不到（SPA 长连接）、`wait_for_timeout` 硬编码 |
| 5 | 最后才怀疑测试代码 | 反复改测试而 CI 一直挂，问题大概率在环境 |

1. 去 Actions 页面看 `junit.xml`（Artifacts）或直接读 CI log
2. 本地 `pytest tests/api/test_{module}_api.py -v` 复现
3. 本地通过、CI 失败 → **先对照上表排查环境**，不要改测试代码
4. 如果是断言失败（本地也挂），修测试代码后推送
5. Allure 报告地址：`https://felixdi.github.io/practice-ai-testing/api-allure-report/`

### 首次部署 Pages

`gh-pages` 分支由 CI 自动创建。首次推送后去 `Settings → Pages` 选择 `gh-pages` 分支即可。

---

## 通用编码规范

```python
# ✅ 文件头
from __future__ import annotations
from typing import Any

# ✅ 类型注解
def test_something(self, client: BrandClient) -> None:

# ✅ 断言含诊断信息
assert r.status_code == 200, f"期望200, 实际{r.status_code} {r.text}"

# ✅ 唯一数据用 uuid
import uuid
slug = f"test-{uuid.uuid4().hex[:8]}"

# ❌ 禁止硬编码
url = "https://api.practicesoftwaretesting.com/brands"  # 走 config
time.sleep(2)                                           # 用 expect 等待

# ❌ 禁止硬编码 venv 路径
PYTEST = str(PROJECT_ROOT / ".venv" / "bin" / "pytest")  # 跨平台炸
```

- **运行命令统一走 `uv run`**：`uv run pytest`、`uv run python`，**禁止**直接调用 `.venv/bin/python` 或硬编码 venv 路径（跨平台不兼容）
- 测试文件：API `test_{module}_api.py`、UI `test_{page}.py`、集成 `test_{flow}.py`；函数：`test_{场景描述}`；类：`Test{模块名}`
- 公共能力封装到 `src/`，不放在 `tests/` 下
- 遵循 PEP8，命名语义化
- `uv add 包名`，禁止 `pip install`
- pytest 配置集中在 `pyproject.toml` 的 `[tool.pytest.ini_options]`
- 运行测试：项目根目录 `pytest`（由 `.venv` 提供环境）

---

## 踩坑速查

> 以下是本项目特有的高频陷阱。新增模块或修测试时必须参考。

| # | 坑 | 现象 | 正确做法 |
|:--:|------|------|------|
| 1 | **固定账号 + 可变状态 = 409** | module 夹具收藏了商品 A，function 测试也想收藏 → 409 | function 级测试用 `_get_unfavorited_product()` 先查列表 |
| 2 | **module 夹具 token 过期** | 全量跑 12+ 分钟，后面测试 POST/PUT 全返回 401 | 在 `ctx` 夹具里加 `uc.login()` 重新登录 |
| 3 | **硬编码 slug 跨 CI run 冲突** | 上次 CI 创建了 `slug="unauth-x"`，这次再创 → 409 | 用 `uuid.uuid4().hex[:8]` 动态生成唯一值 |
| 4 | **地址校验服务不可用（永久）** | `POST /invoices` 返回 422 "city does not belong to country"，7+ 种地址变体（DE/NL/US、全称/缩写）全部失败，已验证为服务端地址校验数据库已失效 | 当前不可修复，依赖 `_mod_invoice` 的 14 条测试级联 skip，skip reason 明确标注为服务端问题；恢复后可删 fallback 逻辑 |
| 5 | **商品 ID 数据竞争** | 添加商品到购物车返回 422 "product id is invalid" | 遍历前 5 个商品，找到一个能成功添加的 |
| 6 | **OpenAPI 文档 ≠ 实际行为** | 文档说 400，实际 422；文档说 404，实际 204 | 以实测为准，代码里 `assert status_code in (X, Y)` 弹性断言 |
| 7 | **同一账号多测试文件共享** | `customer@practicesoftwaretesting.com` 被多个文件同时用 | 只读操作用固定账号；写操作注册独立账号 |
| 8 | **`except Exception` + `pytest.skip` 掩盖真实 Bug** | fixture 用裸 `except Exception: pytest.skip(...)` 跳过所有错误 → 产品 ID 过期导致页面加载失败本应爆红，却表现为"7 skipped Cloudflare" | fixture 必须按异常类型分派：`AssertionError → pytest.fail()`（测试 Bug）、`TimeoutError → skip`（环境问题）；详见[UI fixture 编码规范](#ui-fixture-编码规范) |
| 9 | **测试账号角色与接口权限不匹配** | 报表端点需要管理员权限，但 fixture 使用 `customer@...` 导致全部 15 条测试返回 403 后 skip | 验证每个模块的权限需求。Report 类存在 `admin@practicesoftwaretesting.com / welcome01`，创建客户端时使用对应角色的账号 |

## Agent 规范（占位，待多 Agent 工作流启用后补充）

> 当前项目仅单 Agent 模式。后续启用 Workflow 多 Agent 编排时，在此补充 Agent 分工、通信协议、工作目录隔离策略。
