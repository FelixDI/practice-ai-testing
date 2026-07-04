# Header 组件 UI 测试用例

> **被测组件**：Header（跨页面顶部导航栏）  
> **出现页面**：全部页面（HomePage / LoginPage / RegisterPage / CategoryPage 等）  
> **组件文件**：`src/ui/components/header.py`  
> **设计说明**：现有测试已覆盖搜索/分类跳转，本文件只补充未覆盖的导航链接、语言切换、登录态完整菜单。

---

## 页面功能区域

| 区域 | data-test 范围 | 数量 |
|------|------|:--:|
| 未登录导航 | `nav-home` / `nav-categories` / `nav-rentals` / `nav-contact` / `nav-sign-in` + 分类下拉 4 个 | 9 |
| 搜索（仅列表页） | `search-query` / `search-reset` / `search-submit` | 3 |
| 语言切换 | `language-select` + `lang-{de,el,en,es,fr,nl,tr}` | 8 |
| 登录态导航 | `nav-menu` + 6 个子项 | 7 |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_HEADER_001 | P0 | Contact 导航链接 | 未登录 HomePage | 点击 nav-contact | URL 变为 `/contact` |
| UI_HEADER_002 | P0 | Rentals 导航链接 | 未登录 HomePage | 点击 nav-rentals | URL 变为 `/rentals` |
| UI_HEADER_003 | P0 | Categories 下拉含所有子分类 | 未登录 HomePage | 点击 nav-categories | nav-hand-tools / nav-power-tools / nav-other / nav-special-tools 可见 |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_HEADER_004 | P1 | 全部未登录导航元素存在 | 未登录 HomePage | 检查 9 个 nav-* 元素 | 全部 visible |
| UI_HEADER_005 | P1 | 语言切换菜单展开 | 未登录 HomePage | 点击 language-select | lang-{de,el,en,es,fr,nl,tr} 可见 |
| UI_HEADER_006 | P1 | 登录后全部用户菜单元素存在 | 已登录 HomePage | 点击 nav-menu | nav-my-account / nav-my-favorites / nav-my-profile / nav-my-invoices / nav-my-messages / nav-sign-out 全部 visible |
| UI_HEADER_007 | P1 | 登出后恢复未登录导航 | 已登录 HomePage | 执行 sign_out() | nav-sign-in 可见，nav-menu 消失 |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_HEADER_008 | P2 | navigate_to_category 通用方法 | 未登录 HomePage | 调用 navigate_to_category("power-tools") | URL 变为 `/category/power-tools` |
| UI_HEADER_009 | P2 | 搜索区按钮存在 | 未登录 HomePage | 检查 search-reset / search-submit | 两个 button 均 visible |
