"""Anthropic 协议客户端实现

这个客户端实现了 Anthropic API 协议，用于与 Anthropic 兼容的 API 进行交互。
支持的 API 包括：
- Anthropic 官方 API (Claude)
- GLM API（使用 Anthropic 兼容协议）
- MiniMax API（使用 Anthropic 兼容协议）

特性：
- 流式响应处理，支持精确的 TTFT 指标测量
- 支持多种内容块类型（TextBlock, ThinkingBlock）
- 自动重试机制（指数退避）
- 高精度性能计时
- 完善的错误处理
"""

from typing import Dict, List, Any, Iterator
from anthropic import Anthropic
from anthropic.types import Message
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base_client import BaseClient, StreamMetrics
from .streaming_mixin import StreamingMixin


class AnthropicClient(StreamingMixin, BaseClient):
    """Anthropic 协议客户端

    这个类继承自 StreamingMixin 和 BaseClient，提供 Anthropic 协议的完整实现。

    Attributes:
        _client: Anthropic SDK 客户端实例
    """

    def __init__(self, base_url: str, api_key: str, model: str, max_retries: int = 3, timeout: int = 120):
        """
        初始化 Anthropic 客户端

        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型名称
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
        """
        super().__init__(base_url, api_key, model, max_retries, timeout)

        # 初始化 Anthropic 客户端
        self._client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries
        )

    def _extract_text_from_response(self, response) -> str:
        """
        从响应中提取文本内容，处理不同类型的内容块

        支持的内容块类型：
        - TextBlock (标准 Anthropic 响应)
        - ThinkingBlock (MiniMax 等实现)

        Args:
            response: API 响应对象

        Returns:
            str: 提取的完整文本
        """
        text_parts = []
        for block in response.content:
            if hasattr(block, 'text'):
                # TextBlock 类型 - 标准 Anthropic 响应
                text_parts.append(block.text)
            elif hasattr(block, 'thinking'):
                # ThinkingBlock 类型 - MiniMax 等特殊实现
                text_parts.append(block.thinking)
            else:
                # 其他类型，尝试转换为字符串
                text_parts.append(str(block))
        return ''.join(text_parts)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> StreamMetrics:
        """
        流式聊天请求，捕获性能指标

        这个方法使用 StreamingMixin 提供的通用流式处理逻辑，只需要提供
        Anthropic 特定的流式执行器。

        执行流程：
        1. 创建 Anthropic 流式请求
        2. 使用 StreamingMixin._execute_streaming_request() 处理响应
        3. 自动计算性能指标（TTFT、生成速度等）

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            max_tokens: 最大生成 token 数
            temperature: 温度参数，控制输出的随机性（0-1）
            **kwargs: 其他传递给 Anthropic API 的参数

        Returns:
            StreamMetrics: 包含性能指标和响应文本的对象
                - ttft_ms: Time to First Token（首次响应时间，毫秒）
                - total_time_ms: 总响应时间（毫秒）
                - generation_time_ms: 生成时间（毫秒）
                - output_tokens: 输出 token 数量
                - tokens_per_second: 生成速度（tokens/秒）
                - inter_token_latency_ms: 平均 token 间延迟（毫秒）
                - text: 完整响应文本
        """
        # 创建流式执行器（返回一个迭代器）
        def stream_executor() -> Iterator[str]:
            """Anthropic 流式执行器，产生文本片段"""
            # Anthropic SDK 使用上下文管理器处理流式响应
            with self._client.messages.stream(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            ) as stream:
                # text_stream 产生文本片段
                for text in stream.text_stream:
                    yield text

        # 使用 StreamingMixin 的通用流式处理逻辑
        return self._execute_streaming_request(
            messages=messages,
            parameters={
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            },
            stream_executor=stream_executor
        )

    def validate_connection(self) -> bool:
        """
        验证 API 连接

        Returns:
            bool: 连接是否有效
        """
        try:
            # 发送一个简单的测试请求
            response = self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            print(f"连接验证失败: {e}")
            return False

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
        try:
            response = self._client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            # 使用通用的文本提取方法，支持多种内容块类型
            return self._extract_text_from_response(response)
        except Exception as e:
            print(f"非流式聊天请求失败: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict: 模型信息
        """
        info = super().get_model_info()
        info["client_type"] = "anthropic"
        return info
