# ProfilePage 模块 UI 测试用例

> **被测页面**：Toolshop 个人资料页（`/account/profile`）  
> **编写规范**：遵循项目 CLAUDE.md  
> **页面说明**：需登录。3 个功能区：① 个人信息编辑（名字/邮箱/电话/地址）+ ② 密码修改 + ③ TOTP 两步验证设置。

---

## 页面功能区域

| 区域 | data-test | 说明 |
|------|------|------|
| 页面标题 | `page-title` | "Profile" |
| 名字 | `first-name` | 文本输入（预填） |
| 姓氏 | `last-name` | 文本输入（预填） |
| 邮箱 | `email` | 文本输入（预填） |
| 电话 | `phone` | 文本输入 |
| 地址 | `street` `postal_code` `city` `state` `country` | 地址字段 |
| 更新按钮 | `update-profile-submit` | 提交个人信息 |
| 当前密码 | `current-password` | 改密码验证 |
| 新密码 | `new-password` | 新密码输入 |
| 确认新密码 | `new-password-confirm` | 确认新密码 |
| 改密按钮 | `change-password-submit` | 提交密码修改 |
| TOTP 密钥 | `totp-secret` | TOTP 密钥（只读/生成） |
| TOTP 验证码 | `totp-code` | 输入验证码 |
| 验证按钮 | `verify-totp` | 验证 TOTP |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROFILE_001 | P0 | 个人资料页正常加载 | 已登录 | 访问 `/account/profile` | page-title "Profile" visible；3 个提交按钮 visible |
| UI_PROFILE_002 | P0 | 个人信息字段预填 | 已登录 | 访问 `/account/profile` | first-name / last-name / email 非空（注册时填的值） |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROFILE_003 | P1 | 密码修改区域正常渲染 | 已登录 | 访问 profile 页 | 4 个密码相关元素 visible（无客户端校验） |
| UI_PROFILE_004 | P1 | 错误密码触发服务端错误 | 已登录 | 填错 current-password + 新密码 → 提交 | 有 alert 错误提示（demo 可能不返回） |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROFILE_005 | P2 | 地址字段全部渲染 | 已登录 | 访问 profile 页 | street/postal_code/city/state/country 均 visible（country 为 textbox 非 select） |

## P3 深度防御

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROFILE_006 | P3 | XSS 注入不崩溃 | 已登录 | 在 first-name 输入 `<script>alert(1)</script>` → 更新 | 页面不崩溃，Header 可见 |
