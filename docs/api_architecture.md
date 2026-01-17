# API 客户端架构

## 概述

本系统使用适配器模式支持多种 API 协议，包括 OpenAI 协议和 Anthropic 协议。通过抽象基类和混入类的设计，实现了代码复用和灵活扩展。

**核心目标**：
- 统一接口：所有 API 客户端提供相同的公共方法
- 流式优先：优先使用流式 API 以获取精确的 TTFT 指标
- 错误处理：优雅处理网络错误，返回部分结果
- 易于扩展：添加新 API 客户端只需实现少量方法

## 架构设计

### 类层次结构

```
BaseClient (抽象基类)
├── 定义统一的客户端接口
├── 提供性能指标计算
└── 管理模型信息

StreamingMixin (混入类)
├── 提供通用流式处理逻辑
├── 消除代码重复
└── 模板方法模式

OpenAIClient (OpenAI 协议)
├── 继承 StreamingMixin 和 BaseClient
├── 实现 OpenAI 特定的流式执行器
└── 用于 DeepSeek 等 OpenAI 兼容 API

AnthropicClient (Anthropic 协议)
├── 继承 StreamingMixin 和 BaseClient
├── 实现 Anthropic 特定的流式执行器
└── 用于 GLM、MiniMax 等 Anthropic 兼容 API

MiniMaxClient (MiniMax 专用)
├── 继承 BaseClient（不使用 StreamingMixin）
├── 处理特殊的认证和内容块格式
└── 用于 MiniMax Judge API
```

### 设计原则

#### 1. 单一职责原则
每个类只负责一个明确的职责：
- `BaseClient`: 定义接口和计算指标
- `StreamingMixin`: 提供流式处理逻辑
- 具体客户端类: 实现特定协议的适配

#### 2. 开闭原则
对扩展开放，对修改封闭：
- 新增 API 客户端只需继承基类
- 不需要修改现有代码

#### 3. 依赖倒置原则
依赖抽象而非具体实现：
- 所有代码依赖 `BaseClient` 接口
- 不依赖具体的客户端实现

#### 4. 模板方法模式
`StreamingMixin` 使用模板方法模式：
```python
# 基类提供算法框架
def _execute_streaming_request(self, ...):
    # 1. 记录开始时间
    # 2. 调用抽象方法（由子类实现）
    for text_chunk in stream_executor():
        # 3. 处理响应
    # 4. 计算指标

# 子类实现特定步骤
def stream_executor():
    # 返回特定协议的流式迭代器
```

## 核心组件详解

### 1. BaseClient (抽象基类)

**文件**: `src/api/base_client.py`

**职责**：
- 定义所有客户端的统一接口
- 提供性能指标计算方法
- 管理模型配置信息

**核心方法**：

```python
@abstractmethod
def stream_chat(self, messages, **kwargs) -> StreamMetrics:
    """流式聊天请求（抽象方法，子类必须实现）"""
    pass

@abstractmethod
def chat(self, messages, **kwargs) -> str:
    """非流式聊天请求（抽象方法，子类必须实现）"""
    pass

@abstractmethod
def validate_connection(self) -> bool:
    """验证 API 连接（抽象方法，子类必须实现）"""
    pass

def _calculate_metrics(self, ...) -> StreamMetrics:
    """计算性能指标（具体方法，所有子类共享）"""
    # TTFT、生成速度、token 间延迟等
```

**数据结构**：

```python
@dataclass
class StreamMetrics:
    """流式响应指标"""
    ttft_ms: float                    # 首次响应时间（毫秒）
    total_time_ms: float              # 总响应时间（毫秒）
    generation_time_ms: float         # 生成时间（毫秒）
    output_tokens: int                # 输出 token 数量
    tokens_per_second: float          # 生成速度（tokens/秒）
    inter_token_latency_ms: float     # 平均 token 间延迟（毫秒）
    text: str                         # 完整响应文本
```

### 2. StreamingMixin (混入类)

**文件**: `src/api/streaming_mixin.py`

**职责**：
- 提供通用的流式响应处理逻辑
- 消除 OpenAI 和 Anthropic 客户端的代码重复
- 实现时间戳记录和文本累积

**核心方法**：

```python
def _execute_streaming_request(
    self,
    messages: List[Dict[str, str]],
    parameters: Dict[str, Any],
    stream_executor: Callable[[], Iterator[str]]
) -> StreamMetrics:
    """
    执行流式请求的通用逻辑

    Args:
        messages: 消息列表
        parameters: 请求参数
        stream_executor: 流式执行器（由子类提供）

    Returns:
        StreamMetrics: 性能指标
    """
    request_start = time.perf_counter()
    first_token_time = None
    token_timestamps = []
    full_text = ""

    try:
        for text_chunk in stream_executor():
            if first_token_time is None:
                first_token_time = time.perf_counter()
            full_text += text_chunk
            token_timestamps.append(time.perf_counter())

        request_end = time.perf_counter()
        return self._calculate_metrics(...)

    except Exception as e:
        request_end = time.perf_counter()
        print(f"流式请求出错: {e}")
        return self._calculate_metrics(...)
```

**为什么使用混入类而不是直接在基类中实现？**

1. **灵活性**: 不是所有客户端都需要流式处理
2. **职责分离**: 将流式处理逻辑与基本接口定义分离
3. **代码复用**: OpenAI 和 Anthropic 客户端共享流式逻辑

### 3. OpenAIClient (OpenAI 协议)

**文件**: `src/api/openai_client.py`

**继承**: `StreamingMixin` + `BaseClient`

**支持的 API**：
- OpenAI 官方 API
- DeepSeek API（OpenAI 兼容）
- 其他 OpenAI 兼容的服务

**关键特性**：
- 使用 `openai` SDK
- 支持流式响应
- 自动重试机制（指数退避）

**实现要点**：

```python
class OpenAIClient(StreamingMixin, BaseClient):
    def stream_chat(self, messages, max_tokens=1024, temperature=0.7, **kwargs):
        # 创建 OpenAI 特定的流式执行器
        def stream_executor():
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        # 使用混入类的通用流式处理逻辑
        return self._execute_streaming_request(
            messages=messages,
            parameters={...},
            stream_executor=stream_executor
        )
```

### 4. AnthropicClient (Anthropic 协议)

**文件**: `src/api/anthropic_client.py`

**继承**: `StreamingMixin` + `BaseClient`

**支持的 API**：
- Anthropic 官方 API (Claude)
- GLM API（Anthropic 兼容）
- MiniMax API（Anthropic 兼容）

**关键特性**：
- 使用 `anthropic` SDK
- 支持多种内容块类型（TextBlock, ThinkingBlock）
- 流式文本流处理

**特殊处理**：

```python
def _extract_text_from_response(self, response) -> str:
    """
    从响应中提取文本内容，处理不同类型的内容块

    支持的内容块类型：
    - TextBlock: 标准 Anthropic 响应
    - ThinkingBlock: MiniMax 等特殊实现
    """
    text_parts = []
    for block in response.content:
        if hasattr(block, 'text'):
            text_parts.append(block.text)
        elif hasattr(block, 'thinking'):
            text_parts.append(block.thinking)
        else:
            text_parts.append(str(block))
    return ''.join(text_parts)
```

### 5. MiniMaxClient (MiniMax 专用)

**文件**: `src/api/minimax_client.py`

**继承**: 仅 `BaseClient`

**用途**：MiniMax Judge API

**特殊处理**：
- 自定义 HTTP 头格式（Bearer Token）
- 使用 `httpx` 直接请求
- 支持特殊的内容块解析

## 流式处理流程

### 完整流程图

```
┌─────────────────────────────────────────────────────────┐
│ 1. 用户调用 client.stream_chat(messages, ...)           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 客户端创建流式执行器 (stream_executor)                │
│    - OpenAI: _client.chat.completions.create(stream=True)│
│    - Anthropic: _client.messages.stream()              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 调用 _execute_streaming_request(stream_executor)    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 记录 request_start = time.perf_counter()             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. 遍历流式响应                                         │
│    for text_chunk in stream_executor():                 │
│      ├─ 首次 token？→ 记录 first_token_time             │
│      ├─ 累积文本: full_text += text_chunk               │
│      └─ 记录时间戳: token_timestamps.append(...)         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. 记录 request_end = time.perf_counter()               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 7. 计算性能指标                                         │
│    return self._calculate_metrics(...)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 8. 返回 StreamMetrics                                   │
│    - ttft_ms: 首次响应时间                              │
│    - total_time_ms: 总响应时间                          │
│    - tokens_per_second: 生成速度                        │
│    - text: 完整文本                                     │
└─────────────────────────────────────────────────────────┘
```

### 指标计算详解

#### TTFT (Time to First Token)

**定义**: 从发送请求到收到第一个 token 的时间

**计算公式**:
```python
TTFT = first_token_time - request_start
```

**意义**:
- 用户体验的关键指标
- 反映服务器响应速度
- 包括网络延迟和首 token 生成时间

#### 总响应时间

**定义**: 完整请求的持续时间

**计算公式**:
```python
total_time = request_end - request_start
```

#### 生成时间

**定义**: 从第一个 token 到最后一个 token 的时间

**计算公式**:
```python
generation_time = total_time - TTFT
```

#### 生成速度

**定义**: 每秒生成的 token 数量

**计算公式**:
```python
tokens_per_second = output_tokens / generation_time
```

**意义**:
- 衡量模型吞吐量
- 影响长文本生成体验

#### Token 间延迟

**定义**: 连续 token 之间的平均时间

**计算公式**:
```python
inter_token_latency = average(
    token_timestamps[i] - token_timestamps[i-1]
    for i in range(1, len(token_timestamps))
)
```

**意义**:
- 反映生成稳定性
- 延迟波动越小，体验越流畅

## 错误处理策略

### 重试机制

使用 `tenacity` 库实现指数退避：

```python
@retry(
    stop=stop_after_attempt(3),          # 最多重试 3 次
    wait=wait_exponential(
        multiplier=1,                    # 基础等待时间
        min=2,                          # 最小等待 2 秒
        max=10                          # 最大等待 10 秒
    ),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
def stream_chat(self, ...):
    # 流式请求实现
    pass
```

**重试策略**：
- 第 1 次失败：等待 2 秒后重试
- 第 2 次失败：等待 4 秒后重试
- 第 3 次失败：等待 8 秒后重试
- 3 次都失败：抛出异常

### 部分结果返回

即使发生错误，也返回已收集的部分结果：

```python
try:
    for text_chunk in stream_executor():
        full_text += text_chunk
        # ...
except Exception as e:
    # 即使出错也返回部分结果
    return self._calculate_metrics(
        request_start=request_start,
        first_token_time=first_token_time,
        request_end=request_end,
        token_timestamps=token_timestamps,
        text=full_text  # 已收集的部分文本
    )
```

**优势**：
- 不会因为网络中断而丢失所有数据
- 便于调试和问题定位
- 提供更好的用户体验

## 扩展新客户端

### 步骤指南

#### 1. 继承基类

```python
from src.api.base_client import BaseClient
from src.api.streaming_mixin import StreamingMixin

class NewAPIClient(StreamingMixin, BaseClient):
    """新 API 客户端"""
    pass
```

#### 2. 实现 `__init__`

```python
def __init__(
    self,
    base_url: str,
    api_key: str,
    model: str,
    max_retries: int = 3,
    timeout: int = 120
):
    super().__init__(base_url, api_key, model, max_retries, timeout)
    self._client = NewAPISDK(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries
    )
```

#### 3. 实现 `stream_chat`

```python
def stream_chat(
    self,
    messages: List[Dict[str, str]],
    max_tokens: int = 1024,
    temperature: float = 0.7,
    **kwargs
) -> StreamMetrics:
    # 创建流式执行器
    def stream_executor():
        stream = self._client.stream.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        for chunk in stream:
            yield chunk.text

    # 使用混入类的通用逻辑
    return self._execute_streaming_request(
        messages=messages,
        parameters={...},
        stream_executor=stream_executor
    )
```

#### 4. 实现 `chat`

```python
def chat(
    self,
    messages: List[Dict[str, str]],
    max_tokens: int = 1024,
    temperature: float = 0.7,
    **kwargs
) -> str:
    response = self._client.chat.create(
        model=self.model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs
    )
    return response.text
```

#### 5. 实现 `validate_connection`

```python
def validate_connection(self) -> bool:
    try:
        response = self._client.chat.create(
            model=self.model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True
    except Exception as e:
        print(f"连接验证失败: {e}")
        return False
```

#### 6. 在 `config.yaml` 中添加配置

```yaml
apis:
  new_api:
    base_url: "https://api.newapi.com/v1"
    api_key_env: "NEW_API_KEY"
    model: "new-model-v1"
    max_retries: 3
    timeout: 120
```

#### 7. 在 `BenchmarkRunner._init_clients()` 中注册

```python
def _init_clients(self):
    # ... 现有客户端初始化 ...

    elif api_name == "new_api":
        client = NewAPIClient(
            base_url=api_config["base_url"],
            api_key=api_key,
            model=api_config["model"],
            max_retries=api_config.get("max_retries", 3),
            timeout=api_config.get("timeout", 120)
        )

    self.clients[api_name] = client
```

## 性能优化建议

### 1. 连接池

对于高并发场景，使用连接池：

```python
from httpx import HTTPConnectionPool

self._client = OpenAI(
    http_client=httpx.Client(
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    )
)
```

### 2. 超时配置

根据任务类型调整超时：

```python
# 短任务
client = OpenAIClient(..., timeout=30)

# 长任务
client = OpenAIClient(..., timeout=300)
```

### 3. 批量请求

对于多个独立请求，使用异步：

```python
import asyncio

async def batch_stream_chat(clients, messages):
    tasks = [client.stream_chat(msg) for client in clients]
    results = await asyncio.gather(*tasks)
    return results
```

## 总结

API 客户端架构通过以下设计实现了高质量和可维护性：

1. **代码复用**: StreamingMixin 消除了约 150 行重复代码
2. **统一接口**: 所有客户端提供相同的 API
3. **易于扩展**: 添加新客户端只需实现少量方法
4. **错误处理**: 完善的重试和部分结果返回机制
5. **高精度计时**: 使用 `time.perf_counter()` 确保测量准确

这种架构为基准测试系统提供了坚实的基础，支持对多种 LLM API 进行公平、准确的性能对比。
