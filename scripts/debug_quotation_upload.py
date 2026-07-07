"""
报价单详情页 Phase 7+8 独立调试脚本（录制版流程）

直接跳转报价单详情页，按 Codegen 录制流程执行：
1. 勾选 C4 合同复选框
2. 上传附件
3. 产品选配 → 添加 → 确认提交
4. 提交报价单 → 勾选 C4 → 确认
"""
import os
import re
import sys
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.sales_login_page import SalesLoginPage
from pages.quotation_page import QuotationPage
from utils.logger import get_logger

logger = get_logger(__name__)

SALES_USERNAME = "xuzw"
SALES_PASSWORD = "123qwe"
QUOTATION_URL = "https://zjtest.gyuncai.com/mall/mall-view-admin/businessOrder/detail?orderId=53488"
ATTACHMENT_FILE = r"C:\Users\wangt-aw\Downloads\test_datas\渠道订单导入模版.xlsx"


def _resolve_attachment_path(filename: str) -> str:
    if os.path.isabs(filename):
        return filename
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for sub in ("", "data"):
        path = os.path.join(base_dir, sub, filename)
        if os.path.exists(path):
            return path
    logger.warning(f"附件未找到: {filename}，回退原始路径")
    return filename


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # ====== 销售登录 ======
            logger.info("--- 销售登录 ---")
            SalesLoginPage(page).open().sales_login(SALES_USERNAME, SALES_PASSWORD)

            # ====== 跳转报价单详情页 ======
            logger.info(f"--- 跳转: {QUOTATION_URL} ---")
            page.goto(QUOTATION_URL, wait_until="networkidle")
            page.wait_for_timeout(15000)
            qp = QuotationPage(page)

            # ====== 勾选「审批通过后自动生成C4合同」复选框 ======
            logger.info("--- 勾选 C4 合同复选框 ---")
            target = page.locator("label.el-checkbox").filter(
                has_text=re.compile(r"审批通过后自动生成C4合同")
            )
            target.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            target.click(force=True)
            page.wait_for_timeout(300)
            # 备用：JS 原生 click 兜底
            # if not target.locator("input.el-checkbox__original").is_checked():
            #     page.evaluate("""() => {
            #         const labels = document.querySelectorAll('label.el-checkbox');
            #         for (const label of labels) {
            #             if (label.textContent.includes('审批通过后自动生成C4合同')) {
            #                 label.click(); break;
            #             }
            #         }
            #     }""")
            #     page.wait_for_timeout(300)
            logger.info("C4 合同复选框已勾选")

            # ====== 上传附件 ======
            logger.info("--- 上传附件 ---")
            qp.upload_attachment(_resolve_attachment_path(ATTACHMENT_FILE))
            logger.info("上传附件完成")

            # ====== 产品选配 + 添加 + 确认提交 ======
            logger.info("--- 产品选配 → 添加 → 确认提交 ---")
            qp.click_product_config()
            page.wait_for_timeout(3000)

            # --- 修改套数数量（el-input-number spinbutton）---
            qty_input = page.locator("input[role=\"spinbutton\"]").nth(1)
            qty_input.wait_for(state="visible", timeout=5000)
            qty_input.click()
            qty_input.fill("2")
            qty_input.press("Enter")
            logger.info("套数设为 2")
            # 备用B：JS set value + dispatchEvent
            # page.evaluate("""() => {
            #     const spin = document.querySelectorAll('input[role="spinbutton"]')[1];
            #     if (spin) { spin.value = '2'; spin.dispatchEvent(new Event('input',{bubbles:true})); }
            # }""")
            # 备用C：click 递增按钮
            # page.locator(".el-input-number__increase").nth(1).click()

            page.wait_for_timeout(500)

            # --- 添加商品 ---
            page.get_by_role("button", name="").nth(1).click()
            logger.info("添加商品按钮已点击")
            # 备用B：文本定位
            # page.locator("button:has-text('添加')").nth(1).click(force=True)
            # 备用C：JS click
            # page.evaluate("""() => {
            #     const btns = document.querySelectorAll('.el-dialog button[class*="add"]');
            #     if (btns.length > 0) btns[btns.length - 1].click();
            # }""")

            page.wait_for_timeout(1000)

            # --- 确认提交（按钮被弹窗截断不可见）---
            # 滚动所有可能的弹窗容器，让底部按钮进入视口
            page.evaluate("""() => {
                const body = document.querySelector('.el-dialog__body');
                if (body) body.scrollTop = body.scrollHeight;
                const dialog = document.querySelector('.el-dialog');
                if (dialog) dialog.scrollTop = dialog.scrollHeight;
                const wrapper = document.querySelector('.el-dialog__wrapper');
                if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
            }""")
            page.wait_for_timeout(500)
            btn = page.get_by_text("确认提交", exact=True)
            btn.scroll_into_view_if_needed()
            btn.click(force=True)
            logger.info("确认提交已点击")
            # 备用B：修改弹窗 CSS 高度
            # page.evaluate("""() => {
            #     const d = document.querySelector('.el-dialog');
            #     if (d) { d.style.maxHeight='95vh'; d.style.overflow='visible'; }
            #     const b = document.querySelector('.el-dialog__body');
            #     if (b) { b.style.maxHeight='80vh'; b.style.overflowY='auto'; }
            # }""")
            # page.get_by_role("button", name="确认提交").click(force=True)
            # 备用C：JS 原生 dispatchEvent
            # page.evaluate("""() => {
            #     const els = document.querySelectorAll('span, button, div');
            #     for (const el of els) {
            #         if (el.textContent.trim()==='确认提交') {
            #             el.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
            #             return;
            #         }
            #     }
            # }""")

            logger.info("产品选配完成")

            # ====== 提交报价单 + 勾选 C4 + 确认 ======
            logger.info("--- 提交报价单 → 勾选 C4 → 确认 ---")
            (
                qp
                .submit_quotation()
                .check_auto_contract()
                .confirm_dialog()
            )
            logger.info("提交完成")

            logger.info("=" * 50)
            logger.info("调试脚本执行完成")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"执行失败: {e}")
            raise
        finally:
            input("按 Enter 关闭浏览器...")
            context.close()
            browser.close()


if __name__ == "__main__":
    run()
