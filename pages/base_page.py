"""
BasePage - 所有页面对象的基类

封装 Playwright Page 对象，提供：
1. 定位器增强（data-testid 自动转换）
2. 智能等待（禁止 time.sleep）
3. 通用操作封装（点击/填充/获取文本/导航）
4. 断言封装（基于 Playwright expect）
5. 截图能力（用于失败诊断和报告）

规范约束：
- 所有定位器推荐使用 data-testid 属性
- 页面对象方法必须包含断言或返回新页面对象
"""
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import Page, Locator, expect

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """
    页面对象基类

    所有业务页面对象（LoginPage / HomePage 等）应继承此类，
    通过 self.page 操作浏览器，通过 self.locate() 获取元素。
    """

    def __init__(self, page: Page):
        self.page = page
        self.timeout = settings.TIMEOUT
        self.network_idle_timeout = settings.NETWORK_IDLE_TIMEOUT
        self._url: Optional[str] = None

    # ==========================================
    # 定位器增强
    # ==========================================
    def locate(self, selector: str, **kwargs) -> Locator:
        """
        返回 Locator，自动处理 data-testid 前缀

        支持的 selector 格式：
            "data-testid=username"  -> [data-testid='username']
            "#login-btn"            -> 保持原样
            ".menu-item"            -> 保持原样
            "text=登录"             -> 保持原样

        Args:
            selector: 定位表达式
            **kwargs: 传递给 page.locator 的额外参数

        Returns:
            Locator 对象
        """
        normalized = self._normalize_selector(selector)
        return self.page.locator(normalized, **kwargs)

    @staticmethod
    def _normalize_selector(selector: str) -> str:
        """将 data-testid=xxx 转换为 CSS 属性选择器"""
        if selector.startswith("data-testid="):
            testid = selector.split("=", 1)[1]
            return f"[data-testid='{testid}']"
        return selector

    def locate_any(self, *selectors: str) -> Locator:
        """
        返回第一个匹配到的 Locator（多选择器容错）

        依次尝试 selectors，返回第一个可见元素的 Locator。
        若全部未匹配，返回第一个 selector 的 Locator（由调用方处理异常）。

        Args:
            *selectors: 多个定位表达式（优先级从高到低）

        Returns:
            第一个匹配到的 Locator
        """
        for selector in selectors:
            normalized = self._normalize_selector(selector)
            locator = self.page.locator(normalized)
            if locator.is_visible():
                return locator
        # 全部不可见，返回第一个（调用方 expect visible 会抛异常）
        return self.locate(selectors[0])

    def get_by_text(self, text: str, **kwargs):
        """返回匹配文本的 Locator（封装 page.get_by_text）"""
        return self.page.get_by_text(text, **kwargs)

    def get_by_role(self, role: Any, **kwargs):
        """返回匹配角色的 Locator（封装 page.get_by_role）"""
        return self.page.get_by_role(role, **kwargs)

    def click_any(self, *selectors: str, timeout: Optional[int] = None) -> "BasePage":
        """
        点击第一个可见的匹配元素（多选择器容错）

        Args:
            *selectors: 多个定位表达式（优先级从高到低）
            timeout: 超时时间（ms）

        Returns:
            self（支持链式调用）
        """
        for selector in selectors:
            try:
                if self.is_visible(selector):
                    logger.debug(f"click_any 命中选择器: {selector}")
                    self.click(selector)
                    return self
            except Exception:
                continue
        logger.warning(f"click_any 未找到任何匹配元素: {selectors}")
        self.screenshot(f"WARN_click_any_not_found_{selectors[0].replace('=', '_')[:3]}")
        return self

    def click_first(self, *selectors: str, timeout: Optional[int] = None) -> "BasePage":
        """
        依次尝试 selectors，点击第一个存在的匹配元素（.first）

        适用于复选框、单选框等可能存在但不可见的元素（Element UI 中
        复选框通常被隐藏，用 label/span 覆盖），用 click_any 会因
        is_visible 检查而错过。

        Args:
            *selectors: 多个定位表达式（优先级从高到低）
            timeout: 单次定位超时（ms）

        Returns:
            self（支持链式调用）
        """
        _timeout = timeout or self.timeout
        for selector in selectors:
            try:
                normalized = self._normalize_selector(selector)
                self.page.locator(normalized).first.click(timeout=_timeout)
                logger.debug(f"click_first 命中: {selector}")
                return self
            except Exception:
                continue
        logger.warning(f"click_first 未命中任何选择器: {selectors}")
        return self


    def wait_for_any_visible(self, *selectors: str, timeout: Optional[int] = None) -> "BasePage":
        """
        等待任意一个元素可见

        Args:
            *selectors: 多个定位表达式
            timeout: 超时时间（ms）

        Returns:
            self
        """
        timeout = timeout or self.timeout
        for selector in selectors:
            try:
                self.wait_for_visible(selector, timeout=timeout)
                logger.debug(f"wait_for_any_visible 命中选择器: {selector}")
                return self
            except Exception:
                continue
        logger.warning(f"wait_for_any_visible 未找到任何可见元素: {selectors}")
        return self

    # ==========================================
    # 导航
    # ==========================================
    def navigate(self, path: str = "") -> "BasePage":
        """
        导航到指定路径

        Args:
            path: 相对路径（会拼接 BASE_URL），或完整 URL

        Returns:
            self（支持链式调用）
        """
        url = path if path.startswith("http") else f"{settings.BASE_URL}{path}"
        logger.info(f"导航至: {url}")
        self.page.goto(url, wait_until="domcontentloaded",
                       timeout=settings.NAVIGATION_TIMEOUT)
        self.wait_for_network_idle()
        return self

    def get_current_url(self) -> str:
        """获取当前页面URL"""
        return self.page.url

    def get_title(self) -> str:
        """获取当前页面标题"""
        return self.page.title()

    # ==========================================
    # 交互操作（带自动等待）
    # ==========================================
    def click(self, selector: str, **kwargs) -> "BasePage":
        """
        点击元素（自动等待可操作状态）

        Args:
            selector: 定位表达式
            **kwargs: 传递给 locator.click 的参数（如 timeout, position, force 等）
        """
        logger.debug(f"点击元素: {selector}")
        click_timeout = kwargs.pop("timeout", self.timeout)
        self.locate(selector).click(timeout=click_timeout, **kwargs)
        return self

    def fill(self, selector: str, text: str, **kwargs) -> "BasePage":
        """
        填充输入框（自动清空后输入）

        Args:
            selector: 定位表达式
            text: 要输入的文本
            **kwargs: 传递给 locator.fill 的参数（如 timeout 等）
        """
        logger.debug(f"填充 {selector}: {text}")
        fill_timeout = kwargs.pop("timeout", self.timeout)
        self.locate(selector).fill(text, timeout=fill_timeout, **kwargs)
        return self

    def fill_any(self, *selectors: str, text: str, **kwargs) -> "BasePage":
        """
        向第一个可见的匹配输入框填充文本（多选择器容错）

        Args:
            *selectors: 多个定位表达式（优先级从高到低）
            text: 要输入的文本
            **kwargs: 传递给 locator.fill 的参数

        Returns:
            self（支持链式调用）
        """
        for selector in selectors:
            try:
                if self.is_visible(selector):
                    logger.debug(f"fill_any 命中选择器: {selector}")
                    self.fill(selector, text, **kwargs)
                    return self
            except Exception:
                continue
        logger.warning(f"fill_any 未找到任何可见输入框: {selectors}")
        # 清理选择器中的非法字符，用于文件名
        import re
        safe_selector = re.sub(r'[<>:"/\\|?*\[\]\'=]', '_', selectors[0])[:30]
        self.screenshot(f"WARN_fill_any_not_found_{safe_selector}")
        return self

    def get_text(self, selector: str) -> str:
        """
        获取元素文本内容（等待可见后读取）

        Args:
            selector: 定位表达式

        Returns:
            元素的 text_content
        """
        self.wait_for_visible(selector)
        return self.locate(selector).text_content(timeout=self.timeout) or ""

    def is_visible(self, selector: str) -> bool:
        """
        判断元素是否可见（不抛异常）

        Args:
            selector: 定位表达式

        Returns:
            bool
        """
        try:
            return self.locate(selector).is_visible(timeout=self.timeout)
        except Exception:
            return False

    def count(self, selector: str) -> int:
        """获取匹配元素数量"""
        return self.locate(selector).count()

    # ==========================================
    # 等待机制（禁止 time.sleep）
    # ==========================================
    def wait_for_visible(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """等待元素可见"""
        self.locate(selector).wait_for(state="visible", timeout=timeout or self.timeout)
        return self

    def wait_for_hidden(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """等待元素隐藏/消失"""
        self.locate(selector).wait_for(state="hidden", timeout=timeout or self.timeout)
        return self

    def wait_for_attached(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """等待元素挂载到DOM"""
        self.locate(selector).wait_for(state="attached", timeout=timeout or self.timeout)
        return self

    def wait_for_network_idle(self) -> "BasePage":
        """等待网络空闲（确保SPA异步请求完成）"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=self.network_idle_timeout)
        except Exception as e:
            logger.warning(f"等待networkidle超时（非致命）: {e}")
        return self

    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> "BasePage":
        """
        等待URL匹配指定模式（支持正则字符串）

        Args:
            url_pattern: URL匹配模式
            timeout: 超时时间
        """
        self.page.wait_for_url(url_pattern, timeout=timeout or self.timeout)
        return self

    # ==========================================
    # 截图
    # ==========================================
    def screenshot(self, name: Optional[str] = None, full_page: bool = True) -> str:
        """
        截图并保存到 screenshots 目录

        Args:
            name: 文件名（不含扩展名），为空则自动生成
            full_page: 是否截取整页

        Returns:
            截图文件的绝对路径
        """
        ts = time.strftime("%Y%m%d_%H%M%S")
        if not name:
            name = f"{ts}_screenshot_{uuid.uuid4().hex[:6]}"
        else:
            name = f"{ts}_{name}"
        path = settings.screenshot_path / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=full_page)
        logger.info(f"截图已保存: {path}")
        return str(path)

    # ==========================================
    # 断言封装（基于 Playwright expect）
    # ==========================================
    def assert_visible(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """断言元素可见"""
        expect(self.locate(selector)).to_be_visible(timeout=timeout or self.timeout)
        return self

    def assert_hidden(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """断言元素不可见"""
        expect(self.locate(selector)).to_be_hidden(timeout=timeout or self.timeout)
        return self

    def assert_text(self, selector: str, expected: str,
                    timeout: Optional[int] = None) -> "BasePage":
        """断言元素文本内容等于预期值"""
        expect(self.locate(selector)).to_have_text(expected, timeout=timeout or self.timeout)
        return self

    def assert_contains_text(self, selector: str, expected: str,
                             timeout: Optional[int] = None) -> "BasePage":
        """断言元素文本包含预期值"""
        expect(self.locate(selector)).to_contain_text(expected,
                                                       timeout=timeout or self.timeout)
        return self

    def assert_value(self, selector: str, expected: str,
                     timeout: Optional[int] = None) -> "BasePage":
        """断言输入框值等于预期"""
        expect(self.locate(selector)).to_have_value(expected, timeout=timeout or self.timeout)
        return self

    def assert_url_contains(self, expected: str) -> "BasePage":
        """断言当前URL包含预期字符串"""
        expect(self.page).to_have_url(expected)
        return self

    def assert_count(self, selector: str, expected: int,
                     timeout: Optional[int] = None) -> "BasePage":
        """断言匹配元素数量"""
        expect(self.locate(selector)).to_have_count(expected, timeout=timeout or self.timeout)
        return self

    def assert_enabled(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """断言元素可用"""
        expect(self.locate(selector)).to_be_enabled(timeout=timeout or self.timeout)
        return self

    def assert_disabled(self, selector: str, timeout: Optional[int] = None) -> "BasePage":
        """断言元素不可用"""
        expect(self.locate(selector)).to_be_disabled(timeout=timeout or self.timeout)
        return self

    def scroll_to_bottom(self) -> "BasePage":
        """滚动到页面底部"""
        logger.debug("滚动到页面底部")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        return self

    # ==========================================
    # 文件上传
    # ==========================================
    def upload_file(self, selector: str, file_path: str, **kwargs) -> "BasePage":
        """
        上传文件到指定元素
        
        Args:
            selector: 文件输入框定位器
            file_path: 要上传的文件路径
            **kwargs: 传递给 locator.set_input_files 的参数
            
        Returns:
            self（支持链式调用）
        """
        logger.debug(f"上传文件 {file_path} 到 {selector}")
        self.locate(selector).set_input_files(file_path, timeout=self.timeout, **kwargs)
        return self
    
    def upload_files(self, selector: str, file_paths: list[str | Path], **kwargs) -> "BasePage":
        """
        上传多个文件到指定元素
        
        Args:
            selector: 文件输入框定位器
            file_paths: 要上传的文件路径列表
            **kwargs: 传递给 locator.set_input_files 的参数
            
        Returns:
            self（支持链式调用）
        """
        logger.debug(f"上传多个文件 {file_paths} 到 {selector}")
        self.locate(selector).set_input_files(file_paths, timeout=self.timeout, **kwargs)
        return self
