"""
文件处理工具模块

提供文件验证、路径处理等工具函数。
"""
from pathlib import Path
from typing import Optional


def validate_file_exists(file_path: str) -> bool:
    """
    验证文件是否存在
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件存在返回 True，否则返回 False
    """
    return Path(file_path).is_file()


def get_file_size_mb(file_path: str) -> Optional[float]:
    """
    获取文件大小（MB）
    
    Args:
        file_path: 文件路径
        
    Returns:
        float: 文件大小（MB），文件不存在返回 None
    """
    path = Path(file_path)
    if not path.is_file():
        return None
    return path.stat().st_size / (1024 * 1024)


def validate_image_file(file_path: str, max_size_mb: float = 5.0) -> tuple[bool, str]:
    """
    验证图片文件是否有效
    
    Args:
        file_path: 图片文件路径
        max_size_mb: 最大文件大小（MB）
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    path = Path(file_path)
    
    # 检查文件是否存在
    if not path.is_file():
        return False, f"文件不存在: {file_path}"
    
    # 检查文件扩展名
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    if path.suffix.lower() not in valid_extensions:
        return False, f"不支持的文件格式: {path.suffix}"
    
    # 检查文件大小
    size_mb = get_file_size_mb(file_path)
    if size_mb and size_mb > max_size_mb:
        return False, f"文件大小超过 {max_size_mb}MB: {size_mb:.2f}MB"
    
    return True, "文件验证通过"


def sanitize_filename(filename: str) -> str:
    """
    清理文件名（移除非法字符）
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
