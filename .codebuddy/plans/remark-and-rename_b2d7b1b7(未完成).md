---
name: remark-and-rename
overview: 重命名全部产品测试文件 + 为两个测试文件添加动态日期备注
todos:
  - id: rename-file
    content: 重命名 tests/test_customer_order_recorded.py 为 tests/test_customer_allProducts.py
    status: pending
  - id: add-remark-all-products
    content: 修改 test_customer_allProducts.py：导入 datetime，订单确认链中插入 fill_remark("全部产品专区UI自动化+日期")
    status: pending
    dependencies:
      - rename-file
  - id: update-remark-enterprise
    content: 修改 test_customer_enterprise.py：导入 datetime，更新备注为 "企业专区UI自动化+日期"
    status: pending
  - id: run-verify
    content: 依次运行两个测试用例验证修改正确性
    status: pending
    dependencies:
      - add-remark-all-products
      - update-remark-enterprise
---

## 用户需求

在两个客户下单测试用例的订单确认页添加动态日期备注，并重命名全部产品测试文件。

## 核心功能

1. 重命名 `tests/test_customer_order_recorded.py` → `tests/test_customer_allProducts.py`
2. 全部产品测试：订单确认链中新增 `fill_remark("全部产品专区UI自动化+YYYY-MM-DD")`，插入在 `.select_invoice("明细")` 与 `.submit_order()` 之间
3. 企业专区测试：备注内容从 `"企业专区ui自动化"` 更新为 `"企业专区UI自动化+YYYY-MM-DD"`
4. 日期使用 `datetime.now().strftime("%Y-%m-%d")` 动态生成

## 技术方案

### 修改范围

仅涉及 2 个测试文件的轻量修改，无需新增页面对象方法（`fill_remark()` 已存在于 `order_confirm_page.py` L114-127）。

### 实现步骤

**Step 1：文件重命名**

- `tests/test_customer_order_recorded.py` → `tests/test_customer_allProducts.py`
- 无其他文件引用，安全重命名

**Step 2：全部产品测试 (`test_customer_allProducts.py`)**

- 文件头部新增 `from datetime import datetime`
- 在 `run()` 函数内生成日期：`today = datetime.now().strftime("%Y-%m-%d")`
- 订单确认链 L43-46 修改为：

```python
order_confirm.select_payment("先货后款") \
             .select_contract("否") \
             .select_invoice("明细") \
             .fill_remark(f"全部产品专区UI自动化{today}") \
             .submit_order()
```

**Step 3：企业专区测试 (`test_customer_enterprise.py`)**

- 文件头部新增 `from datetime import datetime`
- 在 `run()` 函数内生成日期：`today = datetime.now().strftime("%Y-%m-%d")`
- L62 修改为：`order.fill_enterprise_zone_order(f"企业专区UI自动化{today}")`

### 影响范围

- 仅修改测试文件的备注文案和文件名，不影响页面对象层和业务流程
- `fill_remark()` 方法已通过 `texterea` 定位 + `fill()` 实现，无需改动