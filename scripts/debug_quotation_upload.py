"""
报价单详情页 Phase 7+8 独立调试脚本（录制版流程）

直接跳转报价单详情页，按 Codegen 录制流程执行：
1. 勾选 C4 合同复选框
2. 上传附件
3. 产品选配 → 添加 → 确认提交
4. 提交报价单 → 确认（不操作弹框中的 C4 复选框）
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
QUOTATION_URL = "https://zjtest.gyuncai.com/mall/mall-view-admin/businessOrder/detail?orderId=53497"
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
        logger.info("[Step 1/9] 浏览器启动完成")

        try:
            # ====== 销售登录 ======
            logger.info("[Step 2/9] 开始销售登录 ---")
            logger.info("  → 打开登录页面")
            login_page = SalesLoginPage(page)
            login_page.open()
            logger.info("  → 登录页面已打开")

            logger.info("  → 执行登录: 账号=%s", SALES_USERNAME)
            login_page.sales_login(SALES_USERNAME, SALES_PASSWORD)
            logger.info("  → 销售登录完成 ✓")

            # ====== 跳转报价单详情页 ======
            logger.info("[Step 3/9] 跳转报价单详情页 ---")
            logger.info("  → 跳转 URL: %s", QUOTATION_URL)
            page.goto(QUOTATION_URL, wait_until="networkidle")
            page.wait_for_timeout(15000)
            qp = QuotationPage(page)
            logger.info("  → 报价单详情页加载完成 ✓")

            # ====== 勾选「审批通过后自动生成C4合同」复选框 ======
            logger.info("[Step 4/9] 勾选 C4 合同复选框 ---")
            target = page.locator("label.el-checkbox").filter(
                has_text=re.compile(r"审批通过后自动生成C4合同")
            ).locator("span.el-checkbox__input")
            logger.info("  → 定位复选框并滚动到可见区域")
            target.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            logger.info("  → 点击复选框（span.el-checkbox__input）")
            target.click(force=True)
            page.wait_for_timeout(300)
            logger.info("  → C4 合同复选框已勾选 ✓")

            # ====== 上传附件 ======
            logger.info("[Step 5/9] 上传附件 ---")
            attachment_path = _resolve_attachment_path(ATTACHMENT_FILE)
            logger.info("  → 附件路径: %s", attachment_path)
            qp.upload_attachment(attachment_path)
            logger.info("  → 上传附件完成 ✓")



            # ====== 产品选配 + 添加 + 确认提交 ======
            logger.info("[Step 6/9] 产品选配 ---")
            logger.info("  → 点击产品选配按钮")
            qp.click_product_config()
            page.wait_for_timeout(3000)
            logger.info("  → 产品选配弹框已打开 ✓")

            logger.info("  → 设置弹框 .box_content 固定高度 600px")
            page.add_style_tag(content="""
                [aria-label="报价单-产品方案选配"] .box_content {
                    height: 600px !important;
                    overflow-y: auto;
                }
            """)
            logger.info("  → 弹框 .box_content CSS 已注入 ✓")

            logger.info("  → 修改套数数量")
            qty_input = page.locator("input[role=\"spinbutton\"]").nth(1)
            qty_input.wait_for(state="visible", timeout=5000)
            qty_input.click()
            qty_input.fill("2")
            qty_input.press("Enter")
            logger.info("  → 套数设为 2 ✓")
            page.wait_for_timeout(500)

            logger.info("  → 断言弹窗底部金额 ¥17200.00")
            price_locator = page.locator(
                '[aria-label="报价单-产品方案选配"]'
            ).locator("text=17200.00")
            if price_locator.is_visible(timeout=5000):
                logger.info("  → 断言通过：弹窗底部已出现 ¥17200.00 元 ✓")
            else:
                logger.warning("  → 断言失败：未找到 ¥17200.00 元，等待确认提交按钮出现")
                page.get_by_text("确认提交", exact=True).wait_for(state="visible", timeout=10000)
                logger.info("  → 确认提交按钮已出现 ✓")

            logger.info("  → 滚动弹窗容器到底部")
            page.evaluate("""() => {
                const body = document.querySelector('.el-dialog__body');
                if (body) body.scrollTop = body.scrollHeight;
                const dialog = document.querySelector('.el-dialog');
                if (dialog) dialog.scrollTop = dialog.scrollHeight;
                const wrapper = document.querySelector('.el-dialog__wrapper');
                if (wrapper) wrapper.scrollTop = wrapper.scrollHeight;
            }""")
            page.wait_for_timeout(500)
            logger.info("  → 弹窗已滚动到底部 ✓")

            logger.info("  → 点击「确认提交」按钮")
            btn = page.get_by_text("确认提交", exact=True)
            btn.scroll_into_view_if_needed()
            btn.click(force=True)
            logger.info("  → 确认提交已点击 ✓")

            logger.info("  → 移除弹窗遮罩 .v-modal")
            page.evaluate("""() => {
                document.querySelectorAll('.v-modal').forEach(el => el.remove());
            }""")
            page.wait_for_timeout(500)
            logger.info("  → 遮罩已清除 ✓")

            # ====== 提交报价单 + 确认（不操作弹框中的 C4 复选框）======
            logger.info("[Step 7/9] 点击提交报价单 ---")
            logger.info("  → 点击页面底部「提交报价单」按钮")
            qp.submit_quotation()
            logger.info("  → 提交报价单按钮已点击 ✓")

            logger.info("[Step 8/9] 确认弹框（跳过复选框操作）---")
            logger.info("  → 开始断言弹框 + 点击确定按钮")
            qp.confirm_dialog()
            logger.info("  → 确认弹框已处理 ✓")

            logger.info("[Step 9/9] 提交完成 ✓")

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
