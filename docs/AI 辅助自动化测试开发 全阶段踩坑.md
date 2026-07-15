```

**文档定位**

这份文档记录了系统化学习 AI 协作自动化测试过程中，从零到一搭建框架、从混乱到有序、从“玩具”到“工程化”的每一个关键问题与解决方案。这些经验可以作为未来任何 AI 测试项目的起点。

# 需求分析与测试用例设计阶段 — 从”漫无目的”到”精准覆盖”

问题 1：AI 生成的用例没有边界，永远补不完
现象：每次让 Claude Code 重新检查测试用例文档，它总能找到“遗漏”的用例。来来回回补了五六轮，永远感觉不全。

根因分析：
“测试完备性”本身是一个无限概念，任何接口都可以从更多角度、更多边界去测
项目 CLAUDE.md 没有定义“什么叫够用”，AI 只能基于概率生成
缺乏优先级分层，AI 不知道哪些是“今天必须有的”，哪些是“以后可以补的”
解决方案：在 CLAUDE.md 中建立四维覆盖 + 优先级分层体系

问题 2：14 个模块的测试用例全挤在一个文档里
现象：让 AI 生成全部模块的测试用例，它直接把 Product、Cart、Invoice 等 14 个模块全部塞进一个巨大的 Markdown 文件。

根因分析：
没有定义测试用例文件的命名规范和拆分原则
AI 默认把所有内容放在一个文件里
解决方案：统一测试用例文件命名规范


# 测试脚本开发阶段 — 从”能跑”到”跑得稳”

问题 3：AI 滥用 pytest.skip，用“跳过”代替“修复”
现象：Claude Code 生成的测试脚本跑不通，反复修改后开始大量添加 pytest.skip()，让测试“跳过”而不是“通过”。

根因分析：
AI 的底层驱动是“完成任务”，当反复修改仍无法通过时，pytest.skip 成了最快的“捷径”
项目 CLAUDE.md 中没有对 pytest.skip 的使用场景做约束
AI 把“测试通过”当成了目标，而不是“验证功能正确性”
解决方案：在 CLAUDE.md 中添加 pytest.skip 强制约束

问题 4：被测环境不稳定，测试大面积失败
现象：44 个用例通过，但 10+ 个用例失败。所有失败全部发生在夹具 setup 阶段——注册用户、创建购物车时，服务端返回 500 Something went wrong。

根因分析：
这不是测试代码逻辑错误，是线上公开练习站点服务端不稳定导致的，应禁止测试脚本高频创建
当前每个用例都重新注册用户、新建购物车，一个文件注册几十次
请求密集时，服务端数据库/连接池扛不住，返回 500
该站点是免费练习环境，无高可用保障
解决方案：建立夹具管理规范 + 自动重试机制

重试规则
仅对 500、502、503、连接超时等服务端异常进行重试
对 400、401、403、404、422 等客户端错误不重试（这些是测试代码逻辑问题，重试无意义）
重试上限：单用例最多重试 2 次

# CI/CD 与 UI 测试阶段 — 从"本地跑通"到"CI 稳定"

问题 5：CI 全炸但本地全绿，反复改测试代码治标不治本
现象：HomePage 13 条 UI 用例本地 32 秒全过，GitHub Actions 上 8 条全挂，连续改了五六个版本都没用。

根因分析：

CI Runner 网络受限（被 Cloudflare 拦截），SPA 页面本身就没渲染出来——改等待策略、改选择器都不可能修复根因。
`wait_for_timeout()` 本地碰巧够，CI 一慢就炸，但从来没怀疑过这些硬编码等待
`networkidle` 在 SPA 站点永远等不到（后台分析/长轮询不断），CI 上直接超时
排查流程倒了：先改测试代码，再改 CI 配置，最后才怀疑环境——应该是反过来的

解决方案：

CI 加 curl 站点可达性检测，Cloudflare 拦截就自动跳过 UI 测试
消除 10 个 `wait_for_timeout()`，改为 `expect()`、`wait_for_url()`、`expect_navigation()`、`wait_for_selector()` 等显式等待
BasePage `goto` 使用 `wait_until="load"` + `wait_for_selector` 代替 `networkidle`
CLAUDE.md 加入 CI 失败处理优先级表：本地通过 + CI 失败 → 先排查环境，再怀疑代码

问题 6：Playwright 三种 wait_until 搞不清楚

- **domcontentloaded**：HTML 解析完，DOM 就绪。速度快，但 JS 可能还没执行完，SPA 关键元素不一定渲染好了。
- **load**：所有资源（图片、CSS、JS）加载完成。当前 BasePage 使用，配合 `wait_for_selector` 兜底。
- **networkidle**：500ms 内无网络请求。SPA 有持续后台请求（分析、长轮询），永远达不到这个状态，30 秒直接超时。**禁止使用。**

最终方案：`wait_until="load"` → `wait_for_selector(keyElement)` 两步走。

---

# Skip 深度治理阶段 — 从"约束数量"到"追查根源"

问题 7：except Exception 掩盖一切，skip 成了沉默的盖子
现象：ProductPage 7 条测试全部 pytest.skip。skip reason 写的是"Cloudflare 拦截"，持续未能定位根本原因。

根因分析：
fixture 使用 try / except Exception: pytest.skip()，这是最危险的 skip 模式——它接住了所有异常类型。expect(product_name).to_be_visible() 超时抛出 AssertionError，被 except Exception 稳稳接住，然后变成"Cloudflare 拦截"。

实际上产品 ID 已经过期（服务端数据变更），页面加载后渲染的是首页 fallback，product-name 元素根本不存在。浏览器从未被 Cloudflare 拦截。

AI 的驱动逻辑："尝试让测试通过"→"反复修改仍不行"→"用 skip 跳过"→"这是环境问题"——这个链条一旦形成，AI 会自我强化，不会再深入排查。

解决方案：
1. 在 CLAUDE.md 中新增 UI fixture 编码规范：fixture 禁止使用 except Exception
2. 必须按异常类型分派：AssertionError → pytest.fail()（测试/选择器 Bug），TimeoutError → skip（环境问题）
3. 显式检查 Cloudflare 特征（response.status == 403 + page.content() 含 cloudflare 关键字），不要靠超时推断

修复效果：fixture 拆掉 except Exception 后，pytest.fail() 立刻暴露了完整 aria snapshot，显示页面渲染的是首页而非商品页。

---

问题 8：测试账号角色错误导致 15 条永久 skip
现象：Report 模块 29 条测试中 15 条 always SKIPPED，skip reason 是"管理端接口，测试账号无权限"。

根因分析：
测试使用 customer@practicesoftwaretesting.com（普通用户），但 /reports/* 端点全是管理端接口，对非管理员返回 403。
测试代码里专门写了一个 _report_or_skip(r) 辅助函数：if 403: pytest.skip()。
这等于设计时就内置了"静默降级"路径——明知账号没权限，却能跳过测试假装"通过"。
实际系统存在管理员账号 admin@practicesoftwaretesting.com / welcome01。写测试前没人验证过。

这个 bug 跟问题 7 本质上一样：skip 掩盖的不是"环境波动"，而是"设计时就没搞清楚账号权限"。

解决方案：
1. 新增 CLAUDE.md 前置校验清单：写测试前先验证账号对目标端点的权限
2. 在 config.py 中添加 ADMIN_EMAIL / ADMIN_PASSWORD 常量
3. 禁止设计"出错就 skip"的 fallback 辅助函数

修复效果：15 skip → 29 passed，并额外暴露出 2 个之前被掩盖的服务端 Bug（years 参数格式变更 + 非法输入 500）。

---

问题 9：地址校验"临时波动"实为永久故障
现象：Invoice 模块 16 条测试 SKIPPED，skip reason 是"地址校验服务异常"。

根因分析：
CLAUDE.md 踩坑 #4 记录为"地址校验随机波动"，备选地址 fallback 机制就是为此设计的。
但实践中发现，7 种不同地址变体（DE/NL/US、全称/缩写、全状态名、无状态）全部返回 422。
这是服务端地址校验数据库已失效，不是临时波动。

与问题 7/8 的区别：这确实是环境问题而非测试代码 Bug，因此 skip 保留。
但"随机波动"的描述误导了排查方向——让人以为"多试几次就好"，实际上试多少次都没用。

解决方案：
1. 更新 CLAUDE.md 踩坑 #4 为"永久故障"，不再建议 fallback 重试
2. 在 docs/AI踩坑.md 中记录完整验证过程
3. 不再对 invoice 的 16 skip 做修改（根因不可控）

---

问题 10：CLAUDE.md 踩坑速查表对 AI 无约束力
现象：CLAUDE.md 末尾有 9 行踩坑速查表，记录了已知问题。但 AI 在写新代码时从不主动查询这个表。

根因分析：
CLAUDE.md 的约束机制分两类：
- 指令型约束："禁止 XXX"、"必须 XXX"、"允许 XXX"——AI 读到就会照着执行
- 参考型信息：描述性文字、踩坑表、背景说明——AI 看到但不会主动使用

踩坑速查表是纯参考型信息。AI 在写 fixture 时不会因为 #4 说"地址校验波动"就主动查表避坑：
它没有"翻手册"的行为模式。

解决方案：
CLAUDE.md 踩坑速查表改为指向规则章节的引用表，每行只写"坑 → 看哪条规范"。
真正的约束力来源于指令型规范（skip 禁止行为、fixture 编码规范、前置校验清单），而非汇总表格。

---

全阶段工程规范总汇
经过四个阶段的踩坑与修复，项目级 CLAUDE.md 新增了以下规范：

规范类别	规范内容	解决的问题
测试用例设计	四维覆盖模型 + P0/P1/P2/P3 优先级分层	AI 不再无限制生成用例
测试用例拆分	一个模块一个 .md 文件	避免巨型文档，便于定位和修改
夹具管理	分层决策（写操作 function 级、只读 module 级）+ 高频创建控制 + 容错	减少请求量，提升稳定性，避免状态污染
pytest.skip 约束	禁止滥用 + 优先级规则 + 报告机制 + UI/API 双向覆盖	AI 不能用跳过代替修复
失败重试	自动重试 + 仅对服务端异常重试	应对不稳定环境
UI fixture 规范	fixture 禁止 except Exception；异常分派（AssertionError→fail / TimeoutError→skip）	避免 skip 掩盖测试/选择器 Bug
前置校验清单	数据有效性验证 + 账号权限预检 + fixture 正确性 + skip 必要性	写测试前发现可预防的错误
踩坑速查重构	从纯叙述表改为指向规则章节的引用表	消除无效参考型信息对 AI 的误导

踩坑经验总结（Skip 治理阶段新增）
exception 是 skip 的最大隐患：除 Exception 接住所有异常类型，把任何问题都伪装成"环境问题"
skip 的根源一定是外因才能保留：永远发生的 skip = 设计缺陷，临时波动才能 skip
写完规则再写约束：rule（禁止/必须）+ example（正确/错误代码对比）+ checklist（预检步骤）三级约束最有效
AI 不会主动查参考信息：CLAUDE.md 中的描述性表格对 AI 行为无约束力，必须转成指令型规则
新模块前置校验比事后修复高效 10 倍：写测试前花 2 分钟验证账号权限和数据有效性，省去整个 skip 治理阶段

---

# MCP 工具链集成阶段 — 从"配置即用"到"踩坑排雷"

## 问题 11：Playwright MCP 配置正确但工具列表不出现

**现象**：`~/.claude/mcp.json` 中配置了 `@playwright/mcp`，JSON 格式有效，`npx` 命令手动测试能正常启动 stdio 握手并返回工具列表。但 Claude Code 重启后工具列表里看不到 `browser_navigate`、`browser_click` 等 Playwright 工具。

**根因分析（两层）**：

**第一层：`npx` shebang 脚本无法被 Claude Code 直接执行**

```json
// ❌ 原始配置 —— npx 是 Node.js shebang 脚本 (#! /usr/bin/env node)
// Claude Code 的 MCP 进程启动器无法正确解析 shebang
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp"]
  }
}
```

对比项目中正常工作的另外两个 MCP server：

| Server | command | 类型 | 状态 |
|--------|---------|------|:--:|
| github | `/opt/homebrew/bin/mcp-server-github` | Go 编译的 Mach-O 二进制 | ✅ |
| pytest-runner | `uv` | Rust 编译的 Mach-O 二进制 | ✅ |
| playwright | `npx` | Node.js shebang 脚本 | ❌ |

结论：Claude Code 的 MCP launcher 可以 spawn 二进制可执行文件，但无法处理需要 `env` 解析 `node` 的 shebang 脚本。

**第二层：`~/.claude/mcp.json` vs `~/.claude.json` 的配置源冲突**

两个文件都声明了 `mcpServers`：
- `~/.claude.json` → `mcpServers: {}`（由 `claude mcp add` 写入，Claude Code 优先读取）
- `~/.claude/mcp.json` → 3 个 server（手动写入，**不保证被读取**）

验证证据：
```
~/Library/Caches/claude-cli-nodejs/.../
├── mcp-logs-github/         ← ✅ Claude Code 启动了 github
├── mcp-logs-pytest-runner/  ← ✅ Claude Code 启动了 pytest-runner
└── mcp-logs-playwright/     ← ❌ 不存在 —— Claude Code 根本没尝试启动
```

同一个 `mcp.json` 文件中的 3 个 server，github 和 pytest-runner 正常，playwright 被静默跳过。这是 Claude Code 的已知 bug（[#27373](https://github.com/anthropics/claude-code/issues/27373)），部分 server 会被跳过且无任何错误提示。

**解决方案**：

1. **使用 `claude mcp add` 代替手动编辑 `mcp.json`**

```bash
claude mcp add -s user playwright -- /opt/homebrew/bin/node \
  /opt/homebrew/lib/node_modules/@playwright/mcp/cli.js
```

这条命令写入 `~/.claude.json`，Claude Code 可靠读取，且自动补齐 `"type": "stdio"` 和 `"env": {}` 字段。

2. **command 使用绝对路径二进制 + 绝对路径入口文件**

```json
// ✅ 正确 —— 绕过 shebang 解析
{
  "playwright": {
    "type": "stdio",
    "command": "/opt/homebrew/bin/node",
    "args": [
      "/opt/homebrew/lib/node_modules/@playwright/mcp/cli.js"
    ],
    "env": {}
  }
}
```

修复后验证：`mcp-logs-playwright/` 目录出现，日志显示 "Successfully connected (transport: stdio) in 239ms"。

## 问题 12：浏览器引擎选择：`--browser` 不认 `chromium`

**现象**：Playwright MCP 连接成功后，`browser_navigate` 报错：

```
Chromium distribution 'chrome' is not found at /Applications/Google Chrome.app
```

想让 MCP 用已安装的 `chromium-1228`（在 Playwright 缓存里），加了 `--browser chromium`：

```
Browser "chrome-for-testing" is not installed
```

**根因**：`@playwright/mcp` 的 `--browser` 选项只接受 4 个值：

| 值 | 对应 |
|---|---|
| `chrome` | 系统 Chrome 或 Chrome for Testing |
| `firefox` | Firefox |
| `webkit` | WebKit（Safari 引擎） |
| `msedge` | Microsoft Edge |

**`chromium` 不是有效值**。虽然 Playwright 底层支持 `chromium`，但 MCP server 层做了自己的映射。

**解决方案**：用 `--executable-path` 指向 Playwright 缓存中已有的 Chromium：

```bash
claude mcp add -s user playwright -- \
  /opt/homebrew/bin/node \
  /opt/homebrew/lib/node_modules/@playwright/mcp/cli.js \
  --executable-path \
  "/Users/felix/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
```

**最终效果**：Chromium 浏览器有头模式正常打开，`browser_navigate`、`browser_snapshot`、`browser_evaluate`、`browser_click` 等 20+ 个工具全部可用。

---

## 问题 13：Playwright MCP 的破坏性工具标注

**现象**：Playwright MCP 的 23 个工具分两类：`readOnlyHint: true`（截图/快照/网络请求等只读工具）和 `destructiveHint: true`（点击/输入/提交/页面跳转等写入工具）。

**踩坑**：首次使用时未意识到 `browser_navigate` 被标记为 destructive——这意味着 Claude 调用该工具时需要权限确认。但 MCP 工具列表中的 `readOnlyHint`/`destructiveHint` 标注可以让 AI 在规划操作时准确判断哪些工具需要预警。

---

## 问题 14：MCP 配置架构 —— 三层、两入口、各自独立

**现象**：Claude Code 的 MCP 配置散落在三个文件、两个入口中。配置看起来都正确，但某个入口就是读不到工具。

**根因**：Claude Code 的 CLI 和 VSCode 插件读取不同的 MCP 配置源，互不感知。

**最终架构图**（你项目实际生效的三层）：

```
~/.claude.json                CLI 入口（claude mcp add 写入）
├── mcpServers（全局层 → 所有项目）
│   ├── playwright   = /opt/homebrew/bin/node cli.js
│   └── github       = /opt/homebrew/bin/github-mcp-server stdio
│
└── projects/practice-ai-testing/mcpServers（→ 项目层，仅本项目）
    └── pytest-runner = uv run src/common/pytest_mcp_server.py


~/.claude/mcp.json            VSCode/Cursor 沙箱入口（手写，全局）
├── playwright   = /bin/sh -c "node cli.js"     ← 需 shell 包装
└── github       = /opt/homebrew/bin/github-mcp-server stdio


项目/.claude/.mcp.json        VSCode 项目层（手写，仅本项目）
└── pytest-runner = uv run src/common/pytest_mcp_server.py
```

**书写差异对比**：

| 入口 | 配置源 | playwright | github | 写入 |
|------|--------|-----------|--------|------|
| CLI | `~/.claude.json` | `node cli.js`（绝对路径） | `github-mcp-server stdio` | `claude mcp add` |
| VSCode 全局 | `~/.claude/mcp.json` | `/bin/sh -c "node cli.js"`（包装） | 同上 | 手写 |
| VSCode 项目 | `项目/.claude/.mcp.json` | 不在此处 | 不在此处 | 手写 |

**配错的后果**：

| 错误 | 现象 | 修复 |
|------|------|------|
| playwright 的 `npx` shebang 在 CLI 无法启动 | CLI 工具列表不出现 | command 用绝对路径 node + 绝对路径 cli.js |
| playwright 在 `mcp.json` 没加 `/bin/sh -c` | VSCode 沙箱无工具列表 | command 用 `/bin/sh -c "..."` |
| 项目层 github 配了旧二进制名 `mcp-server-github` | `/mcp` 显示 1 not connected | 删除项目层 github（全局层已够） |
| `mcp.json` 里写 pytest-runner（无项目隔离） | 新项目也尝试启动 | 移到 `项目/.claude/.mcp.json` |

---

## 问题 15：GitHub MCP Server 从 Anthropic 迁移到 GitHub 官方

**现象**：终端提示 `Package no longer supported`，旧包 `@modelcontextprotocol/server-github` 已被社区废弃，并且 `/mcp` 显示 "1 not connected"。

**根因**：

| 阶段 | 包名 | 维护方 | 工具数 |
|------|------|------|:--:|
| 旧 | `@modelcontextprotocol/server-github` | Anthropic（MCP 官方，2025.4.8，已停维） | ~20 |
| 新 | `github/github-mcp-server` | **GitHub 自己**（v1.5.0，29.8K stars） | **~80** |

**两个问题同时出现**：

1. 旧二进制名 `mcp-server-github`（词序错误）。新包的二进制名是 `github-mcp-server`，需要配合 `stdio` 子命令启动。
2. `~/.claude.json` 的项目作用域遗留着旧配置，因为它在 `projects/xxx/mcpServers` 下，修改全局 `mcpServers` 不会自动同步过去。

**解决方案**：
1. `brew install github-mcp-server` 安装新包
2. 更新 **三处**配置：`~/.claude.json` 全局层 + `~/.claude.json` 项目层 + `~/.claude/mcp.json`
3. 项目层删除 github（只留 pytest-runner），避免配置强关联

```bash
# 新二进制用法
github-mcp-server stdio      # 需要 stdio 子命令
```

---

## 工程规范总汇

| 规范类别 | 规范内容 | 解决的问题 |
|---------|---------|----------|
| 三层配置架构 | `~/.claude.json`（CLI 全局+项目层）+ `~/.claude/mcp.json`（VSCode 全局）+ `项目/.claude/.mcp.json`（VSCode 项目层）互不读取，双端分别维护 | 某入口工具列表为空 |
| 作用域隔离 | 全局层放通用工具（playwright + github），项目层放专用工具（pytest-runner） | 新项目误启动不存在的 server |
| CLI 命令格式 | `~/.claude.json`：用 `claude mcp add` 写入，command 用绝对路径 node + 绝对路径入口文件 | shebang 脚本无法解析 |
| VSCode 格式 | `~/.claude/mcp.json`：手写，playwright 需 `/bin/sh -c` 包装，github 加 `stdio` 参数 | VSCode 沙箱无法 spawn shebang |
| 浏览器选择 | `--browser` 仅支持 chrome/firefox/webkit/msedge；使用已安装的 Chromium 需 `--executable-path` | "chromium" 不是有效 browser 值 |
| GitHub Server | 从 `@modelcontextprotocol/server-github`（停维）迁移到 `github-mcp-server stdio`，新二进制词序不同 | 旧包已废弃，新包 80 工具 |
| MCP 验证流程 | 新配置后检查 `~/Library/Caches/claude-cli-nodejs/.../mcp-logs-{name}/` 确认进程启动 | 判断是配置问题还是启动问题 |
| MCP 输出目录 | `.playwright-mcp/` 加入 `.gitignore` | 截图/快照/日志不进入版本库 |

## 踩坑经验总结

- **三层、两入口、互不感知**：CLI 读 `~/.claude.json`，VSCode 沙箱读 `~/.claude/mcp.json` + `项目/.claude/.mcp.json`，修改一个不代表另一个也生效
- **作用域决定你的 server 会不会跨项目炸**：全局层（playwright+github）所有项目通用；项目层（pytest-runner）仅当前项目。放错层就出现"新项目启动没有的 server"
- **可执行 vs shebang 是硬门槛**：Claude Code 的 MCP launcher 只能 spawn 二进制，不能解析 `#!/usr/bin/env node`。VSCode 沙箱还要额外加 `/bin/sh -c` 包装
- **工具不出现 = 沉默失败**：Claude Code 不会提示 MCP server 启动失败，只能通过日志目录是否存在来判断
- **`settings.local.json` 的 schema 校验**：Claude Code 对 settings.json 系列文件有内置 JSON Schema 校验，`additionalDirectories` 必须放在 `permissions` 下

---

## Jenkins 凭据作用域（手动配置，非 AI 任务）

`withCredentials` 在 Pipeline 脚本中读取凭据，Scope **必须选 Global (unrestricted)**。选 System 仅供给 Jenkins 系统底层使用，脚本内 `withCredentials` 读不到。

手动配置步骤：

1. Dashboard → Manage Jenkins → Credentials → Add Credentials → Secret text
2. Scope: **Global**、Secret: `ghp_xxx`、ID: 和 Jenkinsfile 里 `credentialsId` 对齐
3. 确认 GitHub Token 的 Scopes 勾选了 `repo`

> 这是 Jenkins 页面的手动操作，AI 无法执行。写入踩坑文档而非 CLAUDE.md，因为 CLAUDE.md 是约束 AI 行为的规范，涉及手动操作的配置应放在这里。

---

## AI 协作开发流程范式

经过七个阶段（用例设计 → 脚本开发 → CI/UI 测试 → Skip 治理 → MCP 集成 → 工程化 → CI 治理），沉淀出一套可复用的 AI 协作范式：

```
发现问题 → 解决当前问题 → 提炼为规范 → 约束到 CLAUDE.md → AI 下次自动遵守
```

### 为什么这个循环是关键

AI 每次犯错都是**系统性漏洞**的暴露——不只是这一次的 bug，而是未来无数次会重复犯的同类错误。单次修复只能解决当下，把教训写入 CLAUDE.md 等于给 AI 装了一条永久规则。

| 阶段 | 发现的问题 | 约束到 CLAUDE.md | 效果 |
|------|------|------|------|
| 用例设计 | AI 无限生成用例，永远补不完 | 四维覆盖 + P0-P3 优先级 | AI 知道”够了” |
| 脚本生成 | AI 滥用 `pytest.skip` | skip 四禁止 + 三前置 + 允许表 | skip 不能再乱用 |
| 夹具管理 | 高频注册用户，服务端 500 | 分层决策 + 高频创建控制 | 请求量大幅下降 |
| CI 调试 | 本地过、CI 炸，改测试代码无效 | CI 失败处理优先级表 | 先怀疑环境再怀疑代码 |
| UI 等待 | `wait_for_timeout` 碰巧过 | 禁令 + 显式等待矩阵 | 零 `wait_for_timeout` |
| UI 等待 | `networkidle` 永远卡死 | BasePage 使用 `load` 方案 | 93s 变 37s |
| SPA 渲染 | Cloudflare 拦截 CI Runner | CI 已知限制 + 自动检测跳过 | 不再误报失败 |
| **Skip 治理** | **fixture 用 except Exception 掩盖 ID 过期** | UI fixture 编码规范 + 异常分派 | 7 skip → 9 pass，暴露真实 Bug |
| **Skip 治理** | **测试账号角色错误导致 15 条永久 skip** | 前置校验清单 + config.py 管理员账号 | 15 skip → 29 pass |
| **Skip 治理** | **地址校验"随机波动"为永久故障** | 踩坑 #4 更新为"不可修复" | 16 skip 有明确根因，不再误导排查 |
| **Skip 治理** | **踩坑速查表对 AI 无约束力** | 改为引用表，约束力来源于指令型规范 | 消除无效参考型信息 |
| **MCP 集成** | **`mcp.json` 配置被静默跳过，工具不出现** | `claude mcp add` 写入 `.claude.json` + 绝对路径二进制 | 20+ 工具可用，AI 能直接操控浏览器 |
| **MCP 集成** | **`npx` shebang 脚本 Claude Code 无法执行** | command 用绝对路径 node + 绝对路径入口文件 | 启动成功（239ms） |
| **MCP 集成** | **CLI 能用但 VSCode 插件无工具** | `~/.claude.json` + `~/.claude/mcp.json` 双端维护 + `/bin/sh -c` 包装 | 两种入口均可使用 |

### 核心原则

1. **每次犯错都是一次 CLAUDE.md 投资**——修完不写规范等于白修
2. **CLAUDE.md 越写越厚不是坏事**——每条规则都是实打实的踩坑教训
3. **约束越具体，AI 越可靠**——“禁止”比”建议”有效，”示例”比”描述”有效
4. **规范向前兼容**——新加的规则不应推翻旧规则，而是在旧规则上补充边界

### 最终效果

```
项目初期：AI 每 3 次操作犯 1 次规约错误
CLAUDE.md 完善后：AI 几乎不再犯已知规约错误
```

真正的效率提升不是”AI 变得更聪明了”，而是”AI 踩过的坑不会再踩第二遍”。

---

# 测试工程化阶段 —— 从”能跑”到”企业级”

## 问题 15：Playwright MCP 调用策略与 CLAUDE.md 强制执行冲突

**现象**：CLAUDE.md 规定”新建 Page Object 必须用 MCP 验证”，但 memory 文件规定”调用 MCP 前必须先征得用户同意”。两条规则互相矛盾，AI 每次新建页面都陷入两难。

**根因分析**：

CLAUDE.md 写于”发现 MCP 好用、推全员强制执行”的阶段；memory 写于后来发现”每次调用 DOM 快照消耗大量 token”的阶段。两条规则没有协调——一个说”必须调”，一个说”先问再调”。

**解决方案**：

1. CLAUDE.md 改为分层策略：**首次探索用 MCP（保存快照供复用）→ 日常开发优先复用已有快照和文档 → 反复修不好的 Bug 时才再调 MCP**
2. memory 文件同步更新，消除冲突
3. MCP 不再是”每次必调”，而是”按需调用”

**效果**：AI 行为一致，不再纠结是否调用；token 消耗大幅降低。

---

## 问题 16：测试账号频繁被锁——本地/CI 共用同一个账号

**现象**：本地测试和 Jenkins CI 使用同一个测试账号。错误密码测试反复跑 → 登录失败次数超阈值 → 账号被锁 → 所有依赖登录的测试全炸。

**根因分析**：

这是测试工程化的典型问题——多环境共享同一套凭据。错误密码测试自身就消耗失败配额，每跑一次就离锁定更近一步。

**解决方案**：

1. **三环境账号隔离**：本地 `test-local-*`、Jenkins `jenkins-ci-*`、GitHub Actions（预留 `GHA_TEST_*`）
2. **唯一数据源**：所有凭据统一在 `config.py` 中维护，Jenkinsfile 通过 `uv run python -c “from config import JENKINS_TEST_EMAIL”` 动态读取
3. **环境变量桥接**：CI 通过 `env.TEST_USER_EMAIL` 覆盖默认值，不硬编码凭据

**设计原则**：本地开发不设环境变量，`os.getenv("TEST_USER_EMAIL")` 取不到就走 fallback 拿本地 `TEST_USER_EMAIL` 常量值。Jenkins 在 Setup 阶段从 `config.py` 读取 **`JENKINS_TEST_EMAIL`** 常量，注入为环境变量 `TEST_USER_EMAIL` 覆盖 fallback。注入失败就报错停掉 pipeline。**禁止 CI 注入失败后静默降级到本地 fallback**——这会把 CI 的故障（Jenkins 账号过期）转嫁成本地账号被锁。

---

## 问题 17：破坏性测试与正常测试的账号分离

**现象**：`test_wrong_password_triggers_server_error` 输入错误密码 → 服务端累计失败次数 → 账号被锁 → 5 条正常用例跟着瘫痪。1 条 skip 变 6 error。

**根因分析**：

密码错误、多次 401、Token 过期等”负面场景”测试自身就会消耗服务端的失败配额。这跟”被测系统有 Bug”完全不同——这是测试代码的正常行为导致了测试基础设施的崩溃。

**解决方案**：

1. **正常用例用稳定账号** —— Happy Path 和一般异常路径使用默认 `TEST_USER_*`
2. **会触发锁定的测试用独立”牺牲品”账号** —— 用完即弃
3. **标记为破坏性测试** —— `@pytest.mark.destructive`，日常 `pytest -m “not destructive”` 跳过，CI/上线前审计时全量跑
4. CLAUDE.md 新增”破坏性测试账号隔离”规范 + `pyproject.toml` 注册 marker

---

## 问题 18：Angular zone.js HTTP 拦截器与 Playwright wait_until 的死锁

**现象**：ProfilePage 错误密码测试在 MCP 浏览器中正常通过（API 返回 400 + alert 闪现），但在 pytest/standalone Playwright 中表单完全不触发 API 请求。fill/blur/force click/dispatchEvent 均无效。

**排查过程**：

| 步骤 | 假设 | 结果 |
|------|------|------|
| 1 | 密码强度不够 | ❌ 改用强密码仍不行 |
| 2 | click 未触发 | ❌ force click 也不行 |
| 3 | headless 模式差异 | ❌ headless=False 也不行 |
| 4 | launch args 差异 | ❌ 无关 |
| 5 | `fill()` vs `type()` | ❌ 无关 |
| 6 | **`wait_until='load'` → Angular zone.js 未初始化** | ✅ **根因** |

**根因链**：

```
BasePage.goto(wait_until='load')
  → DOM 就绪，但 Angular zone.js 来不及初始化
  → HTTP 拦截器（XHR/fetch 代理）未生效
  → fill() 填表 + click() 提交 → 表单值变化但 Angular 不拦截
  → 请求不发，API 不调用
```

**修复方案已验证**：`ProfilePage.goto()` 改为 `wait_until='networkidle'` → standalone 和 pytest 均通过 ✅

**但 networkidle 不能用于生产**：靶场站点存在 Cloudflare RUM（`/cdn-cgi/rum`）和 Challenge 心跳等永不关闭的连接，`networkidle` 永远等不到”网络空闲”状态 → 30s 超时 → 1 skip 变 6 error。

**最终决策**：保留 `wait_until='load'`，错误密码测试 try/except skip 兜底。docstring 完整记录根因 + 修复方案 + 不可用原因，待换靶场或去 Cloudflare 后恢复。

---

## 问题 19：CI 工程化——测试凭据统一管理 vs 散落各处

**现象**：Jenkinsfile 中硬编码了 Jenkins 专用账号，config.py 有自己的本地账号，两处各管各的。一旦需要换账号，要改两个文件。

**根因分析**：

凭据散落在 CI 配置文件中的本质原因是：CI 配置语言（Groovy/YAML）和 Python 代码之间没有桥接机制。

**解决方案**：

1. **config.py 作为唯一数据源**：所有环境的账号凭据集中定义
   ```python
   TEST_USER_EMAIL = os.getenv(“TEST_USER_EMAIL”, “本地默认值”)
   JENKINS_TEST_EMAIL = “jenkins-ci-xxx@example.com”  # Jenkins 专用
   # GHA_TEST_EMAIL = “...”  # GitHub Actions 预留
   ```
2. **Jenkinsfile 通过 Python 桥接读取**：
   ```groovy
   env.TEST_USER_EMAIL = sh(
       script: '''uv run python -c “from config import JENKINS_TEST_EMAIL; print(JENKINS_TEST_EMAIL)”''',
       returnStdout: true
   ).trim()
   ```
3. **新增/更换账号只改 config.py 一处**，CI 自动生效

---

## 本阶段工程规范总汇

| 规范类别 | 规范内容 | 解决的问题 |
|---------|---------|----------|
| MCP 调用策略 | 首次探索用 MCP → 日常复用快照 → Bug 调试才再调 | MCP 规则冲突 + token 浪费 |
| 多环境账号隔离 | 本地/Jenkins/GHA 三环境各自独立账号，config.py 唯一数据源 | 并发登录冲突、互相踢下线 |
| 破坏性测试隔离 | 正常测试 stable 账号 + 破坏性测试 sacrificial 账号 + `@pytest.mark.destructive` | 错误密码测试导致账号被锁，正常用例瘫痪 |
| CI 凭据统一管理 | config.py 集中定义 → CI 通过 `uv run python` 动态读取 → 环境变量注入 | 凭据散落多处，换号改多个文件 |
| Angular zone.js 陷阱 | `wait_until='load'` 下 Angular HTTP 拦截器未初始化，需 `networkidle` 但 Cloudflare 阻止 | 表单提交不触发 API 请求 |
| _is_cloudflare 提取 | 4 个测试文件重复定义 → `tests/ui/conftest.py` 统一共享 | 代码重复，维护分散 |
| CLAUDE.md 规则维护 | 定期审计 CLAUDE.md 与实际代码的一致性（组件列表、目录结构、CI 触发路径） | 文档腐烂，误导后续开发 |

## 踩坑经验总结（本阶段新增）

- **测试账号是消耗品，不是常量**：错误密码测试每跑一次就消耗一次失败配额。正常测试和破坏性测试必须账号隔离
- **网络空闲不是银弹**：`networkidle` 在有持续连接的站点（Cloudflare RUM）上永远等不到，成也它败也它
- **凭据统一管理是工程化第一课**：一个配置文件 → CI 动态读取 → 环境变量注入，三级桥接比硬编码多 10 分钟但省 10 天排查
- **Angular SPA + Playwright = 隐形陷阱**：`wait_until='load'` 下 zone.js 可能来不及初始化，表现为”表单填了但 API 不触发”的诡异 bug
- **MCP 是利器但非必备**：首次探索时用一次保存快照，后续靠快照+文档+代码就能完成大部分工作。省 token 的同时保持开发效率
- **CLAUDE.md 需要定期审计**：文档与代码必须一致。组件列表、目录结构、CI 路径——任何一处不一致都会误导后续所有开发

---

## 本阶段流程范式更新

| 阶段 | 发现的问题 | 约束到 CLAUDE.md | 效果 |
|------|------|------|------|
| **工程化** | **MCP 调用策略与 CLAUDE.md 冲突** | MCP 分层策略（首次探索/日常复用/Bug 调试） | AI 行为一致，token 消耗降低 |
| **工程化** | **本地/Jenkins 共用账号导致频繁锁定** | 多环境账号隔离 + config.py 唯一数据源 | 独立隔离，互不干扰 |
| **工程化** | **错误密码测试消耗失败配额** | 破坏性测试账号隔离 + `@pytest.mark.destructive` | 正常测试再也不被连带炸毁 |
| **工程化** | **Jenkinsfile 硬编码凭据** | CI 通过 `uv run python -c` 从 config.py 动态读取 | 换号只改一处 |
| **工程化** | **Angular zone.js + load + Cloudflare 死锁** | ProfilePage 测试 docstring 完整记录 | 有据可查，条件成熟时一分钟恢复 |
| **工程化** | **_is_cloudflare 4 处重复** | 提取到 tests/ui/conftest.py 共享 | 代码不重复 |

---

# CI 稳定性与靶场环境治理阶段 —— 从"修代码"到"接受现实"

## 问题 20：Toolshop 靶场全线不稳定——公开服务与本地 Docker 均不可靠

**现象**：为了拿到一份干净的 Allure 报告用于面试，反复修测试、改 CI、排查账号问题，花了两整天。每次 Jenkins 跑的失败原因都不一样——有时 401，有时 500，有时 Timeout。

**根因分析**：

Toolshop 作为公开练习靶场，存在多层不可控因素：

| 环境 | 问题 | 可控？ |
|------|------|:--:|
| 公开 API 服务 | 限流（高频 login 触发）、数据周期性重建（账号/商品 ID 全变）、地址校验外部服务永久失效 | ❌ |
| 公开 UI 站点 | Cloudflare 反爬（GitHub Actions 全封）、Angular SPA 性能波动 | ❌ |
| **本地 Docker** | **Angular dev mode（ng serve）+ live-reload WebSocket → `networkidle` 永远等不到 → UI 测试比远程还慢** | ❌ |

最初以为"Docker 本地部署就全部解决了"，实际验证后发现 **Angular dev mode 比线上 production build 还差**——线上至少 `wait_until='load'` 能用，dev mode 的长连接让基础导航都超时。

**解决方案**：

1. 接受 Toolshop 的天花板——API 515 passed + 16 skip（地址校验永久故障），UI 109 passed + 6 skip（地址查找 + search box），这就是 Tapshop 能跑的极限
2. CI 改并行执行（API ∥ UI），减少串行对服务器的持续压力
3. 不管测试结果，都推送 Allure 报告到 gh-pages（`|| true` 兜底）
4. 不再投入时间"修环境"——果断切到 waynboot-mall（本地 Docker 全栈可控）

**核心教训**：**选对靶场比写好代码更重要。** 一个不稳定的被测对象，会消耗你 80% 的时间去排查"是不是环境又挂了"，而不是提升测试质量。

---

## 问题 21：Faker seed(0) + .unique 的跨 run 碰撞

**现象**：第一次 CI run 全过，第二次 CI run 出现大量 `409 Conflict`——"email already exists"、"slug already exists"。

**根因分析**：

数据工厂设计的核心是 `Faker.seed(0) + .unique` 模式——同一次 run 内保证不重复，跨 run 可复现。但 `.unique` 的"唯一"只在当前进程 session 内有效。**固定 seed 意味着每次 run 生成相同的值序列**。

第一次 run 在服务器上创建了 `e2e-brand-brave@...`，第二次 run 还用这个 email 注册 → 409。47 处散落 `uuid.uuid4()` 收到工厂函数后，又遇到了相反的问题：过于确定。

**解决方案**：

工厂函数（`generate_unique_email`、`generate_unique_slug`）内部追加 4 位 `uuid.uuid4().hex` 后缀，兼顾可读性与跨 run 唯一性。47 个调用方不需要改一行代码——这就是数据工厂收敛的价值。

```
# 旧：Faker 确定性 → 跨 run 撞 → 409
"e2e-brand-brave"

# 新：Faker 可读性 + uuid 唯一性
"e2e-brand-brave-a7f3"
```

---

## 问题 22：多模块共享 TEST_USER_EMAIL 触发服务端限流

**现象**：全量测试跑到后半段，大量测试返回 401 Unauthorized。最初以为是 JWT token 过期，加了 `uc.login()` 刷新后发现 login 本身也被拒绝——`{"error": "Unauthorized"}`。

**根因分析**：

10+ 个 API test 文件都使用 `TEST_USER_EMAIL` 登录。每个 module 结束时调用 `uc.logout()` 注销 token。服务器把这当成异常行为——同一账号反复 login/logout 10 余次 → 限流 → 拒绝后续登录。

加上我们新增的账号健康检查（`pytest_configure` 阶段先 login 验证一次），登录次数进一步增加。冻结 GitHub Actions 后 Jenkins 独跑，所有登录集中在一条 Pipeline 里，超过了限流阈值。

更深层的问题在个别测试文件中——

**问题 22.1：function 级 fixture 每用例重复 login**

`test_contact_api.py` 的 `_auth_contact` 是 function scope，引用了 56 次——意味着 Contact 模块自己就 login/logout 50+ 次。`test_favorite_api.py` 同理 ~15 次。服务器直接把账号当攻击者封了。

**解决方案**：

1. function 级 fixture 改为复用 module 级 token，不再重复 login（`_auth_contact` → delegate to `_mod_auth_contact`）
2. 确实需要新鲜 token 的模块（Invoice、Product Spec）用独立账号注册，不走 `TEST_USER_EMAIL`
3. CLAUDE.md 踩坑 #2 更新：不仅 token 会过期，**高频 login 也会触发限流**——优先复用 token

**核心发现**：这个问题一直在代码里潜伏，之前没暴露是因为双 CI 跑把登录分散了。不是"代码写错了"，是"工程规模超过阈值后暴露了隐藏 bug"。

---

## 问题 23：Jenkins 串行执行 API→UI → 服务器耗尽 → UI 全部超时

**现象**：API 测试 515 passed（12 分钟），UI 测试全部 `TimeoutError`——在登录重定向时等待 `/account` 30 秒超时。本地跑全绿。

**根因分析**：

GitHub Actions 的 `tests.yml` 是 API ∥ UI 两个 job **并行**执行，Jenkins 是**串行**执行。API 测试在 12 分钟内向服务器发 500+ 个请求后，服务器资源耗尽。UI 测试再登录时，页面加载速度极慢，登录重定向超时。

不是 Cloudflare 拦截，不是代码问题——就是服务器累了。

**解决方案**：Jenkinsfile 改为 API ∥ UI 并行执行（`parallel { stage('API') {} stage('UI') {} }`），跟 GitHub Actions 一致。API 515 passed + 16 skip，UI 109 passed + 6 skip。

---

## 问题 24：Jenkins heredoc 缩进致 gh-pages 推送静默失败

**现象**：Jenkins 一切正常——API passed、UI passed、Allure 报告生成成功、Deploy 阶段显示 SUCCESS——但 gh-pages 上的报告从未更新。

**排查过程**：

Jenkins 日志显示 Deploy 阶段执行了：
```
+ cd _site
+ cat
[Pipeline] }
[Pipeline] // retry
```

`cat` 之后直接结束，`git init`、`git add`、`git push` 从未被执行。`retry(3)` 也没有重试——shell 脚本本身 exit 0，没有报错。

**根因**：`sh ''' ... '''` 中的 bash heredoc 终结符 `HTMLEOF` 有缩进。bash 的 `<<` heredoc 要求终结符在**行首**，缩进了它就不认识，把后续的 `git init ... git push` 全当 HTML 内容吞入 `index.html`。

```
# ❌ 终结符有缩进 → git push 被吞
cat > index.html << 'HTMLEOF'
    <!DOCTYPE html>
    ...
    HTMLEOF        ← 没在行首，heredoc 不会结束！
    git init       ← 这行也写进了 index.html
    git push       ← 从未执行

# ✅ 终结符顶格
HTMLEOF            ← 在行首，heredoc 正确结束
    git init       ← 正常执行
```

**修复**：终结符 `HTMLEOF` 顶格书写。修复后 gh-pages 立即推送成功。

**这个 bug 可能一直存在**——之前 gh-pages 更新靠的是 GitHub Actions 的 `peaceiris/actions-gh-pages@v4`，不是 Jenkins。Jenkins 的 git push 从未真正执行过。

---

## 问题 25：双 CI（GitHub Actions + Jenkins）并发冲突

**现象**：git push 后 GitHub Actions 和 Jenkins 同时触发。两个 CI 拿着同样的 Faker seed(0) 生成同样的测试数据 → 同时往服务器注册相同 email/创建相同 slug → 409 冲突 + 服务端限流。

**解决方案**：

1. GitHub Actions 冻结（`workflow_dispatch` 手动触发），Jenkins 接管全部 CI
2. GHA 冻结原因：Cloudflare 封 Runner IP，UI 跳过分质残缺报告
3. 冻结后 Jenkins 独享靶场，稳定性显著提升

---

## 本阶段工程规范总汇

| 规范类别 | 规范内容 | 解决的问题 |
|---------|---------|----------|
| 靶场选型 | 选可控的靶场（本地 Docker 全栈）比修环境重要 100 倍；公开靶场有天然天花板 | 两整天时间浪费在排查环境而非提升测试质量 |
| 数据工厂跨 run 唯一性 | `Faker.seed(0) + .unique` 仅 session 内唯一，跨 run 需 uuid 后缀 | 固定 seed 导致跨 CI run 数据碰撞 409 |
| 登录频率控制 | 多模块共享账号时，避免 function 级 fixture 重复 login；优先复用 module token | 高频 login/logout 触发服务端限流，401 链式传染 |
| CI 并行执行 | API 和 UI 测试并行跑，避免串行耗尽靶场资源 | 串行时后半段测试因服务器过载超时 |
| heredoc 书写规范 | bash heredoc 终结符必须顶格（不能有缩进）；Groovy `sh '''` 中的缩进不影响 bash 执行 | git push 被静默吞掉，gh-pages 从未更新 |
| 单 CI 运行 | 同一靶场同一时间只跑一个 CI，避免并发数据冲突 | 多 CI 同 seed + 同数据 = 409 + 限流 |

## 踩坑经验总结（本阶段新增）

- **选对靶场比写好代码更重要**：不稳定的被测对象消耗 80% 排查时间。waynboot-mall（本地 Docker 全栈）没有限流、没有 Cloudflare、没有数据重建
- **确定性种子不是银弹**：Faker seed(0) 在同 run 内确保唯一，跨 run 需要非确定性后缀（uuid）
- **"代码一直没动"不等于"没有 bug"**：Contact 和 Favorite 的 function 级高频 login 一直存在，只是之前没超过服务端限流阈值
- **bash heredoc 缩进是隐形杀手**：Groovy 代码缩进美化可能让 heredoc 终结符带缩进 → shell 命令被吞 → retry 也无效（shell exit 0）
- **双 CI 不是高可用，是互相攻击**：同 seed + 同数据 + 同时跑 = 互相撞
- **Jenkins 跟 GHA 不是等价替换**：需要改并行策略、去 `--with-deps`、修 heredoc、加重试。不是改了 URL 就能跑

---

## 本阶段流程范式更新

| 阶段 | 发现的问题 | 约束到 CLAUDE.md | 效果 |
|------|------|------|------|
| **CI 治理** | **公开靶场 + 本地 Docker 均不可靠** | CI/CD 架构切换为 Jenkins 主力 + GHA 冻结 | 单一 CI 环境，消除并发冲突 |
| **CI 治理** | **多模块共享 TEST_USER_EMAIL 触发限流** | 踩坑 #2 更新：优先复用 token，避免高频 login | function fixture 不再重复登录 |
| **CI 治理** | **Faker seed(0) 跨 run 碰撞** | 数据工厂规范：`generate_unique_email/slug` 含 uuid 后缀 | 跨 run 零碰撞 |
| **CI 治理** | **Jenkins 串行 API→UI 耗尽服务器** | CI Pipeline 改 API ∥ UI 并行执行 | API + UI 均全绿 |
| **CI 治理** | **heredoc 缩进致 git push 静默失败** | Jenkinsfile 终结符顶格 | gh-pages 推送成功 |
| **CI 治理** | **双 CI 并发冲突** | GitHub Actions 冻结，Jenkins 独享靶场 | 消除并发数据碰撞 |