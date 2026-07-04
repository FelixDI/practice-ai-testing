# ProductCard 组件 UI 测试用例

> **被测组件**：ProductCard（商品卡片）  
> **出现页面**：HomePage / CategoryPage / SearchPage  
> **组件文件**：`src/ui/components/product_card.py`  
> **说明**：商品卡片含图片、名称、CO₂ 评级、价格、对比按钮，缺货时显示缺货标签。

---

## 卡片 DOM 结构

```
<a data-test="product-{ID}" href="/product/{ID}">
  <img alt="{name}">
  <button data-test="compare-btn">
  <h5 data-test="product-name">{name}</h5>
  <div data-test="co2-rating-badge">A B C D E</div>
  <span data-test="product-price">$价格</span>
  <span data-test="out-of-stock">Out of stock</span>  (条件出现)
</a>
```

---

## P0 核心链路

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CARD_001 | P0 | 卡片渲染含核心元素 | HomePage | 获取第一张 product_card，检查子元素 | product-name 有文本；product-price 可见；co2-rating-badge 可见 |
| UI_CARD_002 | P0 | 点击卡片跳转详情 | HomePage | 通过 product_card(0).click() | URL 变为 `/product/{id}` |

## P1 关键异常

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CARD_003 | P1 | 对比按钮可点击切换状态 | HomePage | 点击第一张卡片的 compare-btn | aria-pressed 值翻转 |

## P2 边界覆盖

| 用例编号 | 优先级 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |
|------|:--:|------|------|------|------|
| UI_CARD_004 | P2 | 缺货卡片显示 out-of-stock 标签 | HomePage（存在缺货卡片时） | 查找含 out-of-stock 的卡片 | out-of-stock 元素 visible |
