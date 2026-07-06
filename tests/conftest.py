"""
测试级 Pytest Fixtures

职责：
1. 提供页面对象实例（LoginPage / CustomerLoginPage 等）
2. 提供多角色已登录会话（运营/销售/客户）
3. 提供测试数据加载 fixture

业务角色说明：
    operation - 运营人员（管理商品、订单、营销活动）
    sales     - 销售人员（管理客户、报价、合同）
    customer  - 客户（浏览商品、下单、查看订单）
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pages.customer_login_page import CustomerLoginPage
from data.data_loader import load_yaml, load_users_by_role
from utils.logger import get_logger

if TYPE_CHECKING:
    from pages.home_page import HomePage

logger = get_logger(__name__)


@pytest.fixture
def customer_home_session(page) -> "HomePage":
    """
    客户角色已登录会话（使用 CustomerLoginPage）

    登录成功后返回 HomePage，可直接用于客户下单流程测试。

    Returns:
        HomePage: 客户主页对象（已登录状态）
    """
    from pages.home_page import HomePage

    logger.info("创建客户登录会话（CustomerLoginPage）")
    login_page = CustomerLoginPage(page)

    # 从 .env 读取客户账号，如果有多个公司需要指定公司名称
    # 公司名称可以通过环境变量 CUSTOMER_COMPANY_NAME 配置
    import os
    company_name = os.getenv("CUSTOMER_COMPANY_NAME", "上海燃气崇明有限公司")

    home_page = login_page.open().customer_login(company_name=company_name)
    home_page.assert_on_home_page()
    logger.info("客户登录会话已建立，当前在客户主页")
    return home_page


@pytest.fixture(scope="session")
def test_config():
    """加载测试配置数据"""
    try:
        return load_yaml("test_config.yaml")
    except FileNotFoundError:
        return {}


@pytest.fixture
def users_data():
    """加载全部用户测试数据"""
    return load_yaml("users.yaml")


@pytest.fixture
def operation_users():
    """运营角色用户数据"""
    return load_users_by_role("operation")


@pytest.fixture
def sales_users():
    """销售角色用户数据"""
    return load_users_by_role("sales")


@pytest.fixture
def customer_users():
    """客户角色用户数据"""
    return load_users_by_role("customer")
