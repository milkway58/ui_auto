---
name: customer-public-zone-order-flow
overview: 将客户下单测试流程从 "new营销专区12" 切换为 "客户公共专区"，涉及 home_page.py 定位器默认值和 test_customer_order.py 测试用例的专区名称更新。
todos:
  - id: update-home-page
    content: 修改 pages/home_page.py：将 MARKETING_ZONE 常量、select_marketing_zone 默认参数及 docstring 中的 "new营销专区12" 替换为 "客户公共专区"
    status: pending
  - id: update-test-cases
    content: 修改 tests/test_customer_order.py：将所有硬编码的 "new营销专区12" 替换为 "客户公共专区"
    status: pending
---

## 用户需求

将客户下单业务流程从现有的 "new营销专区12" 切换为 "客户公共专区"。

## 核心功能

- 修改 `HomePage` 页面对象中的营销专区定位器和默认参数
- 修改 `test_customer_order.py` 测试用例中所有硬编码的专区名称
- 更新相关 docstring 描述，保持文档与代码一致

## 技术方案

纯文本替换，不涉及架构变更。改动范围限定在两个文件：页面对象层 `pages/home_page.py` 和测试用例层 `tests/test_customer_order.py`。

## 修改清单

### `pages/home_page.py`

| 行号 | 变更内容 |
| --- | --- |
| L6 | docstring: `new营销专区12` → `客户公共专区` |
| L41 | `MARKETING_ZONE = "text=new营销专区12"` → `"text=客户公共专区"` |
| L76 | `zone_name: str = "new营销专区12"` → `"客户公共专区"` |
| L81 | docstring: `默认 "new营销专区12"` → `默认 "客户公共专区"` |


### `tests/test_customer_order.py`

| 行号 | 变更内容 |
| --- | --- |
| L3 | docstring: `选择 new营销专区12` → `选择 客户公共专区` |
| L76 | `select_marketing_zone("new营销专区12")` → `"客户公共专区"` |
| L98 | 同上 |
| L131 | 同上 |
| L181 | 同上 |


## 注意事项

- `select_marketing_zone` 方法内部使用 `f"text={zone_name}"` 构造选择器，传入纯专区名称即可，无需带 `text=` 前缀
- 现有 5 个测试用例中有 4 个用例显式传参调用 `select_marketing_zone("new营销专区12")`，1 个用例使用默认参数；修改后客户端调用均适配新的专区名称