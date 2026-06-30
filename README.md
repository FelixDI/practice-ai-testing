# practice-ai-testing

基于 Claude Code + DeepSeek V4 Pro 的 AI 协作自动化测试项目

被测对象：Practice Software Testing
- UI 地址：https://practicesoftwaretesting.com
- API 地址：https://api.practicesoftwaretesting.com

技术栈：Python 3.12 · Pytest · Playwright · Requests · Allure · GitHub Actions

## 目录结构

<!-- PROJECT_STRUCTURE_START -->
```
practice-ai-testing/
├── docs/
│   ├── test-cases/
│   └── practice_software_testing_api.json
├── src/
│   ├── api/
│   │   ├── client/
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── common/
│   │   └── __init__.py
│   ├── ui/
│   │   ├── pages/
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── api/
│   │   └── __init__.py
│   ├── integration/
│   │   └── __init__.py
│   ├── ui/
│   │   └── __init__.py
│   ├── __init__.py
│   └── conftest.py
├── CLAUDE.md
├── README.md
├── main.py
├── pyproject.toml
├── update_tree.py
└── uv.lock

13 directories, 18 files
```
<!-- PROJECT_STRUCTURE_END -->