# Invoice 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Invoice 依赖 Cart（含商品）—— 创建订单需要已有购物车 cart_id

---

## 端点覆盖（10 个）

### 1.1 订单列表 · GET /invoices

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_001 | P0 | 获取订单列表 | 已创建至少一张订单 | `GET /invoices`（需登录） | HTTP 200 或 401；返回 JSON 数组 |
| API_INVOICE_002 | P1 | 未登录获取订单列表 | 无 | `GET /invoices`，无 Token | HTTP 401 |
| API_INVOICE_003 | P2 | 分页 page=0 | 已登录 | `GET /invoices?page=0` | HTTP 200 或 400 |

### 1.2 创建订单（登录用户） · POST /invoices

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_004 | P0 | 创建订单（bank-transfer） | 已登录、已创建含商品的 cart | `POST /invoices`，完整 billing + payment_method=`"bank-transfer"` + bank_name/account_name/account_number + cart_id | HTTP 200；响应含 id、invoice_number、status、total、invoicelines |
| API_INVOICE_005 | P0 | 创建订单（credit-card） | 同上 | payment_method=`"credit-card"` + credit_card_number/expiration_date/cvv/card_holder_name | HTTP 200 |
| API_INVOICE_006 | P0 | 创建订单（cash-on-delivery） | 同上 | payment_method=`"cash-on-delivery"`，payment_details = `{}` | HTTP 200 |
| API_INVOICE_007 | P0 | 创建订单（gift-card） | 同上 | payment_method=`"gift-card"` + gift_card_number/validation_code | HTTP 200 |
| API_INVOICE_008 | P0 | 创建订单（buy-now-pay-later） | 同上 | payment_method=`"buy-now-pay-later"` + monthly_installments | HTTP 200 |
| API_INVOICE_009 | P1 | 缺少 billing_street | 已登录 | 请求体不传 billing_street | HTTP 422 |
| API_INVOICE_010 | P1 | 缺少 payment_method | 已登录 | 请求体不传 payment_method | HTTP 422 |
| API_INVOICE_011 | P1 | 非法 payment_method | 已登录 | payment_method = `"bitcoin"` | HTTP 422 |
| API_INVOICE_012 | P1 | 不存在的 cart_id | 已登录 | cart_id = `"nonexistent-99999"` | HTTP 404 或 422 |
| API_INVOICE_013 | P1 | 空 cart 创建订单 | 已登录、创建空 cart | cart_id 指向无商品的 cart | HTTP 422 |
| API_INVOICE_014 | P1 | 未登录创建订单 | 无 | `POST /invoices`，无 Token | HTTP 401 |

### 1.3 创建访客订单 · POST /invoices/guest

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_015 | P0 | 创建访客订单 | 已创建含商品的 cart | `POST /invoices/guest`，含 guest_email/guest_first_name/guest_last_name + billing + payment + cart_id | HTTP 200 |
| API_INVOICE_016 | P1 | 访客订单缺少 guest_email | 同上 | 请求体不传 guest_email | HTTP 422 |
| API_INVOICE_017 | P1 | 访客订单缺少 billing 字段 | 同上 | 请求体不传 billing_city | HTTP 422 |

### 1.4 订单详情 · GET /invoices/{invoiceId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_018 | P0 | 查询存在的订单 | 已创建订单 | `GET /invoices/{id}`（需登录） | HTTP 200；响应含 id、invoice_number、user_id、status、total、invoicelines（数组含 product 嵌套） |
| API_INVOICE_019 | P1 | 查询不存在的订单 | 已登录 | `GET /invoices/nonexistent-99999` | HTTP 404 |
| API_INVOICE_020 | P1 | 未登录查询订单 | 无 | `GET /invoices/{id}`，无 Token | HTTP 401 |

### 1.5 更新订单 · PUT /invoices/{invoiceId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_021 | P0 | 全量更新订单 | 已登录、已创建订单 | `PUT /invoices/{id}`，完整合法 JSON | HTTP 200 |
| API_INVOICE_022 | P1 | 更新不存在的订单 | 已登录 | `PUT /invoices/nonexistent-99999` | HTTP 404 |
| API_INVOICE_023 | P1 | 未登录更新订单 | 无 | `PUT /invoices/{id}`，无 Token | HTTP 401 |

### 1.6 部分更新订单 · PATCH /invoices/{invoiceId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_024 | P0 | 部分更新订单 | 已登录、已创建订单 | `PATCH /invoices/{id}`，只传 `{"billing_city":"NewCity"}` | HTTP 200 |
| API_INVOICE_025 | P1 | PATCH 不存在的订单 | 已登录 | `PATCH /invoices/nonexistent-99999` | HTTP 404 |
| API_INVOICE_026 | P1 | 未登录部分更新 | 无 | `PATCH /invoices/{id}`，无 Token | HTTP 401 |

### 1.7 更新订单状态 · PUT /invoices/{invoiceId}/status

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_027 | P0 | 更新订单状态为 SHIPPED | 已登录、已创建订单 | `PUT /invoices/{id}/status`，`{"status":"SHIPPED"}` | HTTP 200 |
| API_INVOICE_028 | P1 | 更新为非法状态值 | 已登录 | status = `"CANCELLED"`（不在枚举中） | HTTP 422 |
| API_INVOICE_029 | P1 | 更新不存在订单的状态 | 已登录 | `PUT /invoices/nonexistent-99999/status` | HTTP 404 |
| API_INVOICE_030 | P1 | 未登录更新状态 | 无 | `PUT /invoices/{id}/status`，无 Token | HTTP 401 |
| API_INVOICE_031 | P2 | status_message 超长（51 字符） | 已登录 | status_message 传入 51 字符 | HTTP 422 |
| API_INVOICE_032 | P2 | status_message 不足 5 字符 | 已登录 | status_message 传入 `"OK"`（2 字符） | HTTP 422 |

### 1.8 下载 PDF · GET /invoices/{invoice_number}/download-pdf

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_033 | P0 | 下载订单 PDF | 已登录、已知 invoice_number | `GET /invoices/{invoice_number}/download-pdf` | HTTP 200；返回 PDF 内容或重定向 |
| API_INVOICE_034 | P1 | 下载不存在的订单 PDF | 已登录 | `GET /invoices/INV-00000000/download-pdf` | HTTP 404 |
| API_INVOICE_035 | P1 | 未登录下载 PDF | 无 | `GET /invoices/{num}/download-pdf`，无 Token | HTTP 401 |

### 1.9 PDF 状态查询 · GET /invoices/{invoice_number}/download-pdf-status

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_036 | P0 | 查询 PDF 生成状态 | 已登录、已知 invoice_number | `GET /invoices/{invoice_number}/download-pdf-status` | HTTP 200 |
| API_INVOICE_037 | P1 | 不存在订单的 PDF 状态 | 已登录 | `GET /invoices/INV-00000000/download-pdf-status` | HTTP 404 |
| API_INVOICE_038 | P1 | 未登录查询 PDF 状态 | 无 | `GET /invoices/{num}/download-pdf-status`，无 Token | HTTP 401 |

### 1.10 搜索订单 · GET /invoices/search

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_039 | P0 | 搜索订单 | 已登录 | `GET /invoices/search?q=<invoice_number>` | HTTP 200；返回匹配结果 |
| API_INVOICE_040 | P1 | 搜索无匹配 | 已登录 | `GET /invoices/search?q=xyznonexistent999` | HTTP 200；返回空数组 |
| API_INVOICE_041 | P1 | 未登录搜索 | 无 | `GET /invoices/search?q=test`，无 Token | HTTP 401 |
| API_INVOICE_042 | P2 | 搜索不传 q 参数 | 已登录 | `GET /invoices/search` | HTTP 200 或 400 |

### 1.11 边界补充

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_043 | P2 | billing_street 超长 | 已登录、已创建 cart | `POST /invoices`，billing_street 传入 256 字符 | HTTP 422 |
| API_INVOICE_044 | P2 | billing_city 超长 | 同上 | billing_city 传入 256 字符 | HTTP 422 |
| API_INVOICE_045 | P2 | billing_postal_code 超长 | 同上 | billing_postal_code 传入 256 字符 | HTTP 422 |
| API_INVOICE_050 | P2 | billing_state 超长 | 同上 | billing_state 传入 256 字符 | HTTP 422 |
| API_INVOICE_051 | P2 | billing_country 超长 | 同上 | billing_country 传入 256 字符 | HTTP 422 |

### 1.12 缺失必填字段补充

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_052 | P1 | 缺少 billing_state | 已登录、已创建 cart | 请求体不传 billing_state | HTTP 422 |
| API_INVOICE_053 | P1 | 缺少 billing_country | 同上 | 请求体不传 billing_country | HTTP 422 |
| API_INVOICE_054 | P1 | PUT 更新时缺少 billing_street | 已登录、已创建订单 | `PUT /invoices/{id}`，不传 billing_street | HTTP 422 |

### 1.13 payment_details 子字段校验

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_046 | P1 | bank-transfer 缺少 account_number | 已登录、已创建 cart | payment_method=`"bank-transfer"`，不传 account_number | HTTP 422 |
| API_INVOICE_047 | P1 | credit-card 缺少 cvv | 同上 | payment_method=`"credit-card"`，不传 cvv | HTTP 422 |
| API_INVOICE_055 | P1 | credit-card 缺少 expiration_date | 同上 | payment_method=`"credit-card"`，不传 expiration_date | HTTP 422 |
| API_INVOICE_048 | P1 | gift-card 缺少 validation_code | 同上 | payment_method=`"gift-card"`，不传 validation_code | HTTP 422 |
| API_INVOICE_056 | P1 | bnpl 缺少 monthly_installments | 同上 | payment_method=`"buy-now-pay-later"`，不传 monthly_installments | HTTP 422 |

### 1.14 状态枚举遍历

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_057 | P2 | 更新状态为 AWAITING_FULFILLMENT | 已登录、已创建订单 | `PUT /invoices/{id}/status`，status = `"AWAITING_FULFILLMENT"` | HTTP 200 |
| API_INVOICE_058 | P2 | 更新状态为 ON_HOLD | 同上 | status = `"ON_HOLD"` | HTTP 200 |
| API_INVOICE_059 | P2 | 更新状态为 AWAITING_SHIPMENT | 同上 | status = `"AWAITING_SHIPMENT"` | HTTP 200 |
| API_INVOICE_060 | P2 | 更新状态为 COMPLETED | 同上 | status = `"COMPLETED"` | HTTP 200 |

### 1.15 权限/状态组合

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_046 | P1 | bank-transfer 缺少 account_number | 已登录、已创建 cart | payment_method=`"bank-transfer"`，不传 account_number | HTTP 422 |
| API_INVOICE_047 | P1 | credit-card 缺少 cvv | 同上 | payment_method=`"credit-card"`，不传 cvv | HTTP 422 |
| API_INVOICE_048 | P1 | gift-card 缺少 validation_code | 同上 | payment_method=`"gift-card"`，不传 validation_code | HTTP 422 |

### 1.15 权限/状态组合

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_INVOICE_049 | P3 | 用户 A 查看用户 B 的订单（横向越权） | 注册 A 和 B，A 创建订单，B 登录 | B 的 Token 访问 `GET /invoices/{A_order_id}` | HTTP 403 或 404 |
| API_INVOICE_061 | P3 | billing_street 含 XSS 片段 | 已登录、已创建 cart | `POST /invoices`，billing_street = `"<script>alert(1)</script>"` | HTTP 200 或 422（应转义） |
| API_INVOICE_062 | P3 | Token 过期后创建订单 | 已登录→token 失效 | `POST /invoices`，带过期 Token | HTTP 401 |
| API_INVOICE_063 | P3 | Token 过期后更新订单状态 | 已登录→token 失效 | `PUT /invoices/{id}/status`，带过期 Token | HTTP 401 |

---

## 覆盖统计（Invoice）

| 优先级 | 用例数 | 占比 | 内容 |
|:--:|:--:|:--:|------|
| P0 | 13 | 22% | 创建（5 种支付方式）、列表、详情、PUT/PATCH 更新、状态更新、PDF 下载/状态、搜索 |
| P1 | 31 | 52% | 缺字段(422)、不存在(404)、未登录(401)、非法枚举值、空 cart、payment_details 子字段缺失、billing 必填字段缺失 |
| P2 | 15 | 25% | 分页边界、status_message 边界、搜索缺 q、billing 字段超长、status 全枚举遍历 |
| P3 | 1 | 2% | 横向越权 |
| **合计** | **60** | 100% | 10 端点全覆盖 |

### 五种支付方式覆盖

| 支付方式 | payment_details 字段 | 用例 |
|------|------|:--:|
| bank-transfer | bank_name, account_name, account_number | API_INVOICE_004 |
| credit-card | credit_card_number, expiration_date, cvv, card_holder_name | API_INVOICE_005 |
| cash-on-delivery | `{}`（空对象） | API_INVOICE_006 |
| gift-card | gift_card_number, validation_code | API_INVOICE_007 |
| buy-now-pay-later | monthly_installments | API_INVOICE_008 |

### 核心业务链路

```
User 登录 → POST /carts（创建购物车）→ POST /carts/{id}（加商品）
    → POST /invoices（创建订单，5 种支付方式）
    → GET /invoices/{id}（验证 invoicelines 含商品嵌套）
    → PUT /invoices/{id}/status（更新状态 SHIPPED）
    → GET /invoices/{num}/download-pdf（下载发票 PDF）
    → GET /invoices/search（搜索确认）
```
