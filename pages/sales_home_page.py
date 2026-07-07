"""
SalesHomePage - 销售角色首页页面对象

继承 BasePage，封装销售首页操作：
- 搜索产品
- 加入购物车
- 打开购物车页面（处理 popup 新窗口）
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.logger import get_logger

if TYPE_CHECKING:
    from pages.cart_page import SalesCartPage

logger = get_logger(__name__)


class SalesHomePage(BasePage):
    """
    销售角色首页页面对象

    登录成功后进入此页面，提供搜索和购物车入口。

    用法:
        sales_home = SalesHomePage(page)
        sales_cart_page = sales_home.search_product("10004188").add_to_cart().open_cart()
    """

    # ---------- 页面元素定位器 ----------
    SEARCH_INPUT_ALT = [
        "input[placeholder='请输入搜索关键字']",
        "input[placeholder*='搜索']",
        "[class*='search'] input",
        "input[type='search']",
    ]

    SEARCH_BTN_ALT = [
        ".input_btn > .svg-icon > use",
        ".input_btn",
        "[class*='search-btn']",
        "button:has-text('搜索')",
    ]

    ADD_TO_CART_ALT = [
        "span.linear_btn:has-text('加入购物车'):visible",
        ".el-table__body span.linear_btn:has-text('加入购物车'):visible",
        "text=加入购物车",
        "button:has-text('加入购物车')",
        "[class*='add-cart']",
    ]

    CART_LINK_ALT = [
        "text=购物车",
        "a:has-text('购物车')",
        "[class*='cart']",
    ]

    def __init__(self, page: Page):
        super().__init__(page)

    # ==========================================
    # 搜索产品
    # ==========================================
    def search_product(self, keyword: str) -> "SalesHomePage":
        """
        搜索产品

        Args:
            keyword: 搜索关键字（如产品编码 "10004188"）

        Returns:
            self（支持链式调用）
        """
        logger.info(f"搜索产品: {keyword}")
        # 等待搜索输入框可见
        self.wait_for_any_visible(*self.SEARCH_INPUT_ALT, timeout=1000)
        # 输入搜索关键字
        self.fill_any(*self.SEARCH_INPUT_ALT, text=keyword)
        # 点击搜索按钮
        self.click_any(*self.SEARCH_BTN_ALT)
        # 尝试等待 networkidle，但页面可能有长轮询，超时也不阻断
        self.wait_for_network_idle()
        # 关键：显式等待搜索结果中物料编码出现
        self._wait_for_search_result(keyword)
        logger.info(f"搜索完成: {keyword}")
        return self

    def _wait_for_search_result(self, keyword: str) -> None:
        """等待搜索结果表格中物料编码可见"""
        logger.info(f"等待搜索结果物料编码: {keyword}")
        try:
            expect(self.page.locator(f"text={keyword}").first).to_be_visible(timeout=2000)
            logger.info(f"物料编码 {keyword} 已出现")
        except Exception as e:
            logger.warning(f"等待物料编码出现超时或失败: {e}")
            self.screenshot("WARN_search_result_not_found")

    # ==========================================
    # 加入购物车
    # ==========================================
    def add_to_cart(self, index: int = 1) -> "SalesHomePage":
        """
        点击「加入购物车」按钮

        Args:
            index: 按钮序号（从1开始），默认第1个

        Returns:
            self（支持链式调用）
        """
        logger.info(f"点击第 {index} 个「加入购物车」按钮")

        # 优先使用 span.linear_btn 精确定位，并限定 :visible 避免命中隐藏克隆 DOM
        target = "span.linear_btn:has-text('加入购物车'):visible"
        try:
            count = self.count(target)
            if count >= index:
                btn = self.locate(target).nth(index - 1)
                btn.scroll_into_view_if_needed()
                btn.click(force=True)
                logger.info("已加入购物车")
                return self
        except Exception:
            pass

        # 备用：直接用 get_by_text
        try:
            btn = self.page.get_by_text("加入购物车").nth(index - 1)
            btn.scroll_into_view_if_needed()
            btn.click(force=True)
            logger.info("已加入购物车（get_by_text 备用）")
            return self
        except Exception as e:
            logger.error(f"点击加入购物车失败: {e}")
            self.screenshot("FAIL_add_to_cart")
            raise

    # ==========================================
    # 打开购物车（弹出新窗口）
    # ==========================================
    def open_cart(self) -> "SalesCartPage":
        """
        点击购物车链接，打开购物车页面（新窗口 popup）

        Returns:
            SalesCartPage: 购物车页面对象（基于 popup 窗口的 page）
        """
        from pages.cart_page import SalesCartPage

        logger.info("点击购物车链接，等待新窗口弹出...")
        with self.page.expect_popup() as popup_info:
            self.locate("text=购物车").first.click()

        cart_page_obj = popup_info.value
        logger.info(f"购物车新窗口已打开: {cart_page_obj.url}")
        return SalesCartPage(cart_page_obj)

    def assert_search_results_visible(self) -> "SalesHomePage":
        """断言搜索结果显示（确认表格中至少有一个加入购物车按钮可见）"""
        logger.info("断言搜索结果可见")
        # 用 span.linear_btn 精确匹配，并限定 :visible 避免命中隐藏克隆 DOM
        expect(self.locate("span.linear_btn:has-text('加入购物车'):visible").first).to_be_visible(timeout=3000)
        return self
