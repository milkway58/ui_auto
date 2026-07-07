
"""封装购物车操作。区分销售员与客户角色：

- **CartPage**（基类）：共享的商品选择方法 + 定位器常量
- **CustomerCartPage**（客户）：选商品 → 订单确认 → OrderPage
- **SalesCartPage**（销售）：选商品 → 生成报价单 → 选商机 → 查看报价单

定位策略：优先 data-testid，复选框使用 :nth(0) 选择第一个
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

if TYPE_CHECKING:
    from pages.order_page import OrderPage

logger = get_logger(__name__)


class CartPage(BasePage):
    """购物车基类 — 提供共享的商品选择方法和定位器常量。不应直接实例化，请使用 CustomerCartPage 或 SalesCartPage。"""

    # ---------- 页面元素定位器 ----------
    PRODUCT_CHECKBOX_ALT = ["data-testid=product-checkbox", "[type='checkbox'][class*='product']", "[class*='checkbox']"]
    CHECKBOX_GROUP_ALT = ["[aria-label='checkbox-group'] label span", "[class*='checkbox-group'] label span"]
    ORDER_CONFIRM_ALT = ["data-testid=order-confirm-button", "text=订单确认", "[class*='order-confirm']"]
    CART_ITEM_ALT = ["data-testid=cart-item", "[class*='cart-item']"]
    EMPTY_CART_MESSAGE = "text=购物车为空, text=暂无商品"
    SELECT_ALL_ALT = ["data-testid=select-all-checkbox", "text=全选", "[class*='select-all']"]
    GENERATE_QUOTATION_ALT = ["button:has-text('生成报价单')", "text=生成报价单"]
    CONTINUE_ORDER_ALT = ["button:has-text('继续下单')", "text=继续下单"]
    OPPORTUNITY_INPUT_ALT = [
        ".el-select input[type='text']",
        ".el-select",
        "input[placeholder*='请选择']",
        "[placeholder='请选择']",
        "input[placeholder='请选择']",
    ]
    VIEW_QUOTATION_ALT = [
        "button:has-text('查看报价单')",
        "[role='button']:has-text('查看报价单')",
        "text=查看报价单",
        "a:has-text('查看报价单')",
        "[class*='quotation']",
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        self._url = "/cart"

    # ==========================================
    # 商品选择（客户 & 销售共用）
    # ==========================================
    def select_first_product(self) -> "CartPage":
        """勾选购物车中第一个商品复选框"""
        logger.info("勾选第一个商品复选框")
        self.click_first(
            ".el-checkbox__inner",
            ".el-checkbox",
            "label >> span",
            "label",
        )
        self.page.wait_for_timeout(300)
        self.scroll_to_bottom()
        self.page.wait_for_timeout(300)
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


class CustomerCartPage(CartPage):
    """
    客户购物车页面对象

    用法:
        cart_page = CustomerCartPage(page)
        order_page = cart_page.select_first_product().click_order_confirm()
    """

    def select_first_product(self) -> "CustomerCartPage":
        """勾选购物车中第一个商品复选框"""
        return cast("CustomerCartPage", super().select_first_product())

    # ==========================================
    # 客户：订单确认
    # ==========================================
    def click_order_confirm(self) -> "OrderPage":
        """点击订单确认按钮，进入订单确认页。Returns: OrderPage"""
        from pages.order_page import OrderPage

        logger.info("点击订单确认按钮")
        self.assert_cart_not_empty()
        self.click_any(*self.ORDER_CONFIRM_ALT)
        self.wait_for_network_idle()
        logger.info("已进入订单确认页")
        return OrderPage(self.page)


class SalesCartPage(CartPage):
    """
    销售购物车页面对象

    用法:
        cart_page = SalesCartPage(page)
        (cart_page
         .select_first_product()
         .generate_quotation()
         .continue_order()
         .select_opportunity("商机名称")
         .confirm_info_form())
        quotation_page_obj = cart_page.click_view_quotation()
    """

    def select_first_product(self) -> "SalesCartPage":
        """勾选购物车中第一个商品复选框"""
        return cast("SalesCartPage", super().select_first_product())

    # ==========================================
    # 销售：勾选商品 > 生成报价单 > 继续下单
    # ==========================================
    def select_product_by_group_checkbox(self, index: int = 1) -> "SalesCartPage":
        """通过 checkbox-group 内的复选框选择商品。index: 0=全选，1=第一个商品"""
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

    def generate_quotation(self) -> "SalesCartPage":
        """点击「生成报价单」按钮"""
        logger.info("点击「生成报价单」")
        self.click_any(*self.GENERATE_QUOTATION_ALT)
        self.wait_for_network_idle()
        return self

    def continue_order(self) -> "SalesCartPage":
        """点击「继续下单」按钮"""
        logger.info("点击「继续下单」")
        self.click_any(*self.CONTINUE_ORDER_ALT)
        self.wait_for_network_idle()
        self.page.wait_for_timeout(3000)
        return self

    def select_opportunity(self, opportunity_name: str) -> "SalesCartPage":
        """选择商机并确认信息填写弹窗"""
        logger.info(f"选择商机: {opportunity_name}")
        self.page.wait_for_timeout(2000)

        # 打开下拉框（链末尾 .first 避开 strict mode 多元素匹配）
        select = (
            self.page.get_by_placeholder("请选择")
            .or_(self.page.locator(".el-select:visible"))
            .or_(self.page.locator(".el-select__caret"))
            .first
        )
        select.wait_for(state="visible", timeout=5000)
        select.click()
        self.page.wait_for_timeout(1000)

        # 在下拉选项中查找商机
        item = (
            self.page.locator(".el-select-dropdown__item:visible")
            .filter(has_text=opportunity_name)
            .first
        )
        item.wait_for(state="visible", timeout=5000)
        item.click()
        self.page.wait_for_timeout(1000)

        logger.info(f"商机已选择: {opportunity_name}")
        return self.confirm_info_form()

    def confirm_info_form(self) -> "SalesCartPage":
        """点击信息填写弹窗中的「确定」按钮"""
        logger.info("点击信息填写确认按钮")
        self.page.get_by_label("信息填写").get_by_text("确 定").click()
        logger.info("信息填写弹窗已确认")
        self.page.wait_for_timeout(3000)
        return self

    def click_view_quotation(self) -> "Page":
        """点击「查看报价单」按钮，打开报价单详情页（新窗口 popup）。Returns: 报价单详情页的 Page 对象"""
        logger.info("点击「查看报价单」，等待新窗口弹出...")
        with self.page.expect_popup() as popup_info:
            self.page.get_by_role("button", name="查看报价单").click()
        quotation_page = popup_info.value
        logger.info(f"报价单新窗口已打开: {quotation_page.url}")
        return quotation_page
