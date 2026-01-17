"""MiniMax 专用客户端

由于 MiniMax API 的认证格式与标准 Anthropic API 不同，
需要使用自定义客户端来确保正确的请求头格式
"""

import time
from typing import Dict, List, Any
import httpx

from .base_client import BaseClient, StreamMetrics


class MiniMaxClient(BaseClient):
    """MiniMax 专用客户端 - 使用正确的认证格式"""

    def __init__(self, base_url: str, api_key: str, model: str, max_retries: int = 3, timeout: int = 120):
        """
        初始化 MiniMax 客户端

        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型名称
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
        """
        super().__init__(base_url, api_key, model, max_retries, timeout)

        # 创建 httpx 客户端
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        非流式聊天请求

        Args:
            messages: 消息列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            str: 完整响应文本
        """
        try:
            # 构建请求 URL
            url = "/v1/messages"

            # 构建请求数据
            data = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }

            # 发送请求
            response = self._client.post(url, json=data)
            response.raise_for_status()

            # 解析响应
            result = response.json()

            # 提取文本内容
            text_parts = []
            for block in result.get("content", []):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "thinking":
                    text_parts.append(block.get("thinking", ""))

            return ''.join(text_parts)

        except httpx.HTTPStatusError as e:
            print(f"MiniMax API 请求失败: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
            raise
        except Exception as e:
            print(f"MiniMax 客户端请求出错: {e}")
            raise

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> StreamMetrics:
        """
        流式聊天请求（占位实现，MiniMax Judge 主要使用非流式）

        Args:
            messages: 消息列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            StreamMetrics: 性能指标
        """
        import time

        request_start = time.perf_counter()

        # 使用非流式请求模拟
        text = self.chat(messages, max_tokens, temperature, **kwargs)

        request_end = time.perf_counter()

        # 返回简化的指标
        return self._calculate_metrics(
            request_start=request_start,
            first_token_time=request_start,  # 假设立即响应
            request_end=request_end,
            token_timestamps=[],  # 无流式 token 时间戳
            text=text
        )

    def validate_connection(self) -> bool:
        """
        验证 API 连接

        Returns:
            bool: 连接是否有效
        """
        try:
            response = self._client.post(
                "/v1/messages",
                json={
                    "model": self.model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Hi"}]
                }
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"MiniMax 连接验证失败: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict: 模型信息
        """
        info = super().get_model_info()
        info["client_type"] = "minimax"
        return info

    def __del__(self):
        """清理资源"""
        if hasattr(self, '_client'):
            self._client.close()
