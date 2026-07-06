"""
快速登录测试

验证客户登录流程是否能正常工作。
"""

import pytest


class TestQuickLogin:
    """快速登录测试"""

    def test_customer_login(self, page):
        """测试客户登录流程"""
        from pages.customer_login_page import CustomerLoginPage
        from pages.home_page import HomePage

        print("\n" + "="*50)
        print("开始测试客户登录流程")
        print("="*50)

        # 1. 打开登录页
        login_page = CustomerLoginPage(page)
        login_page.open()
        print("✓ 1. 登录页已打开")

        # 2. 执行登录
        home_page = login_page.customer_login()
        print("✓ 2. 登录成功")

        # 3. 断言在首页
        home_page.assert_on_home_page()
        print("✓ 3. 确认在客户首页")

        print("\n" + "="*50)
        print("✅ 客户登录测试通过！")
        print("="*50)

        return home_page


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
