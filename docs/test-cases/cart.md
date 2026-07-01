# Cart 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Cart 依赖 Product 的商品数据——需要有效 product_id 才能添加购物车商品

---

## 端点覆盖（6 个）

### 1.1 创建购物车 · POST /carts

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CART_001 | P0 | 创建购物车 | 无 | `POST /carts`，无请求体 | HTTP 201；响应含 cart id |

### 1.2 添加商品到购物车 · POST /carts/{id}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CART_002 | P0 | 添加商品到购物车 | 已创建 cart、已知有效 product_id | `POST /carts/{cart_id}`，传入 `{"product_id":"<valid>", "quantity":2}` | HTTP 200；响应含商品信息 |
| API_CART_003 | P1 | 缺少 product_id | 已创建 cart | 只传 `{"quantity":1}` | HTTP 422 |
| API_CART_004 | P1 | 缺少 quantity | 已创建 cart | 只传 `{"product_id":"<valid>"}` | HTTP 422 |
| API_CART_005 | P1 | 不存在的 product_id | 已创建 cart | product_id = `"nonexistent-99999"` | HTTP 404 或 422 |
| API_CART_006 | P1 | 向不存在的 cart 添加商品 | 无 | `POST /carts/nonexistent-99999` | HTTP 404 |
| API_CART_007 | P2 | quantity = 0 | 已创建 cart | quantity = 0 | HTTP 422 |
| API_CART_008 | P2 | 负值 quantity | 已创建 cart | quantity = -1 | HTTP 422 |
| API_CART_009 | P2 | quantity 极大值 | 已创建 cart | quantity = 99999 | HTTP 200 或 422 |
| API_CART_010 | P2 | quantity 为字符串 | 已创建 cart | quantity = `"abc"` | HTTP 422 |
| API_CART_011 | P1 | 重复添加相同商品 | 已添加过该 product_id | 再次添加相同 product_id | HTTP 200（累加数量）或 409 |

### 1.3 获取购物车 · GET /carts/{cartId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CART_012 | P0 | 获取已存在的购物车 | 已创建 cart 并添加了商品 | `GET /carts/{cart_id}` | HTTP 200；响应含 id 和商品列表，每项含 product_id/quantity |
| API_CART_013 | P0 | 获取空购物车 | 刚创建 cart，未添加商品 | `GET /carts/{cart_id}` | HTTP 200；商品列表为空 |
| API_CART_014 | P1 | 获取不存在的购物车 | 无 | `GET /carts/nonexistent-99999` | HTTP 404 |

### 1.4 更新商品数量 · PUT /carts/{cartId}/product/quantity

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CART_015 | P0 | 更新购物车中商品数量 | 已创建 cart 并添加商品 | `PUT /carts/{cart_id}/product/quantity`，传入新 quantity | HTTP 200；随后 `GET /carts/{cart_id}` 验证数量已变更 |
| API_CART_016 | P1 | 更新不存在 cart 中的数量 | 无 | `PUT /carts/nonexistent-99999/product/quantity` | HTTP 404 |
| API_CART_017 | P1 | 更新 cart 中不存在的商品 | 已创建 cart | product_id 为未添加过的商品 | HTTP 404 或 422 |
| API_CART_018 | P2 | 更新 quantity 为 0 | 已创建 cart 并添加商品 | quantity = 0 | HTTP 200（移除商品）或 422 |

### 1.5 从购物车移除商品 · DELETE /carts/{cartId}/product/{productId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CART_019 | P0 | 从购物车移除商品 | 已创建 cart 并添加商品 | `DELETE /carts/{cart_id}/product/{product_id}` | HTTP 204；随后 `GET /carts/{cart_id}` 验证商品已移除 |
| API_CART_020 | P1 | 移除 cart 中不存在的商品 | 已创建 cart | product_id 为未添加过的商品 | HTTP 404 或 422 |
| API_CART_021 | P1 | 从不存在的 cart 移除商品 | 无 | `DELETE /carts/nonexistent-99999/product/<valid_id>` | HTTP 404 |

### 1.6 删除购物车 · DELETE /carts/{cartId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CART_022 | P0 | 删除购物车 | 已创建 cart | `DELETE /carts/{cart_id}` | HTTP 204；随后 `GET /carts/{cart_id}` → 404 |
| API_CART_023 | P1 | 删除不存在的购物车 | 无 | `DELETE /carts/nonexistent-99999` | HTTP 404 |
| API_CART_024 | P3 | 重复删除同一购物车 | 已删除一次 | 再次 `DELETE /carts/{cart_id}` | HTTP 404 |

### 1.7 边界/状态补充

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CART_025 | P2 | product_id 为空字符串 | 已创建 cart | `POST /carts/{cart_id}`，product_id = `""` | HTTP 422 |
| API_CART_026 | P3 | 更新已移除商品的数量 | cart 中有商品 A→已移除 | `PUT /carts/{cart_id}/product/quantity`，product_id = A | HTTP 404 |

---

## 覆盖统计（Cart）

| 优先级 | 用例数 | 占比 | 内容 |
|:--:|:--:|:--:|------|
| P0 | 8 | 31% | 创建→添加→获取→更新数量→移除→删除 完整链路 |
| P1 | 11 | 42% | 缺字段(422)、不存在(404)、重复添加 |
| P2 | 6 | 23% | quantity 边界(0/负/极大/字符串)、product_id 空字符串 |
| P3 | 1 | 4% | 重复删除、更新已移除商品 |
| **合计** | **26** | 100% | 6 端点全覆盖 |

### 核心业务链路

```
POST /carts (创建) → POST /carts/{id} (加商品) → GET /carts/{id} (验证)
    → PUT /carts/{id}/product/quantity (改数量) → GET /carts/{id} (验证)
    → DELETE /carts/{id}/product/{pid} (移除商品) → GET /carts/{id} (验证已移除)
    → DELETE /carts/{id} (删除购物车) → GET /carts/{id} (验证 404)
```
