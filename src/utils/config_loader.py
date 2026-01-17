"""配置加载器"""

import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        Dict: 配置字典
    """
    # 加载环境变量
    load_dotenv()

    # 读取 YAML 配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def get_api_config(config: Dict[str, Any], api_name: str) -> Optional[Dict[str, Any]]:
    """
    获取特定 API 的配置

    Args:
        config: 总配置
        api_name: API 名称

    Returns:
        Optional[Dict]: API 配置，如果不存在返回 None
    """
    apis = config.get("apis", {})
    return apis.get(api_name)


def get_benchmark_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取基准测试配置

    Args:
        config: 总配置

    Returns:
        Dict: 基准测试配置
    """
    return config.get("benchmark", {})


def get_quality_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取质量评估配置

    Args:
        config: 总配置

    Returns:
        Dict: 质量评估配置
    """
    return config.get("quality", {})


def get_report_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取报告配置

    Args:
        config: 总配置

    Returns:
        Dict: 报告配置
    """
    return config.get("report", {})


def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置是否有效

    Args:
        config: 配置字典

    Returns:
        bool: 配置是否有效
    """
    # 检查必需的配置项
    required_sections = ["apis", "benchmark", "report"]
    for section in required_sections:
        if section not in config:
            print(f"错误: 配置缺少必需的部分 '{section}'")
            return False

    # 检查 API 配置
    apis = config.get("apis", {})
    if not apis:
        print("错误: 没有配置任何 API")
        return False

    # 检查环境变量
    for api_name, api_config in apis.items():
        api_key_env = api_config.get("api_key_env")
        if api_key_env and not os.getenv(api_key_env):
            print(f"警告: 未找到环境变量 {api_key_env} (API: {api_name})")

    return True
