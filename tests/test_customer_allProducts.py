"""
客户全部产品专区下单流程测试（Codegen 录制版）

流程:
1. 客户登录 (18501375833 / 123qwe) → 关闭"我知道了"弹窗
2. 首页 → 全部产品 → new营销专区12
3. 点击产品 → 产品详情 popup
4. 数量 dblclick +1 → 立即加购 → 购物车 popup
5. 勾选商品 → 订单确认 → 继续下单
6. 订单确认页填写 → 提交 → 断言"生成订单成功"
"""

import re
import pytest
from datetime import datetime

from pages.cart_page import CartPage
from pages.order_confirm_page import OrderConfirmPage


@pytest.mark.customer
@pytest.mark.order(2)
def test_customer_all_products_order(page):
    """客户全部产品专区下单全流程（Codegen 录制 selector，不上 POM）"""

    page.goto("https://zjtest.gyuncai.com/mall/view/login")
    page.get_by_text("密码登录").click()
    page.get_by_placeholder("请输入您的手机号码").click()
    page.get_by_placeholder("请输入您的手机号码").fill("18501375833")
    page.get_by_placeholder("登录密码").click()
    page.get_by_placeholder("登录密码").fill("123qwe")
    page.get_by_role("button", name="立即登录").click()
    page.get_by_role("button", name="我知道了").click()
    page.locator("div:nth-child(23) > .item > .item_img_box > .name_box > .text > .el-button").click()
    page.get_by_text("全部产品").first.click()
    page.get_by_role("tab", name="new营销专区12").click()
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    page.wait_for_timeout(2000)

    with page.expect_popup() as page1_info:
        page.get_by_label("new营销专区12").get_by_role("img").nth(1).click()
    page1 = page1_info.value
    page1.get_by_role("button", name="").first.dblclick()
    page1.get_by_role("button", name="立即加购").click()

    with page1.expect_popup() as page2_info:
        page1.locator("div").filter(has_text=re.compile(r"^购物车$")).click()
    page2 = page2_info.value

    cart_page = CartPage(page2)
    cart_page.select_first_product()
    page2.get_by_text("订单确认").click()
    page2.get_by_role("button", name="继续下单").click()

    order_confirm = OrderConfirmPage(page2)
    order_confirm.select_payment("先货后款") \
                 .select_contract("否") \
                 .select_invoice("明细") \
                 .fill_remark(f"全部产品专区UI自动化{datetime.now().strftime('%Y-%m-%d')}") \
                 .submit_order()
    order_confirm.view_order()
