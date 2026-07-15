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

import re
from pathlib import Path
from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect

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
        expect(upload_btn).to_be_enabled(timeout=5000)
        with self.page.expect_file_chooser() as fc_info:
            upload_btn.click()
        fc_info.value.set_files(file_path)
        self.page.wait_for_timeout(300)
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
        self.page.wait_for_timeout(300)
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
        checkbox = (
            self.page.locator("label")
            .filter(has_text=re.compile(r"^审批通过后自动生成C4合同$"))
            .locator(".el-checkbox__inner")
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
        点击弹窗中的「确 定」按钮（方案A: footer primary + force）

        Args:
            label: 弹窗 aria-label（如 "提示"），不传则取最后一个「确 定」按钮

        Returns:
            self（支持链式调用）
        """
        logger.info(f"点击确认弹窗「确 定」, label={label or 'auto-last'}")

        # 定位弹框容器
        if label:
            dialog = self.page.get_by_label(label)
        else:
            dialog = self.page.locator(".el-dialog__wrapper:visible").last

        # 点击前断言弹框状态（标题含"提示" + "确定"按钮存在）
        self._assert_dialog_ready(dialog, context=label or "auto-last")

        # # 方案A: footer primary + force click 绕过 actionability 检测
        # btn = dialog.locator(".el-dialog__footer button.el-button--primary")
        # btn.wait_for(state="attached", timeout=5000)
        # btn.click(force=True)
        # logger.info("确认按钮已点击（方案A: footer primary + force）")


        # # 方案C: JS evaluate 强制触发（备选）
        btn = dialog.locator("button:has-text('确 定')")
        btn.evaluate("el => el.click()")
        logger.info("确认按钮已点击（方案C: JS click）")

        dialog.wait_for(state="hidden", timeout=10000)
        return self

    def _assert_dialog_ready(self, dialog, context: str = "") -> None:
        """
        断言弹框就绪：标题含"提示" + "确定"按钮已挂载

        Args:
            dialog: Playwright Locator for the dialog wrapper
            context: 描述信息，用于失败日志
        """
        ctx = f"[{context}]" if context else ""

        # 断言1: 标题含"提示"
        title_loc = dialog.locator(".el-dialog__title, .el-dialog__header")
        try:
            expect(title_loc.first).to_contain_text("提示", timeout=5000)
            logger.info(f"✓ 弹框断言通过: 标题「提示」存在 {ctx}")
        except Exception:
            title_html = title_loc.first.inner_html()[:300] if title_loc.count() > 0 else "NOT_FOUND"
            logger.error(f"✗ 弹框断言失败: 标题「提示」不存在 {ctx}\n"
                         f"  → DOM 诊断: {title_html}")
            raise AssertionError(
                f"弹框标题「提示」断言失败 [{context}]\n"
                f"  DOM: {title_html}"
            )

        # 断言2: "确定"按钮存在
        btn_loc = dialog.locator("button:has-text('确 定')")
        try:
            expect(btn_loc.first).to_be_attached(timeout=5000)
            logger.info(f"✓ 弹框断言通过: 「确定」按钮已挂载 {ctx}")
        except Exception:
            btn_count = btn_loc.count()
            wrapper_html = dialog.first.inner_html()[:500] if dialog.count() > 0 else "NOT_FOUND"
            logger.error(f"✗ 弹框断言失败: 「确定」按钮不存在 {ctx}\n"
                         f"  → 匹配按钮数: {btn_count}\n"
                         f"  → DOM 诊断: {wrapper_html}")
            raise AssertionError(
                f"弹框「确定」按钮断言失败 [{context}]\n"
                f"  匹配按钮数: {btn_count}\n"
                f"  DOM: {wrapper_html}"
            )

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
        self.page.wait_for_timeout(300)
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
