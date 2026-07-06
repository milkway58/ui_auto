"""
销售登录流程测试用例

URL: https://zjtest.gyuncai.com/mall/view/buyerLogin
账号: qinxd / 123qwe
"""
import pytest

from pages.sales_login_page import SalesLoginPage
from pages.home_page import HomePage
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.sales
@pytest.mark.login
@pytest.mark.smoke
class TestSalesLogin:
    """销售登录流程测试"""

    @pytest.mark.order(1)
    def test_sales_login_success(self, page):
        """
        销售角色登录成功流程

        步骤:
        1. 打开销售登录页 /mall/view/buyerLogin
        2. 输入用户名 + 密码
        3. 点击登录
        4. 关闭首次弹窗（如有）
        5. 断言登录成功
        """
        logger.info("========== 销售登录测试 ==========")

        login_page = SalesLoginPage(page)
        home_page: HomePage = login_page.open().sales_login(
            username="qinxd",
            password="123qwe",
        )

        home_page.assert_on_home_page()
        logger.info("✓ 销售登录流程通过")
