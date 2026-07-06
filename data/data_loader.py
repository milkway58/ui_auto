"""
数据加载器模块

提供统一的测试数据加载能力，支持 YAML / JSON / CSV 格式。
测试数据统一存放在 data/ 目录下。

用法:
    from data.data_loader import load_yaml, load_json, load_csv
    users = load_yaml("users.yaml")
"""
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

from config.settings import BASE_DIR


DATA_DIR: Path = BASE_DIR / "data"


def _resolve_path(file_name: str) -> Path:
    """
    解析数据文件路径，支持相对路径和绝对路径

    Args:
        file_name: 文件名或路径（相对 data/ 目录或绝对路径）

    Returns:
        Path 对象
    """
    p = Path(file_name)
    if p.is_absolute():
        return p
    if not p.suffix:
        p = p.with_suffix(".yaml")
    if not p.parent.exists() or str(p.parent) == ".":
        p = DATA_DIR / p
    return p


def load_yaml(file_name: str) -> Any:
    """
    加载 YAML 数据文件

    Args:
        file_name: 文件名（相对 data/ 目录）或绝对路径

    Returns:
        解析后的数据（通常是 dict 或 list）

    Raises:
        FileNotFoundError: 文件不存在
    """
    path = _resolve_path(file_name)
    if not path.exists():
        raise FileNotFoundError(f"YAML数据文件不存在: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(file_name: str) -> Any:
    """
    加载 JSON 数据文件

    Args:
        file_name: 文件名（相对 data/ 目录）或绝对路径

    Returns:
        解析后的数据

    Raises:
        FileNotFoundError: 文件不存在
    """
    path = _resolve_path(file_name)
    if not path.exists():
        raise FileNotFoundError(f"JSON数据文件不存在: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(file_name: str, encoding: str = "utf-8") -> List[Dict[str, str]]:
    """
    加载 CSV 数据文件，首行作为字段名

    Args:
        file_name: 文件名（相对 data/ 目录）或绝对路径
        encoding: 文件编码，默认 utf-8

    Returns:
        List[Dict]: 每行一个字典，key 为首行字段名

    Raises:
        FileNotFoundError: 文件不存在
    """
    path = _resolve_path(file_name)
    if not path.exists():
        raise FileNotFoundError(f"CSV数据文件不存在: {path}")
    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_users_by_role(role: str, file_name: str = "users.yaml") -> List[Dict[str, Any]]:
    """
    根据角色加载用户测试数据

    Args:
        role: 角色标识 - operation(运营) / sales(销售) / customer(客户)
        file_name: 用户数据文件名，默认 users.yaml

    Returns:
        List[Dict]: 该角色下的用户数据列表

    Raises:
        KeyError: 角色在数据文件中不存在
    """
    data = load_yaml(file_name)
    role_key = role.lower().strip()
    if role_key not in data:
        raise KeyError(f"角色 '{role}' 在 {file_name} 中不存在，可用: {list(data.keys())}")
    users = data[role_key]
    if isinstance(users, dict):
        users = [users]
    return users
