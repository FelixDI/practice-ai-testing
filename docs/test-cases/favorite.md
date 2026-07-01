# Favorite 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Favorite 依赖 User（登录态）和 Product（有效 product_id）—— 需先登录获取 token，且需要已知存在的商品 ID

---

## 端点覆盖（4 个）

### 1.1 添加收藏 · POST /favorites

> **Request**: `FavoriteRequest { product_id: string }`  
> **Response (200)**: `FavoriteResponse { id, product_id, user_id }`  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_001 | P0 | 收藏商品成功 | 已登录、已知有效 product_id | `POST /favorites`，传入 `{"product_id":"<valid>"}` | HTTP 200；响应含 `id`、`product_id`、`user_id`，`product_id` 与入参一致 |
| API_FAVORITE_002 | P0 | 收藏商品时缺少 product_id | 已登录 | `POST /favorites`，传入空 JSON `{}` | HTTP 422 |
| API_FAVORITE_003 | P1 | 未登录收藏商品 | 无有效 token | `POST /favorites`，传入 `{"product_id":"<valid>"}`，不带 Authorization 头 | HTTP 401 |
| API_FAVORITE_004 | P1 | 收藏不存在的商品 | 已登录 | `POST /favorites`，传入 `{"product_id":"nonexistent-99999"}` | HTTP 404 |
| API_FAVORITE_005 | P1 | 重复收藏同一商品 | 已登录、该商品已收藏 | 再次 `POST /favorites`，传入同一 `product_id` | HTTP 409 |

### 1.2 获取收藏列表 · GET /favorites

> **Response (200)**: 数组，元素为 `FavoriteResponse { id, product_id, user_id }`  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_006 | P0 | 获取收藏列表（有数据） | 已登录、已收藏至少 1 个商品 | `GET /favorites` | HTTP 200；返回非空数组，每项含 `id`、`product_id`、`user_id` |
| API_FAVORITE_007 | P0 | 获取收藏列表（空列表） | 已登录、未收藏任何商品 | `GET /favorites` | HTTP 200；返回空数组 `[]` |
| API_FAVORITE_008 | P1 | 未登录获取收藏列表 | 无有效 token | `GET /favorites`，不带 Authorization 头 | HTTP 401 |

### 1.3 获取指定收藏 · GET /favorites/{favoriteId}

> **Response (200)**: `FavoriteResponse { id, product_id, user_id }`  
> **Auth**: ✅ 需要登录  
> **Param**: `favoriteId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_009 | P0 | 获取指定收藏详情 | 已登录、已知有效 favorite_id | `GET /favorites/{favorite_id}` | HTTP 200；响应含 `id`、`product_id`、`user_id`，`id` 与 favorite_id 一致 |
| API_FAVORITE_010 | P1 | 未登录获取指定收藏 | 无有效 token | `GET /favorites/{favorite_id}`，不带 Authorization 头 | HTTP 401 |
| API_FAVORITE_011 | P1 | 获取不存在的收藏 | 已登录 | `GET /favorites/nonexistent-99999` | HTTP 404 |

### 1.4 取消收藏 · DELETE /favorites/{favoriteId}

> **Response (204)**: No Content  
> **Auth**: ✅ 需要登录  
> **Param**: `favoriteId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_012 | P0 | 取消收藏成功 | 已登录、已知有效 favorite_id | `DELETE /favorites/{favorite_id}` | HTTP 204；随后 `GET /favorites/{favorite_id}` 返回 404 |
| API_FAVORITE_013 | P1 | 未登录取消收藏 | 无有效 token | `DELETE /favorites/{favorite_id}`，不带 Authorization 头 | HTTP 401 |
| API_FAVORITE_014 | P1 | 取消不存在的收藏 | 已登录 | `DELETE /favorites/nonexistent-99999` | HTTP 404 |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 6 | Happy Path（收藏、查列表、查详情、取消收藏）+ 缺失必填字段（422） |
| P1 | 8 | 未登录操作（401 × 4）、不存在资源（404 × 3）、重复收藏（409） |
| **合计** | **14** | 覆盖 4 个端点的核心链路 + 关键异常路径 |

---

---

## P2 边界用例

### 2.1 添加收藏 · POST /favorites（product_id 边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_015 | P2 | product_id 为空字符串 | 已登录 | `POST /favorites`，传入 `{"product_id":""}` | HTTP 422 |
| API_FAVORITE_016 | P2 | product_id 为纯空格 | 已登录 | `POST /favorites`，传入 `{"product_id":"   "}` | HTTP 422（或 404） |
| API_FAVORITE_017 | P2 | product_id 为超长字符串 | 已登录 | `POST /favorites`，传入 256 字符长的 product_id | HTTP 422 |
| API_FAVORITE_018 | P2 | product_id 含特殊字符 | 已登录 | `POST /favorites`，传入 `{"product_id":"<script>alert(1)</script>"}` | HTTP 422（或 404） |
| API_FAVORITE_019 | P2 | product_id 为 null | 已登录 | `POST /favorites`，传入 `{"product_id":null}` | HTTP 422 |
| API_FAVORITE_020 | P2 | product_id 字段类型错误（数字） | 已登录 | `POST /favorites`，传入 `{"product_id":12345}` | HTTP 422 |
| API_FAVORITE_021 | P2 | 请求体包含额外未知字段 | 已登录 | `POST /favorites`，传入 `{"product_id":"<valid>","extra_field":"ignored"}` | HTTP 200（忽略额外字段）或 422 |

### 2.2 获取指定收藏 · GET /favorites/{favoriteId}（favoriteId 边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_022 | P2 | favoriteId 包含特殊字符 | 已登录 | `GET /favorites/<script>` | HTTP 404 或 422 |
| API_FAVORITE_023 | P2 | favoriteId 为超长字符串 | 已登录 | `GET /favorites/` + 256 字符长 ID | HTTP 404 或 422 |
| API_FAVORITE_029 | P2 | favoriteId 为空字符串 | 已登录 | `GET /favorites/`（路径末尾无 ID） | HTTP 404 或 405 |

### 2.3 获取收藏列表 · GET /favorites（响应结构边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_030 | P2 | 空收藏列表响应结构校验 | 已登录、该账号无任何收藏 | `GET /favorites` | HTTP 200；响应为 `[]`，非 null 非对象 |

### 2.4 取消收藏 · DELETE /favorites/{favoriteId}（favoriteId 边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_024 | P2 | 删除已取消的收藏（重复删除） | 已登录、该 favorite 已删除 | `DELETE /favorites/{deleted_favorite_id}` | HTTP 404 或 409 |
| API_FAVORITE_031 | P2 | DELETE favoriteId 为空字符串 | 已登录 | `DELETE /favorites/`（路径末尾无 ID） | HTTP 404 或 405 |

---

## P2 用例汇总

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 13 | product_id 空值/null/类型错误/超长/特殊字符/额外字段；favoriteId 特殊字符/超长/空字符串；空列表结构校验；重复删除 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 6 |
| P1 | 8 |
| P2 | 13 |
| **合计** | **27** |

---

## P3 深度防御用例

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_FAVORITE_025 | P3 | 横向越权：用户 A 查看用户 B 的收藏详情 | 用户 A 登录、已知用户 B 的 favorite_id | 用户 A 的 token 请求 `GET /favorites/{b_favorite_id}` | HTTP 404（不应返回他人收藏） |
| API_FAVORITE_026 | P3 | 横向越权：用户 A 删除用户 B 的收藏 | 用户 A 登录、已知用户 B 的 favorite_id | 用户 A 的 token 请求 `DELETE /favorites/{b_favorite_id}` | HTTP 404（不应操作他人收藏） |
| API_FAVORITE_027 | P3 | Token 过期后获取收藏列表 | 使用已过期的 token | `GET /favorites`，带过期 Authorization 头 | HTTP 401 |
| API_FAVORITE_028 | P3 | 登出后添加收藏 | 已登出（token 失效） | `POST /favorites`，带已登出的 token | HTTP 401 |
| API_FAVORITE_032 | P3 | 横向越权：用户 A 获取用户 B 的收藏列表 | 用户 A 登录、用户 B 已有收藏 | 用户 A 的 token 请求 `GET /favorites` | HTTP 200；返回数组中不应含用户 B 的收藏（验证所有 `user_id` 均等于用户 A） |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 6 |
| P1 | 8 |
| P2 | 13 |
| P3 | 5 |
| **合计** | **32** |
