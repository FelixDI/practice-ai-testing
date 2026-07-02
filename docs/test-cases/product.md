# Product 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Product 依赖 Brand 和 Category 的已有数据（brand_id / category_id）

---

## 端点覆盖（8 个）

### 1.1 商品列表 · GET /products

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_001 | P0 | 获取商品列表 | 无 | `GET /products` | HTTP 200；返回非空 JSON 数组，每个元素含 id、name、price、brand（嵌套对象）、category（嵌套对象） |
| API_PRODUCT_002 | P0 | 按品牌筛选 | 已知品牌 slug | `GET /products?by_brand=<brand_slug>` | HTTP 200；返回的商品 brand.slug 等于筛选值 |
| API_PRODUCT_003 | P0 | 按分类筛选 | 已知分类 slug | `GET /products?by_category=<category_slug>` | HTTP 200；返回的商品 category.slug 等于筛选值 |
| API_PRODUCT_004 | P0 | 按租赁属性筛选 | 无 | `GET /products?is_rental=1` | HTTP 200；返回的商品 is_rental 均为 true |
| API_PRODUCT_005 | P0 | 按价格区间筛选 | 无 | `GET /products?between=10,100` | HTTP 200；返回的商品 price 在 [10, 100] 区间 |
| API_PRODUCT_006 | P0 | 排序参数 | 无 | `GET /products?sort=price` | HTTP 200；返回列表按 price 排序 |
| API_PRODUCT_007 | P1 | 分页参数 | 无 | `GET /products?page=1` | HTTP 200；返回第一页商品 |
| API_PRODUCT_008 | P2 | 分页边界值 page=0 | 无 | `GET /products?page=0` | HTTP 200 或 400；不做崩溃即可 |

### 1.2 商品搜索 · GET /products/search

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_009 | P0 | 搜索匹配商品 | 无 | `GET /products/search?q=hammer` | HTTP 200；返回非空列表，商品 name/description 含关键词 |
| API_PRODUCT_010 | P1 | 搜索无匹配 | 无 | `GET /products/search?q=xyznonexistent999` | HTTP 200；返回空数组 `[]` |
| API_PRODUCT_011 | P2 | 搜索不传 q 参数 | 无 | `GET /products/search` | HTTP 200（q 可选）或 200 返回全量 |
| API_PRODUCT_012 | P3 | 搜索特殊字符 | 无 | `GET /products/search?q=<script>` | HTTP 200；不崩溃即可 |

### 1.3 商品详情 · GET /products/{productId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_013 | P0 | 查询存在的商品 | 已知有效 productId | `GET /products/{id}` | HTTP 200；响应含 id、name、price、description、brand（嵌套对象含 id/name）、category（嵌套对象含 id/name）、in_stock、is_rental |
| API_PRODUCT_014 | P1 | 查询不存在的商品 | 无 | `GET /products/nonexistent-id-99999` | HTTP 404 |
| API_PRODUCT_015 | P1 | productId 为空或非法 | 无 | `GET /products/ ` | HTTP 404 |

### 1.4 相关商品 · GET /products/{productId}/related

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_016 | P0 | 获取相关商品 | 已知有效 productId | `GET /products/{id}/related` | HTTP 200；返回商品列表（可能为空数组） |
| API_PRODUCT_017 | P1 | 不存在的商品相关 | 无 | `GET /products/nonexistent-id-99999/related` | HTTP 404 |

### 1.5 创建商品 · POST /products

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_018 | P0 | 创建商品 | 已知有效 brand_id、category_id | `POST /products`，传入 name、description、price、brand_id、category_id | HTTP 200 或 201；响应含 id、name、price |
| API_PRODUCT_019 | P1 | 缺少 name | 无 | 请求体中不传 name | HTTP 422 |
| API_PRODUCT_020 | P1 | 缺少 price | 无 | 请求体中不传 price | HTTP 422 |
| API_PRODUCT_021 | P1 | 不存在的 category_id | 无 | category_id 传入 `nonexistent-99999` | HTTP 422 或 200（取决于校验策略） |
| API_PRODUCT_022 | P1 | 不存在的 brand_id | 无 | brand_id 传入 `nonexistent-99999` | HTTP 422 或 200 |
| API_PRODUCT_023 | P2 | 负值 price | 无 | price 传入 `-9.99` | HTTP 422 |
| API_PRODUCT_024 | P1 | 空请求体 | 无 | `POST /products`，发送 `{}` | HTTP 422 |

### 1.6 更新商品 · PUT /products/{productId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_025 | P0 | 全量更新商品 | 创建测试商品 | `PUT /products/{id}`，传入完整合法 JSON | HTTP 200；随后 `GET /products/{id}` 验证字段已变更 |
| API_PRODUCT_026 | P1 | 更新不存在的商品 | 无 | `PUT /products/nonexistent-id-99999` | HTTP 404 |

### 1.7 部分更新商品 · PATCH /products/{productId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_027 | P0 | 部分更新商品名称 | 创建测试商品 | `PATCH /products/{id}`，只传 `{"name":"Patched Product"}` | HTTP 200；name 变更，其他字段不变 |
| API_PRODUCT_028 | P1 | PATCH 不存在的商品 | 无 | `PATCH /products/nonexistent-id-99999` | HTTP 404 |

### 1.8 删除商品 · DELETE /products/{productId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_029 | P0 | 删除商品 | 创建测试商品 | `DELETE /products/{id}` | HTTP 204 或 401；删除成功后 `GET /products/{id}` → 404 |
| API_PRODUCT_030 | P1 | 删除不存在的商品 | 无 | `DELETE /products/nonexistent-id-99999` | HTTP 404 或 401 |
| API_PRODUCT_031 | P3 | 重复删除同一商品 | 已删除一次 | 再次 `DELETE /products/{id}` | HTTP 404 或 401 |

---

### 1.9 边界补充

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_032 | P2 | price 为零 | 已知 brand_id、category_id | `POST /products`，price = 0 | HTTP 200/201 或 422 |
| API_PRODUCT_033 | P2 | price 极大值 | 同上 | price = 999999999.99 | HTTP 200/201 或 422 |
| API_PRODUCT_034 | P2 | name 为空字符串 | 同上 | name = `""` | HTTP 422 |
| API_PRODUCT_035 | P2 | name 超长（255+字符） | 同上 | name 传入 256 字符 | HTTP 422 |
| API_PRODUCT_036 | P1 | 缺少 brand_id | 无 | 请求体不传 brand_id | HTTP 422 |
| API_PRODUCT_037 | P1 | 缺少 category_id | 无 | 请求体不传 category_id | HTTP 422 |
| API_PRODUCT_038 | P2 | co2_rating 非法值 | 已知 ID | co2_rating 传入 `"X"`（非 A-E） | HTTP 422 或 200 |
| API_PRODUCT_039 | P2 | between 非法格式 | 无 | `GET /products?between=abc` | HTTP 200（按全量返回）或 400 |
| API_PRODUCT_040 | P2 | sort 非法值 | 无 | `GET /products?sort=invalid_field` | HTTP 200（忽略排序）或 400 |
| API_PRODUCT_041 | P2 | 组合筛选 by_brand + by_category | 已知 brand_slug + category_slug | `GET /products?by_brand=X&by_category=Y` | HTTP 200；返回同时满足两条件的商品 |
| API_PRODUCT_046 | P2 | product_image_id 不存在 | 已知 brand_id、category_id | `POST /products`，product_image_id 传入不存在值 | HTTP 422 或 200 |
| API_PRODUCT_047 | P2 | description 超长 | 同上 | description 传入 5000 字符 | HTTP 422 |
| API_PRODUCT_048 | P1 | is_location_offer 为 true | 同上 | `POST /products`，is_location_offer = true | HTTP 200/201；响应 is_location_offer = true |

### 1.10 权限/状态组合

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_042 | P1 | 未登录创建商品 | 无 | `POST /products`，无 Token | HTTP 401 |
| API_PRODUCT_043 | P1 | 未登录全量更新商品 | 无 | `PUT /products/{id}`，无 Token | HTTP 401 |
| API_PRODUCT_044 | P1 | 未登录部分更新商品 | 无 | `PATCH /products/{id}`，无 Token | HTTP 401 |
| API_PRODUCT_045 | P1 | 未登录删除商品 | 无 | `DELETE /products/{id}`，无 Token | HTTP 401 |

### 1.11 P3 深度防御补充

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_PRODUCT_049 | P3 | description 含 XSS 片段 | 已知 brand_id、category_id | `POST /products`，description = `"<script>alert(1)</script>"` | HTTP 200/201（应转义，不应执行脚本） |
| API_PRODUCT_050 | P3 | Token 过期后更新商品 | 创建商品→token 失效 | `PUT /products/{id}`，带过期 Token | HTTP 401 |
| API_PRODUCT_051 | P3 | Token 过期后删除商品 | 创建商品→token 失效 | `DELETE /products/{id}`，带过期 Token | HTTP 401 |

## 覆盖统计（Product）

| 端点 | 用例数 | 正常 | 异常 | 边界 |
|------|:--:|:--:|:--:|:--:|
| GET /products | 8 | 6 | 0 | 2 |
| GET /products/search | 4 | 2 | 1 | 1 |
| GET /products/{id} | 3 | 1 | 2 | 0 |
| GET /products/{id}/related | 2 | 1 | 1 | 0 |
| POST /products | 7 | 1 | 5 | 1 |
| PUT /products/{id} | 2 | 1 | 1 | 0 |
| PATCH /products/{id} | 2 | 1 | 1 | 0 |
| DELETE /products/{id} | 3 | 1 | 2 | 0 |
| 边界补充 | 13 | 2 | 4 | 7 |
| 权限/状态 | 4 | 0 | 0 | 4 |
| **合计** | **48** | **16** | **17** | **15** |
