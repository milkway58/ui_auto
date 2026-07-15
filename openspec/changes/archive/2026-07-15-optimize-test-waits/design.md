## Context

三个 UI 自动化测试用例（`test_sales_order.py`、`test_customer_allProducts.py`、`test_customer_enterprise.py`）中使用了大量 `page.wait_for_timeout(N)` 硬编码盲等，全量回归耗时 ~104s（最近一次运行：1 failed + 2 passed）。

现有 BasePage 已提供 `wait_for_visible()`、`wait_for_hidden()`、`wait_for_network_idle()` 等条件等待方法，但测试用例和页面对象中并未统一使用。全局 `TIMEOUT=10000ms`、`NETWORK_IDLE_TIMEOUT=5000ms` 已配置为较短的超时值。

## Goals / Non-Goals

**Goals:**
- 将 `wait_for_timeout` 盲等替换为 Playwright 条件等待，让测试"等到条件满足即继续"而非"等够时间再继续"
- 三个用例全量回归总耗时从 ~104s 降至 60-75s
- 保持或提升稳定性（条件等待比盲等更可靠，不依赖操作系统调度）
- 修复 test_sales_order 购物车 `select_first_product()` 偶发浏览器关闭问题

**Non-Goals:**
- 不修改全局配置（settings.py 中的 TIMEOUT 值不动）
- 不对 base_page.py 做架构变更
- 不引入新的第三方依赖
- 不改变测试逻辑流程

## Decisions

### D1：盲等替换原则 — "等什么就检测什么"

每个 `wait_for_timeout(N)` 替换为对应的条件检测，不泛化处理：

| 盲等场景 | 替换策略 |
|----------|----------|
| 页面/弹框加载 | `wait_for_load_state("networkidle")` 或 `wait_for(state="visible")` |
| 复选框状态 | `expect(input).to_be_checked()`（C4 规范推荐方式） |
| 弹框关闭 | `dialog.wait_for(state="hidden")` |
| 搜索结果渲染 | `row.wait_for(state="visible")` |
| 登录跳转 | 等待首页标识元素可见 |
| 滑动渲染 | 等待目标交互元素可见 |

**备选方案**：全局缩减所有盲等到 500ms — 简单但不解决根本问题，弱弱网环境会 flaky。

### D2：超时设置为 10s

所有新增条件等待超时设为 10s，与全局 `TIMEOUT` 对齐。比原来盲等长但按需唤醒，实际耗时远小于盲等。

### D3：cart_page.select_first_product 崩溃修复

根因分析：`click_first` 遍历 4 个选择器，若页面未渲染完成则全部未命中，Playwright 每个选择器默认等待 10s（`self.timeout`），遍历最坏情况 40s，且超时后不抛异常仅 warn，后续操作在无效页面上执行导致浏览器意外关闭。

修复方式：在 `select_first_product()` 开头增加 `wait_for_visible(".el-checkbox__inner", timeout=10000)` 确保物料已渲染。

### D4：优先删冗余，再替盲等

有两处完全冗余的盲等（cart L179、order L89），直接删除而非替换。前者后方已有 `wait_for(state="visible")`，后者后方已有 `expect().to_be_visible()`。

### D5：保留 ≤300ms 的动画等待

300ms 及以下的小等待（如 CSS 过渡动画、滚动稳定）不修改，收益微小且改动风险大。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 条件等待在网络极慢时可能比盲等更慢 | 统一 10s 超时上限，与全局 TIMEOUT 一致，不会无限等待 |
| 某些条件等待选择器可能在特殊场景未命中 | 替换时保留原选择器链，优先使用已验证的选择器逻辑 |
| 修改 cart_page 影响三个测试用例 | 共享页面对象修改后，三个用例统一自测验证 |
| 自测失败 2 次 | 立即停止修改，与用户沟通确认下一步 |
