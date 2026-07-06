"""
基础框架验证测试

验证点：
1. 所有页面对象能正常导入
2. BasePage 的基础方法存在
3. 配置文件能正常加载
4. Fixtures 能正常工作的基础检查

使用方法：
    pytest test_framework_basic.py -v
"""

from playwright.sync_api import Page
import pytest

from config.settings import settings
from pages.base_page import BasePage
from pages.customer_login_page import CustomerLoginPage


class TestFrameworkBasic:
    """框架基础验证测试（不依赖实际测试环境）"""

    def test_imports(self):
        """验证所有模块能正常导入"""
        # 这些导入在文件顶部已经完成，如果不报错说明导入正常
        assert BasePage is not None
        assert CustomerLoginPage is not None
        assert settings is not None

    def test_settings_load(self):
        """验证配置文件能正常加载"""
        assert settings.ENV == "test"
        assert settings.BASE_URL is not None
        assert settings.TIMEOUT > 0

    def test_customer_login_page_instantiation(self, page: Page):
        """验证 CustomerLoginPage 能正常实例化"""
        login_page = CustomerLoginPage(page)
        assert login_page is not None
        assert login_page._url == "/login"

    def test_base_page_methods_exist(self, page: Page):
        """验证 BasePage 的基础方法存在"""
        base_page = BasePage(page)
        # 验证关键方法存在
        assert hasattr(base_page, 'navigate')  # 打开页面（不是 open）
        assert hasattr(base_page, 'fill')
        assert hasattr(base_page, 'click')
        assert hasattr(base_page, 'wait_for_visible')
        assert hasattr(base_page, 'assert_visible')
        assert hasattr(base_page, 'assert_contains_text')
        assert hasattr(base_page, 'screenshot')

    def test_settings_credentials(self):
        """验证多角色凭据配置能正常读取"""
        # 注意：这些凭据是从 .env 读取的，如果没有配置会报错
        try:
            op_creds = settings.get_credentials("operation")
            assert "username" in op_creds
            assert "password" in op_creds
        except Exception as e:
            pytest.skip(f"运营角色凭据未配置: {e}")

        try:
            sales_creds = settings.get_credentials("sales")
            assert "username" in sales_creds
            assert "password" in sales_creds
        except Exception as e:
            pytest.skip(f"销售角色凭据未配置: {e}")

        try:
            customer_creds = settings.get_credentials("customer")
            assert "username" in customer_creds
            assert "password" in customer_creds
        except Exception as e:
            pytest.skip(f"客户角色凭据未配置: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
