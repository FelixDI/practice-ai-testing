```

**文档定位**

这份文档记录了系统化学习 AI 协作自动化测试过程中，从零到一搭建框架、从混乱到有序、从“玩具”到“工程化”的每一个关键问题与解决方案。这些经验可以作为未来任何 AI 测试项目的起点。

# 第一阶段：测试用例设计 — 从“漫无目的”到“精准覆盖”

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


# 第二阶段：测试脚本生成 — 从“能跑”到“跑得稳”

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

# 第三阶段：CI/CD 与 UI 测试 — 从"本地跑通"到"CI 稳定"

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

# 第四阶段：Skip 深度治理 — 从"约束数量"到"追查根源"

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

全阶段工程规范总汇（第四阶段更新）
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

踩坑经验总结（第四阶段新增）
exception 是 skip 的最大隐患：除 Exception 接住所有异常类型，把任何问题都伪装成"环境问题"
skip 的根源一定是外因才能保留：永远发生的 skip = 设计缺陷，临时波动才能 skip
写完规则再写约束：rule（禁止/必须）+ example（正确/错误代码对比）+ checklist（预检步骤）三级约束最有效
AI 不会主动查参考信息：CLAUDE.md 中的描述性表格对 AI 行为无约束力，必须转成指令型规则
新模块前置校验比事后修复高效 10 倍：写测试前花 2 分钟验证账号权限和数据有效性，省去整个 skip 治理阶段

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

经过三个阶段（用例设计 → 脚本生成 → CI/UI 测试），沉淀出一套可复用的 AI 协作范式：

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

```