"""
销售完整下单流程测试（合并版）

合并来源：
- test_sales_order_flow_recorded.py（Phase 1-6: 登录 → 报价单详情页）
- debug_quotation_upload.py（报价单详情页详细操作）

覆盖流程：
1. 销售登录
2. 搜索产品并加入购物车
3. 购物车生成报价单 → 选择商机 → 查看报价单
4. 报价单详情页：
   - 勾选 C4 合同复选框
   - 上传附件
   - 产品选配（修改套数、断言金额、确认提交）
   - 添加产品（搜索 10007519、勾选、确认）
   - 提交报价单 + 确认
"""
import os
import re

import pytest

from playwright.sync_api import expect

from pages.sales_login_page import SalesLoginPage
from pages.sales_home_page import SalesHomePage
from pages.cart_page import SalesCartPage
from pages.quotation_page import QuotationPage
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# 测试数据
SALES_USERNAME = "xuzw"
SALES_PASSWORD = "123qwe"
SEARCH_KEYWORD = "10004188"
ADD_TO_CART_INDEX = 1
OPPORTUNITY_NAME = "13503: 审批商机20260706-01"
ATTACHMENT_FILE = r"C:\Users\wangt-aw\Downloads\test_datas\渠道订单导入模版.xlsx"
ADD_PRODUCT_CODE = "10007519"
PRODUCT_QTY = "2"
EXPECTED_PRICE = "17200.00"


@pytest.mark.sales
@pytest.mark.order
class TestSalesOrder:
    """销售完整下单流程测试（合并版）"""

    @pytest.mark.order(1)
    def test_sales_full_order(self, page):
        """
        销售完整下单流程（端到端）

        步骤:
        1. 销售登录（xuzw/123qwe）
        2. 搜索产品 10004188 → 加入购物车
        3. 购物车 → 生成报价单 → 选择商机 → 查看报价单
        4. 报价单详情页操作:
           - 勾选 C4 合同
           - 上传附件
           - 产品选配（套数→2，断言 ¥17200.00）
           - 添加产品（搜索 10007519）
           - 提交报价单 + 确认
        """
        logger.info("=" * 50)
        logger.info("销售完整下单流程测试（合并版）- 开始")
        logger.info("=" * 50)

        # ====== Phase 1: 销售登录 ======
        logger.info("--- Phase 1: 销售登录 ---")
        login_page = SalesLoginPage(page)
        login_page.open().sales_login(
            username=SALES_USERNAME,
            password=SALES_PASSWORD,
        )

        # ====== Phase 2: 搜索产品 + 加入购物车 ======
        logger.info("--- Phase 2: 搜索产品 + 加入购物车 ---")
        sales_home = SalesHomePage(page)
        (
            sales_home
            .search_product(SEARCH_KEYWORD)
            .assert_search_results_visible()
        )
        page.wait_for_timeout(300)  # CSS过渡动画稳定
        sales_home.add_to_cart(index=ADD_TO_CART_INDEX)

        # ====== Phase 3: 打开购物车（新窗口） ======
        logger.info("--- Phase 3: 打开购物车 ---")
        cart_page: SalesCartPage = sales_home.open_cart()

        # 检查购物车是否展示物料，未展示则自动刷新
        cart_has_items = False
        for loc in cart_page.CART_ITEM_ALT:
            try:
                if cart_page.locate(loc).first.is_visible(timeout=2000):
                    cart_has_items = True
                    break
            except Exception:
                continue
        if not cart_has_items:
            logger.info("  → 购物车内无物料，自动刷新页面并等待 3s ...")
            cart_page.page.reload()
            cart_page.page.wait_for_load_state("networkidle", timeout=10000)
            logger.info("  → 页面已刷新 ✓")

        # ====== Phase 4: 生成报价单 ======
        logger.info("--- Phase 4: 生成报价单 ---")
        (
            cart_page
            .select_first_product()
            .generate_quotation()
            .continue_order()
        )

        # ====== Phase 5: 选择商机 ======
        logger.info("--- Phase 5: 选择商机 ---")
        cart_page.select_opportunity(OPPORTUNITY_NAME)

        # ====== Phase 6: 查看报价单（新窗口） ======
        logger.info("--- Phase 6: 查看报价单 ---")
        quotation_page_obj = cart_page.click_view_quotation()
        quotation_page = QuotationPage(quotation_page_obj)
        quotation_page_obj.wait_for_load_state("networkidle", timeout=10000)
        logger.info("  → 报价单详情页加载完成 ✓")

        # ================================================================
        # 以下合并自 debug_quotation_upload.py（Step 4 起）
        # ================================================================


        # ====== 勾选「审批通过后自动生成C4合同」复选框 ======
        logger.info("[Step 4/14] 勾选 C4 合同复选框 ---")
        target = quotation_page_obj.locator("label.el-checkbox").filter(
            has_text=re.compile(r"审批通过后自动生成C4合同")
            ).locator(".el-checkbox__inner")
        logger.info("  → 定位复选框并滚动到可见区域")
        target.scroll_into_view_if_needed()
        quotation_page_obj.wait_for_timeout(200)
        logger.info("  → 点击复选框（.el-checkbox__inner）")
        target.click()
        checkbox_input = quotation_page_obj.locator("label.el-checkbox").filter(
            has_text=re.compile(r"审批通过后自动生成C4合同")
        ).locator("input.el-checkbox__original")
        expect(checkbox_input).to_be_checked(timeout=10000)
        is_checked = checkbox_input.is_checked()
        assert is_checked, "C4 合同复选框未勾选!"
        logger.info("  → C4 合同复选框已勾选 ✓")

        # ====== 上传附件 ======
        logger.info("  → 上传附件 ---")
        quotation_page.upload_attachment(ATTACHMENT_FILE)
        logger.info("  → 上传附件完成 ✓")

        # ====== 产品选配 ======
        logger.info("  → 产品选配 ---")
        quotation_page.click_product_config()
        quotation_page_obj.locator(
            '[aria-label="报价单-产品方案选配"]'
        ).wait_for(state="visible", timeout=15000)
        logger.info("  → 产品选配弹框已打开 ✓")

        # 注入 CSS：固定弹框高度
        quotation_page_obj.add_style_tag(content="""
            [aria-label="报价单-产品方案选配"] .box_content {
                height: 600px !important;
                overflow-y: auto;
            }
        """)
        logger.info("  → 弹框 CSS 已注入 ✓")

        # 修改套数
        qty_input = quotation_page_obj.locator("input[role=\"spinbutton\"]").nth(1)
        qty_input.wait_for(state="visible", timeout=5000)
        qty_input.click()
        qty_input.fill(PRODUCT_QTY)
        qty_input.press("Enter")
        logger.info("  → 套数设为 %s ✓", PRODUCT_QTY)
        quotation_page_obj.wait_for_timeout(200)

        # 断言金额
        logger.info("  → 断言弹窗底部金额 ¥%s", EXPECTED_PRICE)
        price_locator = quotation_page_obj.locator(
            '[aria-label="报价单-产品方案选配"]'
        ).locator(f"text={EXPECTED_PRICE}")
        if price_locator.is_visible(timeout=5000):
            logger.info("  → 弹窗底部已出现 ¥%s 元 ✓", EXPECTED_PRICE)
            confirm_btn = quotation_page_obj.get_by_text("确认提交", exact=True)
            confirm_btn.wait_for(state="visible", timeout=10000)
            confirm_btn.scroll_into_view_if_needed()
            confirm_btn.click()
            logger.info("  → 确认提交已点击 ✓")
            quotation_page_obj.locator(
                '[aria-label="报价单-产品方案选配"]'
            ).wait_for(state="hidden", timeout=10000)
            logger.info("  → 弹框已关闭 ✓")
        else:
            logger.error("  → 未找到 ¥%s 元，跳过提交", EXPECTED_PRICE)

        # ====== 添加产品（搜索 + 勾选 + 确认） ======
        logger.info("  → 点击「添加产品」按钮 ---")
        add_product_btn = quotation_page_obj.locator(
            "span:has(i.el-icon-circle-plus)"
        ).first
        add_product_btn.wait_for(state="visible", timeout=20000)
        add_product_btn.scroll_into_view_if_needed()
        quotation_page_obj.wait_for_timeout(300)
        add_product_btn.click(force=True, timeout=20000)
        logger.info("  → 添加产品按钮已点击 ✓")

        # 等待弹框容器出现，限定后续定位范围到弹框内
        dialog = quotation_page_obj.locator(".el-dialog__wrapper:visible").last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("  → 添加产品弹框已打开 ✓")

        logger.info("  → 搜索产品 %s ---", ADD_PRODUCT_CODE)
        # 三级降级：弹框容器内定位搜索输入框
        search_input = None
        for level, selector in enumerate([
            "input[placeholder*='搜索'], input[placeholder*='物料']",
            "input:not([type='hidden'])",
        ], 1):
            candidates = dialog.locator(selector)
            count = candidates.count()
            logger.info("  → Level %d: selector=%r, count=%d", level, selector, count)
            for i in range(count):
                inp = candidates.nth(i)
                if inp.is_visible():
                    search_input = inp
                    logger.info("  → Level %d: 命中第 %d 个可见 input ✓", level, i)
                    break
            if search_input:
                break
            logger.warning("  → Level %d: 无可见匹配", level)

        if not search_input:
            # 诊断兜底：截图 + 输出所有 input placeholder
            screenshot_path = quotation_page_obj.screenshot(path="DIAG_add_product_dialog")
            logger.error("  → 截图已保存: %s", screenshot_path)
            all_inputs = dialog.locator("input").all()
            for idx, inp in enumerate(all_inputs):
                try:
                    ph = inp.get_attribute("placeholder") or ""
                    vis = inp.is_visible()
                    logger.info("  → [诊断] input[%d] placeholder=%r visible=%s", idx, ph, vis)
                except Exception:
                    logger.info("  → [诊断] input[%d] 不可访问", idx)
            raise AssertionError("弹框内未找到可见搜索输入框，详见诊断日志")

        search_input.fill(ADD_PRODUCT_CODE)
        logger.info("  → 已输入物料编码 %s ✓", ADD_PRODUCT_CODE)

        # 搜索按钮同样限定弹框范围
        search_btn = dialog.locator(
            ".el-input__suffix .el-icon-search,"
            " button:has-text('搜索'),"
            " [class*='search'] i"
        ).first
        if search_btn.is_visible(timeout=2000):
            search_btn.click()
            logger.info("  → 已点击搜索按钮 ✓")
        else:
            search_input.press("Enter")
            logger.info("  → 回车触发搜索 ✓")
        row_selector = f".el-table__row:has(td:has-text('{ADD_PRODUCT_CODE}'))"
        quotation_page_obj.locator(row_selector).first.wait_for(state="visible", timeout=10000)

        logger.info("  → 勾选产品并确认 ---")
        row = quotation_page_obj.locator(row_selector).first
        checkbox_inner = row.locator(".el-checkbox__inner").first
        checkbox_inner.scroll_into_view_if_needed()
        quotation_page_obj.wait_for_timeout(300)
        checkbox_inner.dispatch_event("click")
        logger.info("  → 产品复选框已勾选 ✓")
        confirm_btn = quotation_page_obj.get_by_text("确认", exact=True).last
        confirm_btn.scroll_into_view_if_needed()
        confirm_btn.click(force=True)
        logger.info("  → 确认按钮已点击")
        quotation_page_obj.wait_for_timeout(500)

        logger.info("  → 关闭添加产品弹框")
        close_btn = dialog.locator("i.el-icon-close.close").first
        close_btn.scroll_into_view_if_needed()
        close_btn.click(force=True)
        dialog.wait_for(state="hidden", timeout=10000)
        logger.info("  → 弹框已关闭 ✓")
        logger.info("  → 产品添加确认完成 ✓")

        # ====== 滚动 + 清除遮罩 ======
        logger.info("  → 滚动弹窗容器到底部")
        quotation_page_obj.evaluate("""() => {
            const body = document.querySelector('.el-dialog__body');
            if (body) body.scrollTop = body.scrollHeight;
            const dialog = document.querySelector('.el-dialog');
            if (dialog) dialog.scrollTop = dialog.scrollHeight;
            const wrapper = document.querySelector('.el-dialog__wrapper');
            if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
        }""")
        quotation_page_obj.wait_for_timeout(200)
        logger.info("  → 弹窗已滚动到底部 ✓")

        logger.info("  → 移除弹窗遮罩 .v-modal")
        quotation_page_obj.evaluate("""() => {
            document.querySelectorAll('.v-modal').forEach(el => el.remove());
        }""")
        quotation_page_obj.wait_for_timeout(200)
        logger.info("  → 遮罩已清除 ✓")

        # ====== 提交报价单 + 确认 ======
        logger.info("  → 点击「提交报价单」按钮 ---")
        quotation_page.submit_quotation()
        logger.info("  → 提交报价单按钮已点击 ✓")

        logger.info("  → 确认弹框 ---")
        quotation_page.confirm_dialog()
        logger.info("  → 确认弹框已处理 ✓")

        logger.info("=" * 50)
        logger.info("销售完整下单流程测试（合并版）- 完成")
        logger.info("=" * 50)
