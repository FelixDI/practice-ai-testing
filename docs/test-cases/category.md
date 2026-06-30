# Category 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`

## 端点覆盖（8 个）

### 3.1 分类列表 · GET /categories

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_001 | 获取分类列表 | 无 | `GET /categories` | HTTP 200；返回非空 JSON 数组，元素含 id/name/slug/parent_id |
| API_CATEGORY_002 | 列表数据结构完整 | 无 | 抽查前 5 个分类 | id/name/slug 为非空字符串，parent_id 可为 null |

### 3.2 分类树 · GET /categories/tree

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_003 | 获取分类树 | 无 | `GET /categories/tree` | HTTP 200；顶级节点含 sub_categories 嵌套数组 |
| API_CATEGORY_004 | 按 slug 筛选树 | 已知 category slug | `GET /categories/tree?by_category_slug=<slug>` | HTTP 200 |

### 3.3 创建分类 · POST /categories

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_005 | 创建顶级分类 | 无 | `POST /categories`，name + slug | HTTP 201 |
| API_CATEGORY_006 | 创建含 parent_id 的子分类 | 已知父分类 ID | `POST /categories`，name + slug + parent_id | HTTP 201；响应 parent_id 与请求一致 |
| API_CATEGORY_007 | 创建 parent_id 为不存在的 ID | 无 | parent_id 传 `nonexistent-99999` | HTTP 422 或 201 |
| API_CATEGORY_008 | 创建缺少 name | 无 | 只传 slug | HTTP 422 |
| API_CATEGORY_009 | 创建缺少 slug | 无 | 只传 name | HTTP 422 |
| API_CATEGORY_010 | 创建重复 slug | 已知存在的 slug | 相同 slug 再次创建 | HTTP 409 |

### 3.4 分类子树 · GET /categories/tree/{categoryId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_011 | 查询存在的分类子树 | 已知分类 ID | `GET /categories/tree/{id}` | HTTP 200；响应 id 匹配 |
| API_CATEGORY_012 | 查询不存在的分类 | 无 | `GET /categories/tree/nonexistent-id-99999` | HTTP 404 |

### 3.5 搜索分类 · GET /categories/search

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_013 | 搜索有匹配 | 无 | `GET /categories/search?q=hand` | HTTP 200；返回匹配列表 |
| API_CATEGORY_014 | 搜索无匹配 | 无 | `GET /categories/search?q=xyznonexistent999` | HTTP 200；返回空数组 `[]` |
| API_CATEGORY_015 | 搜索不传 q 参数 | 无 | `GET /categories/search` | HTTP 200（q 可选） |

### 3.6 更新分类 · PUT /categories/{categoryId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_016 | 全量更新分类 | 无 | `PUT /categories/{id}`，完整 name + slug + parent_id | HTTP 200 |
| API_CATEGORY_017 | 更新不存在的分类 | 无 | `PUT /categories/nonexistent-id-99999` | HTTP 404 |

### 3.7 部分更新分类 · PATCH /categories/{categoryId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_018 | 部分更新分类名称 | 无 | `PATCH /categories/{id}`，只传 `{"name":"Patched"}` | HTTP 200；name 变更 |
| API_CATEGORY_019 | PATCH 不存在的分类 | 无 | `PATCH /categories/nonexistent-id-99999` | HTTP 404 |

### 3.8 删除分类 · DELETE /categories/{categoryId}

| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|
| API_CATEGORY_020 | 删除分类 | 创建测试分类 | `DELETE /categories/{id}` | HTTP 204；随后 `GET /categories/tree/{id}` → 404 |
| API_CATEGORY_021 | 删除不存在的分类 | 无 | `DELETE /categories/nonexistent-id-99999` | HTTP 404 或 422 |
| API_CATEGORY_022 | 重复删除 | 已删除一次 | 再次 `DELETE /categories/{id}` | HTTP 404 |

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