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
│   │   ├── brand.md
│   │   ├── cart.md
│   │   ├── category.md
│   │   ├── invoice.md
│   │   ├── product.md
│   │   └── user.md
│   └── practice_software_testing_api.json
├── src/
│   ├── api/
│   │   ├── client/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── brand_client.py
│   │   │   ├── cart_client.py
│   │   │   ├── category_client.py
│   │   │   ├── invoice_client.py
│   │   │   ├── product_client.py
│   │   │   └── user_client.py
│   │   └── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── ui/
│   │   ├── pages/
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_brand_api.py
│   │   ├── test_cart_api.py
│   │   ├── test_category_api.py
│   │   ├── test_invoice_api.py
│   │   ├── test_product_api.py
│   │   └── test_user_api.py
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

13 directories, 38 files
```
<!-- PROJECT_STRUCTURE_END -->