"""
OrderConfirmPage - 订单确认页页面对象

封装订单确认页操作：
- 选择支付方式、合同类型、发票类型
- 提交订单（含截图+断言）
- 查看订单（弹窗处理）

定位策略：text= 文字定位 + role 按钮定位
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class OrderConfirmPage(BasePage):
    """
    订单确认页页面对象

    用法:
        order_page = OrderConfirmPage(page)
        order_page.select_payment("先货后款") \
                   .select_contract("否") \
                   .select_invoice("明细") \
                   .submit_order()
    """

    # ---------- 页面元素定位器 ----------
    # 截图名称（不含路径和扩展名，base_page 自动加时间戳和 .png）
    SCREENSHOT_SUBMIT = "SUBMIT_before"

    def __init__(self, page: Page):
        super().__init__(page)
        self._url = "/order_confirm"

    # ==========================================
    # 订单信息填写
    # ==========================================
    def select_payment(self, method: str = "先货后款") -> "OrderConfirmPage":
        """选择支付方式"""
        logger.info(f"选择支付方式: {method}")
        self.page.get_by_text(method, exact=True).click()
        return self

    def select_contract(self, contract_type: str = "否") -> "OrderConfirmPage":
        """选择纸质合同（否/是）"""
        logger.info(f"选择合同类型: {contract_type}")
        self.page.get_by_text(contract_type, exact=True).click()
        return self

    def select_invoice(self, invoice_type: str = "明细") -> "OrderConfirmPage":
        """选择发票类型"""
        logger.info(f"选择发票类型: {invoice_type}")
        self.page.get_by_text(invoice_type, exact=True).click()
        return self

    # ==========================================
    # 提交订单
    # ==========================================
    def submit_order(self) -> "OrderConfirmPage":
        """
        提交订单：截图 → 等待 → 双层点击 → 断言成功

        流程:
        1. 截图保存提交前页面
        2. 等待 2s
        3. 点击 p 标签"提交订单"（触发确认弹窗）
        4. 等待 1s
        5. 点击 button"提交订单"（确认提交）
        6. 等待 3s
        7. 断言"生成订单成功"
        """
        logger.info("提交订单：截图 → 等待 → 提交")
        self.screenshot(self.SCREENSHOT_SUBMIT)
        self.page.wait_for_timeout(2000)

        # 第一步：p标签触发确认
        self.page.locator("p").filter(has_text="提交订单").click()
        self.page.wait_for_timeout(1000)

        # 第二步：button确认提交
        self.page.get_by_role("button", name="提交订单", exact=True).click()
        self.page.wait_for_timeout(3000)

        # 断言成功
        expect(self.page.get_by_text("生成订单成功")).to_be_visible()
        logger.info("[OK] 订单提交成功")

        return self

    # ==========================================
    # 企业专区专用字段
    # ==========================================
    def select_source_end(self, option: str = "控制端") -> "OrderConfirmPage":
        """
        选择来源端（企业专区专用字段）

        Args:
            option: 来源端选项，默认"控制端"

        Returns:
            self（支持链式调用）
        """
        logger.info(f"选择来源端: {option}")
        self.page.get_by_text(option, exact=True).click()
        return self

    def fill_remark(self, text: str) -> "OrderConfirmPage":
        """
        填写订单备注（企业专区专用字段）

        Args:
            text: 备注文本

        Returns:
            self（支持链式调用）
        """
        logger.info(f"填写备注: {text}")
        self.page.locator("textarea").click()
        self.page.locator("textarea").fill(text)
        return self

    def fill_enterprise_zone_order(self, remark: str = "") -> "OrderConfirmPage":
        """
        企业专区一站式订单填写 + 提交

        依次执行: 先货后款 → 否(合同) → 控制端 → 备注 → 提交

        Args:
            remark: 备注文本

        Returns:
            self（支持链式调用）
        """
        logger.info("企业专区订单一站式填写")
        return (
            self.select_payment("先货后款")
            .select_contract("否")
            .select_source_end("控制端")
            .fill_remark(remark)
            .submit_order()
        )

    # ==========================================
    # 查看订单
    # ==========================================
    def view_order(self) -> Page | None:
        """
        点击"查看订单"——优先浏览器弹窗，回退页面内模态框

        Returns:
            弹窗 Page 对象（popup 模式），或 None（模态框模式）
        """
        logger.info("点击查看订单")

        # 优先 browser popup
        try:
            with self.page.expect_popup(timeout=5000) as page_info:
                self.page.get_by_role("button", name="查看订单").click()
            order_page = page_info.value
            logger.info("查看订单（popup 模式）")
            return order_page
        except Exception:
            # 回退页面内模态框
            self.page.get_by_role("button", name="查看订单").click()
            self.page.wait_for_timeout(2000)
            logger.info("查看订单（模态框模式）")
            return None
