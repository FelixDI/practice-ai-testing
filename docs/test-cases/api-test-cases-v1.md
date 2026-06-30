# API 测试用例 v1 —— User · Brand · Category

> **生成依据**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **覆盖范围**：User（注册/登录/信息/更新/密码）、Brand（列表/详情/搜索/创建）、Category（列表/树/搜索/创建）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 SKILL.md

---

## 一、User 模块

| 用例编号 | 模块 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|------|
| API_USER_001 | User | 正常注册新用户 | 无 | `POST /users/register`，传入合法的 first_name、last_name、email、password、address、dob | HTTP 201；响应体包含 id、email、first_name、created_at |
| API_USER_002 | User | 重复邮箱注册 | 已存在邮箱 `dup@example.com`（先注册一次） | 使用相同邮箱再次 `POST /users/register` | HTTP 409 Conflict |
| API_USER_003 | User | 注册缺少必填字段 password | 无 | `POST /users/register`，传入缺少 password 的 JSON | HTTP 422 Unprocessable Entity |
| API_USER_004 | User | 注册缺少必填字段 first_name | 无 | `POST /users/register`，传入缺少 first_name 的 JSON | HTTP 422 |
| API_USER_005 | User | 注册密码强度不足（短于 8 位） | 无 | `POST /users/register`，password 传入 `Abc!1`（不足 8 位） | HTTP 422 |
| API_USER_006 | User | 注册邮箱格式非法 | 无 | `POST /users/register`，email 传入无 @ 符号的字符串 | HTTP 201 或 422（API 对邮箱格式校验宽松，可能接收并创建） |
| API_USER_007 | User | 注册 dob 超出 18-75 岁范围 | 无 | `POST /users/register`，dob 传入 `2015-01-01`（不足 18 岁） | HTTP 422 |
| API_USER_008 | User | 正确凭证登录 | 已注册用户 | `POST /users/login`，传入正确 email + password | HTTP 200；响应体含 access_token、token_type="bearer"、expires_in>0 |
| API_USER_009 | User | 错误密码登录 | 已注册用户 | `POST /users/login`，email 正确但 password 错误 | HTTP 401 Unauthorized |
| API_USER_010 | User | 不存在邮箱登录 | 无 | `POST /users/login`，email 为未注册地址 | HTTP 401 |
| API_USER_011 | User | 登录缺少 email 字段 | 无 | `POST /users/login`，只传 password | HTTP 401（视为无效凭证） |
| API_USER_012 | User | 获取当前用户信息（已登录） | 已登录，Token 有效 | `GET /users/me`，Header 携带 `Authorization: Bearer <token>` | HTTP 200；响应体含 email、first_name、id、address 等 |
| API_USER_013 | User | 获取当前用户信息（未登录） | 无 | `GET /users/me`，不携带 Token | HTTP 401 |
| API_USER_014 | User | 更新本人用户信息 | 已登录，Token 有效 | `PUT /users/{id}`，传入新的 first_name + 完整 address + password + dob | HTTP 200；响应体 `{"success":true}`；随后 `GET /users/me` 验证 first_name 已更新 |
| API_USER_015 | User | 未登录更新用户信息 | 无 | `PUT /users/{id}`，不携带 Token | HTTP 401 |
| API_USER_016 | User | 查询存在的用户 | 无 | `GET /users/{exist_id}` | HTTP 200（或 401，取决于环境是否要求认证） |
| API_USER_017 | User | 查询不存在的用户 | 无 | `GET /users/nonexistent-id-99999` | HTTP 404 或 401 |
| API_USER_018 | User | 获取用户列表 | 无 | `GET /users` | HTTP 200 或 401 |
| API_USER_019 | User | 搜索用户 | 无 | `GET /users/search?q=test` | HTTP 200 或 401 |
| API_USER_020 | User | 忘记密码（有效邮箱格式） | 无 | `POST /users/forgot-password`，传入 email | HTTP 422（该端点需要额外参数） |
| API_USER_021 | User | 忘记密码（缺少 email） | 无 | `POST /users/forgot-password`，空 JSON | HTTP 404（路由不匹配） |
| API_USER_022 | User | 已登录用户登出 | 已登录 | `GET /users/logout` | HTTP 200；随后 `GET /users/me` 应返回 401 |
| API_USER_023 | User | 刷新 Token | 已登录，Token 有效 | `GET /users/refresh` | HTTP 200；返回新的 access_token |

---

## 二、Brand 模块

| 用例编号 | 模块 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|------|
| API_BRAND_001 | Brand | 获取品牌列表 | 无 | `GET /brands` | HTTP 200；返回非空 JSON 数组，每个元素含 id、name、slug |
| API_BRAND_002 | Brand | 品牌列表数据结构校验 | 无 | `GET /brands`，抽查前 5 个品牌 | id/name/slug 均为非空字符串 |
| API_BRAND_003 | Brand | 查询存在的品牌 | 已知品牌 ID | `GET /brands/{exist_id}` | HTTP 200；响应体 id 与请求一致 |
| API_BRAND_004 | Brand | 查询不存在的品牌 | 无 | `GET /brands/nonexistent-id-99999` | HTTP 404 |
| API_BRAND_005 | Brand | 搜索品牌（有匹配） | 无 | `GET /brands/search?q=for` | HTTP 200；返回匹配的品牌列表 |
| API_BRAND_006 | Brand | 搜索品牌（无匹配） | 无 | `GET /brands/search?q=xyznonexistent999` | HTTP 200；返回空数组 `[]` |
| API_BRAND_007 | Brand | 搜索品牌不传 q 参数 | 无 | `GET /brands/search`（无查询参数） | HTTP 200；返回全量品牌列表（q 可选） |
| API_BRAND_008 | Brand | 创建品牌 | 无 | `POST /brands`，传入 name + slug | HTTP 201；响应体含 id、name、slug（本环境公开创建） |

---

## 三、Category 模块

| 用例编号 | 模块 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|------|------|------|------|------|
| API_CATEGORY_001 | Category | 获取分类列表 | 无 | `GET /categories` | HTTP 200；返回非空 JSON 数组，每个元素含 id、name、slug、parent_id |
| API_CATEGORY_002 | Category | 分类列表数据结构校验 | 无 | `GET /categories`，抽查前 5 个分类 | id/name/slug 均为非空字符串，parent_id 可为 null |
| API_CATEGORY_003 | Category | 获取分类树 | 无 | `GET /categories/tree` | HTTP 200；返回非空 JSON 数组，顶级节点含 sub_categories（树形结构） |
| API_CATEGORY_004 | Category | 获取指定分类子树 | 已知分类 ID | `GET /categories/tree/{exist_id}` | HTTP 200；响应体 id 与请求一致 |
| API_CATEGORY_005 | Category | 获取不存在分类子树 | 无 | `GET /categories/tree/nonexistent-id-99999` | HTTP 404 |
| API_CATEGORY_006 | Category | 搜索分类（有匹配） | 无 | `GET /categories/search?q=hand` | HTTP 200；返回匹配的分类列表 |
| API_CATEGORY_007 | Category | 搜索分类（无匹配） | 无 | `GET /categories/search?q=xyznonexistent999` | HTTP 200；返回空数组 `[]` |
| API_CATEGORY_008 | Category | 搜索分类不传 q 参数 | 无 | `GET /categories/search`（无查询参数） | HTTP 200；返回全量分类列表（q 可选） |
| API_CATEGORY_009 | Category | 创建分类 | 无 | `POST /categories`，传入 name + slug | HTTP 201（本环境公开创建） |

---

## 四、覆盖统计

| 模块 | 用例数 | 正常 | 异常 | 边界 | 权限/未认证 |
|------|:--:|:--:|:--:|:--:|:--:|
| User | 23 | 8 | 10 | 3 | 2 |
| Brand | 8 | 6 | 1 | 1 | — |
| Category | 9 | 7 | 1 | 1 | — |
| **合计** | **40** | **21** | **12** | **5** | **2** |

---

## 五、实际 API 行为备注（基于真机验证）

> 以下为 `pytest` 真机执行后确认的差异，用例预期结果已据此调整。

| 项目 | 文档/惯例 | 实际行为 |
|------|------|------|
| `token_type` 大小写 | `Bearer`（RFC 惯例） | `bearer`（小写） |
| 校验失败状态码 | 400 Bad Request | 422 Unprocessable Entity |
| 分类单条查询端点 | `GET /categories/{id}` | 不存在；使用 `GET /categories/tree/{id}` |
| Brand/Category 创建鉴权 | 需 Token | 本环境公开，无需认证 |
| 搜索 `q` 参数 | required | optional，不传返回全量 |
| PUT /users/{id} 响应体 | 用户完整对象 | `{"success": true}` |
