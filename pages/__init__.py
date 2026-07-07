"""Pages 包初始化 - 统一导出所有页面对象"""

from pages.base_page import BasePage
from pages.customer_login_page import CustomerLoginPage
from pages.cart_page import CartPage, CustomerCartPage, SalesCartPage
from pages.order_confirm_page import OrderConfirmPage
from pages.enterprise_zone_page import EnterpriseZonePage
from pages.product_detail_page import ProductDetailPage
from pages.sales_login_page import SalesLoginPage
from pages.sales_home_page import SalesHomePage
from pages.quotation_page import QuotationPage

__all__ = [
    "BasePage",
    "CustomerLoginPage",
    "CartPage",
    "CustomerCartPage",
    "SalesCartPage",
    "OrderConfirmPage",
    "EnterpriseZonePage",
    "ProductDetailPage",
    "SalesLoginPage",
    "SalesHomePage",
    "QuotationPage",
]
