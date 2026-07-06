"""
EnterpriseZonePage - 企业专区页面对象

封装企业专区搜索、产品选择操作。
企业专区以 popup 窗口形式打开，需要处理 expect_popup 切换。

用法:
    enter_zone = EnterpriseZonePage.open_from_home(page)
    enter_zone.search_product("外购硬件")
    product_popup = enter_zone.click_product("外购硬件生态物料")
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class EnterpriseZonePage(BasePage):
    """企业专区页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)

    @staticmethod
    def open_from_home(home_page: Page) -> "EnterpriseZonePage":
        """
        从首页打开企业专区 popup

        流程:
        1. 页面滑动到 1/2 处
        2. 等待 2s 确保元素渲染完成
        3. 点击"企业专区"标签，通过 expect_popup 获取新窗口

        Args:
            home_page: 客户首页 Page 对象

        Returns:
            EnterpriseZonePage: 企业专区页面对象（popup 窗口）
        """
        logger.info("从首页打开企业专区")
        # 第一步：滑动到页面 1/2 处
        home_page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        home_page.wait_for_timeout(2000)
        # 第二步：点击"企业专区"打开 popup
        with home_page.expect_popup(timeout=8000) as page_info:
            home_page.get_by_text("企业专区").first.click()
        popup = page_info.value
        logger.info("企业专区 popup 已打开")
        return EnterpriseZonePage(popup)

    def search_product(self, keyword: str) -> "EnterpriseZonePage":
        """
        搜索产品关键字

        Args:
            keyword: 搜索关键字

        Returns:
            self（支持链式调用）
        """
        logger.info(f"搜索产品: {keyword}")
        self.page.get_by_placeholder("搜索名称关键字").click()
        self.page.get_by_placeholder("搜索名称关键字").fill(keyword)
        self.page.get_by_role("button", name="搜索").click()
        try:
            self.page.get_by_text(keyword).first.wait_for(state="visible", timeout=3000)
        except Exception:
            pass
        return self

    def click_product(self, product_name: str) -> Page:
        """
        点击产品名称，打开产品详情 popup

        Args:
            product_name: 产品名称（精确匹配）

        Returns:
            Page: 产品详情页的 popup Page 对象
        """
        logger.info(f"点击产品: {product_name}")
        with self.page.expect_popup(timeout=8000) as page_info:
            self.page.get_by_text(product_name, exact=True).click()
        popup = page_info.value
        logger.info(f"产品详情 popup 已打开: {product_name}")
        return popup
