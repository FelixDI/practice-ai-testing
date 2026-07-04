# CategoryPage 模块 UI 测试用例

> **被测页面**：Toolshop 分类浏览页（`/category/{slug}`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **页面说明**：展示指定分类下的商品列表，支持排序/筛选/分页。无需登录。

---

## 页面功能区域

| 区域 | 说明 | 复用组件 |
|------|------|------|
| 导航栏 | Header 全部元素（含搜索 + nav-cart） | `Header` |
| 筛选区 | Sort / Price Range / Search / Category / Brand / Eco 筛选 | 同 HomePage 筛选区 |
| 商品列表 | 分类过滤后的商品卡片 | `ProductCard` + 分页 |
| 页脚 | DEMO 声明 + 隐私政策 | `Footer` |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CAT_001 | P0 | 分类页面正常加载 | 无 | 访问 `/category/hand-tools` | 页面 URL 含 `/category/hand-tools`；商品卡片数 > 0 |
| UI_CAT_002 | P0 | 分类页含商品列表 | 无 | 访问 `/category/power-tools` | 商品卡片 visible |
| UI_CAT_003 | P0 | 点击商品卡片跳转详情 | 无 | 点击第一张商品卡片 | URL 变为 `/product/{id}` |
| UI_CAT_009 | P0 | 分类标题显示正确名称 | 无 | 访问 `/category/hand-tools`，检查 category_heading | 标题含 "Category: Hand Tools" |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CAT_004 | P1 | 排序在分类页生效 | 无 | 选择排序 option | 商品列表顺序更新 |
| UI_CAT_005 | P1 | 分类页搜索 | 无 | 搜索框输入关键字后回车 | 商品列表过滤 |
| UI_CAT_006 | P1 | 不存在分类返回结果 | 无 | 访问 `/category/nonexistent` | 页面正常加载，商品列表为空或提示无结果 |
| UI_CAT_010 | P1 | Brand 筛选切换 | 无 | 勾选 "ForgeFlex Tools" 品牌 checkbox | checkbox 变为 checked；商品列表重新渲染 |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CAT_007 | P2 | 所有分类路由可访问 | 无 | 分别访问 4 个分类路由 | 每个分类返回商品列表 |
| UI_CAT_008 | P2 | 分页导航存在 | 无 | 检查分页区域 | 分页按钮（Prev/Next/页码）visible |
| UI_CAT_011 | P2 | 子分类筛选与分类联动 | 无 | 在 Power Tools 页勾选 "Drill" 子分类 | checkbox 变为 checked；商品列表重新渲染 |

## P3 深度防御

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CAT_012 | P3 | XSS 注入在分类 slug 中 | 无 | 访问 `/category/<script>alert(1)</script>` | 页面正常加载，Header 可见，无脚本执行 |
