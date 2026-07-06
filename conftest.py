"""
全局 Pytest Fixtures 和 Hooks

职责：
1. 扩展 pytest-playwright 的 browser_context_args（视口/语言/Trace）
2. 测试失败时自动截图 + 保存 Trace + 附加到 Allure
3. 测试成功时也自动截图（按时间戳排序）
4. 提供全局环境信息

依赖 pytest-playwright 插件提供的 browser / context / page 基础 fixture。
"""
import time
import os

import pytest

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """扩展浏览器启动参数"""
    args = {
        **browser_type_launch_args,
        "headless": settings.HEADLESS,
    }
    
    # 禁用浏览器缓存，避免缓存影响测试结果
    args["args"] = args.get("args", []) + [
        "--disable-cache",
        "--disable-application-cache",
        "--disk-cache-size=0",
    ]

    # 如果配置了使用 Chrome，则指定 executable_path
    if settings.BROWSER.lower() == "chrome":
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        
        if os.path.exists(chrome_path):
            args["executable_path"] = chrome_path
            print(f"[INFO] 使用 Chrome 浏览器: {chrome_path}")
        else:
            print("[WARN] 未找到 Chrome，使用默认 Chromium")
    
    return args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """扩展浏览器上下文参数：视口、语言、时区"""
    return {
        **browser_context_args,
        "viewport": settings.viewport,
        "locale": settings.LOCALE,
        "timezone_id": settings.TIMEZONE,
    }


@pytest.fixture(scope="session", autouse=True)
def _session_env_info():
    """会话级：记录运行环境信息"""
    logger.info("=" * 60)
    logger.info(f"测试环境: {settings.ENV}")
    logger.info(f"基础URL: {settings.BASE_URL}")
    logger.info(f"浏览器: {settings.BROWSER} (headless={settings.HEADLESS})")
    logger.info(f"视口: {settings.VIEWPORT_WIDTH}x{settings.VIEWPORT_HEIGHT}")
    logger.info(f"超时: {settings.TIMEOUT}ms | 重试: {settings.RETRY_TIMES}次")
    logger.info("=" * 60)
    yield


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    测试结果报告钩子

    在测试结束时（无论成功或失败）：
    1. 自动截图并保存（文件名含时间戳，按时间排序）
    2. 附加截图到 Allure 报告
    3. 记录测试日志
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        page = item.funcargs.get("page")
        test_name = item.name.replace("/", "_").replace(" ", "_")
        # 时间戳格式：YYYYMMDD_HHMMSS（便于按时间排序）
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        if report.failed:
            status = "FAIL"
            logger.error(f"测试失败: {test_name} | {report.longrepr}")
        else:
            status = "PASS"
            logger.info(f"测试通过: {test_name}")

        if page is not None:
            try:
                screenshot_path = settings.screenshot_path / f"{status}_{timestamp}_{test_name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                logger.info(f"截图已保存: {screenshot_path}")
                _attach_to_allure(str(screenshot_path), f"{status}截图-{test_name}", "image/png")
            except Exception as e:
                logger.warning(f"截图失败: {e}")

        if report.failed and page is not None:
            try:
                html_path = settings.screenshot_path / f"FAIL_{timestamp}_{test_name}.html"
                html_content = page.content()
                html_path.write_text(html_content, encoding="utf-8")
                _attach_to_allure(str(html_path), f"页面源码-{test_name}", "text/html")
            except Exception as e:
                logger.warning(f"保存页面源码失败: {e}")


def _attach_to_allure(file_path: str, name: str, attachment_type: str):
    """将文件附加到 Allure 报告（若 allure 已安装）"""
    try:
        import allure
        with open(file_path, "rb") as f:
            allure.attach(
                f.read(),
                name=name,
                attachment_type=attachment_type,
            )
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"Allure附加失败（可忽略）: {e}")


@pytest.fixture(scope="session")
def base_url() -> str:
    """返回配置的基础URL，供 pytest-base-url 使用"""
    return settings.BASE_URL


@pytest.fixture
def login_page(page):
    """
    登录页面对象 fixture
    
    Args:
        page: Playwright Page 对象（从 pytest-playwright 插件）
        
    Returns:
        LoginPage: 登录页面对象实例
    """
    from pages.login_page import LoginPage
    return LoginPage(page)
