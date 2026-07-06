---
name: pytest-allure-refactor
overview: 将 test_customer_allProducts.py 和 test_customer_enterprise.py 从独立脚本重构为 pytest 用例，接入 pytest-playwright page fixture + Allure 报告。allProducts 保持 codegen 原始写法不上 POM。
todos:
  - id: refactor-enterprise
    content: 重构 test_customer_enterprise.py：sync_playwright 脚本转为 pytest test_customer_enterprise_order(page) 用例，删除浏览器自管理，login 前手动 page.goto 完整 URL 绕过 BASE_URL 问题
    status: completed
  - id: refactor-all-products
    content: 重构 test_customer_allProducts.py：sync_playwright 脚本转为 pytest test_customer_all_products_order(page) 用例，保持 codegen 原始 selector 风格，仅订单确认用 OrderConfirmPage
    status: completed
  - id: verify-both
    content: 依次执行两个重构后的 pytest 用例，验证 popup 传递和 Allure 报告生成
    status: completed
    dependencies:
      - refactor-enterprise
      - refactor-all-products
---

## 用户需求

将两个客户下单测试脚本重构为 pytest 用例，使其能通过 `pytest --alluredir=reports/allure-results` 生成 Allure 报告。

## 核心功能

1. **test_customer_enterprise.py** — 重构为 pytest 用例，保留全部 POM 调用
2. **test_customer_allProducts.py** — 重构为 pytest 用例，登录部分保持 codegen 录制风格的原始 Playwright selector，仅订单确认环节使用 `OrderConfirmPage`
3. 两个重构后的用例均通过 `pytest` 执行，自动生成 Allure 报告（截图 + 断言）

## 约束

- `test_customer_allProducts.py` 登录步骤**不上 POM**，保持 `page.get_by_text()` / `page.locator()` 等原始 selector 写法
- `test_customer_enterprise.py` 的 `CustomerLoginPage` 不使用 `.open()` 方法（BASE_URL 拼接错误），改为手动 `page.goto("完整URL")`
- popup 跨页面传递：验证通过，`expect_popup().value` 机制独立于原 page，多层嵌套正确

## 技术方案

### 重构策略

**test_customer_enterprise.py**（POM 风格）

```
旧: def run(playwright: Playwright) -> None:  (sync_playwright 自管理)
新: def test_customer_enterprise_order(page):  (pytest-playwright fixture)
```

- 删除 `browser/channel/context/page` 手动创建（conftest 已配置 Chrome + 1920x1080）
- 删除 `try/except/finally`（conftest hook 自动截图 + 附加 Allure）
- 登录方案：`page.goto("https://zjtest.gyuncai.com/mall/view/login")` + `CustomerLoginPage(page).customer_login(...)` — 绕过 `settings.BASE_URL` 拼写错误
- 添加 `@pytest.mark.customer` + `@pytest.mark.order(3)`
- 保留末尾 `print("[SUCCESS]")` 或用 `assert` 替代

**test_customer_allProducts.py**（codegen 风格 + 局部 POM）

```
旧: def run(playwright: Playwright) -> None:  (sync_playwright 自管理)
新: def test_customer_all_products_order(page):  (pytest-playwright fixture)
```

- 删除 `browser/context` 手动创建
- 保留所有 `page.goto()` / `page.get_by_text()` / `page.locator()` / `page.expect_popup()` 原始写法
- 订单确认环节保留 `OrderConfirmPage(page2)` 链式调用
- 添加 `@pytest.mark.customer` + `@pytest.mark.order(2)`

### 执行方式

```
# 运行单个用例（含 Allure 报告生成）
python -m pytest tests/test_customer_enterprise.py -v -s

# 运行全部客户用例
python -m pytest tests/ -m customer -v -s

# 查看 Allure 报告
allure serve reports/allure-results
```

### 影响范围

- 只修改 2 个测试文件，不影响 POM 层和 conftest
- `conftest.py` 的 `pytest_runtest_makereport` hook 自动为重构后的用例截图 + 附加 Allure
- `pytest.ini` 已有 `--alluredir=reports/allure-results`，无需修改