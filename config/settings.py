"""
配置管理模块

基于 Pydantic Settings 实现类型安全的多环境配置管理。
支持通过 .env 文件动态切换 dev / test / staging / prod 环境。
"""
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目根目录（config/ 的上一级）
BASE_DIR: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    全局配置类

    通过 .env 文件或环境变量注入，支持运行时动态切换：
        ENV=test python -m pytest
        ENV=staging python -m pytest
    """

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- 基础环境 ----------
    ENV: str = Field(default="test", description="运行环境: dev/test/staging/prod")
    BASE_URL: str = Field(default="https://test.example.com", description="被测系统基础URL")

    # ---------- 浏览器配置 ----------
    BROWSER: str = Field(default="chromium", description="浏览器类型: chromium/firefox/webkit")
    HEADLESS: bool = Field(default=False, description="是否无头模式运行")
    VIEWPORT_WIDTH: int = Field(default=1920, description="视口宽度")
    VIEWPORT_HEIGHT: int = Field(default=1080, description="视口高度")
    LOCALE: str = Field(default="zh-CN", description="浏览器语言")
    TIMEZONE: str = Field(default="Asia/Shanghai", description="浏览器时区")

    # ---------- 超时与重试 ----------
    NETWORK_IDLE_TIMEOUT: int = Field(default=5000, description="网络空闲等待超时(毫秒)")
    TIMEOUT: int = Field(default=10000, description="默认操作超时(毫秒)")
    NAVIGATION_TIMEOUT: int = Field(default=5000, description="导航超时(毫秒)")
    RETRY_TIMES: int = Field(default=2, description="失败重试次数")
    RETRY_DELAY: int = Field(default=1, description="重试间隔(秒)")

    # ---------- 并行执行 ----------
    PARALLEL_WORKERS: str = Field(default="auto", description="并行worker数量")

    # ---------- Trace与截图 ----------
    TRACE_MODE: str = Field(
        default="retain-on-failure",
        description="Trace模式: on/off/retain-on-failure",
    )
    SCREENSHOT_DIR: str = Field(default="reports/screenshots", description="截图保存目录")
    TRACE_DIR: str = Field(default="reports/traces", description="Trace保存目录")

    # ---------- 报告与日志 ----------
    ALLURE_RESULTS_DIR: str = Field(default="reports/allure-results", description="Allure结果目录")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="reports/logs/ui.log", description="日志文件路径")

    # ---------- 多角色默认账号（敏感信息应放.env，此处仅占位） ----------
    OPERATION_USERNAME: str = Field(default="", description="运营角色用户名")
    OPERATION_PASSWORD: str = Field(default="", description="运营角色密码")
    SALES_USERNAME: str = Field(default="", description="销售角色用户名")
    SALES_PASSWORD: str = Field(default="", description="销售角色密码")
    SALES2_USERNAME: str = Field(default="xuzw", description="备用销售角色用户名")
    SALES2_PASSWORD: str = Field(default="123qwe", description="备用销售角色密码")
    CUSTOMER_USERNAME: str = Field(default="", description="客户角色用户名")
    CUSTOMER_PASSWORD: str = Field(default="", description="客户角色密码")

    # ---------- 便捷属性 ----------
    @property
    def sales2_credentials(self) -> dict:
        """返回备用销售账号凭据"""
        return {"username": self.SALES2_USERNAME, "password": self.SALES2_PASSWORD}

    @property
    def viewport(self) -> dict:
        """返回 Playwright viewport 字典"""
        return {"width": self.VIEWPORT_WIDTH, "height": self.VIEWPORT_HEIGHT}

    @property
    def is_headless(self) -> bool:
        """HEADLESS 字段的别名访问"""
        return self.HEADLESS

    @property
    def base_dir(self) -> Path:
        """项目根目录"""
        return BASE_DIR

    @property
    def screenshot_path(self) -> Path:
        """截图目录绝对路径"""
        p = BASE_DIR / self.SCREENSHOT_DIR
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def trace_path(self) -> Path:
        """Trace目录绝对路径"""
        p = BASE_DIR / self.TRACE_DIR
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def log_path(self) -> Path:
        """日志文件绝对路径"""
        p = BASE_DIR / self.LOG_FILE
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def get_credentials(self, role: str) -> dict:
        """
        根据角色名获取登录凭据

        Args:
            role: 角色标识 - operation(运营) / sales(销售) / customer(客户)

        Returns:
            dict: {"username": ..., "password": ...}

        Raises:
            ValueError: 当角色名不支持时
        """
        role_map = {
            "operation": (self.OPERATION_USERNAME, self.OPERATION_PASSWORD),
            "sales": (self.SALES_USERNAME, self.SALES_PASSWORD),
            "customer": (self.CUSTOMER_USERNAME, self.CUSTOMER_PASSWORD),
        }
        key = role.lower().strip()
        if key not in role_map:
            raise ValueError(
                f"不支持的角色: {role}，可选值: {list(role_map.keys())}"
            )
        username, password = role_map[key]
        return {"username": username, "password": password}


# 全局单例
settings = Settings()
