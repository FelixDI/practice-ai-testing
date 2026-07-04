# RegisterPage 模块 UI 测试用例

> **被测页面**：Toolshop 注册页（`/auth/register`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **页面说明**：注册页提供完整用户注册表单（姓名/DOB/地址/邮箱/密码），注册成功后跳转登录页。

---

## 页面功能区域

| 区域 | 说明 | data-test |
|------|------|------|
| 注册表单 | 12 个字段 + 提交按钮 | register-form |
| 名字 | 文本输入 | first-name |
| 姓氏 | 文本输入 | last-name |
| 出生日期 | YYYY-MM-DD 格式 | dob |
| 国家 | 下拉选择（触发邮编查询） | country |
| 邮编 | 文本输入 | postal_code |
| 门牌号 | 文本输入 | house_number |
| 街道 | 文本输入（邮编查询自动填充） | street |
| 城市 | 文本输入（邮编查询自动填充） | city |
| 州/省 | 文本输入（邮编查询自动填充） | state |
| 电话 | 文本输入 | phone |
| 邮箱 | 文本输入 | email |
| 密码 | 密码输入（强度校验） | password |
| 提交按钮 | 提交注册 | register-submit |
| 全局错误 | 表单级错误（重复邮箱等） | register-error |
| 字段错误 | 各字段级校验错误 | {field}-error |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_REG_001 | P0 | 成功注册新用户 | 唯一邮箱 + 合法密码 | 1. 访问 `/auth/register` 2. 填写全部必填字段（合法值）3. 点击 Register | 跳转到 `/auth/login`，注册成功 |
| UI_REG_002 | P0 | 空表单提交校验 | 无 | 1. 访问 `/auth/register` 2. 不填任何内容直接点击 Register | 各必填字段显示错误提示（first-name-error / email-error / password-error 等） |
| UI_REG_003 | P0 | 重复邮箱注册失败 | 已知已注册邮箱 | 1. 访问 `/auth/register` 2. 填写表单，邮箱用 `customer@practicesoftwaretesting.com` 3. 点击 Register | 显示 "A customer with this email address already exists." |

## P1 异常/关键路径

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_REG_004 | P1 | 弱密码被拒（纯数字） | 无 | 1. 访问 `/auth/register` 2. 填写表单，密码为纯数字 8 位 3. 点击 Register | password-error 提示密码要求 |
| UI_REG_005 | P1 | 密码无特殊字符被拒 | 无 | 1. 访问 `/auth/register` 2. 填写表单，密码有大小写+数字但无特殊字符 3. 点击 Register | password-error 提示需特殊字符 |
| UI_REG_006 | P1 | 无效邮箱格式被拒 | 无 | 1. 访问 `/auth/register` 2. 填写表单，邮箱为 `not-an-email` 3. 点击 Register | email-error 提示邮箱格式无效 |
| UI_REG_011 | P1 | Phone 含字母被拒 | 无 | 1. 访问 `/auth/register` 2. 填写表单，phone 为 `abc` 3. 点击 Register | phone-error 提示 "Only numbers are allowed." |
| UI_REG_012 | P1 | 密码最小长度边界 | 无 | 1. 访问 `/auth/register` 2. 填写表单，密码为 5 字符 `Ab1!` 3. 点击 Register | password-error 提示 "minimal 6 characters" |

## P2 边界条件

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_REG_007 | P2 | DOB 无效日期格式 | 无 | 1. 访问 `/auth/register` 2. 填写表单，DOB 为 `abc` 3. 点击 Register | dob-error 提示日期格式无效 |
| UI_REG_008 | P2 | DOB 未来日期 | 无 | 1. 访问 `/auth/register` 2. 填写表单，DOB 为 `2099-01-01` 3. 点击 Register | dob-error 或 register-error 提示日期不合法 |
| UI_REG_009 | P2 | 超长名字输入 | 无 | 1. 访问 `/auth/register` 2. 填写表单，first name 为 200 字符 3. 点击 Register | 页面不崩溃；通过前端校验或被服务端拒绝 |
| UI_REG_013 | P2 | 密码可见性切换 | 无 | 1. 访问 `/auth/register` 2. 输入密码 3. 点击密码框旁 eye icon 4. 再次点击 | 密码 type 在 `password` ↔ `text` 间切换 |

## P3 权限/状态组合

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_REG_010 | P3 | 已登录用户访问注册页 | 使用测试账号已登录 | 1. 登录后直接访问 `/auth/register` | 导航栏显示已登录状态（注册页表单仍显示或跳转） |
| UI_REG_014 | P3 | XSS 注入名字字段 | 无 | 1. 访问 `/auth/register` 2. 输入 `<script>alert(1)</script>` 到 first-name 3. 点击 Register | 页面不崩溃、不弹窗，显示校验错误 |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 3 | 成功注册、空表单校验、重复邮箱 |
| P1 | 5 | 弱密码、无特殊字符、无效邮箱、Phone含字母、密码最小长度 |
| P2 | 4 | DOB 无效格式、DOB 未来日期、超长名字、密码可见性切换 |
| P3 | 2 | 已登录用户访问注册页、XSS 注入 |
| **合计** | **14** | 注册页四维全覆盖 |
