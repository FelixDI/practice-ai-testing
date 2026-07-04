# Footer 组件 UI 测试用例

> **被测组件**：Footer（跨页面页脚）  
> **出现页面**：全部页面  
> **组件文件**：`src/ui/components/footer.py`  
> **说明**：所有 Footer 链接均无 data-test，使用文本定位。

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FOOTER_001 | P0 | 页脚渲染含 DEMO 声明 | HomePage | 检查 footer.container | 文本含 "DEMO application" |
| UI_FOOTER_002 | P0 | 聊天按钮可见 | HomePage | 检查 chat-toggle | button visible |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FOOTER_003 | P1 | GitHub 链接指向正确仓库 | HomePage | 检查 github_link | href 含 "github.com/testsmith-io" |
| UI_FOOTER_004 | P1 | Privacy Policy 链接 | HomePage | 点击 privacy_link | 跳转到 `/privacy` |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_FOOTER_005 | P2 | 全部 4 个页脚链接存在 | HomePage | 检查 4 个链接 | 全部 visible |
