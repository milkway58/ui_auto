"""
ProductDetailPage - 产品详情页面对象

封装商品数量增减、立即加购、跳转购物车操作。
产品详情页以 popup 形式打开。

用法:
    detail = ProductDetailPage(popup_page)
    detail.increase_quantity(2).click_add_to_cart()
    customer_cart_page = ProductDetailPage.go_to_cart(detail.page)
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.cart_page import CustomerCartPage
from utils.logger import get_logger

logger = get_logger(__name__)


class ProductDetailPage(BasePage):
    """产品详情页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)

    def increase_quantity(self, times: int = 1) -> "ProductDetailPage":
        """
        点击数量+按钮指定次数

        Args:
            times: 点击次数（默认1次）

        Returns:
            self（支持链式调用）
        """
        logger.info(f"点击数量+按钮 {times} 次")
        for _ in range(times):
            self.page.get_by_role("button", name="").first.click()
        return self

    def click_add_to_cart(self) -> "ProductDetailPage":
        """
        点击"立即加购"按钮

        Returns:
            self（支持链式调用）
        """
        logger.info("点击立即加购")
        self.page.get_by_role("button", name="立即加购").click()
        return self

    @staticmethod
    def go_to_cart(page: Page) -> CustomerCartPage:
        """
        从当前 page 打开购物车 popup

        Args:
            page: 当前页面的 Page 对象

        Returns:
            CustomerCartPage: 购物车页面对象
        """
        logger.info("打开购物车")
        with page.expect_popup(timeout=8000) as page_info:
            page.locator("div").filter(has_text=re.compile(r"^购物车$")).click()
        cart_page = page_info.value
        logger.info("购物车 popup 已打开")
        return CustomerCartPage(cart_page)
