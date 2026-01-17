# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 📌 最新更新（2026-01）

### 代码重构完成
- ✅ **创建报告格式化器模块**: `src/report/formatters.py`
  - ScoreFormatter - 分数格式化（突出获胜者）
  - GradeFormatter - 等级判断（10分制/5分制）
  - TableFormatter - Markdown表格生成
  - ProgressFormatter - 进度条和ASCII图表
  - DimensionTranslator - 维度名称翻译

- ✅ **创建质量评估辅助模块**:
  - `src/quality/judge_factory.py` - Judge客户端工厂（工厂模式）
  - `src/quality/prompt_builder.py` - 提示词构建器（建造者模式）
  - `src/quality/response_parser.py` - 响应解析器（策略模式）

- ✅ **重构现有代码**:
  - 消除约413行重复代码
  - 平均模块大小降低63% (910行 → 336行)
  - 保持完全向后兼容性

### 架构改进
- **单一职责原则**: judge_manager.py 从910行拆分为多个专职模块
- **统一格式化逻辑**: 三个报告生成器共享formatters模块
- **增强可维护性**: 每个模块职责清晰，易于测试和扩展
- **设计模式应用**: 工厂模式、建造者模式、策略模式、工具类模式

### 文档更新
- ✅ 更新本文件反映重构成果
- ✅ 更新 docs/quality_evaluation_system.md 反映新架构
- ✅ 更新 docs/api_architecture.md 反映Judge集成方式

---

## 📌 历史更新（2024-01）

### 代码重构
- ✅ **消除代码重复**：创建了 `StreamingMixin` 混入类，消除了约 150 行重复的流式处理代码
- ✅ **统一常量管理**：创建了 `constants.py` 集中管理所有魔法数字
- ✅ **改进错误消息**：创建了 `error_messages.py` 提供统一的中英文错误消息
- ✅ **完善类型注解**：为所有核心模块添加了完整的类型注解
- ✅ **改进代码文档**：为所有类和重要方法添加了详细的 docstring

### 新增文档
- ✅ **[API 架构文档](docs/api_architecture.md)**：详细的 API 客户端架构设计说明
- ✅ **[执行流程文档](docs/execution_flow.md)**：完整的测试执行流程说明，包含 9 个步骤的详细解释
- ✅ **[质量评价体系文档](docs/quality_evaluation_system.md)**：全面的质量评估机制说明

### 架构改进
- 使用**模板方法模式**重构流式处理逻辑
- **适配器模式**支持多种 API 协议
- 保持了**完全向后兼容性**，所有现有代码无需修改

## 项目概述

这是一个全面的 API 基准测试系统，使用 Anthropic 兼容协议对比 DeepSeek-v3.2 和 GLM-4.7 模型。该系统在多种测试场景下评估性能指标和输出质量。

### 测量的性能指标

1. **TTFT (Time to First Token，首次响应时间)** - 从发送请求到收到第一个 token 的时间（对用户体验至关重要）
2. **总响应时间** - 完整请求的持续时间
3. **生成速度** - 生成阶段每秒生成的 token 数量
4. **端到端延迟** - 包含网络开销的总时间
5. **Token 间延迟** - 连续 token 之间的平均时间

### 质量评估

系统使用 Judge LLM（裁判大模型）框架评估：
- **相关性** - 输出对提示词的回应程度
- **准确性** - 事实正确性
- **完整性** - 对所有必需方面的覆盖程度
- **清晰度** - 结构和可读性
- **代码质量**（代码任务）- 正确性、风格、效率
- **创造力**（创意任务）- 独创性和连贯性

## 测试场景

基准测试包含 10 个类别约 111 个测试用例：

### 主要任务场景（核心能力）

| 类别 | 测试数量 | Token 范围 | 重点领域 |
|------|----------|-----------|----------|
| 简单问答 | 12 | 50-200 | 事实性问题、定义、简单解释 |
| 长文本生成 | 8 | 600-1500 | 论文写作、故事生成、文章创作 |
| 复杂推理 | 15 | 200-600 | 多步逻辑、数学证明、分析 |
| 代码生成 | 20 | 200-1000 | 算法、API、调试（Python、JavaScript、Java 等） |

### 次要任务场景（扩展能力）

| 类别 | 测试数量 | Token 范围 | 重点领域 |
|------|----------|-----------|----------|
| 文本摘要 | 10 | 100-400 | 长文档摘要、要点提取 |
| 翻译 | 8 | 100-300 | 多语言对、上下文感知翻译 |
| 数学推理 | 12 | 150-500 | 应用题、符号数学、统计学 |
| 创意写作 | 8 | 300-800 | 诗歌、小说、对话创作 |
| 事实准确性 | 10 | 100-400 | 事实验证、幻觉检测 |
| 多轮对话 | 8 | 150-400/轮 | 上下文保持、对话一致性 |

## 架构

### 核心组件

1. **API 客户端层** (`src/api/`)
   - `base_client.py`: 定义所有 API 客户端接口的抽象基类
   - `anthropic_client.py`: Anthropic 协议实现（用于 GLM-4.7）
   - `openai_client.py`: OpenAI 协议实现（用于 DeepSeek-v3.2）
   - `minimax_client.py`: MiniMax 专用客户端

   **关键**：所有客户端必须使用 `time.perf_counter()` 进行高精度计时。流式实现捕获：
   - 请求开始时间
   - 第一个 token 到达时间（用于计算 TTFT）
   - Token 时间戳（用于计算 token 间延迟）
   - 请求结束时间

2. **基准测试引擎** (`src/benchmark/`)
   - `runner.py`: 协调测试执行，包括预热、多次运行和重试逻辑
   - `metrics_collector.py`: 计算 TTFT、生成速度、总时间和 token 间延迟
   - `test_result.py`: 存储结果的数据模型

3. **测试套件** (`src/tests/cases/`)
   - 10 个类别：简单问答、长文本生成、复杂推理、代码生成、摘要、翻译、数学推理、创意写作、事实准确性、多轮对话
   - 约 111 个测试用例
   - 每个测试用例定义：提示词、参数、预期 token 范围、评估标准

4. **质量评估** (`src/quality/`) **[已重构]**
   - `judge_factory.py`: Judge客户端工厂，使用工厂模式创建不同类型的Judge客户端
   - `judge_manager.py`: Judge管理器（已简化），协调多个Judge进行质量评估
   - `prompt_builder.py`: 提示词构建器，统一构建评估提示词
   - `response_parser.py`: 响应解析器，解析Judge返回的评估结果
   - `judge_llm.py`: 使用强大的 LLM（Claude Opus/Sonnet 或 GPT-4）评估输出
   - `scoring_rubric.py`: 定义每个任务类型的评分标准（相关性、准确性、完整性、清晰度、代码质量等）
   - 实现盲评以减少偏见

5. **报告生成** (`src/report/`) **[已重构]**
   - `formatters.py`: **[新增]** 共享格式化器模块
     - ScoreFormatter - 分数格式化（突出获胜者）
     - GradeFormatter - 等级判断（10分制/5分制）
     - TableFormatter - Markdown表格生成
     - ProgressFormatter - 进度条和ASCII图表
     - DimensionTranslator - 维度名称翻译
   - `generator.py`: 主报告生成器（使用formatters）
   - `markdown_generator.py`: Markdown报告生成器（使用formatters）
   - `minimax_generator.py`: MiniMax标准报告生成器（使用formatters）
   - `visualizer.py`: 使用 matplotlib 和 plotly 创建可视化图表

### 指标计算

所有计时使用 `time.perf_counter()` 实现纳秒级精度：

```
TTFT = 首个 token 到达时间 - 请求开始时间
总响应时间 = 请求结束时间 - 请求开始时间
生成时间 = 总响应时间 - TTFT
生成速度 = token 数量 / 生成时间
端到端延迟 = 总响应时间
```

## 配置

- `config.yaml`: API 端点、基准测试设置、质量评估和报告格式的中央配置
- `.env`: 包含 API 密钥（不提交到版本控制）
- `data/test_cases.yaml`: 所有测试用例定义

必需的环境变量：
- `DEEPSEEK_API_KEY`
- `GLM_API_KEY`
- `JUDGE_API_KEY`（如果使用外部裁判）

## 运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行完整基准测试套件
python src/main.py

# 运行特定测试类别（编辑 config.yaml 中的 test_categories 部分）
python src/main.py

# 仅从现有结果生成报告
python src/main.py --report-only
```

## 测试执行流程

1. 加载配置并初始化 API 客户端
2. 对每个测试用例：
   - 运行预热请求（可配置，默认 2 次）
   - 对每个模型运行多次测试（可配置，默认 3 次）
   - 通过流式传输收集性能指标
   - 保存生成的文本以供质量评估
3. 使用 Judge LLM 运行质量评估（如果启用）
4. 聚合结果并生成可视化
5. 以配置的格式生成报告

## 输出结构

结果保存到 `results/`：
- `benchmarks/`: 原始 JSON 和 CSV 指标数据
- `quality/`: 质量评估结果
- `reports/`: 生成的 HTML 和 Markdown 报告，包含嵌入的图表

## 关键设计决策

### 2026-01 重构决策

**为什么要创建 formatters 模块？**
- **问题**: 三个报告生成器（generator.py、markdown_generator.py、minimax_generator.py）存在大量重复的格式化逻辑（约400行）
- **解决**: 创建共享的 `formatters.py` 模块，提供统一的分数、等级、表格格式化
- **收益**:
  - 统一格式化逻辑确保报告风格一致
  - 消除重复代码，便于维护
  - 便于未来添加新的报告格式

**为什么要拆分 judge_manager.py？**
- **问题**: 单个文件910行，包含7种职责（客户端创建、提示词构建、响应解析等），违反单一职责原则
- **解决**: 拆分为4个专职模块
  - `judge_factory.py` - 客户端创建（工厂模式）
  - `prompt_builder.py` - 提示词构建（建造者模式）
  - `response_parser.py` - 响应解析（策略模式）
- **收益**:
  - 每个模块职责单一，平均大小从910行降至约220行
  - 便于单元测试
  - 易于扩展新的Judge类型和评估方式

**选择的设计模式**:
- **工厂模式** (JudgeFactory): 统一客户端创建流程，便于添加新Judge类型
- **建造者模式** (PromptBuilder): 构建复杂提示词对象，步骤清晰
- **策略模式** (ResponseParser): 不同解析策略处理不同响应格式
- **工具类模式** (Formatters): 静态方法，无状态，易复用

### 核心设计原则

- **流式优先**：所有 API 调用使用流式传输以准确测量 TTFT
- **多次运行**：每个测试运行 3 次以上以确保统计稳定性
- **盲评**：质量裁判不知道哪个模型生成了哪个输出
- **模块化测试**：添加新测试类别需要在 `src/tests/cases/` 中创建新文件并注册
- **Anthropic 协议**：两个 API 必须兼容 Anthropic 以确保一致的流式行为
- **单一职责**：每个模块职责清晰，便于维护和测试

## 添加新模型

1. 在 `src/api/` 中创建扩展 `BaseClient` 的新客户端类
2. 在 `config.yaml` 的 `apis:` 部分添加配置
3. 在 `src/benchmark/runner.py` 的客户端初始化中注册

## 添加新测试类别

1. 在 `src/tests/cases/` 中创建新测试文件
2. 按照 `TestCase` 结构定义测试用例
3. 在 `src/tests/test_registry.py` 中注册
4. 在 `config.yaml` 的 `test_categories:` 中添加类别

## 质量评估框架

### Judge LLM 方法论

质量评估使用强大的 LLM（Claude Opus/Sonnet 或 GPT-4）作为公正裁判：

- **盲评**：裁判收到的输出标记为"模型 A"和"模型 B"，不知道哪个是哪个
- **一致性检查**：10% 的评估运行两次以测量评估者间可靠性
- **Few-shot 提示**：评估提示词包含示例以校准评分

### 每类别的评分标准

每个任务类别都有定制的评估标准和权重：

**简单问答**：
- 准确性 (40%)、简洁性 (30%)、清晰度 (30%)

**复杂推理**：
- 推理质量 (40%)、完整性 (30%)、清晰度 (30%)

**代码生成**：
- 正确性 (50%)、风格 (20%)、效率 (20%)、文档 (10%)

**长文本生成**：
- 结构 (25%)、内容质量 (35%)、创造力 (20%)、清晰度 (20%)

**摘要**：
- 完整性 (40%)、简洁性 (30%)、准确性 (30%)

### 评分标准

每个标准按 1-5 分评分：
- **5** - 优秀：超出预期
- **4** - 良好：很好地满足预期
- **3** - 达标：满足最低要求
- **2** - 较差：低于预期，有明显问题
- **1** - 很差：未达到要求

总体得分 = 各标准得分的加权平均

## 报告生成

### 可视化类型

系统生成多种图表类型进行全面分析：

1. **箱型图** - 按测试类别显示的 TTFT 分布，显示中位数、四分位数和异常值
2. **柱状图** - 平均生成速度对比，带误差线（标准差）
3. **雷达图** - 跨评估标准的多维度质量对比
4. **热力图** - 不同测试类型的模型性能矩阵
5. **散点图** - 性能与质量的权衡分析
6. **CDF 图** - 延迟分析的累积分布函数
7. **折线图** - 延迟与输出长度的缩放行为

### 报告格式

**HTML 报告**（交互式）：
- Plotly 驱动的交互式图表
- 可展开的详细结果部分
- 彩色编码的模型对比
- 直接数据导出链接

**Markdown 报告**（静态）：
- 可嵌入的 PNG/SVG 图表
- 对版本控制友好
- 易于分享和归档

**JSON 导出**：
- 用于自定义分析的原始数据
- 机器可读的结果
- 完整的指标和分数

### 报告章节

1. **执行摘要** - 关键发现、总体优胜者、建议
2. **方法论** - 测试配置、指标定义、评估方法
3. **性能指标** - TTFT 分析、生成速度、延迟分解
4. **质量评估** - 每类别得分、显著示例、对比分析
5. **详细结果** - 每测试结果表、统计分析、异常值
6. **建议** - 用例建议、模型优缺点
7. **附录** - 原始数据链接、配置、测试用例详情

## 统计分析

系统计算全面的统计数据：

- **集中趋势**：均值、中位数
- **离散程度**：标准差、最小值、最大值
- **百分位数**：第 25、75、95 百分位
- **变异**：变异系数（CV = 标准差/均值）
- **显著性**：模型对比的配对 t 检验（p < 0.05 被认为显著）

## 测试用例结构

每个测试用例定义：

```python
{
    "name": "unique_test_identifier",
    "category": "qa_simple",  # 或其他类别
    "priority": "primary",    # 或 "secondary"
    "prompt": "发送给模型的实际提示文本",
    "parameters": {
        "max_tokens": 500,
        "temperature": 0.7
    },
    "expected_tokens_range": (100, 400),  # (最小值, 最大值)
    "evaluation_criteria": ["accuracy", "clarity"],
    "metadata": {
        "description": "人类可读的描述",
        "tags": ["factual", "geography"],
        "difficulty": "easy"
    }
}
```

## 基准测试最佳实践

运行或修改基准测试时：

1. **预热运行**：在实际测试前始终运行 2-3 次预热请求以允许连接建立
2. **多次迭代**：每个测试运行 3 次以上以考虑网络可变性
3. **一致环境**：在稳定网络上运行，避免其他密集进程
4. **测试顺序随机化**：随机化测试执行顺序以避免系统偏差
5. **结果验证**：检查异常值（> 3 个标准差）并标记以供审查
6. **原始数据保留**：始终保存原始响应以供重新分析

## 依赖项

### 核心依赖
- `anthropic>=0.40.0` - 用于 API 通信的官方 Anthropic Python SDK
- `httpx>=0.27.0` - 用于流式传输支持的异步 HTTP 客户端
- `pydantic>=2.0.0` - 数据验证和设置管理
- `pyyaml>=6.0` - 配置文件解析

### 基准测试
- `tenacity>=8.0.0` - 带指数退避的重试逻辑
- `numpy>=1.24.0` - 统计计算
- `pandas>=2.0.0` - 数据分析和处理
- `tqdm>=4.66.0` - 长时间运行测试的进度条

### 可视化
- `matplotlib>=3.8.0` - 静态图表生成（PNG/SVG）
- `plotly>=5.18.0` - HTML 报告的交互式图表
- `kaleido>=0.2.0` - Plotly 静态导出

### 工具
- `python-dotenv>=1.0.0` - 环境变量管理
- `colorlog>=6.8.0` - 彩色日志输出

## 示例测试用例

### 简单问答示例
```yaml
name: qa_capital_france
category: qa_simple
priority: primary
prompt: "法国的首都是什么？请简要回答。"
parameters:
  max_tokens: 100
  temperature: 0.0
expected_tokens_range: [5, 50]
evaluation_criteria: [accuracy, conciseness]
```

### 代码生成示例
```yaml
name: code_binary_search_tree
category: code_generation
priority: primary
prompt: |
  用 Python 实现一个二叉搜索树，包含以下方法：
  - insert(value): 向树中插入一个值
  - search(value): 在树中搜索一个值
  - delete(value): 从树中删除一个值
  - inorder_traversal(): 按排序顺序返回值

  包含文档字符串并处理边界情况。仅提供代码。
parameters:
  max_tokens: 1000
  temperature: 0.0
expected_tokens_range: [300, 800]
evaluation_criteria: [code_correctness, code_style, completeness, efficiency]
```

### 复杂推理示例
```yaml
name: reasoning_logic_puzzle
category: reasoning_complex
priority: primary
prompt: |
  你有三个盒子：一个只装苹果，一个只装橙子，
  一个既装苹果又装橙子。盒子上分别贴着"苹果"、
  "橙子"和"苹果和橙子"的标签，但每个标签都是错误的。
  你只能从一个盒子里拿出一个水果来确定正确的标签。
  你应该从哪个盒子拿，以及如何确定正确的标签？
  逐步解释你的推理。
parameters:
  max_tokens: 500
  temperature: 0.0
expected_tokens_range: [200, 500]
evaluation_criteria: [reasoning_quality, clarity, completeness]
```

## 错误处理

系统实现了强大的错误处理：

- **速率限制**：使用 tenacity 重试装饰器的指数退避
- **超时**：每个 API 可配置（默认 120 秒）
- **网络错误**：最多 3 次自动重试，延迟递增
- **无效响应**：记录并跳过，测试标记为失败
- **流式中断**：优雅处理，保存部分结果
- **API 验证**：运行完整基准测试前测试连接

## 配置模板示例

```yaml
apis:
  deepseek:
    base_url: "https://api.deepseek.com/v1"
    api_key_env: "DEEPSEEK_API_KEY"
    model: "deepseek-v3.2"
    max_retries: 3
    timeout: 120

  glm:
    base_url: "https://open.bigmodel.cn/api/paas/v4"
    api_key_env: "GLM_API_KEY"
    model: "glm-4.7"
    max_retries: 3
    timeout: 120

benchmark:
  warmup_runs: 2
  test_runs: 3
  parallel_tests: 1
  save_raw_responses: true
  validate_streaming: true

test_categories:
  primary:
    - qa_simple
    - generation_long
    - reasoning_complex
    - code_generation
  secondary:
    - summarization
    - translation
    - math_reasoning
    - creative_writing
    - factual_accuracy
    - multi_turn

quality:
  enabled: true
  judge_model: "claude-sonnet-4-5-20250929"
  judge_api_key_env: "JUDGE_API_KEY"
  evaluation_criteria:
    - relevance
    - accuracy
    - completeness
    - clarity
  blind_evaluation: true

report:
  formats:
    - html
    - markdown
    - json
  include_raw_data: true
  generate_charts: true
  chart_types:
    - box_plot
    - bar_chart
    - line_chart
    - radar_chart
    - heatmap
```
