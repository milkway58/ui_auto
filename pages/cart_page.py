
"""
封装购物车操作：
- 选择第一个商品复选框
- 点击订单确认按钮，进入订单确认页

定位策略：优先 data-testid，复选框使用 :nth(0) 选择第一个
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

if TYPE_CHECKING:
    from pages.order_page import OrderPage

logger = get_logger(__name__)


class CartPage(BasePage):
    """
    购物车页面对象

    用法:
        cart_page = CartPage(page)
        order_page = cart_page.select_first_product().click_order_confirm()
    """

    # ---------- 页面元素定位器 ----------
    # 商品复选框列表（多选择器容错）
    PRODUCT_CHECKBOX_ALT = ["data-testid=product-checkbox", "[type='checkbox'][class*='product']", "[class*='checkbox']"]
    # 购物车 checkbox-group 内的复选框
    CHECKBOX_GROUP_ALT = ["[aria-label='checkbox-group'] label span", "[class*='checkbox-group'] label span"]
    # 订单确认按钮：多选择器容错
    ORDER_CONFIRM_ALT = ["data-testid=order-confirm-button", "text=订单确认", "[class*='order-confirm']"]
    # 购物车商品列表：多选择器容错
    CART_ITEM_ALT = ["data-testid=cart-item", "[class*='cart-item']"]
    # 购物车为空提示
    EMPTY_CART_MESSAGE = "text=购物车为空, text=暂无商品"
    # 全选复选框
    SELECT_ALL_ALT = ["data-testid=select-all-checkbox", "text=全选", "[class*='select-all']"]
    # 生成报价单按钮
    GENERATE_QUOTATION_ALT = ["button:has-text('生成报价单')", "text=生成报价单"]
    # 继续下单按钮
    CONTINUE_ORDER_ALT = ["button:has-text('继续下单')", "text=继续下单"]
    # 商机选择器
    OPPORTUNITY_INPUT_ALT = ["[placeholder='请选择']", "input[placeholder='请选择']"]
    # 查看报价单按钮
    VIEW_QUOTATION_ALT = ["button:has-text('查看报价单')", "text=查看报价单"]

    def __init__(self, page: Page):
        super().__init__(page)
        self._url = "/cart"

    # ==========================================
    # 商品选择
    # ==========================================
    def select_first_product(self) -> "CartPage":
        """
        勾选购物车中第一个商品复选框

        针对 Element UI 的 el-checkbox 组件，实际 DOM 中
        .el-checkbox__inner 是隐藏的原生 input，通过 click_first
        逐个尝试候选项来命中。
        """
        logger.info("勾选第一个商品复选框")
        self.click_first(
            ".el-checkbox__inner",
            ".el-checkbox",
            "label >> span",
            "label",
        )
        return self

    def select_all_products(self) -> "CartPage":
        """全选所有商品"""
        logger.info("全选所有商品")
        self.click_any(*self.SELECT_ALL_ALT)
        return self

    def assert_cart_not_empty(self) -> "CartPage":
        """断言购物车不为空"""
        logger.info("断言购物车不为空")
        if self.is_visible(self.EMPTY_CART_MESSAGE):
            raise AssertionError("购物车为空，无法继续下单")
        item_count = 0
        for selector in self.CART_ITEM_ALT:
            item_count = self.count(selector)
            if item_count > 0:
                break
        assert item_count > 0, "购物车中没有商品"
        logger.info(f"购物车中有 {item_count} 个商品")
        return self

    # ==========================================
    # 订单确认
    # ==========================================
    def click_order_confirm(self) -> "OrderPage":
        """
        点击订单确认按钮，进入订单确认页

        Returns:
            OrderPage: 订单确认页对象
        """
        from pages.order_page import OrderPage

        logger.info("点击订单确认按钮")
        # 先断言购物车不为空
        self.assert_cart_not_empty()

        # 使用多选择器容错点击
        self.click_any(*self.ORDER_CONFIRM_ALT)
        self.wait_for_network_idle()
        logger.info("已进入订单确认页")
        return OrderPage(self.page)

    # ==========================================
    # 销售下单：勾选商品 > 生成报价单 > 继续下单
    # ==========================================
    def select_product_by_group_checkbox(self, index: int = 1) -> "CartPage":
        """
        通过 checkbox-group 内的复选框选择商品

        Args:
            index: 复选框索引，0=全选，1=第一个商品

        Returns:
            self（支持链式调用）
        """
        logger.info(f"选择 checkbox-group 第 {index} 个复选框")
        for selector in self.CHECKBOX_GROUP_ALT:
            try:
                count = self.count(selector)
                if count > index:
                    self.locate(selector).nth(index).click()
                    logger.info(f"已选择第 {index} 个复选框（选择器: {selector}）")
                    return self
            except Exception:
                continue
        logger.warning("checkbox-group 复选框未找到")
        self.screenshot("WARN_checkbox_group_not_found")
        return self

    def generate_quotation(self) -> "CartPage":
        """
        点击「生成报价单」按钮

        Returns:
            self（支持链式调用）
        """
        logger.info("点击「生成报价单」")
        self.click_any(*self.GENERATE_QUOTATION_ALT)
        self.wait_for_network_idle()
        return self

    def continue_order(self) -> "CartPage":
        """
        点击「继续下单」按钮

        Returns:
            self（支持链式调用）
        """
        logger.info("点击「继续下单」")
        self.click_any(*self.CONTINUE_ORDER_ALT)
        self.wait_for_network_idle()
        return self

    def select_opportunity(self, name: str) -> "CartPage":
        """
        选择商机

        Args:
            name: 商机名称（如 "13501: 审批商机20260701-03"）

        Returns:
            self（支持链式调用）
        """
        logger.info(f"选择商机: {name}")
        # 点击商机选择器打开下拉
        for selector in self.OPPORTUNITY_INPUT_ALT:
            try:
                if self.is_visible(selector):
                    self.locate(selector).click()
                    break
            except Exception:
                continue
        self.page.wait_for_timeout(500)
        # 在下拉列表中选择对应商机
        self.locate(f"text={name}").click()
        self.page.wait_for_timeout(300)
        logger.info(f"已选择商机: {name}")
        return self

    def confirm_info_form(self) -> "CartPage":
        """
        点击信息填写弹窗中的「确 定」按钮

        Returns:
            self（支持链式调用）
        """
        logger.info("点击信息填写确认按钮")
        self.click("text=确 定")
        self.page.wait_for_timeout(500)
        return self

    def click_view_quotation(self) -> "Page":
        """
        点击「查看报价单」按钮，打开报价单详情页（新窗口 popup）

        Returns:
            Page: 报价单详情页的 Page 对象
        """
        logger.info("点击「查看报价单」，等待新窗口弹出...")
        with self.page.expect_popup() as popup_info:
            self.click_any(*self.VIEW_QUOTATION_ALT)
        quotation_page = popup_info.value
        logger.info(f"报价单新窗口已打开: {quotation_page.url}")
        return quotation_page
