# TOTP 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：TOTP（两步验证）依赖 User 模块——需先登录获取 token

---

## 端点覆盖（2 个）

### 1.1 设置 TOTP · POST /totp/setup

> **Response (200)**: object（TOTP 设置结果，含 secret / QR URL）  
> **Response (400)**: TOTP 已启用或其他错误  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_TOTP_001 | P0 | 设置 TOTP 成功 | 已登录、该账号未启用 TOTP | `POST /totp/setup` | HTTP 200；响应含 TOTP secret / QR 相关字段 |
| API_TOTP_002 | P1 | 未登录设置 TOTP | 无有效 token | `POST /totp/setup`，不带 Authorization 头 | HTTP 401 |
| API_TOTP_003 | P1 | 重复设置 TOTP（已启用） | 已登录、TOTP 已启用 | 再次 `POST /totp/setup` | HTTP 400 |

### 1.2 验证 TOTP · POST /totp/verify

> **Request**: `{ access_token: string, totp: string<6-digit> }`  
> **Response (200)**: object（验证成功）  
> **Response (400)**: TOTP 码无效或其他错误  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_TOTP_004 | P0 | 验证有效 TOTP 码 | 已登录、已完成 TOTP setup、能从 setup 响应中提取 secret 生成有效 6 位码 | `POST /totp/verify`，传入有效 `access_token` 和正确 `totp` | HTTP 200；验证成功 |
| API_TOTP_005 | P1 | 验证无效 TOTP 码 | 已登录、已完成 TOTP setup | `POST /totp/verify`，传入 `{"access_token":"<token>","totp":"000000"}` | HTTP 400 |
| API_TOTP_006 | P1 | 未登录验证 TOTP | 无有效 token | `POST /totp/verify`，不带 Authorization 头 | HTTP 401 |
| API_TOTP_007 | P1 | 缺少 access_token | 已登录 | `POST /totp/verify`，只传 `{"totp":"123456"}` | HTTP 400 |
| API_TOTP_008 | P1 | 缺少 totp | 已登录 | `POST /totp/verify`，只传 `{"access_token":"<token>"}` | HTTP 400 |
| API_TOTP_009 | P1 | TOTP 码长度不足（非 6 位） | 已登录 | `POST /totp/verify`，传入 `{"access_token":"<token>","totp":"123"}` | HTTP 400 |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 2 | Happy Path（设置 TOTP、验证有效码） |
| P1 | 7 | 未登录操作（401 × 2）、重复设置（400）、无效码（400）、缺参数（400 × 3） |
| **合计** | **9** | 覆盖 2 个端点的核心链路 + 关键异常路径 |

---

> **说明**：API_TOTP_004（验证有效 TOTP 码）依赖从 `/totp/setup` 响应中提取 secret 并计算 6 位 TOTP 码。若 setup 响应不含明文 secret（仅返回 QR 图片），此用例改为 `pytest.skip`。  

---

## P2 边界用例

### 2.1 验证 TOTP · POST /totp/verify（totp 字段边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_TOTP_010 | P2 | totp 为 5 位数字 | 已登录 | `POST /totp/verify`，totp = `"12345"` | HTTP 400 |
| API_TOTP_011 | P2 | totp 为 7 位数字 | 已登录 | `POST /totp/verify`，totp = `"1234567"` | HTTP 400 |
| API_TOTP_012 | P2 | totp 为空字符串 | 已登录 | `POST /totp/verify`，totp = `""` | HTTP 400 |
| API_TOTP_013 | P2 | totp 含字母 | 已登录 | `POST /totp/verify`，totp = `"abc123"` | HTTP 400 |
| API_TOTP_014 | P2 | totp 含特殊字符 | 已登录 | `POST /totp/verify`，totp = `"12 34"` | HTTP 400 |
| API_TOTP_015 | P2 | totp 为 null | 已登录 | `POST /totp/verify`，totp = `null` | HTTP 400 |
| API_TOTP_016 | P2 | totp 为负数 | 已登录 | `POST /totp/verify`，totp = `"-12345"` | HTTP 400 |

### 2.2 验证 TOTP · POST /totp/verify（access_token 字段边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_TOTP_017 | P2 | access_token 为空字符串 | 已登录 | `POST /totp/verify`，access_token = `""`，totp = `"123456"` | HTTP 400 |
| API_TOTP_018 | P2 | access_token 为已过期 token | 使用已过期 token | `POST /totp/verify`，expired access_token + totp | HTTP 400 |
| API_TOTP_019 | P2 | access_token 为随机字符串 | 已登录 | `POST /totp/verify`，access_token = `"invalid-token-xxxx"` | HTTP 400 |

### 2.3 验证 TOTP · POST /totp/verify（请求体边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_TOTP_020 | P2 | 请求体含额外未知字段 | 已登录 | `POST /totp/verify`，合法字段 + `{"extra":"ignored"}` | HTTP 400 或 422（忽略额外字段） |

---

## P2 用例汇总

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 11 | totp 位数边界（5/7位）、空值/null/字母/特殊字符/负数；access_token 空值/过期/随机；extra field |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 2 |
| P1 | 7 |
| P2 | 11 |
| **合计** | **20** |

---

## P3 深度防御用例

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_TOTP_021 | P3 | 横向越权：用户 A 使用用户 B 的 token 验证 TOTP | 用户 A 登录、已完成 TOTP setup；用户 B 的 valid token | `POST /totp/verify`，传入用户 B 的 `access_token` + 用户 A 生成的正确 `totp` | HTTP 400（token 与当前登录用户不匹配） |
| API_TOTP_022 | P3 | Token 过期后验证 TOTP | TOTP 已 setup、token 已过期 | `POST /totp/verify`，传入过期 access_token + 有效 totp | HTTP 401 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 2 |
| P1 | 7 |
| P2 | 11 |
| P3 | 2 |
| **合计** | **22** |

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 10 | totp 位数边界（5/7位）、空值/null/字母/特殊字符/负数；access_token 空值/过期/随机 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 2 |
| P1 | 7 |
| P2 | 10 |
| **合计** | **19** |
