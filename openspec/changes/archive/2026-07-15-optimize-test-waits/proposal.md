## Why

三个 UI 自动化测试用例中存在大量硬编码 `wait_for_timeout` 盲等（总计约 36s），导致全量回归耗时 ~104s。将盲等替换为条件等待（`wait_for` 状态检测 / `wait_for_load_state` / `expect` 断言），可在不牺牲稳定性的前提下将总耗时降至 60~75s，节省 30-35%。

## What Changes

- **test_sales_order.py**：5 处盲等替换为条件等待，含最大单点 5s（C4 合同勾选后盲等）和 3 处 3s 盲等
- **pages/cart_page.py**：5 处盲等优化，含 1 处完全冗余删除 + 1 处 select_first_product 超时修复
- **pages/order_confirm_page.py**：3 处盲等优化，含 1 处完全冗余删除（已有 expect 断言）
- **pages/quotation_page.py**：1 处冗余删除 + 2 处缩短
- **pages/customer_login_page.py**：1 处登录后盲等替换为页面元素条件等待
- **pages/enterprise_zone_page.py**：1 处滑动后盲等替换为元素可见等待
- **tests/test_customer_allProducts.py**：1 处滚动后盲等替换为元素可见等待

## Capabilities

### New Capabilities

- `test-execution-optimization`: 将硬编码盲等系统性替换为 Playwright 条件等待机制，在保证测试稳定性的前提下缩短执行时间

### Modified Capabilities

<!-- 无已存在规范需要修改 -->

## Impact

- 受影响的文件：`tests/test_sales_order.py`、`pages/cart_page.py`、`pages/order_confirm_page.py`、`pages/quotation_page.py`、`pages/customer_login_page.py`、`pages/enterprise_zone_page.py`、`tests/test_customer_allProducts.py`
- 不影响：全局配置（settings.py）、base_page.py 基础封装、其他测试用例
