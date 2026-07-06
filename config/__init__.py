"""
config 包 - 配置管理

导出全局 settings 单例供其他模块使用：
    from config import settings
    print(settings.BASE_URL)
"""
from config.settings import settings, Settings, BASE_DIR

__all__ = ["settings", "Settings", "BASE_DIR"]
