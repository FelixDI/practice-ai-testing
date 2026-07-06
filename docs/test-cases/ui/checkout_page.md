# CheckoutPage 测试用例设计

> 路由：`/checkout` | 需登录 | 购物车与结账合一（4 步流程：Cart → Sign in → Billing Address → Payment）

## 页面 DOM 实测（Playwright MCP）

| 步骤 | data-test 选择器 | 元素类型 |
|------|------|------|
| Cart | `cart-quantity` | SPAN — 购物车商品数量徽章 |
| Cart | `cart-total` | TD — 总价单元格 |
| Cart → Sign in | `proceed-1` | BUTTON — 第 1 步 Proceed |
| Sign in → Address | `proceed-2` | BUTTON — 第 2 步 Proceed |
| Address | `country` | SELECT — 国家下拉 |
| Address | `postal_code` | INPUT — 邮政编码 |
| Address | `house_number` | INPUT — 门牌号 |
| Address | `street` | INPUT — 街道 |
| Address | `city` | INPUT — 城市 |
| Address | `state` | INPUT — 州/省 |
| Address → Payment | `proceed-3` | BUTTON — 第 3 步 Proceed |
| Payment | `payment-method` | SELECT — 支付方式 |
| Payment | `finish` | BUTTON — Confirm（确认下单） |

> 注：`proceed-1`/`proceed-2`/`proceed-3` 同时存在于 DOM 中，但仅当前步骤对应的按钮可见。

## 测试用例

### P0 —— 核心链路（3 条）

| 编号 | 用例名称 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|------|------|------|
| `UI_CHECKOUT_001` | 购物车页面加载并显示商品 | 已登录；购物车有 1 件商品 | 1. 导航到 `/checkout` 2. 等待 `proceed-1` 可见 | `cart-quantity` 显示数量 ≥1；`cart-total` 显示价格 |
| `UI_CHECKOUT_002` | 完整购买流程（4 步 → Confirm） | 已登录；购物车有 1 件商品 | 1. 导航到 `/checkout` 2. 点击 `proceed-1` → `proceed-2` 3. 填写 Billing Address（`postal_code` + `house_number` + `street` + `city` + `state`） 4. 点击 `proceed-3` 5. 选择 `payment-method` = "Cash on Delivery" 6. 点击 `finish` | 页面跳转到 `/account`（支付成功）；或停留在 `/checkout` 并显示成功提示 |
| `UI_CHECKOUT_003` | 未登录重定向 | 未登录 | 1. 导航到 `/checkout` | 重定向到 `/auth/login` |

### P1 —— 关键异常（3 条）

| 编号 | 用例名称 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|------|------|------|
| `UI_CHECKOUT_004` | Payment Method 未选择时 Confirm 按钮 disabled | 已登录；购物车有商品 | 1. 导航到 `/checkout` 2. 点击 `proceed-1`、`proceed-2` 3. 填写 Billing Address 4. 点击 `proceed-3` | `finish` 按钮为 `disabled`；选择 `payment-method` = "Cash on Delivery" 后 `finish` 变为可点击 |
| `UI_CHECKOUT_005` | Billing Address 必填字段为空时无法继续 | 上述步骤 3 | 1. 在 Billing Address 步骤中留空 `postal_code` 或 `house_number` | `proceed-3` 按钮为 `disabled` |
| `UI_CHECKOUT_006` | 连续点击步骤可返回上一步 | 已登录；购物车有商品 | 1. 完成 Cart → Sign in → Billing Address 2. 点击步骤指示器中 "Cart"（步骤1）| 返回购物车视图，`proceed-1` 可见 |

### P2 —— 边界覆盖（2 条）

| 编号 | 用例名称 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|------|------|------|
| `UI_CHECKOUT_007` | 修改商品数量 | 已登录；购物车有 1 件商品 | 1. 导航到 `/checkout` 2. 修改数量 spinner 为 2 | `cart-total` 更新为 单价×2 |
| `UI_CHECKOUT_008` | 所有支付方式可选 | 进入 Payment 步骤 | 1. 遍历 `payment-method` 的 5 个 option | Bank Transfer / Cash on Delivery / Credit Card / Buy Now Pay Later / Gift Card 均可选 |

### P3 —— 深度防御（1 条）

| 编号 | 用例名称 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|------|------|------|
| `UI_CHECKOUT_009` | XSS 注入 address 字段不崩溃 | 进入 Billing Address 步骤 | 1. 在 `street` 输入 `<script>alert(1)</script>` 2. 填写其余必填字段 3. 点击 `proceed-3` | 页面不崩溃、不弹 alert；正常进入 Payment 步骤 |
