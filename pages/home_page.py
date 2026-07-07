"""
HomePage - 客户登录后的主页对象

客户登录成功后跳转的页面。
"""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class HomePage(BasePage):
    """客户主页页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)

    def close_tip(self) -> "HomePage":
        """关闭'我知道了'弹窗"""
        logger.info("关闭'我知道了'弹窗")
        try:
            self.get_by_role("button", name="我知道了").click(timeout=3000)
        except Exception:
            logger.debug("未找到'我知道了'弹窗")
        return self
