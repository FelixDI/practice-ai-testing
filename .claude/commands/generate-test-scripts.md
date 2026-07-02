---
description: 为指定模块生成 API/UI 自动化测试脚本
---

你是一位资深自动化测试工程师。请严格按以下要求，为 **$ARGUMENTS** 模块生成自动化测试脚本。

## 1. 遵守规范

- 严格遵守项目根目录下的 CLAUDE.md 中的所有约束与规范。
- 严格遵守 ~/.claude/skills/python-automation-test-standard/SKILL.md 中的代码风格和设计模式。
- 参考 tests/api/ 和 src/api/client/ 下已有代码风格，保持一致性。

## 2. 生成流程（严格按顺序）

1. 读取 docs/test-cases/$ARGUMENTS.md，理解该模块的全部用例。
2. **API 测试**：如果 src/api/client/$ARGUMENTS_client.py 不存在，先创建 API Client 类。**UI 测试**：如果 src/ui/pages/$ARGUMENTS_page.py 或 src/ui/components/ 下组件不存在，先创建对应 POM 类。
3. 按 P0 → P1 → P2 的分层顺序生成测试函数，并为 P3 预留位置。
4. 每条测试函数标注对应的用例编号（API: `# [API_BRAND_001]`，UI: `# [UI_LOGIN_001]`）。

## 3. 夹具管理（必须逐条落实）

- **作用域分层决策**：写操作修改共享状态用 `function`，只读操作用 `module`。
- **高频创建控制**：禁止每个用例重复注册用户或创建购物车，封装为 module 级夹具。
- **数据隔离优先**：新增夹具前评估是否污染已有测试的共享状态。
- **固定账号优先复用**：优先使用 config.py 中的 TEST_USER_EMAIL / TEST_USER_PASSWORD。

## 4. 验证（强制执行）

- **单文件**：Hook 已在每次 Write/Edit 后自动跑过被修改文件，确保逐文件即时反馈。
- **模块级回归**：所有文件生成完成后，用 MCP 工具 `run_pytest($ARGUMENTS)` 做模块级回归确认，分析失败原因并修复，直到全部用例通过。
