# LoginPage 模块 UI 测试用例

> **被测页面**：Toolshop 登录页（`/auth/login`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **页面说明**：登录页提供邮箱+密码表单登录、Google 第三方登录入口、注册/忘记密码链接。

---

## 页面功能区域

| 区域 | 说明 | data-test |
|------|------|------|
| 登录表单 | 邮箱 + 密码 + 提交按钮 | login-form, email, password, login-submit |
| 错误提示 | 登录失败消息 | login-error |
| 注册链接 | 跳转到注册页 | register-link |
| 忘记密码 | 跳转到密码重置页 | forgot-password-link |
| 导航栏 | 公共导航栏（复用 Header） | nav-home, nav-sign-in, nav-categories 等 |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_LOGIN_001 | P0 | 正常登录成功 | 已知有效测试账号 | 1. 访问 `/auth/login` 2. 输入正确邮箱和密码 3. 点击 Login 按钮 | 跳转到 `/account`；导航栏出现用户菜单 |
| UI_LOGIN_002 | P0 | 错误密码登录失败 | 无 | 1. 访问 `/auth/login` 2. 输入正确邮箱 + 错误密码 3. 点击 Login | 停留在 `/auth/login`；显示 "Invalid email or password" 错误消息 |
| UI_LOGIN_003 | P0 | 空表单提交校验 | 无 | 1. 访问 `/auth/login` 2. 不填任何内容直接点击 Login | 表单校验阻止提交（HTML5 required）；停留在登录页 |

## P1 异常/关键路径

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_LOGIN_004 | P1 | 不存在邮箱登录失败 | 无 | 1. 访问 `/auth/login` 2. 输入不存在的邮箱 + 任意密码 3. 点击 Login | 显示 "Invalid email or password" |
| UI_LOGIN_005 | P1 | 跳转到注册页 | 无 | 1. 访问 `/auth/login` 2. 点击 "Register your account" 链接 | 跳转到 `/auth/register` |
| UI_LOGIN_006 | P1 | 跳转到忘记密码页 | 无 | 1. 访问 `/auth/login` 2. 点击 "Forgot your Password?" 链接 | 跳转到 `/auth/forgot-password` |

## P2 边界条件

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_LOGIN_007 | P2 | 超长邮箱输入 | 无 | 1. 访问 `/auth/login` 2. 输入 200+ 字符的邮箱 3. 点击 Login | 页面不崩溃，显示错误提示或校验拦截 |
| UI_LOGIN_008 | P2 | 超长密码输入 | 无 | 1. 访问 `/auth/login` 2. 输入正常邮箱 + 200+ 字符密码 3. 点击 Login | 页面不崩溃，显示错误提示 |
| UI_LOGIN_009 | P2 | SQL 注入类邮箱输入 | 无 | 1. 访问 `/auth/login` 2. 输入 `' OR '1'='1` 3. 点击 Login | 页面不崩溃，显示 "Invalid email or password"，不发生注入 |
| UI_LOGIN_011 | P2 | 密码可见性切换 | 无 | 1. 访问 `/auth/login` 2. 输入密码 3. 点击密码框旁 eye icon 4. 再次点击 | 密码 type 在 `password` ↔ `text` 间切换 |

## P3 权限/状态组合

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_LOGIN_010 | P3 | 已登录用户访问登录页导航栏状态 | 使用测试账号已登录 | 1. 登录后直接访问 `/auth/login` | 页面不跳转但导航栏保持已登录状态（显示用户菜单/Sign out） |
| UI_LOGIN_012 | P3 | XSS 脚本注入防御 | 无 | 1. 访问 `/auth/login` 2. 输入 `<script>alert(1)</script>` 到邮箱字段 3. 点击 Login | 页面不崩溃、不执行脚本，显示校验错误 |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 3 | 正常登录、错误密码、空表单校验 |
| P1 | 3 | 不存在邮箱、注册跳转、忘记密码跳转 |
| P2 | 4 | 超长邮箱、超长密码、SQL 注入、密码可见性切换 |
| P3 | 2 | 已登录用户访问登录页、XSS 注入 |
| **合计** | **12** | 登录页四维全覆盖 |
