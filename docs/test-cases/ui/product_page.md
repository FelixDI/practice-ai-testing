# ProductPage 模块 UI 测试用例

> **被测页面**：Toolshop 商品详情页（`/product/{id}`）  
> **编写规范**：遵循项目 CLAUDE.md  
> **页面说明**：展示单个商品的详细信息、规格、操作按钮（加购/收藏/对比）和相关推荐。无需登录。

---

## 页面功能区域

| 区域 | data-test | 说明 |
|------|------|------|
| 商品信息 | `product-name` / `unit-price` / `product-description` | 名称、价格、描述 |
| CO₂ 评级 | `co2-rating-badge` | A~E 环保等级 |
| 数量控件 | `decrease-quantity` / `quantity` / `increase-quantity` | 加减数量 |
| 操作按钮 | `add-to-cart` / `add-to-favorites` / `add-to-compare` | 加购/收藏/对比 |
| 规格表 | `specs-title` / `product-specs` / `spec-row` / `spec-name` / `spec-value` | 规格参数 |
| 相关推荐 | 复用 ProductCard 组件 | 底部相关商品 |

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROD_001 | P0 | 商品详情页正常加载 | 商品 ID 有效（fixture 从 API 动态获取） | 访问 `/product/{id}` | product-name / unit-price / product-description 均 visible |
| UI_PROD_002 | P0 | 加购按钮可用 | 商品详情页 | 点击 Add to cart | 按钮可点击；页面无报错 |
| UI_PROD_003 | P0 | 数量可增加 | 商品详情页 | 点击 increase-quantity | quantity 值变为 2 |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROD_004 | P1 | 无效商品 ID 返回 404 | 不存在 ID | 访问 `/product/invalid` | 页面正常加载（可能显示 404 或重定向） |
| UI_PROD_005 | P1 | 数量不能低于 1 | 数量=1 | 点击 decrease-quantity | quantity 仍为 1 |
| UI_PROD_006 | P1 | 规格表渲染 | 商品详情页 | 检查 specs 区域 | specs-title visible；至少有一条 spec-row |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROD_007 | P2 | 收藏按钮存在于详情页 | 商品详情页 | 检查 add-to-favorites | button visible |
| UI_PROD_008 | P2 | 相关推荐区域含商品 | 商品详情页 | 检查底部推荐商品 | 至少一张相关商品卡片 visible |

## P3 深度防御

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_PROD_009 | P3 | XSS 注入在商品 ID 中 | 无 | 访问 `/product/<script>alert(1)</script>` | 页面不崩溃，Header 可见 |
