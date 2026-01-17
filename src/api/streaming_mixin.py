"""流式处理混入类

提供统一的流式处理逻辑，减少 OpenAI 和 Anthropic 客户端的代码重复。

设计模式：
    使用模板方法模式（Template Method Pattern）：
    - 基类提供通用算法框架（_execute_streaming_request）
    - 子类实现特定步骤（_create_stream_executor）

使用方法：
    1. 客户端类继承 StreamingMixin
    2. 实现 _create_stream_executor() 方法
    3. 在 stream_chat() 中调用 _execute_streaming_request()

示例：
    class OpenAIClient(StreamingMixin, BaseClient):
        def _create_stream_executor(self, messages, parameters):
            # 返回一个迭代器，产生文本片段
            stream = self._client.chat.completions.create(...)
            return (chunk.choices[0].delta.content for chunk in stream if ...)
"""

from abc import abstractmethod
from typing import Dict, List, Any, Callable, Iterator
import time

from .base_client import StreamMetrics


class StreamingMixin:
    """流式处理混入类，提供通用的流式响应处理逻辑

    这个类封装了流式请求的通用逻辑，包括：
    - 时间戳记录（请求开始、首个 token、每个 token、请求结束）
    - 文本累积
    - 错误处理
    - 指标计算

    子类只需要实现 _create_stream_executor() 方法，提供特定协议的流式执行器。
    """

    def _execute_streaming_request(
        self,
        messages: List[Dict[str, str]],
        parameters: Dict[str, Any],
        stream_executor: Callable[[], Iterator[str]]
    ) -> StreamMetrics:
        """执行流式请求的通用逻辑

        这个方法实现了流式请求的完整生命周期：

        执行流程：
        1. 记录请求开始时间 (request_start)
        2. 调用 stream_executor 获取流式响应迭代器
        3. 遍历流式响应：
           - 记录首个 token 到达时间 (first_token_time)
           - 累积文本内容 (full_text)
           - 记录每个 token 的时间戳 (token_timestamps)
        4. 处理异常情况
        5. 计算并返回性能指标

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            parameters: 请求参数字典，包含：
                - max_tokens: 最大生成 token 数
                - temperature: 温度参数
                - 其他模型特定参数
            stream_executor: 流式执行器函数，返回一个迭代器
                迭代器产生 str 类型的文本片段

        Returns:
            StreamMetrics: 包含以下性能指标的对象：
                - ttft_ms: Time to First Token（首次响应时间，毫秒）
                - total_time_ms: 总响应时间（毫秒）
                - generation_time_ms: 生成时间（毫秒）
                - output_tokens: 输出 token 数量
                - tokens_per_second: 生成速度（tokens/秒）
                - inter_token_latency_ms: 平均 token 间延迟（毫秒）
                - text: 完整响应文本

        注意：
            - 即使发生错误，也会返回已收集的部分结果
            - 错误信息会打印到控制台
            - 使用 time.perf_counter() 确保高精度计时
        """
        # 记录请求开始时间（使用高精度计时器）
        request_start = time.perf_counter()

        # 初始化变量
        first_token_time = None
        token_timestamps = []
        full_text = ""

        try:
            # 执行流式请求（由具体客户端实现）
            # stream_executor 是一个迭代器，产生文本片段
            for text_chunk in stream_executor():
                # 记录首个 token 到达时间
                if first_token_time is None:
                    first_token_time = time.perf_counter()

                # 累积文本内容
                full_text += text_chunk

                # 记录每个 token 的时间戳
                token_timestamps.append(time.perf_counter())

            # 记录请求结束时间
            request_end = time.perf_counter()

            # 计算性能指标（由 BaseClient 提供）
            return self._calculate_metrics(
                request_start=request_start,
                first_token_time=first_token_time,
                request_end=request_end,
                token_timestamps=token_timestamps,
                text=full_text
            )

        except Exception as e:
            # 发生错误时，记录结束时间并返回部分结果
            request_end = time.perf_counter()
            print(f"流式请求出错: {e}")

            # 即使出错也返回已收集的部分结果
            return self._calculate_metrics(
                request_start=request_start,
                first_token_time=first_token_time,
                request_end=request_end,
                token_timestamps=token_timestamps,
                text=full_text
            )
