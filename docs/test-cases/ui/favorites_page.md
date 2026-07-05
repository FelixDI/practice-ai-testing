# FavoritesPage 模块 UI 测试用例

> **被测页面**：Toolshop 收藏夹页（`/account/favorites`）  
> **编写规范**：遵循项目 CLAUDE.md  
> **页面说明**：需登录。展示用户收藏的商品列表。新账号无收藏时为空页面（仅 H1 "Favorites"）。

---

## 页面功能区域

| 区域 | data-test | 说明 |
|------|------|------|
| 页面标题 | `page-title` | "Favorites" |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FAV_001 | P0 | 收藏页正常加载 | 已登录 | 访问 `/account/favorites` | page-title "Favorites" visible |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FAV_002 | P1 | 未登录访问重定向 | 未登录 | 访问 `/account/favorites` | 重定向到 `/auth/login` |
