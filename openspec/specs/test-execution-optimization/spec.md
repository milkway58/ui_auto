# test-execution-optimization

## Purpose

定义 UI 自动化测试执行优化规范，将硬编码盲等（`wait_for_timeout`）替换为 Playwright 条件等待，提升测试执行速度和稳定性。

## Requirements

### Requirement: 盲等替换为条件等待

测试用例和页面对象中的所有 `page.wait_for_timeout(N)`（N > 500ms）SHALL 替换为对应的 Playwright 条件等待方法，使测试按实际条件唤醒而非盲等固定时间。

#### Scenario: 页面加载等待
- **WHEN** 测试触发页面刷新（`page.reload()`）或打开新窗口（`expect_popup()`）
- **THEN** 后续等待 SHALL 使用 `wait_for_load_state("networkidle")` 或 `wait_for(state="visible")` 检测目标元素，而非 `wait_for_timeout(3000)`

#### Scenario: 复选框状态等待
- **WHEN** 测试点击 Element UI 复选框后需要确认勾选状态
- **THEN** SHALL 使用 `expect(input.el-checkbox__original).to_be_checked()` 等待状态到位，而非 `wait_for_timeout(5000)`

#### Scenario: 弹框关闭等待
- **WHEN** 测试点击确认按钮后等待弹框关闭
- **THEN** SHALL 使用 `dialog.wait_for(state="hidden")` 检测弹框 DOM 移除，而非 `wait_for_timeout(3000)`

#### Scenario: 搜索结果等待
- **WHEN** 测试触发搜索操作后等待结果显示
- **THEN** SHALL 使用 `row.wait_for(state="visible")` 检测结果行出现，而非 `wait_for_timeout(1500)`

#### Scenario: 登录跳转等待
- **WHEN** 测试提交登录表单后等待页面跳转
- **THEN** SHALL 等待首页标识元素（如用户名文本）可见，而非 `wait_for_timeout(2000)`

### Requirement: 冗余盲等删除

代码中若某处 `wait_for_timeout` 后方已有等效的条件等待（如 `expect().to_be_visible()`），则该盲等 SHALL 直接删除。

#### Scenario: 提交订单后冗余等待
- **WHEN** `order_confirm_page.submit_order()` 第二步点击提交按钮后
- **THEN** 后方的 `wait_for_timeout(3000)` SHALL 删除，因为 L92 已有 `expect("生成订单成功").to_be_visible()` 提供等效等待

#### Scenario: 选择商机开头冗余等待
- **WHEN** `cart_page.select_opportunity()` 方法开头
- **THEN** 开头的 `wait_for_timeout(2000)` SHALL 删除，因为 L188 `wait_for(state="visible")` 已提供等效等待

### Requirement: 购物车复选框渲染保障

`cart_page.select_first_product()` 在执行 `click_first` 遍历选择器之前，SHALL 先等待 `.el-checkbox__inner` 元素变为可见，避免元素未渲染导致所有选择器未命中引发长时间超时和浏览器意外关闭。

#### Scenario: 购物车页面已渲染
- **WHEN** 调用 `select_first_product()`
- **THEN** SHALL 先执行 `wait_for_visible(".el-checkbox__inner", timeout=10000)` 确保物料复选框已渲染

### Requirement: 自测失败快速终止

所有修改完成后执行三个测试用例全量回归。若任一同一个用例连续失败 2 次，SHALL 立即停止所有修改操作并与用户沟通。

#### Scenario: 自测连续失败
- **WHEN** 同一测试用例在修改后连续执行 2 次均失败
- **THEN** SHALL 停止所有优化工作，向用户报告失败详情并等待指示
