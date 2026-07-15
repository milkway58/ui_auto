## 1. test_sales_order.py 盲等优化

- [x] 1.1 L86 (300ms) — CSS 动画等待保留不变
- [x] 1.2 L105 (3000ms) — 购物车刷新后盲等 → `cart_page.page.wait_for_load_state("networkidle", timeout=10000)`
- [x] 1.3 L125 (3000ms) — 报价单新窗口加载盲等 → `quotation_page_obj.wait_for_load_state("networkidle", timeout=10000)`
- [x] 1.4 L140 (200ms) — 滚动稳定保留不变
- [x] 1.5 L143 (5000ms) — C4 合同复选框点击后盲等 → `expect(input.el-checkbox__original).to_be_checked(timeout=10000)` + `assert`
- [x] 1.6 L212 (300ms) — 按钮滚动后保留不变
- [x] 1.7 L270 (1500ms) — 搜索结果盲等 → 对结果表格行使用 `wait_for(state="visible", timeout=10000)`
- [x] 1.8 L278 (300ms) — 复选框滚动后保留不变
- [x] 1.9 L285 (3000ms) — 添加产品确认按钮后盲等 → 确认后等 500ms + 点击关闭按钮 + `dialog.wait_for(state="hidden")`（确认不关闭弹框，需手动关）
- [x] 1.10 L291 (500ms) — 已重构：关闭按钮从 page 级改为 dialog 级定位，关闭后 `wait_for(state="hidden")`

## 2. pages/cart_page.py 盲等优化 + 崩溃修复

- [x] 2.1 L63-68 — `select_first_product()` 开头增加 `wait_for_visible(".el-checkbox__inner", timeout=10000)` 确保物料已渲染
- [x] 2.2 L69 (300ms) — 勾选后动画保留不变
- [x] 2.3 L71 (300ms) — 滚动后动画保留不变
- [x] 2.4 L173 (3000ms) — 继续下单后盲等 → 等待下一步元素（商机下拉框 placeholder）变为 visible
- [x] 2.5 L179 (2000ms) — **直接删除**（L188 已有 `wait_for(state="visible")`）
- [x] 2.6 L190 (1000ms) — 下拉框打开后盲等 → 等待 `.el-select-dropdown:visible` 出现
- [x] 2.7 L200 (1000ms) — 选择商机项后盲等 → 缩短到 300ms
- [x] 2.8 L210 (3000ms) — 信息填写弹窗确认后盲等 → 等待弹窗 `[aria-label="信息填写"]` 变为 hidden

## 3. pages/order_confirm_page.py 盲等优化

- [x] 3.1 L81 (2000ms) — 截图后等待 → 缩短到 500ms
- [x] 3.2 L85 (1000ms) — 第一步提交后盲等 → 等待提交确认弹框变为 visible
- [x] 3.3 L89 (3000ms) — **直接删除**（L92 已有 `expect("生成订单成功").to_be_visible()`）
- [x] 3.4 L172 (2000ms) — 模态框回退模式盲等 → 等待模态框容器变为 visible

## 4. pages/quotation_page.py + 登录导航页 盲等优化

- [x] 4.1 quotation L245 (1000ms) — **直接删除**（调用处已有 `wait_for(state="visible")`）
- [x] 4.2 quotation L118 (1000ms) — 提交报价单后盲等 → 缩短到 300ms
- [x] 4.3 quotation L269 (1000ms) — 确认提交后盲等 → 缩短到 300ms
- [x] 4.4 quotation L102 (1000ms) — 上传附件后盲等 → 缩短到 300ms，等待成功提示可选
- [x] 4.5 quotation L178 (1000ms) — 确认弹框 JS 点击后盲等 → 等待弹框变为 hidden
- [x] 4.6 customer_login_page.py L187 (2000ms) — 登录后盲等 → 等待首页标识元素（`text=您好`）visible
- [x] 4.7 enterprise_zone_page.py L50 (2000ms) — 滑动后盲等 → 等待 `text=企业专区` 按钮 visible
- [x] 4.8 test_customer_allProducts.py L38 (2000ms) — 滚动后盲等 → 等待 `role=tab, name=new营销专区12` visible

## 5. 全量回归验证

- [ ] 5.1 执行 `test_sales_order.py` 单用例，确认通过且耗时 < 50s
- [ ] 5.2 执行 `test_customer_allProducts.py` 单用例，确认通过
- [ ] 5.3 执行 `test_customer_enterprise.py` 单用例，确认通过
- [ ] 5.4 执行三个用例全量回归，确认全部通过且总耗时 < 80s
- [ ] 5.5 如任一同一个用例连续失败 2 次，立即停止并报告
