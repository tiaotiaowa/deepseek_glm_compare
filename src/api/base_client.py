"""API 客户端抽象基类"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass
import time


@dataclass
class StreamMetrics:
    """流式响应指标"""
    ttft_ms: float  # Time to First Token (毫秒)
    total_time_ms: float  # 总响应时间 (毫秒)
    generation_time_ms: float  # 生成时间 (毫秒)
    output_tokens: int  # 输出 token 数量
    tokens_per_second: float  # 生成速度 (tokens/秒)
    inter_token_latency_ms: float  # 平均 token 间延迟 (毫秒)
    text: str  # 完整响应文本


class BaseClient(ABC):
    """API 客户端抽象基类"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        max_retries: int = 3,
        timeout: int = 120
    ):
        """
        初始化客户端

        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型名称
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
        """
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self._client = None

    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> StreamMetrics:
        """
        流式聊天请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数（max_tokens, temperature 等）

        Returns:
            StreamMetrics: 包含性能指标和响应文本的对象
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        非流式聊天请求（用于质量评估）

        Args:
            messages: 消息列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            str: 完整响应文本
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        验证 API 连接

        Returns:
            bool: 连接是否有效
        """
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict: 模型信息
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }

    def _calculate_metrics(
        self,
        request_start: float,
        first_token_time: Optional[float],
        request_end: float,
        token_timestamps: List[float],
        text: str
    ) -> StreamMetrics:
        """
        计算性能指标

        Args:
            request_start: 请求开始时间
            first_token_time: 第一个 token 到达时间
            request_end: 请求结束时间
            token_timestamps: 所有 token 的时间戳
            text: 完整响应文本

        Returns:
            StreamMetrics: 计算出的指标
        """
        total_time_ms = (request_end - request_start) * 1000
        output_tokens = len(token_timestamps)

        if first_token_time is not None and output_tokens > 0:
            ttft_ms = (first_token_time - request_start) * 1000
            generation_time_ms = (request_end - first_token_time) * 1000
            tokens_per_second = output_tokens / (request_end - first_token_time)
        else:
            ttft_ms = 0
            generation_time_ms = 0
            tokens_per_second = 0

        # 计算 token 间延迟
        if output_tokens > 1:
            inter_token_latencies = [
                (token_timestamps[i] - token_timestamps[i-1]) * 1000
                for i in range(1, len(token_timestamps))
            ]
            inter_token_latency_ms = sum(inter_token_latencies) / len(inter_token_latencies)
        else:
            inter_token_latency_ms = 0

        return StreamMetrics(
            ttft_ms=ttft_ms,
            total_time_ms=total_time_ms,
            generation_time_ms=generation_time_ms,
            output_tokens=output_tokens,
            tokens_per_second=tokens_per_second,
            inter_token_latency_ms=inter_token_latency_ms,
            text=text
        )
