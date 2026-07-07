"""
QuotationPage - 报价单页面对象

继承 BasePage，封装报价单详情页操作：
- 上传附件
- 提交报价单
- 勾选自动生成C4合同
- 产品选配
- 确认提交
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class QuotationPage(BasePage):
    """
    报价单详情页面对象

    在购物车点击「查看报价单」后进入此页面，处理报价单提交流程。

    用法:
        quotation_page = QuotationPage(page)
        quotation_page.upload_attachment("file.xlsx").submit_quotation()
    """

    # ---------- 页面元素定位器 ----------
    UPLOAD_BTN_ALT = [
        "button:has-text('上传附件')",
        "text=上传附件",
    ]

    SUBMIT_QUOTATION_ALT = [
        "button:has-text('提交报价单')",
        "text=提交报价单",
    ]

    AUTO_CONTRACT_LABEL = "text=审批通过后自动生成C4合同"
    AUTO_CONTRACT_CHECKBOX_ALT = [
        "label:has-text('审批通过后自动生成C4合同') span",
        "[class*='checkbox']:has(+ label:has-text('C4合同'))",
    ]

    CONFIRM_BTN_ALT = [
        "button:has-text('确 定')",
        "text=确 定",
    ]

    PRODUCT_CONFIG_ALT = [
        "text=产品选配",
        "button:has-text('产品选配')",
        "a:has-text('产品选配')",
    ]

    ADD_PRODUCT_BTN_ALT = [
        "button:has-text('添加')",
        "button:has-text('添加商品')",
        "[class*='add']",
    ]

    CONFIRM_SUBMIT_ALT = [
        "text=确认提交",
        "button:has-text('确认提交')",
    ]

    def __init__(self, page: Page):
        super().__init__(page)

    # ==========================================
    # 上传附件
    # ==========================================
    def upload_attachment(self, file_path: str | Path) -> "QuotationPage":
        """
        上传附件

        Args:
            file_path: 文件路径（如 "渠道订单导入模版.xlsx"）

        Returns:
            self（支持链式调用）
        """
        logger.info(f"上传附件: {file_path}")
        # 等待第1个「上传附件」按钮变为可见且启用
        upload_btn = self.page.get_by_role("button", name="上传附件").first
        upload_btn.wait_for(state="visible", timeout=10000)
        self.page.wait_for_timeout(500)  # 等 disabled 解除
        # 通过 file_chooser 拦截文件对话框，匹配录制的 click + set_input_files 模式
        with self.page.expect_file_chooser() as fc_info:
            upload_btn.click()
        fc_info.value.set_files(file_path)
        self.page.wait_for_timeout(3000)
        logger.info("附件上传完成")
        return self

    # ==========================================
    # 提交报价单
    # ==========================================
    def submit_quotation(self) -> "QuotationPage":
        """
        点击「提交报价单」按钮

        Returns:
            self（支持链式调用）
        """
        logger.info("点击「提交报价单」")
        self.click_any(*self.SUBMIT_QUOTATION_ALT)
        # 显式等待：提交响应（正常 3s）
        self.page.wait_for_timeout(3000)
        return self

    # ==========================================
    # 勾选自动生成C4合同
    # ==========================================
    def check_auto_contract(self) -> "QuotationPage":
        """
        勾选「审批通过后自动生成C4合同」

        Returns:
            self（支持链式调用）
        """
        logger.info("勾选「审批通过后自动生成C4合同」")
        # 录制方式：先定位含 C4 合同文本的 label，再取其内部 .el-checkbox__input span
        checkbox = (
            self.page.locator("label")
            .filter(has_text=re.compile(r"^审批通过后自动生成C4合同$"))
            .locator("span.el-checkbox__input")
        )
        checkbox.wait_for(state="visible", timeout=5000)
        checkbox.click()
        logger.info("已勾选自动生成C4合同")
        return self

    # ==========================================
    # 确认弹窗
    # ==========================================
    def confirm_dialog(self, label: str | None = None) -> "QuotationPage":
        """
        点击弹窗中的「确 定」按钮（自动定位最后弹出的可见弹窗）

        Args:
            label: 弹窗 aria-label（如 "提示"），不传则取最后弹出的弹窗

        Returns:
            self（支持链式调用）
        """
        logger.info(f"点击确认弹窗「确 定」, label={label or 'auto-last'}")
        btn = None
        if label:
            # 精确定位指定弹窗
            try:
                dialog = self.page.get_by_label(label)
                btn = dialog.locator("button:has-text('确 定')")
                btn.wait_for(state="visible", timeout=5000)
            except Exception:
                logger.warning(f"通过 label={label} 定位弹窗失败，降级到 last")
        if not btn:
            # 兜底：取最后弹出的可见弹窗（最新弹窗即目标）
            btn = self.page.locator(
                ".el-dialog__wrapper:visible"
            ).last.locator("button:has-text('确 定')")
        btn.click(force=True)
        self.page.wait_for_timeout(3000)
        return self

    # ==========================================
    # 产品选配
    # ==========================================
    def click_product_config(self) -> "QuotationPage":
        """
        点击「产品选配」

        Returns:
            self（支持链式调用）
        """
        logger.info("点击「产品选配」")
        self.click_any(*self.PRODUCT_CONFIG_ALT)
        self.wait_for_network_idle()
        return self

    def add_product(self) -> "QuotationPage":
        """
        在产品选配页面中，点击添加商品按钮

        Returns:
            self（支持链式调用）
        """
        logger.info("点击添加商品按钮")
        # 显式等待：产品选配页面加载（正常 3s）
        self.page.wait_for_timeout(3000)
        # 点击第二个添加按钮（录制中使用 nth=1）
        for selector in self.ADD_PRODUCT_BTN_ALT:
            try:
                count = self.count(selector)
                if count >= 2:
                    self.locate(selector).nth(1).click()
                    logger.info("已点击添加商品按钮")
                    return self
            except Exception:
                continue
        logger.warning("未找到添加商品按钮")
        self.screenshot("WARN_add_product_btn")
        return self

    def confirm_submit(self) -> "QuotationPage":
        """
        点击「确认提交」按钮

        Returns:
            self（支持链式调用）
        """
        logger.info("点击「确认提交」")
        self.click_any(*self.CONFIRM_SUBMIT_ALT)
        # 显式等待：提交请求响应（正常 3s）
        self.page.wait_for_timeout(3000)
        return self

    # ==========================================
    # 完整流程便捷方法
    # ==========================================
    def complete_submission(self, attachment_path: str | Path) -> "QuotationPage":
        """
        一键完成报价单提交流程：
        上传附件 > 提交报价单 > 勾选C4合同 > 确认

        Args:
            attachment_path: 附件文件路径

        Returns:
            self
        """
        return (
            self.upload_attachment(attachment_path)
            .submit_quotation()
            .check_auto_contract()
            .confirm_dialog()
        )

    def complete_product_config(self) -> "QuotationPage":
        """
        一键完成产品选配流程：
        产品选配 > 添加产品 > 确认提交 > 提交报价单 > 确认

        Returns:
            self
        """
        return (
            self.click_product_config()
            .add_product()
            .confirm_submit()
            .submit_quotation()
            .confirm_dialog()
        )
