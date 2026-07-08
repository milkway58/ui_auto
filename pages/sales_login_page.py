"""
SalesLoginPage - 销售角色登录页面对象

继承 BasePage，封装销售角色登录逻辑。
登录成功后返回 HomePage，实现页面流转。

URL: https://zjtest.gyuncai.com/mall/view/buyerLogin
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Page

from config.settings import settings
from pages.base_page import BasePage
from utils.logger import get_logger

if TYPE_CHECKING:
    from pages.home_page import HomePage

logger = get_logger(__name__)


class SalesLoginPage(BasePage):
    """
    销售角色登录页面对象

    用法:
        login_page = SalesLoginPage(page)
        home_page = login_page.open().sales_login()
    """

    # 完整URL，避免依赖BASE_URL被.env还原影响
    SALES_URL = "https://zjtest.gyuncai.com/mall/view/buyerLogin"

    USERNAME_INPUT_ALT = [
        "input[placeholder='请输入您的手机号码']",
        "input[placeholder*='手机号码']",
        "input[placeholder*='用户名']",
        "input[placeholder*='账号']",
        "input[type='tel']",
        "input[type='text']",
    ]

    PASSWORD_INPUT_ALT = [
        "input[placeholder='登录密码']",
        "input[placeholder*='密码']",
        "input[type='password']",
    ]

    LOGIN_BUTTON_ALT = [
        "button:has-text('立即登录')",
        "button:has-text('登录')",
        "text=立即登录",
    ]

    FIRST_LOGIN_DIALOG_BTN = "button:has-text('我知道了')"

    SALES_HOME_INDICATOR_ALT = [
        "text=徐滋惟",
        "text=您好！",
        "text=全部产品分类",
        "[class*='home']",
        "[class*='welcome']",
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        self._url = self.SALES_URL

    def open(self) -> "SalesLoginPage":
        """打开销售登录页，等待登录表单可见"""
        logger.info("打开销售登录页")
        self.navigate(self._url or self.SALES_URL)
        self.wait_for_any_visible(*self.USERNAME_INPUT_ALT, timeout=3000)
        return self

    def sales_login(
        self,
        username: str | None = None,
        password: str | None = None,
    ) -> "HomePage":
        """
        销售角色登录流程

        Args:
            username: 销售用户名（为 None 时从 settings 读取）
            password: 销售密码（为 None 时从 settings 读取）

        Returns:
            HomePage: 登录成功后的主页对象
        """
        from pages.home_page import HomePage

        if username is None or password is None:
            creds = settings.get_credentials("sales")
            username = username or creds["username"]
            password = password or creds["password"]

        logger.info(f"销售登录，用户: {username}")

        # 1. 等待账号输入框加载
        logger.info("步骤1: 等待账号输入框加载")
        self.wait_for_any_visible(*self.USERNAME_INPUT_ALT, timeout=3000)

        # 2. 输入用户名
        logger.info(f"步骤2: 输入用户名: {username}")
        self.fill_any(*self.USERNAME_INPUT_ALT, text=username)

        # 3. 输入密码
        logger.info("步骤3: 输入密码")
        self.fill_any(*self.PASSWORD_INPUT_ALT, text=password)

        # 4. 点击登录按钮
        logger.info("步骤4: 点击登录")
        self.click_any(*self.LOGIN_BUTTON_ALT, timeout=3000)

        logger.info("登录请求已提交，等待页面响应...")
        # 等待首页标识元素可见（替代硬编码 3s）
        for selector in self.SALES_HOME_INDICATOR_ALT[:2]:
            try:
                self.wait_for_visible(selector, timeout=5000)
                break
            except Exception:
                continue
        # 兜底等待确保 Vue Router 完成跳转
        self.page.wait_for_timeout(1000)

        # 5. 关闭首次弹窗
        try:
            logger.info("步骤5: 检查是否需要关闭首次登录弹窗")
            self.wait_for_visible(self.FIRST_LOGIN_DIALOG_BTN, timeout=3000)
            btn = self.locate(self.FIRST_LOGIN_DIALOG_BTN)
            btn.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true }))")
            logger.info("[OK] 已关闭首次登录弹窗（JS dispatchEvent）")
        except Exception as e:
            logger.info(f"未找到首次登录弹窗，跳过。原因: {e}")

        # 6. 断言登录成功
        logger.info("步骤6: 断言登录成功...")
        self.assert_login_success(timeout=1500)

        logger.info("[SUCCESS] 销售登录成功，返回 HomePage")
        return HomePage(self.page)

    def assert_login_success(self, timeout: int = 3000) -> "SalesLoginPage":
        """断言登录成功（销售首页标识元素可见）"""
        logger.info("断言销售登录成功")
        for selector in self.SALES_HOME_INDICATOR_ALT:
            try:
                self.wait_for_visible(selector, timeout=timeout)
                logger.info(f"登录成功断言通过（匹配: {selector}）")
                return self
            except Exception:
                continue
        logger.error("登录成功断言失败：未找到销售首页标识元素")
        self.screenshot("FAIL_sales_login_assert")
        raise AssertionError("销售登录未成功，请检查凭据或页面跳转逻辑")
