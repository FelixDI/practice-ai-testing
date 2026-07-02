# Postcode 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Postcode（邮编查询）无前置业务依赖，公开接口无需登录

---

## 端点覆盖（1 个）

### 1.1 邮编查地址 · GET /postcode-lookup

> **Params**: `country` (query, required), `postcode` (query, required), `house_number` (query, optional)  
> **Response (200)**: object（地址详情）  
> **Response (422)**: 参数校验失败  
> **Response (502)**: 上游查询服务失败  
> **Auth**: ❌ 无需登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_POSTCODE_001 | P0 | 完整参数查询（含门牌号） | 已知有效 country、postcode、house_number | `GET /postcode-lookup?country=DE&postcode=10115&house_number=1` | HTTP 200；返回地址详情对象 |
| API_POSTCODE_002 | P0 | 查询（不含门牌号） | 已知有效 country、postcode | `GET /postcode-lookup?country=DE&postcode=10115` | HTTP 200；返回地址详情对象 |
| API_POSTCODE_003 | P0 | 缺少 country | 无 | `GET /postcode-lookup?postcode=10115` | HTTP 422 |
| API_POSTCODE_004 | P0 | 缺少 postcode | 无 | `GET /postcode-lookup?country=DE` | HTTP 422 |
| API_POSTCODE_005 | P1 | 无效的 country 代码 | 无 | `GET /postcode-lookup?country=XX&postcode=10115` | HTTP 422 |
| API_POSTCODE_006 | P1 | 无效的 postcode 格式 | 无 | `GET /postcode-lookup?country=DE&postcode=!@#$%` | HTTP 422 |
| API_POSTCODE_007 | P1 | 不存在的邮编 | 无 | `GET /postcode-lookup?country=DE&postcode=00000` | HTTP 200（空结果）或 422 |
| API_POSTCODE_008 | P1 | country 为空字符串 | 无 | `GET /postcode-lookup?country=&postcode=10115` | HTTP 422 |
| API_POSTCODE_009 | P1 | postcode 为空字符串 | 无 | `GET /postcode-lookup?country=DE&postcode=` | HTTP 422 |
| API_POSTCODE_023 | P1 | 使用非法 HTTP 方法 | 无 | `POST /postcode-lookup` | HTTP 405（Method Not Allowed） |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 4 | Happy Path（完整查询、仅必填参数）+ 缺失必填字段（422 × 2） |
| P1 | 5 | 无效 country/postcode 格式（422 × 3）、空字符串参数（422 × 2） |
| **合计** | **9** | 覆盖 1 个端点的核心链路 + 关键异常路径 |

---

> **说明**：Postcode 模块仅 1 个公开查询端点，无 Auth 无鉴权。502（上游服务失败）为不可控外部依赖，不设计专门用例触发。  

---

## P2 边界用例

### 2.1 country 参数边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_POSTCODE_010 | P2 | country 为 1 个字符 | 无 | `GET /postcode-lookup?country=D&postcode=10115` | HTTP 422 |
| API_POSTCODE_011 | P2 | country 为 4 个字符 | 无 | `GET /postcode-lookup?country=DEUT&postcode=10115` | HTTP 422 |
| API_POSTCODE_012 | P2 | country 为小写 | 无 | `GET /postcode-lookup?country=de&postcode=10115` | HTTP 200 或 422 |
| API_POSTCODE_013 | P2 | country 为数字 | 无 | `GET /postcode-lookup?country=12&postcode=10115` | HTTP 422 |
| API_POSTCODE_014 | P2 | country 含特殊字符 | 无 | `GET /postcode-lookup?country=D<E&postcode=10115` | HTTP 422 |

### 2.2 postcode 参数边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_POSTCODE_015 | P2 | postcode 超长（50 字符） | 无 | `GET /postcode-lookup?country=DE&postcode=1234567890...`（50位） | HTTP 422 |
| API_POSTCODE_016 | P2 | postcode 含空格 | 无 | `GET /postcode-lookup?country=DE&postcode=101 15` | HTTP 200 或 422 |
| API_POSTCODE_017 | P2 | postcode 含字母数字混合 | 无 | `GET /postcode-lookup?country=GB&postcode=SW1A1AA` | HTTP 200（英国邮编为字母数字混合） |
| API_POSTCODE_018 | P2 | postcode 为纯特殊字符 | 无 | `GET /postcode-lookup?country=DE&postcode=!@#$%` | HTTP 422 |

### 2.3 house_number 参数边界

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_POSTCODE_019 | P2 | house_number 超长（100 字符） | 无 | `GET /postcode-lookup?country=DE&postcode=10115&house_number=` + 100个A | HTTP 422 |
| API_POSTCODE_020 | P2 | house_number 含特殊字符 | 无 | `GET /postcode-lookup?country=DE&postcode=10115&house_number=<script>` | HTTP 422 |
| API_POSTCODE_021 | P2 | house_number 为空字符串 | 无 | `GET /postcode-lookup?country=DE&postcode=10115&house_number=` | HTTP 200（等同于不传） |
| API_POSTCODE_022 | P2 | house_number 为负数 | 无 | `GET /postcode-lookup?country=DE&postcode=10115&house_number=-1` | HTTP 200 或 422 |
| API_POSTCODE_024 | P2 | house_number 为超长纯数字（50 位） | 无 | `GET /postcode-lookup?country=DE&postcode=10115&house_number=` + 50个9 | HTTP 200 或 422 |

---

## P2 用例汇总

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 13 | country 长度/大小写/数字/特殊字符 × 5；postcode 超长/空格/字母数字/特殊字符 × 4；house_number 超长/特殊字符/空/负数 × 4 |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 4 |
| P1 | 6 |
| P2 | 14 |
| **合计** | **24** |
