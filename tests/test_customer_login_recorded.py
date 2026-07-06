"""
客户登录流程测试用例（Codegen 录制版）

基于 playwright codegen 录制的实际操作步骤，
封装到 CustomerLoginPage POM 后生成。
录制时间：2025-07-03
操作角色：客户（customer）
"""

import pytest

from pages.customer_login_page import CustomerLoginPage
from pages.home_page import HomePage
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.customer
@pytest.mark.login
@pytest.mark.smoke
class TestCustomerLoginRecorded:
    """客户登录录制流程测试"""

    @pytest.mark.order(1)
    def test_customer_login_from_portal(self, page):
        """
        客户从 Portal 门户 → 密码登录 → 选择公司 → 完成登录

        对应录制步骤：
        1. Portal 页面点击"登录"
        2. 切换到"密码登录"
        3. 输入手机号 + 密码
        4. 点击"立即登录"
        5. 关闭"我知道了"首次弹窗
        6. 选择公司"上海燃气崇明有限公司"
        7. 断言登录成功
        """
        logger.info("========== 客户登录录制版测试 ==========")

        login_page = CustomerLoginPage(page)
        home_page: HomePage = login_page.open().customer_login()

        home_page.assert_on_home_page()
        logger.info("✓ 客户登录录制流程通过")

    @pytest.mark.order(2)
    def test_assert_company_name_visible(self, page):
        """断言登录后公司名称可见（录制中 Assert visibility）"""
        logger.info("========== 断言公司名称可见 ==========")

        login_page = CustomerLoginPage(page)
        home_page: HomePage = login_page.open().customer_login()
        home_page.assert_on_home_page()

        # 对应于录制中：Assert visibility: text="上海燃气崇明有限公司"
        home_page.assert_contains_text("text=您好！上海燃气崇明有限公司", "上海燃气崇明有限公司")
        logger.info("✓ 公司名称断言通过")
