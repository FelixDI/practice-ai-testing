# HomePage 模块 UI 测试用例

> **被测页面**：Toolshop 首页（`/`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **页面说明**：首页展示商品列表、分类导航、搜索框。无需登录。

---

## 页面功能区域

| 区域 | 说明 | data-test |
|------|------|------|
| 导航栏 | Home / Categories / Sign in | nav-home, nav-categories, nav-sign-in |
| 搜索框 | 全文搜索商品 | search-query |
| 分类菜单 | Hand/Power/Other/Special Tools | nav-hand-tools, ... |
| 排序 | 商品列表排序 | sort |
| 商品卡片 | 商品图片/名称/价格/库存 | card |
| 通知栏 | 页面顶部通知 | notification-bar |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_HOME_001 | P0 | 首页正常加载 | 无 | 访问 `/`，等待页面渲染 | 页面标题含 "Practice Software Testing"；商品卡片数 > 0 |
| UI_HOME_002 | P0 | 搜索商品 | 无 | 在搜索框输入 `hammer` 回车 | 页面跳转或商品列表过滤，显示 hammer 相关商品 |
| UI_HOME_003 | P0 | 分类导航跳转 | 无 | 点击 "Hand Tools" 分类 | URL 变为 `/category/hand-tools`；商品列表更改 |
| UI_HOME_004 | P0 | 点击商品进入详情 | 无 | 点击第一张商品卡片 | URL 变为 `/product/{id}`；页面显示商品详情 |

## P1 异常/关键路径

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_HOME_005 | P1 | 空搜索 | 无 | 搜索框为空直接回车 | 页面不崩溃，保持当前列表 |
| UI_HOME_006 | P1 | 排序切换 | 无 | 下拉选择不同排序方式 | 商品列表顺序变化 |
| UI_HOME_007 | P1 | 分类菜单展开/收起 | 无 | 点击 Categories 按钮 | 下拉菜单出现/消失 |
| UI_HOME_008 | P1 | 导航栏 Sign in 链接 | 未登录 | 点击 Sign in | 跳转到 `/auth/login` |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 4 | 首页加载、搜索、分类导航、商品详情跳转 |
| P1 | 4 | 空搜索、排序、菜单交互、登录入口 |
| **合计** | **8** | 首页核心交互全覆盖 |
