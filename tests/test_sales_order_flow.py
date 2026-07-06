"""
销售完整下单业务流程测试

覆盖流程：
1. 销售登录
2. 搜索产品并加入购物车
3. 购物车生成报价单
4. 选择商机继续下单
5. 报价单详情页上传附件并提交
6. 产品选配并确认提交

基于录制脚本优化，使用 POM 框架重构。
"""
import os

import pytest

from pages.sales_login_page import SalesLoginPage
from pages.sales_home_page import SalesHomePage
from pages.cart_page import CartPage
from pages.quotation_page import QuotationPage
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# 测试数据
SALES_USERNAME = "xuzw"
SALES_PASSWORD = "123qwe"
SEARCH_KEYWORD = "10004188"
ADD_TO_CART_INDEX = 1
OPPORTUNITY_NAME = "13501: 审批商机20260701-03"
ATTACHMENT_FILE = "渠道订单导入模版.xlsx"


@pytest.mark.sales
@pytest.mark.order
@pytest.mark.smoke
class TestSalesOrderFlow:
    """销售完整下单流程测试"""

    @pytest.mark.order(1)
    def test_sales_full_order_flow(self, page):
        """
        销售完整下单流程（端到端）

        步骤:
        1. 销售登录（xuzw/123qwe）
        2. 搜索产品 10004188
        3. 加入购物车
        4. 打开购物车（新窗口）
        5. 选择商品并生成报价单
        6. 继续下单，选择商机
        7. 查看报价单（新窗口）
        8. 上传附件
        9. 提交报价单 + 勾选C4合同
        10. 产品选配并确认提交
        """
        logger.info("=" * 50)
        logger.info("销售完整下单流程测试 - 开始")
        logger.info("=" * 50)

        # ====== Phase 1: 销售登录 ======
        logger.info("--- Phase 1: 销售登录 ---")
        login_page = SalesLoginPage(page)
        login_page.open().sales_login(
            username=SALES_USERNAME,
            password=SALES_PASSWORD,
        )

        # ====== Phase 2: 搜索产品 + 加入购物车 ======
        logger.info("--- Phase 2: 搜索产品 + 加入购物车 ---")
        sales_home = SalesHomePage(page)
        (
            sales_home
            .search_product(SEARCH_KEYWORD)
            .assert_search_results_visible()
        )
        # 等待搜索结果渲染完成，避免过早点击导致元素不稳定
        page.wait_for_timeout(2000)
        sales_home.add_to_cart(index=ADD_TO_CART_INDEX)

        # ====== Phase 3: 打开购物车（新窗口） ======
        logger.info("--- Phase 3: 打开购物车 ---")
        cart_page: CartPage = sales_home.open_cart()

        # ====== Phase 4: 生成报价单 ======
        logger.info("--- Phase 4: 生成报价单 ---")
        (
            cart_page
            .select_product_by_group_checkbox(index=1)
            .generate_quotation()
            .continue_order()
        )

        # ====== Phase 5: 选择商机 ======
        logger.info("--- Phase 5: 选择商机 ---")
        cart_page.select_opportunity(OPPORTUNITY_NAME)
        cart_page.confirm_info_form()

        # ====== Phase 6: 查看报价单（新窗口） ======
        logger.info("--- Phase 6: 查看报价单 ---")
        quotation_page_obj = cart_page.click_view_quotation()
        quotation_page = QuotationPage(quotation_page_obj)

        # ====== Phase 7: 上传附件 + 提交报价单 ======
        logger.info("--- Phase 7: 上传附件 + 提交报价单 ---")
        # 构建附件完整路径（优先查找项目根目录及 data 目录）
        attachment_path = _resolve_attachment_path(ATTACHMENT_FILE)
        (
            quotation_page
            .upload_attachment(attachment_path)
            .submit_quotation()
            .check_auto_contract()
            .confirm_dialog()
        )
        # 第二次确认（录制中有两次）
        quotation_page.confirm_dialog()

        # ====== Phase 8: 产品选配并提交 ======
        logger.info("--- Phase 8: 产品选配并提交 ---")
        (
            quotation_page
            .click_product_config()
            .add_product()
            .confirm_submit()
            .submit_quotation()
            .confirm_dialog()
        )

        logger.info("=" * 50)
        logger.info("销售完整下单流程测试 - 完成")
        logger.info("=" * 50)


def _resolve_attachment_path(filename: str) -> str:
    """
    解析附件文件路径，按优先级查找：
    1. 绝对路径直接返回
    2. 项目根目录
    3. data/ 目录
    """
    if os.path.isabs(filename):
        return filename

    base_dir = settings.base_dir

    # 尝试项目根目录
    path = base_dir / filename
    if path.exists():
        return str(path)

    # 尝试 data 目录
    path = base_dir / "data" / filename
    if path.exists():
        return str(path)

    # 回退到文件名本身（让 Playwright 报错定位问题）
    logger.warning(f"附件文件未找到: {filename}，回退到原始路径")
    return filename
