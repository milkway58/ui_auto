"""HomePage - 客户/销售首页页面对象"""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)

# 首页特征元素选择器（容错多匹配）
HOME_INDICATORS: list[str] = [
    "text=全部产品分类",
    "text=全部产品",
    "text=您好！",
    ".home-page",
]


class HomePage(BasePage):
    """客户/销售首页"""

    def __init__(self, page: Page):
        super().__init__(page)

    def assert_on_home_page(self) -> "HomePage":
        """断言当前页面为首页（登录成功验证）"""
        logger.info("断言首页加载")
        for indicator in HOME_INDICATORS:
            try:
                self.wait_for_visible(indicator, timeout=5000)
                logger.info(f"首页断言通过（匹配: {indicator}）")
                return self
            except Exception:
                continue
        raise AssertionError(
            f"首页断言失败：未找到任何特征元素 {HOME_INDICATORS}"
        )
