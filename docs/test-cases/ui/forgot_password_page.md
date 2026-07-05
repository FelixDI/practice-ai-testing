# ForgotPasswordPage 模块 UI 测试用例

> **被测页面**：Toolshop 忘记密码页（`/auth/forgot-password`）  
> **编写规范**：遵循项目 CLAUDE.md  
> **页面说明**：仅一个 email 输入框 + 提交按钮，无需登录。提交后显示确认消息（i18n key: `page.forgot-password.confirm`），无格式校验。

---

## 页面功能区域

| 区域 | data-test | 说明 |
|------|------|------|
| 表单 | `forgot-password-form` | 表单容器 |
| 邮箱 | `email` | 文本输入 |
| 提交 | `forgot-password-submit` | Set New Password 按钮 |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FORGOT_001 | P0 | 忘记密码页正常加载 | 无 | 访问 `/auth/forgot-password` | email / forgot-password-submit / forgot-password-form 均 visible |
| UI_FORGOT_002 | P0 | 有效邮箱提交显示确认消息 | ForgotPasswordPage 已加载 | 输入邮箱 → 点击 Set New Password | alert 含 "page.forgot-password.confirm" |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FORGOT_003 | P1 | 空邮箱提交页面不崩溃 | ForgotPasswordPage 已加载 | 不输入 → 点击提交 | 页面不崩溃，Header 仍可见 |

## P3 深度防御

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FORGOT_004 | P3 | XSS 注入不崩溃 | ForgotPasswordPage 已加载 | 输入 `<script>alert(1)</script>` → 提交 | 页面不崩溃，Header 仍可见 |
