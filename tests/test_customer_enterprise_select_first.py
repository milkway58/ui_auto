"""
客户企业专区下单流程测试（验证 select_first_product 方法）

流程:
1. 客户登录 (18501375833 / 123qwe) → 关闭"我知道了"弹窗
2. 首页 → 企业专区 popup → 搜索"外购硬件"
3. 点击"外购硬件生态物料"→ 产品详情 popup
4. 数量+2 → 立即加购 → 购物车 popup
5. CartPage.select_first_product() 勾选商品 → 订单确认 → 继续下单
6. 订单确认页填写 → 提交 → 断言"生成订单成功"
"""

import pytest
from datetime import datetime

from pages.customer_login_page import CustomerLoginPage
from pages.cart_page import CartPage
from pages.enterprise_zone_page import EnterpriseZonePage
from pages.product_detail_page import ProductDetailPage
from pages.order_confirm_page import OrderConfirmPage


@pytest.mark.customer
@pytest.mark.order(4)
def test_customer_enterprise_select_first(page):
    """客户企业专区下单全流程（使用 CartPage.select_first_product）"""

    # ====== 1. 客户登录 ======
    page.goto("https://zjtest.gyuncai.com/mall/view/login")
    login_page = CustomerLoginPage(page)
    login_page.customer_login(
        username="18501375833",
        password="123qwe",
        company_name="上海燃气崇明有限公司",
    )

    # ====== 2. 进入企业专区，搜索产品 ======
    enter_zone = EnterpriseZonePage.open_from_home(page)
    enter_zone.search_product("外购硬件")

    # ====== 3. 进入产品详情页（新 popup） ======
    product_popup = enter_zone.click_product("外购硬件生态物料")
    product_detail = ProductDetailPage(product_popup)

    # ====== 4. 数量+2 → 立即加购 ======
    product_detail.increase_quantity(2).click_add_to_cart()

    # ====== 5. 购物车 → CartPage.select_first_product() 勾选 ======
    cart_popup = ProductDetailPage.go_to_cart(product_detail.page)
    CartPage(cart_popup).select_first_product()
    cart_popup.get_by_text("订单确认").click()
    cart_popup.get_by_role("button", name="继续下单").click()

    # ====== 6. 订单确认页填写 → 提交 ======
    order = OrderConfirmPage(cart_popup)
    order.fill_enterprise_zone_order(f"企业专区UI自动化{datetime.now().strftime('%Y-%m-%d')}")
