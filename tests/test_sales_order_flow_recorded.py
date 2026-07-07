"""
销售下单流程测试（Codegen 录制版）

基于 Playwright Codegen 录制代码转换，使用 POM 框架重构。
录制商机: 13503: 审批商机20260706-01
"""
import os

import pytest

from pages.sales_login_page import SalesLoginPage
from pages.sales_home_page import SalesHomePage
from pages.cart_page import SalesCartPage
from pages.quotation_page import QuotationPage
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# 测试数据（来自录制）
SALES_USERNAME = "xuzw"
SALES_PASSWORD = "123qwe"
SEARCH_KEYWORD = "10004188"
ADD_TO_CART_INDEX = 1
OPPORTUNITY_NAME = "13503: 审批商机20260706-01"
ATTACHMENT_FILE = "渠道订单导入模版.xlsx"


@pytest.mark.sales
@pytest.mark.order
class TestSalesOrderFlowRecorded:
    """销售下单流程测试（录制版）"""

    @pytest.mark.order(1)
    def test_sales_full_order_flow_recorded(self, page):
        """
        销售完整下单流程（Codegen 录制 → POM 转换）

        步骤:
        1. 销售登录
        2. 搜索产品 10004188 并加入购物车
        3. 打开购物车（新窗口）
        4. 勾选商品 → 生成报价单 → 继续下单
        5. 选择商机 13503
        6. 查看报价单（新窗口）
        7. 上传附件 → 提交报价单 → 勾选 C4 合同
        8. 产品选配 → 确认提交
        """
        logger.info("=" * 50)
        logger.info("销售下单流程测试（录制版）- 开始")
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
        page.wait_for_timeout(500)
        sales_home.add_to_cart(index=ADD_TO_CART_INDEX)

        # ====== Phase 3: 打开购物车（新窗口） ======
        logger.info("--- Phase 3: 打开购物车 ---")
        cart_page: SalesCartPage = sales_home.open_cart()

        # ====== Phase 4: 生成报价单 ======
        logger.info("--- Phase 4: 生成报价单 ---")
        (
            cart_page
            .select_first_product()
            .generate_quotation()
            .continue_order()
        )

        # ====== Phase 5: 选择商机（录制值: 13503） ======
        logger.info("--- Phase 5: 选择商机 ---")
        cart_page.select_opportunity(OPPORTUNITY_NAME)

        # ====== Phase 6: 查看报价单（新窗口） ======
        logger.info("--- Phase 6: 查看报价单 ---")
        quotation_page_obj = cart_page.click_view_quotation()
        quotation_page = QuotationPage(quotation_page_obj)
        # 等待报价单详情页加载完成
        quotation_page_obj.wait_for_timeout(3000)

        # ====== Phase 7: 上传附件 + 提交报价单 ======
        logger.info("--- Phase 7: 上传附件 + 提交报价单 ---")
        attachment_path = _resolve_attachment_path(ATTACHMENT_FILE)
        (
            quotation_page
            .upload_attachment(attachment_path)
            .submit_quotation()
            .check_auto_contract()
            .confirm_dialog()
        )
        # 录制中有第二次确认弹窗
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
        logger.info("销售下单流程测试（录制版）- 完成")
        logger.info("=" * 50)


def _resolve_attachment_path(filename: str) -> str:
    """解析附件文件路径"""
    if os.path.isabs(filename):
        return filename

    base_dir = settings.base_dir

    path = base_dir / filename
    if path.exists():
        return str(path)

    path = base_dir / "data" / filename
    if path.exists():
        return str(path)

    logger.warning(f"附件文件未找到: {filename}，回退到原始路径")
    return filename
