# Product Spec 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Product Spec 依赖 Product 模块——所有规格操作基于有效的 product_id

---

## 端点覆盖（6 个）

### 1.1 获取产品规格列表 · GET /products/{productId}/specs

> **Response (200)**: 规格数组  
> **Auth**: ❌ 无需登录  
> **Param**: `productId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_001 | P0 | 获取产品规格列表 | 已知有效 product_id（该产品有规格） | `GET /products/{product_id}/specs` | HTTP 200；返回规格数组，每项含 `id`、`product_id`、`spec_name`、`spec_value` |
| API_SPEC_041 | P1 | 获取不存在产品的规格列表 | 无 | `GET /products/nonexistent-99999/specs` | HTTP 404 或 200（空数组） |

### 1.2 添加产品规格 · POST /products/{productId}/specs

> **Request**: `{ spec_name*, spec_value*, spec_unit? }`（`*` = 必填）  
> **Response (201)**: `ProductSpecResponse { id, product_id, spec_name, spec_value, spec_unit }`  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_002 | P0 | 添加产品规格（完整字段） | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Weight","spec_value":"1.5","spec_unit":"kg"}` | HTTP 201；响应含 `id`、`product_id`、`spec_name`、`spec_value`、`spec_unit` |
| API_SPEC_003 | P0 | 添加产品规格（仅必填字段） | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Color","spec_value":"Red"}` | HTTP 201；响应含创建的规格，`spec_unit` 为 null |
| API_SPEC_004 | P0 | 添加规格缺少 spec_name | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_value":"100"}` | HTTP 422 |
| API_SPEC_005 | P0 | 添加规格缺少 spec_value | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Width"}` | HTTP 422 |
| API_SPEC_006 | P1 | 未登录添加规格 | 无有效 token | `POST /products/{product_id}/specs`，不带 Authorization 头 | HTTP 401 |
| API_SPEC_007 | P1 | 为不存在的产品添加规格 | 已登录 | `POST /products/nonexistent-99999/specs`，传入完整字段 | HTTP 404（注：文档未显式列出，按 REST 惯例预期） |

### 1.3 获取指定规格 · GET /products/{productId}/specs/{specId}

> **Response (200)**: `ProductSpecResponse { id, product_id, spec_name, spec_value, spec_unit }`  
> **Auth**: ❌ 无需登录  
> **Param**: `productId` (path, required), `specId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_008 | P0 | 获取指定规格详情 | 已知有效 product_id 和 spec_id | `GET /products/{product_id}/specs/{spec_id}` | HTTP 200；响应含 `id`、`product_id`、`spec_name`、`spec_value`、`spec_unit`，`id` 与 spec_id 一致 |
| API_SPEC_009 | P1 | 获取不存在的规格 | 已知有效 product_id | `GET /products/{product_id}/specs/nonexistent-99999` | HTTP 404（注：文档未显式列出，按 REST 惯例预期） |

### 1.4 更新产品规格 · PUT /products/{productId}/specs/{specId}

> **Request**: `{ spec_name?, spec_value?, spec_unit? }`（全部可选）  
> **Response (200)**: 更新结果  
> **Auth**: ✅ 需要登录  
> **Param**: `productId` (path, required), `specId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_010 | P0 | 更新规格值 | 已登录、已知有效 product_id 和 spec_id | `PUT /products/{product_id}/specs/{spec_id}`，传入 `{"spec_value":"2.0"}` | HTTP 200；随后 `GET /products/{product_id}/specs/{spec_id}` 验证 spec_value 已变更 |
| API_SPEC_011 | P0 | 更新规格名称和单位 | 已登录、已知有效 product_id 和 spec_id | `PUT /products/{product_id}/specs/{spec_id}`，传入 `{"spec_name":"Net Weight","spec_unit":"g"}` | HTTP 200；随后 `GET` 验证字段已变更 |
| API_SPEC_012 | P1 | 未登录更新规格 | 无有效 token | `PUT /products/{product_id}/specs/{spec_id}`，不带 Authorization 头 | HTTP 401 |

### 1.5 删除产品规格 · DELETE /products/{productId}/specs/{specId}

> **Response (204)**: No Content  
> **Auth**: ✅ 需要登录  
> **Param**: `productId` (path, required), `specId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_013 | P0 | 删除产品规格成功 | 已登录、已知有效 product_id 和 spec_id | `DELETE /products/{product_id}/specs/{spec_id}` | HTTP 204；随后 `GET /products/{product_id}/specs/{spec_id}` 返回 404 |
| API_SPEC_014 | P1 | 未登录删除规格 | 无有效 token | `DELETE /products/{product_id}/specs/{spec_id}`，不带 Authorization 头 | HTTP 401 |

### 1.6 获取所有规格名称 · GET /product-specs/names

> **Response (200)**: 去重后的规格名称及其值列表  
> **Auth**: ❌ 无需登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_015 | P0 | 获取所有规格名称列表 | 无 | `GET /product-specs/names` | HTTP 200；返回去重后的规格名称及对应值 |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 10 | Happy Path（查列表、添加×2、查详情、更新×2、删除、名称列表）+ 缺失必填字段 × 2 |
| P1 | 8 | 未登录操作（401 × 3）、不存在资源（404 × 5） |
| **合计** | **18** | 覆盖 6 个端点的核心链路 + 关键异常路径 |

---

> **说明**：部分 404 场景在 API 文档中未显式列出（如 `GET /specs/{specId}` 对不存在的 spec），按 RESTful 惯例设计，实际执行时以服务端返回为准。  

---

## P2 边界用例

### 2.1 添加产品规格 · POST /products/{productId}/specs（字段边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_016 | P2 | spec_name 为空字符串 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"","spec_value":"100"}` | HTTP 422 |
| API_SPEC_017 | P2 | spec_value 为空字符串 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Weight","spec_value":""}` | HTTP 422（或 201 允许空值） |
| API_SPEC_018 | P2 | spec_name 为超长字符串 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，spec_name = 256 个 `A` | HTTP 422 |
| API_SPEC_019 | P2 | spec_value 为超长字符串 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，spec_value = 256 个 `B` | HTTP 422（或 201） |
| API_SPEC_020 | P2 | spec_unit 为空字符串 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Width","spec_value":"100","spec_unit":""}` | HTTP 201（空字符串）或 422 |
| API_SPEC_021 | P2 | spec_unit 显式传 null | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Width","spec_value":"100","spec_unit":null}` | HTTP 201；响应 `spec_unit` 为 null |
| API_SPEC_022 | P2 | spec_name 为纯空格 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"   ","spec_value":"100"}` | HTTP 422 |
| API_SPEC_023 | P2 | spec_value 为纯空格 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Width","spec_value":"   "}` | HTTP 201 或 422 |
| API_SPEC_024 | P2 | spec_name 含特殊字符 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，spec_name = `"<b>Bold</b>"` | HTTP 201（服务端应转义） |
| API_SPEC_025 | P2 | 请求体含额外未知字段 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，合法字段 + `{"extra":"ignored"}` | HTTP 201（忽略额外字段）或 422 |
| API_SPEC_042 | P2 | spec_name 为 null | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":null,"spec_value":"100"}` | HTTP 422 |
| API_SPEC_043 | P2 | spec_value 为 null | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，传入 `{"spec_name":"Width","spec_value":null}` | HTTP 422 |

### 2.2 更新产品规格 · PUT /products/{productId}/specs/{specId}（字段边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_026 | P2 | 更新为空请求体 | 已登录、已知有效 product_id 和 spec_id | `PUT /products/{product_id}/specs/{spec_id}`，传入 `{}` | HTTP 200（无变更） |
| API_SPEC_027 | P2 | 更新 spec_unit 为 null | 已登录、已知有效 product_id 和 spec_id | `PUT /products/{product_id}/specs/{spec_id}`，传入 `{"spec_unit":null}` | HTTP 200；随后 GET 验证 spec_unit 变为 null |
| API_SPEC_028 | P2 | 更新 spec_name 为空字符串 | 已登录、已知有效 product_id 和 spec_id | `PUT /products/{product_id}/specs/{spec_id}`，传入 `{"spec_name":""}` | HTTP 422 |
| API_SPEC_029 | P2 | 更新 spec_value 为空字符串 | 已登录、已知有效 product_id 和 spec_id | `PUT /products/{product_id}/specs/{spec_id}`，传入 `{"spec_value":""}` | HTTP 200 或 422 |
| API_SPEC_044 | P1 | 更新不存在的规格 | 已登录、已知有效 product_id | `PUT /products/{product_id}/specs/nonexistent-99999` | HTTP 404 |
| API_SPEC_045 | P1 | 为不存在的产品更新规格 | 已登录、已知有效 spec_id | `PUT /products/nonexistent-99999/specs/{spec_id}` | HTTP 404 或 500 |

### 2.3 路径参数边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_030 | P2 | productId 含特殊字符 | 无 | `GET /products/<script>/specs` | HTTP 404 或 422 |
| API_SPEC_031 | P2 | specId 含特殊字符（查详情） | 已知有效 product_id | `GET /products/{product_id}/specs/<img>` | HTTP 404 或 422 |
| API_SPEC_032 | P2 | specId 含特殊字符（删除） | 已登录、已知有效 product_id | `DELETE /products/{product_id}/specs/'; DROP--` | HTTP 404 或 422 |

### 2.4 重复操作边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_033 | P2 | 删除已删除的规格 | 已登录、该 spec 已删除 | `DELETE /products/{product_id}/specs/{deleted_spec_id}` | HTTP 404 |
| API_SPEC_034 | P2 | 同一产品重复添加同名规格 | 已登录、已存在 spec_name="Weight" | `POST /products/{product_id}/specs`，再次传入 `{"spec_name":"Weight","spec_value":"2.0"}` | HTTP 201（允许）或 409 |

---

## P2 用例汇总

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 21 | spec_name/spec_value/spec_unit 空值/null/超长/空格/特殊字符 × 12；PUT 空 body/null/空字符串 × 4；路径参数特殊字符 × 3；重复操作 × 2 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 10 |
| P1 | 8 |
| P2 | 21 |
| **合计** | **39** |

---

## P3 深度防御用例

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_SPEC_035 | P3 | 非管理员用户尝试添加规格 | 使用普通用户 token（非管理员）登录 | `POST /products/{product_id}/specs`，带普通用户 token | HTTP 401 或 403 |
| API_SPEC_036 | P3 | 非管理员用户尝试更新规格 | 使用普通用户 token 登录、已知 spec_id | `PUT /products/{product_id}/specs/{spec_id}`，带普通用户 token | HTTP 401 或 403 |
| API_SPEC_037 | P3 | 非管理员用户尝试删除规格 | 使用普通用户 token 登录、已知 spec_id | `DELETE /products/{product_id}/specs/{spec_id}`，带普通用户 token | HTTP 401 或 403 |
| API_SPEC_038 | P3 | Token 过期后添加规格 | 使用已过期的 token | `POST /products/{product_id}/specs`，带过期 Authorization 头 | HTTP 401 |
| API_SPEC_039 | P3 | Token 过期后删除规格 | 使用已过期的 token | `DELETE /products/{product_id}/specs/{spec_id}`，带过期 token | HTTP 401 |
| API_SPEC_040 | P3 | spec_value 含 SQL 注入片段 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，spec_value = `"1'; DROP TABLE product_specs; --"` | HTTP 201（服务端应参数化查询，不应报数据库错误） |
| API_SPEC_046 | P3 | spec_name 含 XSS 片段 | 已登录、已知有效 product_id | `POST /products/{product_id}/specs`，spec_name = `"<script>alert(1)</script>"`，spec_value 有效 | HTTP 201（服务端应转义，不应执行脚本） |
| API_SPEC_047 | P3 | Token 过期后更新规格 | 使用已过期的 token | `PUT /products/{product_id}/specs/{spec_id}`，带过期 Authorization 头 | HTTP 401 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 10 |
| P1 | 5 |
| P2 | 24 |
| P3 | 8 |
| **合计** | **47** |

> 注：P0+P1 = 18，加上 P2(21) = 39，加上 P3(8) = 47
