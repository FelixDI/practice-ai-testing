# ContactPage 模块 UI 测试用例

> **被测页面**：Toolshop 留言表单页（`/contact`）  
> **编写规范**：遵循项目 CLAUDE.md  
> **页面说明**：联系客服留言表单，含 7 个表单控件（4 文本+1 下拉+1 附件+1 提交），无需登录。注：该表单为 Demo，提交后无可见成功反馈。

---

## 页面功能区域

| 区域 | data-test | 说明 |
|------|------|------|
| 名字 | `first-name` | 文本输入，必填 |
| 姓氏 | `last-name` | 文本输入，必填 |
| 邮箱 | `email` | 文本输入，必填，email 格式校验 |
| 主题 | `subject` | 下拉选择，必填，6 个选项 |
| 消息 | `message` | 文本输入，必填，最少 50 字符 |
| 附件 | `attachment` | 文件上传，仅 .txt，0kb |
| 提交 | `contact-submit` | 提交按钮 |

### 验证错误信息

| 触发条件 | 错误信息（role=alert） |
|------|------|
| 空字段 | "{Field} is required" |
| 无效 email 格式 | "Email format is invalid" |
| 消息 < 50 字符 | "Message must be minimal 50 characters" |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CONTACT_001 | P0 | 留言表单页正常加载 | 无 | 访问 `/contact` | 7 个 form 元素（first-name/last-name/email/subject/message/attachment/contact-submit）均 visible |
| UI_CONTACT_002 | P0 | 空表单提交显示必填校验 | ContactPage 已加载 | 直接点击 Send | 5 个 alert 提示必填（First name/Last name/Email/Subject/Message is required） |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CONTACT_003 | P1 | 无效邮箱格式显示校验错误 | ContactPage 已加载 | 输入无效邮箱 → 点击 Send | alert "Email format is invalid" |
| UI_CONTACT_004 | P1 | 消息少于 50 字符显示校验错误 | ContactPage 已加载 | 输入短消息 → 点击 Send | alert "Message must be minimal 50 characters" |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CONTACT_005 | P2 | 主题下拉包含占位 + 6 个选项 | ContactPage 已加载 | 展开 subject dropdown | 7 个 option：Select a subject * + Customer service / Webmaster / Return / Payments / Warranty / Status of my order |

## P3 深度防御

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CONTACT_006 | P3 | XSS 注入在表单字段不崩溃 | ContactPage 已加载 | 输入 `<script>alert(1)</script>` 到所有 textbox → 点击 Send | 页面不崩溃，Header 可见 |
