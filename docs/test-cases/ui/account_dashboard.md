# AccountDashboard 模块 UI 测试用例

> **被测页面**：Toolshop 账户概览页（`/account`）  
> **编写规范**：遵循项目 CLAUDE.md  
> **页面说明**：登录后自动跳转的落地页。展示 H1 "My account" + 介绍文字 + 4 个功能入口按钮（Favorites/Profile/Invoices/Messages）。未登录访问重定向到 `/auth/login`。

---

## 页面功能区域

| 区域 | 定位方式 | 说明 |
|------|------|------|
| 页面标题 | `h1` | "My account" |
| 介绍文字 | `p` | "Here you can manage your profile, favorites and orders." |
| 收藏夹入口 | `button "Favorites"` | 导航到 /account/favorites |
| 个人资料入口 | `button "Profile"` | 导航到 /account/profile |
| 订单入口 | `button "Invoices"` | 导航到 /account/invoices |
| 消息入口 | `button "Messages"` | 导航到 /account/messages |
| 用户菜单 | `nav-menu` | 登录后显示用户名，点击展开下拉（nav-my-* 为隐藏的下拉项） |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_ACCT_001 | P0 | 登录后跳转到账户页并展示全部内容 | 已注册用户 | 登录 → 自动跳转 | URL 含 `/account`；H1 "My account" visible；4 个功能按钮 visible；nav-menu / nav-sign-out visible |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_ACCT_002 | P1 | 未登录访问 /account 重定向到登录页 | 未登录 | 直接访问 `/account` | URL 变为 `/auth/login`，login-form visible |
