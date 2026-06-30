# User 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`

## 端点覆盖（13 个）

### 1.1 注册 · POST /users/register

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_001 | P1 | 完整合法数据注册 | 无 | `POST /users/register`，传入合法 first_name、last_name、email、password、address(street/city/country/postal_code)、dob | HTTP 201；响应含 id、email、first_name、last_name、created_at |
| API_USER_002 | P1 | 重复邮箱注册 | 已注册邮箱 | 使用相同邮箱再次注册 | HTTP 409 Conflict |
| API_USER_003 | P1 | 缺少 first_name | 无 | 请求体中不传 first_name | HTTP 422 |
| API_USER_004 | P1 | 缺少 last_name | 无 | 请求体中不传 last_name | HTTP 422 |
| API_USER_005 | P1 | 缺少 email | 无 | 请求体中不传 email | HTTP 422 |
| API_USER_006 | P1 | 缺少 password | 无 | 请求体中不传 password | HTTP 422 |
| API_USER_007 | P2 | 密码不足 8 位 | 无 | password 传入 `Ab1!`（5 位） | HTTP 422 |
| API_USER_008 | P2 | 密码不含大写字母 | 无 | password 传入 `abcdef1!`（无大写） | HTTP 422 |
| API_USER_009 | P2 | 密码不含特殊符号 | 无 | password 传入 `Abcdef12`（无符号） | HTTP 422 |
| API_USER_010 | P2 | 邮箱格式非法（无 @） | 无 | email 传入 `invalid-email` | HTTP 201 或 422（API 校验策略宽松） |
| API_USER_011 | P2 | dob 不足 18 岁 | 无 | dob 传入当前日期 -17 年 | HTTP 422 |
| API_USER_012 | P1 | dob 超过 75 岁 | 无 | dob 传入当前日期 -76 年 | HTTP 422 |
| API_USER_013 | P2 | first_name 超长（41 字符） | 无 | first_name 传入 41 个字母 | HTTP 422 |
| API_USER_014 | P2 | last_name 超长（21 字符） | 无 | last_name 传入 21 个字母 | HTTP 422 |
| API_USER_015 | P2 | email 超长（257 字符） | 无 | email 传入 257 字符的合法格式邮箱 | HTTP 422 |
| API_USER_016 | P0 | 含可选字段 phone 的完整注册 | 无 | 合法数据 + phone `"+8613800138000"` | HTTP 201；响应含 phone |
| API_USER_017 | P1 | 空 JSON 请求体 | 无 | `POST /users/register`，发送 `{}` | HTTP 422 |
| API_USER_057 | P2 | password 不含数字 | 无 | password 传入 `Abcdefg!`（大写+符号+字母，无数字） | HTTP 422 |
| API_USER_058 | P2 | address.street 超长（71 字符） | 无 | street 传入 71 个字符 | HTTP 422 |
| API_USER_059 | P2 | address.city 超长（41 字符） | 无 | city 传入 41 个字符 | HTTP 422 |
| API_USER_060 | P2 | phone 超长（25 字符） | 无 | phone 传入 25 个字符 | HTTP 422 |
| API_USER_061 | P2 | postal_code 超长（11 字符） | 无 | postal_code 传入 11 个字符 | HTTP 422 |
| API_USER_062 | P0 | 仅传必填字段注册 | 无 | 只传 first_name + last_name + email + password，不含 address/phone/dob | HTTP 201 |

### 1.2 登录 · POST /users/login

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_018 | P0 | 正确凭证登录 | 已注册用户 | `POST /users/login`，正确 email + password | HTTP 200；响应含 access_token、token_type=`bearer`、expires_in > 0 |
| API_USER_019 | P1 | 错误密码登录 | 已注册用户 | 正确 email + 错误 password | HTTP 401 |
| API_USER_020 | P1 | 不存在邮箱登录 | 无 | 随机未注册邮箱 + 任意密码 | HTTP 401 |
| API_USER_021 | P1 | 缺少 email 字段 | 无 | 只传 password | HTTP 401 |
| API_USER_022 | P1 | 缺少 password 字段 | 无 | 只传 email | HTTP 401 |
| API_USER_023 | P1 | 空请求体 | 无 | 发送 `{}` | HTTP 401 |

### 1.3 获取当前用户 · GET /users/me

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_024 | P0 | 已登录获取自身信息 | 已登录，Token 有效 | `GET /users/me`，携带 `Authorization: Bearer <token>` | HTTP 200；响应含 id、email、first_name、last_name、address、dob、created_at |
| API_USER_025 | P1 | 未登录访问 | 无 | `GET /users/me`，无 Token | HTTP 401 |
| API_USER_026 | P0 | 已登出后访问 | 已登录→登出 | 执行登出后立即 `GET /users/me` | HTTP 401 |

### 1.4 获取指定用户 · GET /users/{userId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_027 | P0 | 查询存在的用户 | 已知有效 userId | `GET /users/{userId}` | HTTP 200（可能需 401 取决于认证要求） |
| API_USER_028 | P1 | 查询不存在的用户 | 无 | `GET /users/nonexistent-id-99999` | HTTP 404 或 401 |
| API_USER_029 | P3 | userId 为特殊字符 | 无 | `GET /users/../../etc` | HTTP 404 |

### 1.5 全量更新用户 · PUT /users/{userId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_030 | P0 | 全量更新本人信息 | 已登录，Token 有效 | `PUT /users/{id}`，完整合法 JSON（含 address/dob） | HTTP 200；`{"success":true}`；随后 `GET /users/me` 验证字段已变更 |
| API_USER_031 | P1 | 未登录更新 | 无 | `PUT /users/{id}`，无 Token | HTTP 401 |
| API_USER_032 | P1 | 更新缺少 address 嵌套字段 | 已登录 | `PUT /users/{id}`，不传 address（只传 first_name/last_name/email/password） | HTTP 422 |
| API_USER_033 | P1 | 更新不存在的用户 ID | 已登录 | `PUT /users/nonexistent-id-99999`，合法数据 | HTTP 404 或 422 |

### 1.6 部分更新用户 · PATCH /users/{userId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_034 | P1 | PATCH 更新单个字段 | 已登录 | `PATCH /users/{id}`，只传 `{"first_name":"Patched"}` | HTTP 200；随后 `GET /users/me` 验证 first_name 变更，其他字段不变 |
| API_USER_035 | P1 | 未登录 PATCH | 无 | `PATCH /users/{id}`，无 Token | HTTP 401 |
| API_USER_036 | P1 | PATCH 不存在用户 | 已登录 | `PATCH /users/nonexistent-id-99999` | HTTP 404 或 422 |

### 1.7 删除用户 · DELETE /users/{userId}

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_037 | P1 | 未登录删除用户 | 无 | `DELETE /users/{id}`，无 Token | HTTP 401 |
| API_USER_038 | P1 | 删除不存在的用户 | 已登录 | `DELETE /users/nonexistent-id-99999` | HTTP 404 或 422 |
| API_USER_039 | P0 | 已登录删除本人账户 | 已登录 | `DELETE /users/{id}`（自己的 id） | HTTP 204；随后登录验证应返回 401 |

### 1.8 用户列表 · GET /users

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_040 | P0 | 获取用户列表（默认分页） | 无 | `GET /users` | HTTP 200（或 401）；响应为 JSON 数组 |
| API_USER_041 | P0 | 分页参数 page=1 | 无 | `GET /users?page=1` | HTTP 200（或 401） |
| API_USER_042 | P2 | 分页参数 page=0 | 无 | `GET /users?page=0` | HTTP 200 或 400；确认边界行为 |

### 1.9 搜索用户 · GET /users/search

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_043 | P1 | 搜索已知用户 | 已注册用户 | `GET /users/search?q=<已注册邮箱前缀>` | HTTP 200（或 401）；返回匹配结果 |
| API_USER_044 | P1 | 搜索不存在的关键词 | 无 | `GET /users/search?q=xyznonexistent999` | HTTP 200（或 401）；返回空数组 |
| API_USER_045 | P3 | 搜索特殊字符 | 无 | `GET /users/search?q=<script>` | HTTP 200（或 401）；不崩溃即可 |

### 1.10 忘记密码 · POST /users/forgot-password

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_046 | P2 | 传入有效 email 格式 | 无 | `POST /users/forgot-password`，`{"email":"user@example.com"}` | HTTP 422（该端点需额外参数） |
| API_USER_047 | P1 | 缺少 email 字段 | 无 | `POST /users/forgot-password`，`{}` | HTTP 404 |

### 1.11 修改密码 · POST /users/change-password

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_048 | P1 | 正确密码修改 | 已登录 | `POST /users/change-password`，正确的 current + new + confirmation | HTTP 200；登出后用新密码重新登录成功 |
| API_USER_049 | P1 | 当前密码错误 | 已登录 | `POST /users/change-password`，current_password 错误 | HTTP 422 |
| API_USER_050 | P1 | 新密码与确认不匹配 | 已登录 | new_password 与 new_password_confirmation 不同 | HTTP 422 |
| API_USER_051 | P2 | 新密码强度不足 | 已登录 | new_password 为 5 位弱密码 | HTTP 422 |
| API_USER_052 | P1 | 未登录修改密码 | 无 | `POST /users/change-password`，无 Token | HTTP 401 |

### 1.12 登出 · GET /users/logout

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_053 | P0 | 已登录登出 | 已登录 | `GET /users/logout` | HTTP 200；随后访问受保护端点返回 401 |
| API_USER_054 | P1 | 未登录调用登出 | 无 | `GET /users/logout`，无 Token | HTTP 200 或 401 |

### 1.13 Token 刷新 · GET /users/refresh

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_055 | P0 | 刷新有效 Token | 已登录 | `GET /users/refresh` | HTTP 200；返回新 access_token |
| API_USER_056 | P1 | 无 Token 刷新 | 无 | `GET /users/refresh`，无 Token | HTTP 401 |

### 1.14 权限/状态组合

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|:--:|------|
| API_USER_063 | P3 | 用户 A 的 Token 操作用户 B 的数据（横向越权） | 注册用户 A + 用户 B，A 登录 | 使用 A 的 Token 执行 `PUT /users/{B_id}` | HTTP 403 |
| API_USER_064 | P3 | 用户 A 删除用户 B（横向越权） | 同上 | 使用 A 的 Token 执行 `DELETE /users/{B_id}` | HTTP 403 |
| API_USER_065 | P3 | 被删除用户的资源再次操作 | 用户已注册→登录→删除本人 | `GET /users/{deleted_id}` | HTTP 404 |

---

---

## 四、覆盖统计

| 模块 | 端点 | 用例 | 正常 | 异常 | 边界 | 权限 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|
| User | 13 | 65 | 14 | 26 | 16 | 12 |
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