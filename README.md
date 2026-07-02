# practice-ai-testing

Toolshop 电商系统
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
│   │   ├── api/
│   │   │   ├── brand.md
│   │   │   ├── cart.md
│   │   │   ├── category.md
│   │   │   ├── contact.md
│   │   │   ├── favorite.md
│   │   │   ├── image.md
│   │   │   ├── invoice.md
│   │   │   ├── payment.md
│   │   │   ├── postcode.md
│   │   │   ├── product-spec.md
│   │   │   ├── product.md
│   │   │   ├── report.md
│   │   │   ├── totp.md
│   │   │   └── user.md
│   │   ├── integration/
│   │   └── ui/
│   │       └── home_page.md
│   ├── AI 辅助自动化测试开发 全阶段踩坑.md
│   └── practice_software_testing_api.json
├── src/
│   ├── api/
│   │   ├── client/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── brand_client.py
│   │   │   ├── cart_client.py
│   │   │   ├── category_client.py
│   │   │   ├── contact_client.py
│   │   │   ├── favorite_client.py
│   │   │   ├── image_client.py
│   │   │   ├── invoice_client.py
│   │   │   ├── payment_client.py
│   │   │   ├── postcode_client.py
│   │   │   ├── product_client.py
│   │   │   ├── product_spec_client.py
│   │   │   ├── report_client.py
│   │   │   ├── totp_client.py
│   │   │   └── user_client.py
│   │   └── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── pytest_mcp_server.py
│   ├── ui/
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   └── home_page.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_brand_api.py
│   │   ├── test_cart_api.py
│   │   ├── test_category_api.py
│   │   ├── test_contact_api.py
│   │   ├── test_favorite_api.py
│   │   ├── test_image_api.py
│   │   ├── test_invoice_api.py
│   │   ├── test_payment_api.py
│   │   ├── test_postcode_api.py
│   │   ├── test_product_api.py
│   │   ├── test_product_spec_api.py
│   │   ├── test_report_api.py
│   │   ├── test_totp_api.py
│   │   └── test_user_api.py
│   ├── integration/
│   │   └── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_home_page.py
│   ├── __init__.py
│   └── conftest.py
├── CLAUDE.md
├── README.md
├── main.py
├── pyproject.toml
├── update_tree.py
└── uv.lock

16 directories, 68 files
```
<!-- PROJECT_STRUCTURE_END -->



#### API test:
[Allure测试报告](https://felixdi.github.io/practice-ai-testing/api-allure-report/)



#### UI test:
[Allure测试报告](https://felixdi.github.io/practice-ai-testing/ui-allure-report/)