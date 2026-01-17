"""Judge 客户端工厂 - 负责创建和管理 Judge 客户端

这个模块从 judge_manager.py 中提取了客户端创建的逻辑，
使用工厂模式创建不同类型的 Judge 客户端。

使用示例:
    from src.quality.judge_factory import JudgeFactory

    # 根据配置创建所有 Judge
    judges = JudgeFactory.create_all(config)

    # 创建单个 Judge
    client = JudgeFactory.create_single({
        "type": "deepseek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat"
    })
"""

import os
from typing import Dict, List, Any, Optional

from ..api.openai_client import OpenAIClient
from ..api.anthropic_client import AnthropicClient
from ..api.minimax_client import MiniMaxClient


class JudgeFactory:
    """Judge 客户端工厂 - 使用工厂模式创建 Judge 客户端

    从 judge_manager.py 中提取，负责根据配置创建不同类型的客户端
    """

    # Judge 类型到客户端类的映射
    CLIENT_MAP = {
        "deepseek": OpenAIClient,
        "glm": AnthropicClient,
        "minimax": MiniMaxClient
    }

    # Judge 类型到默认配置的映射
    DEFAULT_CONFIGS = {
        "deepseek": {
            "base_url": "https://api.deepseek.com",
        },
        "glm": {
            "base_url": "https://open.bigmodel.cn/api/anthropic",
        },
        "minimax": {
            "base_url": "https://api.minimaxi.com/anthropic",
        }
    }

    @staticmethod
    def create_all(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        根据配置创建所有 Judge 客户端

        Args:
            config: 质量评估配置字典，包含 "judges" 键

        Returns:
            Judge 字典，格式为 {judge_name: {"client": client, "config": config, ...}}
        """
        judges_config = config.get("judges", {})
        judges = {}

        for judge_name, judge_config in judges_config.items():
            # 跳过未启用的 Judge
            if not judge_config.get("enabled", True):
                continue

            # 创建单个 Judge 客户端
            judge_info = JudgeFactory.create_single(judge_config)

            if judge_info:
                # 添加额外信息
                judge_info["config"] = judge_config
                judge_info["type"] = judge_config.get("type", "")
                judge_info["model"] = judge_config.get("model", "")

                judges[judge_name] = judge_info
                print(f"[OK] {judge_name} initialized successfully (model: {judge_info['model']})")

        return judges

    @staticmethod
    def create_single(judge_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建单个 Judge 客户端

        Args:
            judge_config: Judge 配置字典，包含：
                - type: Judge 类型（"deepseek", "glm", "minimax"）
                - api_key_env: API 密钥环境变量名
                - model: 模型名称
                - max_retries: 最大重试次数（可选）
                - timeout: 超时时间（可选）

        Returns:
            包含 "client" 键的字典，如果创建失败返回 None
        """
        judge_type = judge_config.get("type", "")
        judge_model = judge_config.get("model", "")

        # 验证类型
        if judge_type not in JudgeFactory.CLIENT_MAP:
            print(f"[WARNING] Unknown judge type: {judge_type}")
            return None

        # 获取 API key
        api_key_env = judge_config.get("api_key_env", "")
        api_key = os.getenv(api_key_env)

        if not api_key:
            print(f"[WARNING] API key not found for {judge_type} ({api_key_env}), skipping")
            return None

        # 获取配置参数
        max_retries = judge_config.get("max_retries", 3)
        timeout = judge_config.get("timeout", 120)

        # 获取默认配置并合并
        default_config = JudgeFactory.DEFAULT_CONFIGS.get(judge_type, {})
        base_url = judge_config.get("base_url", default_config.get("base_url", ""))

        if not base_url:
            print(f"[WARNING] No base_url found for {judge_type}")
            return None

        try:
            # 使用对应的客户端类创建实例
            client_class = JudgeFactory.CLIENT_MAP[judge_type]
            client = client_class(
                base_url=base_url,
                api_key=api_key,
                model=judge_model,
                max_retries=max_retries,
                timeout=timeout
            )

            return {"client": client}

        except Exception as e:
            print(f"[ERROR] Failed to create {judge_type} client: {e}")
            return None

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        验证 Judge 配置是否有效

        Args:
            config: 配置字典

        Returns:
            是否有效
        """
        if "judges" not in config:
            return False

        judges_config = config["judges"]
        if not isinstance(judges_config, dict):
            return False

        # 检查至少有一个 Judge
        enabled_count = sum(
            1 for jc in judges_config.values()
            if jc.get("enabled", True)
        )

        return enabled_count > 0

    @staticmethod
    def get_supported_types() -> List[str]:
        """
        获取支持的 Judge 类型列表

        Returns:
            Judge 类型列表
        """
        return list(JudgeFactory.CLIENT_MAP.keys())

    @staticmethod
    def get_default_config(judge_type: str) -> Dict[str, Any]:
        """
        获取指定 Judge 类型的默认配置

        Args:
            judge_type: Judge 类型

        Returns:
            默认配置字典
        """
        return JudgeFactory.DEFAULT_CONFIGS.get(judge_type, {}).copy()
