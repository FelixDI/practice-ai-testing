---
description: 按四维覆盖模型为指定模块生成测试用例文档
---

你是一位资深测试工程师。请严格按以下要求，为 Practice Software Testing 电商平台的 **$ARGUMENTS** 模块生成 API 测试用例。

## 1. 遵守规范

- 首先，读取项目根目录下的 CLAUDE.md，了解测试用例设计规范、四维覆盖模型和优先级分层策略。
- 其次，读取全局技能文件 ~/.claude/skills/python-automation-test-standard/SKILL.md，遵守测试用例编写规范。
- 所有接口信息来源于项目根目录下的 API 文档：docs/practice_software_testing_api.json。

## 2. 接口/页面信息获取

- **API 测试**：读取 `docs/practice_software_testing_api.json`，定位 $ARGUMENTS 模块的 paths 和 components/schemas。按 CLAUDE.md「OpenAPI 文档使用原则」只读当前模块，避免全量解析。
- **UI 测试**：参考 CLAUDE.md 页面清单确认路由和需登录状态，通过 Playwright 实测导航获取页面结构和交互元素。

## 3. 生成范围

- 本次处理 **$ARGUMENTS** 模块的全部端点。
- 如涉及依赖模块，在文档中标注前置条件。

## 4. 覆盖维度（严格按照 CLAUDE.md 中的四维覆盖模型）

- **核心链路**：正常业务流程，期望返回 200/201/204。
- **异常路径**：未登录操作（401）、操作不存在的资源（404）、重复操作（409）、缺失必填字段（422）等。
- **边界条件**：按 Schema 逐字段的 maxLength/minLength/format/range/enum 边界值，分页边界（page=0），非法参数等。
- **权限/状态组合**：未登录访问，以及根据模块特点补充越权或状态相关用例。

## 5. 输出格式

- 为每个模块分别创建一个独立的 Markdown 文件。
- 文件命名：`<模块名>.md`（全小写下划线，如 `cart.md`），保存到 `docs/test-cases/` 目录下。
- 每条用例包含一个 Markdown 表格，字段为：
  - 用例编号（如 API_$ARGUMENTS_001）
  - 优先级（P0/P1/P2/P3）
  - 用例标题
  - 前置条件
  - 测试步骤（含具体 API 路径和方法）
  - 预期结果（含 HTTP 状态码和关键响应字段校验）

## 6. 分层交付

- 首先生成 P0+P1 优先级的用例，确认后再生成 P2 边界用例。
- P3 按需生成。
