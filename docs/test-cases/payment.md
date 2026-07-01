# Payment 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Payment 依赖 Invoice 模块——支付校验通常需要关联已生成的订单；本次按接口文档独立设计，前置条件中标注所需订单数据

---

## 端点覆盖（1 个）

### 1.1 支付校验 · POST /payment/check

> **Request**: `PaymentRequest { payment_method: enum<5>, payment_details: oneOf<5> }`  
> **Response (200)**: object（支付校验结果）  
> **Auth**: ❌ 无需登录（接口文档未标注 security）

**payment_method 枚举**：`bank-transfer` | `cash-on-delivery` | `credit-card` | `buy-now-pay-later` | `gift-card`

**payment_details 按支付方式**：

| 支付方式 | details schema | 必填字段 |
|------|------|------|
| bank-transfer | `BankTransferDetails` | bank_name, account_name, account_number |
| cash-on-delivery | `CashOnDeliveryDetails`（空对象） | 无 |
| credit-card | `CreditCardDetails` | credit_card_number, expiration_date, cvv, card_holder_name |
| buy-now-pay-later | `BuyNowPayLaterDetails` | monthly_installments |
| gift-card | `GiftCardDetails` | gift_card_number, validation_code |

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_001 | P0 | cash-on-delivery 支付校验 | 无 | `POST /payment/check`，传入 `{"payment_method":"cash-on-delivery","payment_details":{}}` | HTTP 200；响应含支付校验结果 |
| API_PAYMENT_002 | P0 | credit-card 支付校验 | 已知有效信用卡信息 | `POST /payment/check`，传入 `{"payment_method":"credit-card","payment_details":{"credit_card_number":"...","expiration_date":"...","cvv":"...","card_holder_name":"..."}}` | HTTP 200；响应含支付校验结果 |
| API_PAYMENT_003 | P0 | 缺少 payment_method | 无 | `POST /payment/check`，只传 `{"payment_details":{}}` | HTTP 422 |
| API_PAYMENT_004 | P1 | bank-transfer 支付校验 | 已知有效银行账户信息 | `POST /payment/check`，传入 `{"payment_method":"bank-transfer","payment_details":{"bank_name":"...","account_name":"...","account_number":"..."}}` | HTTP 200；响应含支付校验结果 |
| API_PAYMENT_005 | P1 | gift-card 支付校验 | 已知有效礼品卡信息 | `POST /payment/check`，传入 `{"payment_method":"gift-card","payment_details":{"gift_card_number":"...","validation_code":"..."}}` | HTTP 200；响应含支付校验结果 |
| API_PAYMENT_006 | P1 | buy-now-pay-later 支付校验 | 已知有效分期信息 | `POST /payment/check`，传入 `{"payment_method":"buy-now-pay-later","payment_details":{"monthly_installments":"3"}}` | HTTP 200；响应含支付校验结果 |
| API_PAYMENT_007 | P1 | 无效的 payment_method | 无 | `POST /payment/check`，传入 `{"payment_method":"bitcoin","payment_details":{}}` | HTTP 422 |
| API_PAYMENT_008 | P1 | credit-card 缺少 cvv | 无 | `POST /payment/check`，传入 credit-card 方式但 payment_details 不含 cvv | HTTP 422 |
| API_PAYMENT_009 | P1 | bank-transfer 缺少 account_number | 无 | `POST /payment/check`，传入 bank-transfer 方式但 payment_details 不含 account_number | HTTP 422 |
| API_PAYMENT_010 | P1 | gift-card 缺少 gift_card_number | 无 | `POST /payment/check`，传入 gift-card 方式但 payment_details 不含 gift_card_number | HTTP 422 |
| API_PAYMENT_011 | P1 | payment_details 为 null | 无 | `POST /payment/check`，传入 `{"payment_method":"credit-card","payment_details":null}` | HTTP 422 |
| API_PAYMENT_012 | P1 | payment_method 与 details 类型不匹配 | 无 | `POST /payment/check`，传入 `{"payment_method":"cash-on-delivery","payment_details":{"credit_card_number":"..."}}` | HTTP 422 |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 3 | 最简支付方式 Happy Path（cash-on-delivery）、最常用支付方式（credit-card）、缺少必填字段（422） |
| P1 | 9 | 其余 3 种支付方式 Happy Path、无效枚举值（422）、details 必填字段缺失 × 4、类型不匹配 |
| **合计** | **12** | 覆盖 5 种支付方式的正常链路 + 关键异常路径 |

---

> **说明**：Payment 模块仅 1 个端点 `POST /payment/check`，无 Auth 要求，无 404/409 场景。文档未列出 401 响应，已省略未登录用例。  

---

## P2 边界用例

### 2.1 payment_method 枚举边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_013 | P2 | payment_method 大小写变体 | 无 | `POST /payment/check`，传入 `{"payment_method":"Credit-Card","payment_details":{}}` | HTTP 422（枚举应严格匹配） |
| API_PAYMENT_014 | P2 | payment_method 为空字符串 | 无 | `POST /payment/check`，传入 `{"payment_method":"","payment_details":{}}` | HTTP 422 |

### 2.2 BankTransferDetails 字段边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_015 | P2 | bank_name 为空字符串 | 无 | `POST /payment/check`，bank-transfer + `{"bank_name":"","account_name":"John","account_number":"123"}` | HTTP 422 |
| API_PAYMENT_016 | P2 | account_name 为空字符串 | 无 | bank-transfer + `{"bank_name":"Bank","account_name":"","account_number":"123"}` | HTTP 422 |
| API_PAYMENT_017 | P2 | account_number 为空字符串 | 无 | bank-transfer + `{"bank_name":"Bank","account_name":"John","account_number":""}` | HTTP 422 |
| API_PAYMENT_018 | P2 | bank-transfer 各字段为纯空格 | 无 | bank-transfer + 所有字段为 `"   "` | HTTP 422 |
| API_PAYMENT_019 | P2 | bank-transfer 含额外未知字段 | 无 | bank-transfer 合法字段 + `{"extra":"field"}` | HTTP 200（忽略）或 422 |

### 2.3 CreditCardDetails 字段边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_020 | P2 | credit_card_number 含字母 | 无 | credit-card + `{"credit_card_number":"abcd-efgh-ijkl-mnop","expiration_date":"2025-12","cvv":"123","card_holder_name":"John"}` | HTTP 422 |
| API_PAYMENT_021 | P2 | expiration_date 格式错误 | 无 | credit-card + expiration_date = `"12/2025"`（非 ISO） | HTTP 422 |
| API_PAYMENT_022 | P2 | cvv 为非数字 | 无 | credit-card + cvv = `"abc"` | HTTP 422 |
| API_PAYMENT_023 | P2 | card_holder_name 为空字符串 | 无 | credit-card + `{"credit_card_number":"4111111111111111","expiration_date":"2025-12","cvv":"123","card_holder_name":""}` | HTTP 422 |
| API_PAYMENT_024 | P2 | credit_card_number 超短（不足有效位数） | 无 | credit-card + credit_card_number = `"123"` | HTTP 422 |
| API_PAYMENT_025 | P2 | expiration_date 为已过期日期 | 无 | credit-card + expiration_date = `"2020-01"` | HTTP 200 或 422（取决于业务逻辑） |
| API_PAYMENT_037 | P2 | cvv 为 2 位数字（过短） | 无 | credit-card + cvv = `"12"` | HTTP 422 |
| API_PAYMENT_038 | P2 | cvv 为 5 位数字（过长） | 无 | credit-card + cvv = `"12345"` | HTTP 422 |
| API_PAYMENT_039 | P2 | credit_card_number 无连字符 16 位连写 | 无 | credit-card + credit_card_number = `"4111111111111111"`（无 `-` 分隔） | HTTP 200 或 422 |

### 2.4 GiftCardDetails 字段边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_026 | P2 | gift_card_number 为空字符串 | 无 | gift-card + `{"gift_card_number":"","validation_code":"ABC123"}` | HTTP 422 |
| API_PAYMENT_027 | P2 | validation_code 为空字符串 | 无 | gift-card + `{"gift_card_number":"GIFT-123","validation_code":""}` | HTTP 422 |
| API_PAYMENT_040 | P2 | gift_card_number 含空格分隔 | 无 | gift-card + gift_card_number = `"1234 5678 9012 3456"` | HTTP 200 或 422 |
| API_PAYMENT_041 | P2 | validation_code 为 3 位（过短） | 无 | gift-card + validation_code = `"123"` | HTTP 422 |
| API_PAYMENT_042 | P2 | validation_code 为 5 位（过长） | 无 | gift-card + validation_code = `"12345"` | HTTP 422 |

### 2.5 BuyNowPayLaterDetails 字段边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_028 | P2 | monthly_installments 为 `"0"` | 无 | buy-now-pay-later + `{"monthly_installments":"0"}` | HTTP 422 |
| API_PAYMENT_029 | P2 | monthly_installments 为负数 | 无 | buy-now-pay-later + `{"monthly_installments":"-3"}` | HTTP 422 |
| API_PAYMENT_030 | P2 | monthly_installments 为非数字字符串 | 无 | buy-now-pay-later + `{"monthly_installments":"abc"}` | HTTP 422 |
| API_PAYMENT_031 | P2 | monthly_installments 为空字符串 | 无 | buy-now-pay-later + `{"monthly_installments":""}` | HTTP 422 |
| API_PAYMENT_043 | P2 | monthly_installments 为浮点数 | 无 | buy-now-pay-later + `{"monthly_installments":"3.5"}` | HTTP 200 或 422 |

### 2.6 请求体边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_044 | P1 | 请求体为空 JSON 对象 | 无 | `POST /payment/check`，传入 `{}` | HTTP 422（缺少 payment_method 和 payment_details） |

### 2.7 CashOnDeliveryDetails 边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_032 | P2 | cash-on-delivery 附带多余字段 | 无 | cash-on-delivery + `{"extra":"ignored"}` | HTTP 200（忽略）或 422 |

---

## P2 用例汇总

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 20 | payment_method 枚举边界 × 2；BankTransfer 字段边界 × 5；CreditCard 字段边界 × 6；GiftCard 字段边界 × 2；BNPL 字段边界 × 4；COD 边界 × 1 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 3 |
| P1 | 10 |
| P2 | 27 |
| **合计** | **40** |

---

## P3 深度防御用例

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_PAYMENT_033 | P3 | credit_card_number 含 SQL 注入片段 | 无 | `POST /payment/check`，credit-card + `{"credit_card_number":"' OR '1'='1","expiration_date":"2025-12","cvv":"123","card_holder_name":"John"}` | HTTP 422（不应触发数据库异常） |
| API_PAYMENT_034 | P3 | card_holder_name 含 XSS 片段 | 无 | `POST /payment/check`，credit-card + `{"credit_card_number":"4111111111111111","expiration_date":"2025-12","cvv":"123","card_holder_name":"<script>alert(1)</script>"}` | HTTP 200 或 422（不应回显未转义的脚本） |
| API_PAYMENT_035 | P3 | payment_details 为深层嵌套对象 | 无 | `POST /payment/check`，payment_details 含 5 层嵌套 | HTTP 422 |
| API_PAYMENT_036 | P3 | 超大请求体 | 无 | `POST /payment/check`，payment_details 中各字段为 10KB 字符串 | HTTP 422 |
| API_PAYMENT_045 | P3 | payment_details 为 JSON 嵌套炸弹 | 无 | `POST /payment/check`，payment_details 中含大量重复嵌套（如 100 层 `{"a":...}`） | HTTP 422 或 500（不应导致服务崩溃） |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 3 |
| P1 | 10 |
| P2 | 27 |
| P3 | 5 |
| **合计** | **45** |
