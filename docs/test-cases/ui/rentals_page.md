# RentalsPage 模块 UI 测试用例

> **被测页面**：Toolshop 租赁工具列表页（`/rentals`）  
> **编写规范**：遵循项目 CLAUDE.md  
> **页面说明**：展示可租赁的重型工具列表（挖掘机/推土机/起重机），纯静态展示页，无需登录，无交互操作。

---

## 页面功能区域

| 区域 | data-test | 说明 |
|------|------|------|
| 页面标题 | `page-title` | 标题 "Rentals" |
| 租赁卡片 | `product-{id}` | 每张卡片的容器，id 动态变化 |
| 卡片图片 | `img[alt]` | 工具图片（Excavator / Bulldozer / Crane） |
| 卡片标题 | `h5.card-title` | 工具名称 |
| 卡片描述 | `p.card-text` | 工具描述文本 |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_RENT_001 | P0 | 租赁列表页正常加载 | 无 | 访问 `/rentals` | page-title "Rentals" visible |
| UI_RENT_002 | P0 | 至少有一条租赁工具 | RentalsPage 已加载 | 检查 product card 列表 | 至少 1 个 `data-test^="product-"` 元素 visible |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_RENT_003 | P1 | 卡片同时包含图片、标题、描述 | RentalsPage 已加载 | 检查第一张卡片的子元素 | img + h5.card-title + p.card-text 均 visible |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_RENT_004 | P2 | 租赁工具数量为 3 | RentalsPage 已加载 | 统计 `data-test^="product-"` 元素数量 | count = 3 |
