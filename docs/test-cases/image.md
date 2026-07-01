# Image 模块 API 测试用例

> **被测接口**：Toolshop API v5.0.0（`docs/practice_software_testing_api.json`）  
> **编写规范**：遵循项目 CLAUDE.md 及全局 `~/.claude/skills/python-test-standard/SKILL.md`  
> **依赖说明**：Image（图片资源）依赖 Product 模块——图片数据来源于已创建的商品

---

## 端点覆盖（1 个）

### 1.1 获取图片列表 · GET /images

> **Response (200)**: `ImageResponse[]` —— 每项含 `id`、`by_name`、`by_url`、`source_name`、`source_url`、`file_name`、`title`  
> **Auth**: ❌ 无需登录

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| API_IMAGE_001 | P0 | 获取图片列表 | 无 | `GET /images` | HTTP 200；返回数组，每项含 `id`、`file_name`、`title`、`by_name` 等字段 |
| API_IMAGE_002 | P1 | 使用非法 HTTP 方法 | 无 | `POST /images` | HTTP 405（Method Not Allowed） |

---

## 用例汇总

| 优先级 | 数量 | 覆盖场景 |
|:--:|:--:|------|
| P0 | 1 | Happy Path（获取图片列表） |
| P1 | 1 | 非法 HTTP 方法（405） |
| **合计** | **2** | Image 模块仅 1 个公开只读端点，无 Auth / 无参数 / 无 401/404/409/422 触发路径 |

---

> **说明**：Image 模块极简——仅 `GET /images` 一个公开端点，无鉴权、无参数、无写操作。P2/P3 无可补充的边界或权限场景。确认无误后直接跳过 P2/P3。
