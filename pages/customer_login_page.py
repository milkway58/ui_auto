"""
CustomerLoginPage - 客户专属登录页面对象

继承 BasePage，封装客户角色登录逻辑。
登录成功后返回 HomePage，实现页面流转。

定位策略：优先 data-testid，支持 text= 文字定位。
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


class CustomerLoginPage(BasePage):
    """
    客户专属登录页面对象

    与通用 LoginPage 的区别：
    1. 登录成功后返回 HomePage（页面流转）
    2. 默认从 settings 读取客户凭据（无需每次传入）
    3. 增加客户角色专属断言（跳转客户首页）

    用法:
        login_page = CustomerLoginPage(page)
        home_page = login_page.open().customer_login()
    """

    # ---------- 页面元素定位器（Codegen 录制 + 实际验证后优化） ----------
    # 密码登录切换标签（Vue 组件：login_way_box 内第2个 <p> 子元素）
    PASSWORD_LOGIN_TAB = ".login_way_box > p:last-child"

    # 用户名输入框
    USERNAME_INPUT_ALT = [
        "input[placeholder='请输入您的手机号码']",
        "input[placeholder*='手机号码']",
        "input[placeholder*='用户名']",
        "input[type='tel']",
        "input[type='text']",
    ]

    # 密码输入框
    PASSWORD_INPUT_ALT = [
        "input[placeholder='登录密码']",
        "input[placeholder*='密码']",
        "input[type='password']",
    ]

    # 登录按钮
    LOGIN_BUTTON_ALT = [
        "button:has-text('立即登录')",
        "text=立即登录",
    ]

    # 错误提示信息
    ERROR_MESSAGE_ALT = [
        ".error-message",
        ".login-error",
        "[class*='error']",
    ]

    # 首次登录弹窗"我知道了"按钮
    FIRST_LOGIN_DIALOG_BTN = "button:has-text('我知道了')"

    # 公司列表弹框
    COMPANY_LIST_DIALOG = "text=公司列表"

    # 公司选择
    COMPANY_ITEM_ALT = [
        "text=上海燃气崇明有限公司",
    ]

    # 客户首页标识元素（登录成功后出现）
    CUSTOMER_HOME_INDICATOR_ALT = [
        "text=您好！上海燃气崇明有限公司",
    ]

    LOGOUT_BUTTON_ALT = [
        "data-testid=logout-button",
        "button:has-text('退出')",
        "button:has-text('注销')",
        ".logout-button",
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        # 客户登录地址: BASE_URL + "/login"
        # 完整URL: https://zjtest.gyuncai.com/mall/view/login
        self._url = "/login"

    # ==========================================
    # 页面导航
    # ==========================================
    def open(self) -> "CustomerLoginPage":
        """打开客户登录页，等待登录表单可见"""
        logger.info("打开客户登录页")
        self.navigate(self._url or "/login")
        # 等待登录表单出现
        self.wait_for_any_visible(*self.USERNAME_INPUT_ALT, timeout=2000)
        return self

    # ==========================================
    # 核心操作
    # ==========================================
    def customer_login(
        self,
        username: str | None = None,
        password: str | None = None,
        company_name: str | None = None,
    ) -> "HomePage":
        """
        客户专属登录流程（根据 test_customer_login.yaml 实际流程）

        凭据来源（按优先级）：
        1. 方法参数传入（最高优先级）
        2. settings.get_credentials("customer")（从 .env 读取）

        Args:
            username: 客户用户名（为 None 时从 settings 读取）
            password: 客户密码（为 None 时从 settings 读取）
            company_name: 公司名称（多公司用户需要选择，为 None 时从 .env 读取）

        Returns:
            HomePage: 登录成功后的主页对象
        """
        from pages.home_page import HomePage

        if username is None or password is None:
            creds = settings.get_credentials("customer")
            username = username or creds["username"]
            password = password or creds["password"]

        if company_name is None:
            import os
            company_name = os.getenv("CUSTOMER_COMPANY_NAME", "上海燃气崇明有限公司")

        logger.info(f"客户登录，用户: {username}, 公司: {company_name}")

        # 1. 切换密码登录（根据 YAML 第17-20行）
        try:
            logger.info("步骤1: 切换密码登录")
            # 先等待元素可见
            self.wait_for_visible(self.PASSWORD_LOGIN_TAB, timeout=3000)
            logger.info(f"找到密码登录切换按钮: {self.PASSWORD_LOGIN_TAB}")
            # 用 JS dispatchEvent 触发点击（绕过 Playwright 对 Vue @click 的拦截）
            tab = self.locate(self.PASSWORD_LOGIN_TAB)
            tab.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true }))")
            logger.info("[OK] 已点击密码登录切换按钮（JS dispatchEvent）")
            # 等待密码输入框出现（display:none 变为可见），确认切换生效
            self.page.wait_for_selector("input[type='password']", state="visible", timeout=5000)
            logger.info("[OK] 密码登录切换已生效（密码输入框可见）")
        except Exception as e:
            logger.warning(f"密码登录切换失败，原因: {e}")

        # 2. 等待账号输入框加载（根据 YAML 第22-25行）
        logger.info("步骤2: 等待账号输入框加载")
        self.wait_for_any_visible(*self.USERNAME_INPUT_ALT, timeout=3000)
        logger.info(f"[OK] 账号输入框已加载，使用的选择器: {self.USERNAME_INPUT_ALT}")

        # 3. 输入用户名（根据 YAML 第27-30行）
        logger.info(f"步骤3: 输入用户名: {username}")
        self.fill_any(*self.USERNAME_INPUT_ALT, text=username)
        logger.info(f"[OK] 已输入用户名: {username}")

        # 4. 输入密码（根据 YAML 第32-35行）
        logger.info("步骤4: 输入密码")
        self.fill_any(*self.PASSWORD_INPUT_ALT, text=password)
        logger.info("[OK] 已输入密码")

        # 5. 点击立即登录（根据 YAML 第37-40行）
        logger.info("步骤5: 点击立即登录")
        self.click_any(*self.LOGIN_BUTTON_ALT, timeout=3000)
        logger.info("[OK] 已点击立即登录按钮")

        logger.info("登录请求已提交，等待页面跳转...")
        self.page.wait_for_load_state("networkidle", timeout=10000)
        self.wait_for_visible("text=您好", timeout=5000)
        logger.info("首页标识元素已可见，准备处理弹窗")

        # 6. 关闭首次弹窗（根据 YAML 第42-45行）
        try:
            logger.info("步骤6: 检查是否需要关闭首次登录弹窗")
            self.wait_for_visible(self.FIRST_LOGIN_DIALOG_BTN, timeout=3000)
            logger.info(f"找到首次登录弹窗按钮: {self.FIRST_LOGIN_DIALOG_BTN}")
            # 用 JS dispatchEvent 触发点击（绕过 Playwright 对 Vue @click 的拦截）
            btn = self.locate(self.FIRST_LOGIN_DIALOG_BTN)
            btn.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true }))")
            logger.info("[OK] 已关闭首次登录弹窗（JS dispatchEvent）")
        except Exception as e:
            logger.info(f"未找到首次登录弹窗，跳过。原因: {e}")

        # 7. 等待公司列表弹框（根据 YAML 第47-50行）
        # 8. 选择公司（根据 YAML 第52-55行）
        if company_name:
            try:
                logger.info(f"步骤7-8: 等待公司列表弹框，准备选择公司: {company_name}")
                self.wait_for_visible(self.COMPANY_LIST_DIALOG, timeout=3000)
                logger.info(f"找到公司列表弹框: {self.COMPANY_LIST_DIALOG}")
                self.click(f"text={company_name}", timeout=3000)
                logger.info(f"[OK] 已选择公司: {company_name}")
            except Exception as e:
                logger.info(f"未找到公司列表弹框，跳过公司选择。原因: {e}")

        # 9. 断言登录成功（根据 YAML 第57-61行）
        logger.info("步骤9: 断言登录成功...")
        self.assert_login_success(timeout=1500)
        logger.info("[OK] 登录成功断言通过")

        logger.info("[SUCCESS] 登录成功，返回 HomePage")
        return HomePage(self.page)

    def assert_login_success(self, timeout: int = 3000) -> "CustomerLoginPage":
        """断言登录成功（客户首页标识元素可见）"""
        logger.info("断言客户登录成功")
        for selector in self.CUSTOMER_HOME_INDICATOR_ALT:
            try:
                self.wait_for_visible(selector, timeout=timeout)
                logger.info(f"登录成功断言通过（匹配: {selector}）")
                return self
            except Exception:
                continue
        logger.error("登录成功断言失败：未找到客户首页标识元素")
        self.screenshot("FAIL_login_success_assert")
        raise AssertionError("客户登录未成功，请检查凭据或页面跳转逻辑")

    def assert_login_failed(self, expected_error: str | None = None) -> "CustomerLoginPage":
        """断言登录失败"""
        logger.info(f"断言客户登录失败，预期错误: {expected_error}")
        # 等待任意一个错误提示元素可见
        self.wait_for_any_visible(*self.ERROR_MESSAGE_ALT, timeout=3000)
        if expected_error:
            # 尝试从多个可能的错误提示元素中获取文本
            for selector in self.ERROR_MESSAGE_ALT:
                try:
                    if self.is_visible(selector):
                        self.assert_contains_text(selector, expected_error)
                        break
                except Exception:
                    continue
        return self

    def get_error_message(self) -> str:
        """获取错误提示文本"""
        for selector in self.ERROR_MESSAGE_ALT:
            try:
                if self.is_visible(selector):
                    return self.get_text(selector)
            except Exception:
                continue
        return ""
