# Report 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Report（销售报表）依赖 Invoice 模块——报表数据来源于已生成的订单；测试时需系统存在历史订单数据

---

## 端点覆盖（7 个）

### 1.1 各国销售总额 · GET /reports/total-sales-per-country

> **Response (200)**: 数组  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_001 | P0 | 获取各国销售总额 | 已登录 | `GET /reports/total-sales-per-country` | HTTP 200；返回数组，每项含国家及销售总额字段 |
| API_REPORT_002 | P1 | 未登录获取各国销售总额 | 无有效 token | `GET /reports/total-sales-per-country`，不带 Authorization 头 | HTTP 401 |

### 1.2 热销商品 Top10 · GET /reports/top10-purchased-products

> **Response (200)**: 数组  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_003 | P0 | 获取热销商品 Top10 | 已登录 | `GET /reports/top10-purchased-products` | HTTP 200；返回数组（最多 10 项），每项含商品名及销量 |
| API_REPORT_004 | P1 | 未登录获取热销商品 | 无有效 token | `GET /reports/top10-purchased-products`，不带 Authorization 头 | HTTP 401 |

### 1.3 热销分类 Top10 · GET /reports/top10-best-selling-categories

> **Response (200)**: 数组  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_005 | P0 | 获取热销分类 Top10 | 已登录 | `GET /reports/top10-best-selling-categories` | HTTP 200；返回数组（最多 10 项），每项含分类名及销量 |
| API_REPORT_006 | P1 | 未登录获取热销分类 | 无有效 token | `GET /reports/top10-best-selling-categories`，不带 Authorization 头 | HTTP 401 |

### 1.4 各年度销售总额 · GET /reports/total-sales-of-years

> **Response (200)**: 数组  
> **Auth**: ✅ 需要登录  
> **Param**: `years` (query, optional)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_007 | P0 | 获取各年度销售总额 | 已登录 | `GET /reports/total-sales-of-years` | HTTP 200；返回数组，每项含年份及销售额 |
| API_REPORT_008 | P0 | 指定年份获取销售总额 | 已登录 | `GET /reports/total-sales-of-years?years=2025,2026` | HTTP 200；返回指定年份数据 |
| API_REPORT_009 | P1 | 未登录获取年度销售额 | 无有效 token | `GET /reports/total-sales-of-years`，不带 Authorization 头 | HTTP 401 |

### 1.5 月均销售额 · GET /reports/average-sales-per-month

> **Response (200)**: 数组  
> **Auth**: ✅ 需要登录  
> **Param**: `year` (query, optional)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_010 | P0 | 获取月均销售额（默认年份） | 已登录 | `GET /reports/average-sales-per-month` | HTTP 200；返回数组，每项含月份及月均销售额 |
| API_REPORT_011 | P0 | 指定年份获取月均销售额 | 已登录 | `GET /reports/average-sales-per-month?year=2025` | HTTP 200；返回该年 12 个月数据 |
| API_REPORT_012 | P1 | 未登录获取月均销售额 | 无有效 token | `GET /reports/average-sales-per-month`，不带 Authorization 头 | HTTP 401 |

### 1.6 周均销售额 · GET /reports/average-sales-per-week

> **Response (200)**: 数组  
> **Auth**: ✅ 需要登录  
> **Param**: `year` (query, optional)

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_013 | P0 | 获取周均销售额（默认年份） | 已登录 | `GET /reports/average-sales-per-week` | HTTP 200；返回数组，每项含周次及周均销售额 |
| API_REPORT_014 | P0 | 指定年份获取周均销售额 | 已登录 | `GET /reports/average-sales-per-week?year=2025` | HTTP 200；返回该年周数据 |
| API_REPORT_015 | P1 | 未登录获取周均销售额 | 无有效 token | `GET /reports/average-sales-per-week`，不带 Authorization 头 | HTTP 401 |

### 1.7 各国客户分布 · GET /reports/customers-by-country

> **Response (200)**: 数组  
> **Auth**: ✅ 需要登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_016 | P0 | 获取各国客户分布 | 已登录 | `GET /reports/customers-by-country` | HTTP 200；返回数组，每项含国家及客户数 |
| API_REPORT_017 | P1 | 未登录获取客户分布 | 无有效 token | `GET /reports/customers-by-country`，不带 Authorization 头 | HTTP 401 |
| API_REPORT_029 | P1 | 使用非法 HTTP 方法 | 已登录 | `POST /reports/total-sales-per-country` | HTTP 405（Method Not Allowed） |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 9 | Happy Path（7 个报表端点 × 1 + year/years 参数 × 2） |
| P1 | 8 | 未登录操作（401 × 7）+ 无效 years 格式（P2 待补充） |
| **合计** | **17** | 覆盖 7 个端点的核心链路 + 关键异常路径 |

---

> **说明**：报表端点全部只读、无 404 触发路径（无 path 参数），404 响应在 API 文档中列出但无法构造触发条件。  

---

## P2 边界用例

### 2.1 年度销售总额 · GET /reports/total-sales-of-years（years 参数边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_018 | P2 | years 为单个年份 | 已登录 | `GET /reports/total-sales-of-years?years=2025` | HTTP 200；返回该年数据 |
| API_REPORT_019 | P2 | years 含未来年份 | 已登录 | `GET /reports/total-sales-of-years?years=2050` | HTTP 200；返回空数组或 0 值 |
| API_REPORT_020 | P2 | years 为非数字 | 已登录 | `GET /reports/total-sales-of-years?years=abc` | HTTP 200（忽略）或 422 |
| API_REPORT_021 | P2 | years 为空字符串 | 已登录 | `GET /reports/total-sales-of-years?years=` | HTTP 200（返回全部年份）或 422 |

### 2.2 月均销售额 · GET /reports/average-sales-per-month（year 参数边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_022 | P2 | year 为未来年份 | 已登录 | `GET /reports/average-sales-per-month?year=2050` | HTTP 200；返回 12 个月全 0 值 |
| API_REPORT_023 | P2 | year 为非数字 | 已登录 | `GET /reports/average-sales-per-month?year=abc` | HTTP 200（忽略）或 422 |
| API_REPORT_024 | P2 | year 为负数 | 已登录 | `GET /reports/average-sales-per-month?year=-1` | HTTP 200 或 422 |
| API_REPORT_025 | P2 | year 为空字符串 | 已登录 | `GET /reports/average-sales-per-month?year=` | HTTP 200（默认年份）或 422 |

### 2.3 周均销售额 · GET /reports/average-sales-per-week（year 参数边界）

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_026 | P2 | year 为未来年份 | 已登录 | `GET /reports/average-sales-per-week?year=2050` | HTTP 200；返回周数据全 0 |
| API_REPORT_027 | P2 | year 为非数字 | 已登录 | `GET /reports/average-sales-per-week?year=abc` | HTTP 200 或 422 |
| API_REPORT_028 | P2 | year 为极小值（公元 1 年） | 已登录 | `GET /reports/average-sales-per-week?year=1` | HTTP 200；空数据 |

---

## P2 用例汇总

| 优先级 | 新增 | 覆盖场景 |
|:--:|:--:|------|
| P2 | 11 | years 边界 × 4（单年/未来/非数字/空）；year 边界 × 7（未来/非数字/负数/空/极小值 × 2 端点） |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 9 |
| P1 | 9 |
| P2 | 11 |
| **合计** | **29** |

---

## P3 深度防御用例

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_REPORT_030 | P3 | 非管理员用户访问报表 | 使用普通用户 token（非管理员）登录 | `GET /reports/total-sales-per-country`，带普通用户 token | HTTP 403（Forbidden） |

### 全部用例总览

| 优先级 | 数量 |
|:--:|:--:|
| P0 | 9 |
| P1 | 9 |
| P2 | 11 |
| P3 | 1 |
| **合计** | **30** |
