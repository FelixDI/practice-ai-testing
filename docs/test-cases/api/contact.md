# Contact 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Contact 无前置业务依赖；提交留言（POST /messages）无需登录，查看/回复/状态管理需管理员登录

---

## 端点覆盖（6 个）

### 1.1 提交留言 · POST /messages

> **Request**: `ContactRequest { name?, email?, subject*, message* }`（`*` = 必填）  
> **Response (200)**: object（留言创建结果）  
> **Auth**: ❌ 无需登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_001 | P0 | 提交留言（完整字段） | 无 | `POST /messages`，传入 `{"name":"Test User","email":"test@example.com","subject":"Order Issue","message":"I have a problem with my order."}` | HTTP 200；响应含留言创建结果 |
| API_CONTACT_002 | P0 | 提交留言（仅必填字段） | 无 | `POST /messages`，传入 `{"subject":"General Inquiry","message":"Please help."}` | HTTP 200；响应含留言创建结果 |
| API_CONTACT_003 | P0 | 提交留言缺少 subject | 无 | `POST /messages`，传入 `{"message":"No subject here."}` | HTTP 422 |
| API_CONTACT_004 | P0 | 提交留言缺少 message | 无 | `POST /messages`，传入 `{"subject":"No message body."}` | HTTP 422 |

### 1.2 获取留言列表 · GET /messages

> **Response (200)**: 留言列表（支持分页参数 `page`）  
> **Auth**: ✅ 需要登录  
> **Param**: `page` (query, optional)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_005 | P0 | 获取留言列表 | 已登录 | `GET /messages` | HTTP 200；返回留言数组 |
| API_CONTACT_006 | P0 | 获取留言列表（指定页码） | 已登录 | `GET /messages?page=1` | HTTP 200；返回第 1 页留言数据 |
| API_CONTACT_007 | P1 | 未登录获取留言列表 | 无有效 token | `GET /messages`，不带 Authorization 头 | HTTP 401 |

### 1.3 获取指定留言 · GET /messages/{messageId}

> **Response (200)**: 单条留言详情  
> **Auth**: ✅ 需要登录  
> **Param**: `messageId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_008 | P0 | 获取指定留言详情 | 已登录、已知有效 message_id | `GET /messages/{message_id}` | HTTP 200；响应含留言完整信息 |
| API_CONTACT_009 | P1 | 未登录获取留言详情 | 无有效 token | `GET /messages/{message_id}`，不带 Authorization 头 | HTTP 401 |
| API_CONTACT_010 | P1 | 获取不存在的留言 | 已登录 | `GET /messages/nonexistent-99999` | HTTP 404 |

### 1.4 回复留言 · POST /messages/{messageId}/reply

> **Request**: `ContactRequest { name?, email?, subject*, message* }`  
> **Response (200)**: `ContactReplyResponse`  
> **Auth**: ✅ 需要登录  
> **Param**: `messageId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_011 | P0 | 回复留言成功 | 已登录、已知有效 message_id | `POST /messages/{message_id}/reply`，传入 `{"subject":"Re: Issue","message":"We are looking into it."}` | HTTP 200；响应含回复内容 |
| API_CONTACT_012 | P1 | 未登录回复留言 | 无有效 token | `POST /messages/{message_id}/reply`，不带 Authorization 头 | HTTP 401 |
| API_CONTACT_013 | P1 | 回复不存在的留言 | 已登录 | `POST /messages/nonexistent-99999/reply` | HTTP 404 |
| API_CONTACT_014 | P1 | 回复时缺少 message | 已登录、已知有效 message_id | `POST /messages/{message_id}/reply`，只传 `{"subject":"Re: Issue"}` | HTTP 422 |

### 1.5 更新留言状态 · PUT /messages/{messageId}/status

> **Request**: `{ status: enum<NEW, ON_HOLD, IN_PROGRESS, RESOLVED> }`  
> **Response (200)**: 更新结果  
> **Auth**: ✅ 需要登录  
> **Param**: `messageId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_015 | P0 | 更新留言状态为 IN_PROGRESS | 已登录、已知有效 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":"IN_PROGRESS"}` | HTTP 200 |
| API_CONTACT_016 | P0 | 更新留言状态为 RESOLVED | 已登录、已知有效 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":"RESOLVED"}` | HTTP 200 |
| API_CONTACT_017 | P1 | 未登录更新状态 | 无有效 token | `PUT /messages/{message_id}/status`，不带 Authorization 头 | HTTP 401 |
| API_CONTACT_018 | P1 | 更新不存在的留言状态 | 已登录 | `PUT /messages/nonexistent-99999/status` | HTTP 404 |
| API_CONTACT_019 | P1 | 无效的 status 值 | 已登录、已知有效 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":"DELETED"}` | HTTP 422 |

### 1.6 上传附件 · POST /messages/{messageId}/attach-file

> **Response (200)**: object（文件上传结果）  
> **Auth**: ❌ 无需登录（接口文档未标注 security）  
> **Param**: `messageId` (path, required)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_020 | P0 | 上传附件成功 | 已知有效 message_id、准备一个合法文件 | `POST /messages/{message_id}/attach-file`，multipart 上传文件 | HTTP 200；响应含文件上传结果 |
| API_CONTACT_021 | P1 | 向不存在的留言上传附件 | 无 | `POST /messages/nonexistent-99999/attach-file` | HTTP 404 |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 10 | Happy Path（提交留言 × 2、留言列表 × 2、留言详情、回复、状态更新 × 2、附件上传）+ 缺失必填字段 × 2 |
| P1 | 11 | 未登录操作（401 × 4）、不存在资源（404 × 4）、无效枚举值（422）、回复缺必填字段（422） |
| **合计** | **21** | 覆盖 6 个端点的核心链路 + 关键异常路径 |

---

> **下一步**：P0+P1 确认无误后，继续生成 P2 边界用例（name/email/subject/message 的 maxLength 边界、page 分页边界等）。

---

## P2 边界用例

### 2.1 提交留言 · POST /messages（字段 maxLength 边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_022 | P2 | name 恰好 120 字符 | 无 | `POST /messages`，name = 120 个 `A` | HTTP 200 |
| API_CONTACT_023 | P2 | name 超过 120 字符 | 无 | `POST /messages`，name = 121 个 `A` | HTTP 422 |
| API_CONTACT_024 | P2 | email 恰好 256 字符 | 无 | `POST /messages`，email = `"a"*245 + "@b.com"`（总长 256） | HTTP 200 |
| API_CONTACT_025 | P2 | email 超过 256 字符 | 无 | `POST /messages`，email = 257 字符 | HTTP 422 |
| API_CONTACT_026 | P2 | email 格式非法（缺 @） | 无 | `POST /messages`，email = `"not-an-email"` | HTTP 422 |
| API_CONTACT_027 | P2 | email 格式非法（缺域名） | 无 | `POST /messages`，email = `"user@"` | HTTP 422 |
| API_CONTACT_028 | P2 | subject 恰好 120 字符 | 无 | `POST /messages`，subject = 120 个 `X`，message 有效 | HTTP 200 |
| API_CONTACT_029 | P2 | subject 超过 120 字符 | 无 | `POST /messages`，subject = 121 个 `X` | HTTP 422 |
| API_CONTACT_030 | P2 | subject 为空字符串 | 无 | `POST /messages`，subject = `""`，message 有效 | HTTP 422（必填） |
| API_CONTACT_031 | P2 | message 恰好 250 字符 | 无 | `POST /messages`，message = 250 个 `Y`，subject 有效 | HTTP 200 |
| API_CONTACT_032 | P2 | message 超过 250 字符 | 无 | `POST /messages`，message = 251 个 `Y` | HTTP 422 |
| API_CONTACT_033 | P2 | message 为空字符串 | 无 | `POST /messages`，message = `""`，subject 有效 | HTTP 422（必填） |
| API_CONTACT_034 | P2 | name 含特殊字符（XSS） | 无 | `POST /messages`，name = `"<script>alert(1)</script>"` | HTTP 200（服务端应转义，不应执行脚本） |
| API_CONTACT_035 | P2 | message 含 SQL 注入片段 | 无 | `POST /messages`，message = `"'; DROP TABLE messages; --"` | HTTP 200（无数据库报错泄露） |
| API_CONTACT_055 | P2 | 请求体含额外未知字段 | 无 | `POST /messages`，合法字段 + `{"extra_field":"should be ignored"}` | HTTP 200（忽略）或 422 |
| API_CONTACT_056 | P2 | email 含双 @ 符号 | 无 | `POST /messages`，email = `"a@@b.com"` | HTTP 422 |
| API_CONTACT_057 | P2 | email 含 Unicode 字符 | 无 | `POST /messages`，email = `"测试@example.com"` | HTTP 200 或 422 |
| API_CONTACT_058 | P2 | name 为 null（类型不匹配） | 无 | `POST /messages`，name = `null`，其余字段有效 | HTTP 422 |
| API_CONTACT_059 | P2 | subject 为 null（必填字段类型不匹配） | 无 | `POST /messages`，subject = `null`，message 有效 | HTTP 422 |
| API_CONTACT_060 | P2 | message 为 null（必填字段类型不匹配） | 无 | `POST /messages`，message = `null`，subject 有效 | HTTP 422 |

### 2.2 获取留言列表 · GET /messages（分页边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_036 | P2 | page = 0 | 已登录 | `GET /messages?page=0` | HTTP 200（返回第 1 页）或 422 |
| API_CONTACT_037 | P2 | page 为负数 | 已登录 | `GET /messages?page=-1` | HTTP 422 |
| API_CONTACT_038 | P2 | page 为非数字字符串 | 已登录 | `GET /messages?page=abc` | HTTP 422 |
| API_CONTACT_039 | P2 | page 为极大值（超出总页数） | 已登录 | `GET /messages?page=999999` | HTTP 200；返回空数组 `[]` |
| API_CONTACT_061 | P2 | page 为浮点数 | 已登录 | `GET /messages?page=1.5` | HTTP 200（取整）或 422 |

### 2.3 更新留言状态 · PUT /messages/{messageId}/status（枚举全覆盖）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_040 | P2 | 更新状态为 NEW | 已登录、已知有效 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":"NEW"}` | HTTP 200 |
| API_CONTACT_041 | P2 | 更新状态为 ON_HOLD | 已登录、已知有效 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":"ON_HOLD"}` | HTTP 200 |
| API_CONTACT_042 | P2 | status 为空字符串 | 已登录、已知有效 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":""}` | HTTP 422 |
| API_CONTACT_043 | P2 | status 大小写变体 | 已登录、已知有效 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":"resolved"}` | HTTP 422（枚举应严格匹配大写） |

### 2.4 上传附件 · POST /messages/{messageId}/attach-file（文件边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_044 | P2 | 上传空文件 | 已知有效 message_id | `POST /messages/{message_id}/attach-file`，上传 0 字节文件 | HTTP 200 或 422 |
| API_CONTACT_045 | P2 | 不传文件（缺 multipart body） | 已知有效 message_id | `POST /messages/{message_id}/attach-file`，不带文件 | HTTP 422 |

### 2.5 回复留言 · POST /messages/{messageId}/reply（字段边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_046 | P2 | 回复 message 恰好 250 字符 | 已登录、已知有效 message_id | `POST /messages/{message_id}/reply`，message = 250 个 `Y` | HTTP 200 |
| API_CONTACT_047 | P2 | 回复 message 超过 250 字符 | 已登录、已知有效 message_id | `POST /messages/{message_id}/reply`，message = 251 个 `Y` | HTTP 422 |
| API_CONTACT_062 | P2 | 回复 subject 恰好 120 字符 | 已登录、已知有效 message_id | `POST /messages/{message_id}/reply`，subject = 120 个 `X`，message 有效 | HTTP 200 或 201 |
| API_CONTACT_063 | P2 | 回复 subject 超过 120 字符 | 已登录、已知有效 message_id | `POST /messages/{message_id}/reply`，subject = 121 个 `X` | HTTP 422 |

---

## P2 用例汇总

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 35 | name/email/subject/message maxLength 边界 × 14；email 格式 × 4；null 类型 × 3；特殊字符注入 × 2；extra field；page 分页边界 × 5；status 枚举覆盖 × 4；文件上传边界 × 2 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 10 |
| P1 | 11 |
| P2 | 35 |
| **合计** | **56** |

---

## P3 深度防御用例

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_CONTACT_048 | P3 | 非管理员用户尝试获取留言列表 | 使用普通用户 token（非管理员）登录 | `GET /messages`，带普通用户 Authorization 头 | HTTP 401 或 403（留言管理应为管理员权限） |
| API_CONTACT_049 | P3 | 非管理员用户尝试回复留言 | 使用普通用户 token 登录 | `POST /messages/{message_id}/reply`，带普通用户 token | HTTP 401 或 403 |
| API_CONTACT_050 | P3 | 非管理员用户尝试更新留言状态 | 使用普通用户 token 登录 | `PUT /messages/{message_id}/status`，带普通用户 token | HTTP 401 或 403 |
| API_CONTACT_051 | P3 | Token 过期后获取留言列表 | 使用已过期的 token | `GET /messages`，带过期 Authorization 头 | HTTP 401 |
| API_CONTACT_052 | P3 | Token 过期后回复留言 | 使用已过期的 token | `POST /messages/{message_id}/reply`，带过期 token | HTTP 401 |
| API_CONTACT_053 | P3 | 上传可执行文件（.exe） | 已知有效 message_id | `POST /messages/{message_id}/attach-file`，上传 `.exe` 文件 | HTTP 422（应拒绝危险文件类型） |
| API_CONTACT_054 | P3 | 上传超大文件 | 已知有效 message_id | `POST /messages/{message_id}/attach-file`，上传 50MB 文件 | HTTP 422（应限制文件大小） |
| API_CONTACT_064 | P3 | 非管理员用户查看单条留言 | 使用普通用户 token 登录、已知 message_id | `GET /messages/{message_id}`，带普通用户 token | HTTP 401 或 403 |
| API_CONTACT_065 | P3 | Token 过期后更新留言状态 | 使用已过期的 token | `PUT /messages/{message_id}/status`，带过期 Authorization 头 | HTTP 401 |
| API_CONTACT_066 | P3 | 留言状态逆向流转（RESOLVED → NEW） | 已登录、已知已 RESOLVED 的 message_id | `PUT /messages/{message_id}/status`，传入 `{"status":"NEW"}` | HTTP 422（不允许逆向流转）或 200 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 10 |
| P1 | 11 |
| P2 | 35 |
| P3 | 10 |
| **合计** | **66** |
