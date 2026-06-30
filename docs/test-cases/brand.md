# Brand 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`

## 端点覆盖（7 个）

### 2.1 品牌列表 · GET /brands

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_BRAND_001 | 获取品牌列表 | 无 | `GET /brands` | HTTP 200；返回非空 JSON 数组，元素含 id/name/slug |
| API_BRAND_002 | 列表数据结构完整 | 无 | 抽查前 5 个品牌 | 每个元素的 id/name/slug 均为非空字符串 |

### 2.2 创建品牌 · POST /brands

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_BRAND_003 | 创建品牌 | 无 | `POST /brands`，传入合法 name + slug | HTTP 201；响应含 id/name/slug |
| API_BRAND_004 | 创建缺少 name | 无 | 只传 slug | HTTP 422 |
| API_BRAND_005 | 创建缺少 slug | 无 | 只传 name | HTTP 422 |
| API_BRAND_006 | 创建重复 slug | 已知存在的 slug | 使用相同 slug 再次创建 | HTTP 409 |
| API_BRAND_007 | 创建空请求体 | 无 | `POST /brands`，`{}` | HTTP 422 |

### 2.3 单个品牌 · GET /brands/{brandId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_BRAND_008 | 查询存在的品牌 | 已知品牌 ID | `GET /brands/{id}` | HTTP 200；响应 id 匹配 |
| API_BRAND_009 | 查询不存在的品牌 | 无 | `GET /brands/nonexistent-id-99999` | HTTP 404 |
| API_BRAND_010 | 品牌 ID 为空字符串 | 无 | `GET /brands/ ` | HTTP 404 或 405 |

### 2.4 更新品牌 · PUT /brands/{brandId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_BRAND_011 | 全量更新品牌 | 无 | `PUT /brands/{id}`，完整 name + slug | HTTP 200；响应中 name/slug 已变更 |
| API_BRAND_012 | 更新不存在的品牌 | 无 | `PUT /brands/nonexistent-id-99999` | HTTP 404 |
| API_BRAND_013 | 更新缺少 name | 无 | `PUT /brands/{id}`，只传 slug | HTTP 422 |

### 2.5 部分更新品牌 · PATCH /brands/{brandId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_BRAND_014 | 部分更新品牌名称 | 无 | `PATCH /brands/{id}`，只传 `{"name":"Patched"}` | HTTP 200；name 变更，slug 不变 |
| API_BRAND_015 | PATCH 不存在的品牌 | 无 | `PATCH /brands/nonexistent-id-99999` | HTTP 404 |

### 2.6 删除品牌 · DELETE /brands/{brandId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_BRAND_016 | 删除品牌 | 无 | `DELETE /brands/{id}` | HTTP 204；随后 `GET /brands/{id}` → 404 |
| API_BRAND_017 | 删除不存在的品牌 | 无 | `DELETE /brands/nonexistent-id-99999` | HTTP 404 或 422 |
| API_BRAND_018 | 重复删除同一品牌 | 已删除一次 | 再次 `DELETE /brands/{id}` | HTTP 404 |

### 2.7 搜索品牌 · GET /brands/search

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_BRAND_019 | 搜索有匹配 | 无 | `GET /brands/search?q=for` | HTTP 200；返回匹配列表 |
| API_BRAND_020 | 搜索无匹配 | 无 | `GET /brands/search?q=xyznonexistent999` | HTTP 200；返回空数组 `[]` |
| API_BRAND_021 | 搜索不传 q 参数 | 无 | `GET /brands/search` | HTTP 200；返回全量列表（q 为可选） |

---

---

## 四、覆盖统计

| 模块 | 端点 | 用例 | 正常 | 异常 | 边界 | 权限 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|
| User | 13 | 56 | 12 | 23 | 11 | 10 |
| Brand | 7 | 21 | 10 | 7 | 3 | 1 |
| Category | 8 | 22 | 12 | 8 | 2 | 0 |
| **合计** | **28** | **99** | **34** | **38** | **16** | **11** |

### HTTP 状态码覆盖

| 状态码 | 出现频次 | 覆盖的端点 |
|:--:|:--:|------|
| 200 | ~30 | login/me/refresh/logout/users/brands/categories 读取操作 |
| 201 | ~8 | register/create品牌/create分类 |
| 204 | ~3 | delete 操作 |
| 401 | ~15 | 所有受保护端点未认证场景 |
| 404 | ~12 | 不存在的资源 ID |
| 409 | ~4 | 重复注册/创建 |
| 422 | ~18 | 字段校验失败 |
| 400 | ~2 | 部分边界参数 |

---

## 五、实际 API 行为备注

> 以下为 v1 真机验证确认的 API 行为，v2 用例预期结果已据此校准。

| 项目 | 文档/惯例 | 实际行为 |
|------|------|------|
| token_type 大小写 | `Bearer` | `bearer`（小写） |
| 校验失败状态码 | 400 Bad Request | 422 Unprocessable Entity |
| 分类单条查询 | `GET /categories/{id}` | 仅 `GET /categories/tree/{id}` |
| Brand/Category 创建 | 需 Token | 本环境公开，无需认证 |
| 搜索 q 参数 | required | optional，不传返回全量 |
| PUT /users/{id} 响应 | 用户完整对象 | `{"success": true}` |
| 邮箱格式校验 | 严格 format=email | 宽松，可能接受无 @ 的字符串 |
| PATCH /users/{id} | 部分更新 | 待 v2 验证 |
| DELETE /users/{id} | 删除本人 | 待 v2 验证 |
| PUT/PATCH Brand/Category | 更新 | 待 v2 验证 |
| DELETE Brand/Category | 删除 | 待 v2 验证 |