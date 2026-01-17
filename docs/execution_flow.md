# 测试执行流程详解

## 概述

本文档详细说明基准测试系统的完整执行流程，从配置加载到报告生成。系统通过 `run_benchmark.py` 脚本驱动，支持多种运行模式。

**运行模式**：
- `standard`: 完整 MiniMax 标准评测（100个用例）
- `preview`: 预测试（每个维度1个用例，共4个）
- `single`: 单用例测试（1个用例）
- `original`: 原始对比测试（每类别1个用例）

## 整体流程图

```
┌─────────────────────────────────────────────────────────┐
│ 1. 加载配置文件 (config.yaml)                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 验证配置有效性                                       │
│    - 检查必需配置节                                     │
│    - 验证 API 密钥                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 初始化 API 客户端                                    │
│    - DeepSeek (OpenAI 协议)                            │
│    - GLM (Anthropic 协议)                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 验证 API 连接                                        │
│    - 发送测试请求                                       │
│    - 确认连接可用                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. 预热阶段                                            │
│    - 每个模型 2 次预热请求                              │
│    - 建立 TCP 连接                                      │
│    - 预热模型缓存                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. 正式测试阶段                                        │
│    - 遍历所有测试用例                                   │
│    - 每个测试运行 3 次                                  │
│    - 收集性能指标                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 7. 质量评估 (可选)                                     │
│    - 多个 Judge 并行评估                                │
│    - 计算加权评分                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 8. 数据聚合和统计                                       │
│    - 计算均值、中位数、标准差                           │
│    - 生成汇总统计                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 9. 报告生成                                            │
│    - 保存 JSON 数据                                     │
│    - 生成 Markdown 报告                                 │
│    - 生成 HTML 报告                                     │
└─────────────────────────────────────────────────────────┘
```

## 详细步骤说明

### 步骤 1：配置加载

**文件**: `src/utils/config_loader.py`

**函数**: `load_config()`

**执行内容**：
```python
# 1. 加载环境变量 (.env 文件)
load_dotenv()

# 2. 解析 YAML 配置文件
config = load_config("config.yaml")

# 3. 返回配置字典
return config
```

**配置结构**：
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
  warmup_runs: 2        # 预热次数
  test_runs: 3          # 每个测试的运行次数
  parallel_tests: 1     # 并行测试数
  save_raw_responses: true
  validate_streaming: true

quality:
  enabled: true
  judges:
    deepseek_judge:
      enabled: true
      type: "deepseek"
      weight: 0.30
    glm_judge:
      enabled: true
      type: "glm"
      weight: 0.30
    minimax_judge:
      enabled: true
      type: "minimax"
      weight: 0.40

report:
  formats:
    - html
    - markdown
    - json
  include_raw_data: true
  generate_charts: true
```

### 步骤 2：配置验证

**函数**: `validate_config()`

**验证项**：
```python
# 1. 检查必需的配置节
required_sections = ["apis", "benchmark", "quality", "report"]
for section in required_sections:
    if section not in config:
        raise ConfigError(f"缺少必需的配置节: {section}")

# 2. 验证至少配置了一个 API
if not config.get("apis"):
    raise ConfigError("未配置任何 API")

# 3. 验证 API 密钥环境变量（警告）
for api_name, api_config in config["apis"].items():
    api_key_env = api_config.get("api_key_env", "")
    if not os.getenv(api_key_env):
        print(f"警告: 未找到 {api_name} 的 API key ({api_key_env})")
```

### 步骤 3：客户端初始化

**文件**: `src/benchmark/runner.py`

**类**: `BenchmarkRunner`

**方法**: `_init_clients()`

**初始化流程**：
```python
def _init_clients(self):
    api_configs = self.config.get("apis", {})

    for api_name, api_config in api_configs.items():
        # 从环境变量获取 API key
        api_key = os.getenv(api_config.get("api_key_env", ""))
        if not api_key:
            print(f"警告: 未找到 {api_name} 的 API key，跳过初始化")
            continue

        # 根据配置决定使用哪个协议
        if api_name == "deepseek":
            # DeepSeek 使用 OpenAI 协议
            client = OpenAIClient(
                base_url=api_config["base_url"],
                api_key=api_key,
                model=api_config["model"],
                max_retries=api_config.get("max_retries", 3),
                timeout=api_config.get("timeout", 120)
            )

        elif api_name == "glm":
            # GLM 使用 Anthropic 协议
            client = AnthropicClient(
                base_url=api_config["base_url"],
                api_key=api_key,
                model=api_config["model"],
                max_retries=api_config.get("max_retries", 3),
                timeout=api_config.get("timeout", 120)
            )

        self.clients[api_name] = client
        print(f"✓ {api_name} 客户端初始化成功")
```

**客户端存储**：
```python
self.clients = {
    "deepseek": OpenAIClient(...),
    "glm": AnthropicClient(...)
}
```

### 步骤 4：连接验证

**方法**: `validate_connections()`

**验证方式**：
```python
def validate_connections(self) -> Dict[str, bool]:
    results = {}
    for name, client in self.clients.items():
        print(f"验证 {name} 连接...")
        results[name] = client.validate_connection()
        status = "✓ 成功" if results[name] else "✗ 失败"
        print(f"{name}: {status}")
    return results
```

**验证逻辑**：
```python
def validate_connection(self) -> bool:
    try:
        # 发送一个简单的测试请求
        response = self._client.chat.completions.create(
            model=self.model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True
    except Exception as e:
        print(f"连接验证失败: {e}")
        return False
```

**示例输出**：
```
验证 deepseek 连接...
deepseek: ✓ 成功
验证 glm 连接...
glm: ✓ 成功
```

### 步骤 5：预热阶段

**目的**：
- 建立 TCP 连接
- 预热模型缓存
- 稳定网络延迟

**执行**：
```python
# 从配置获取预热次数
warmup_runs = self.config.get("benchmark", {}).get("warmup_runs", 2)

print("预热阶段...")
for client_name in client_names:
    for i in range(warmup_runs):  # 默认 2 次
        try:
            client = self.clients[client_name]
            client.stream_chat(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            print(f"  {client_name} 预热 {i+1}/{warmup_runs} 完成")
        except Exception as e:
            print(f"  {client_name} 预热 {i+1}/{warmup_runs} 失败: {e}")
```

**示例输出**：
```
预热阶段...
  deepseek 预热 1/2 完成
  deepseek 预热 2/2 完成
  glm 预热 1/2 完成
  glm 预热 2/2 完成
```

### 步骤 6：正式测试

**方法**: `run_benchmark()`

**测试循环**：
```python
def run_benchmark(self, test_cases, show_progress=True):
    benchmark_config = self.config.get("benchmark", {})
    warmup_runs = benchmark_config.get("warmup_runs", 2)
    test_runs = benchmark_config.get("test_runs", 3)  # 默认 3 次

    client_names = list(self.clients.keys())
    total_runs = len(test_cases) * len(client_names) * test_runs

    print(f"\n开始基准测试:")
    print(f"  - 测试用例: {len(test_cases)}")
    print(f"  - 模型: {', '.join(client_names)}")
    print(f"  - 预热运行: {warmup_runs} 次/模型")
    print(f"  - 正式运行: {test_runs} 次/测试")

    # 遍历所有测试用例
    for test_case in test_cases:
        test_name = test_case["name"]
        category = test_case["category"]

        # 遍历所有模型
        for client_name in client_names:
            # 每个测试运行多次
            for run_num in range(1, test_runs + 1):
                # 运行测试
                result = self.run_test_case(test_case, client_name, run_num)

                # 添加到收集器
                self.metrics_collector.add_result(result)

                # 如果失败，打印警告
                if not result.success:
                    print(f"  ✗ {client_name} - {test_name} (运行 {run_num}/{test_runs}) 失败")
```

**单次测试流程**：
```python
def run_test_case(self, test_case, client_name, run_number):
    client = self.clients[client_name]

    try:
        # 1. 提取测试参数
        messages = [{"role": "user", "content": test_case["prompt"]}]
        parameters = test_case.get("parameters", {})

        # 2. 执行流式请求
        metrics = client.stream_chat(
            messages=messages,
            **parameters
        )

        # 3. 创建测试结果
        result = TestResult(
            model_name=client_name,
            test_name=test_case["name"],
            test_category=test_case["category"],
            run_number=run_number,
            ttft_ms=metrics.ttft_ms,
            total_time_ms=metrics.total_time_ms,
            generation_time_ms=metrics.generation_time_ms,
            output_tokens=metrics.output_tokens,
            tokens_per_second=metrics.tokens_per_second,
            inter_token_latency_ms=metrics.inter_token_latency_ms,
            output_text=metrics.text,
            success=True,
            parameters=parameters
        )

        # 4. 质量评估（如果启用）
        if self.quality_enabled and result.success and result.output_text:
            try:
                evaluations = self.judge_manager.evaluate_single_output(
                    output=result.output_text,
                    category=test_case["category"],
                    prompt=test_case["prompt"],
                    model_name=client_name,
                    test_name=test_case["name"]
                )
                result.quality_evaluations = evaluations
            except Exception as e:
                print(f"  ⚠ 质量评估失败: {e}")

        return result

    except Exception as e:
        # 发生错误，创建失败的结果对象
        return TestResult(
            model_name=client_name,
            test_name=test_case["name"],
            test_category=test_case["category"],
            run_number=run_number,
            success=False,
            error_message=str(e),
            parameters=test_case.get("parameters", {})
        )
```

### 步骤 7：质量评估

**涉及模块**:
- `src/quality/judge_factory.py` - Judge客户端工厂 **[2026-01新增]**
- `src/quality/judge_manager.py` - Judge管理器（已简化）
- `src/quality/prompt_builder.py` - 提示词构建器 **[2026-01新增]**
- `src/quality/response_parser.py` - 响应解析器 **[2026-01新增]**

**类**: `JudgeManager`

**2026-01 架构更新**:
质量评估系统已进行模块化重构：
- 客户端创建职责移至 `JudgeFactory`
- 提示词构建职责移至 `PromptBuilder`
- 响应解析职责移至 `ResponseParser`
- `JudgeManager` 现专注于协调评估流程

**评估流程**：
```python
def evaluate_single_output(self, output, category, prompt, model_name, test_name):
    if not self.enabled or not self.judges:
        return {}

    evaluations = {}
    mode = self.evaluation_strategy.get("mode", "parallel")

    if mode == "parallel":
        # 并行评估（默认）
        evaluations = self._evaluate_parallel(
            output, category, prompt, model_name, test_name
        )
    else:
        # 顺序评估
        evaluations = self._evaluate_sequential(
            output, category, prompt, model_name, test_name
        )

    return evaluations
```

**并行评估实现**：
```python
def _evaluate_parallel(self, output, category, prompt, model_name, test_name):
    evaluations = {}

    with ThreadPoolExecutor(max_workers=len(self.judges)) as executor:
        # 提交所有评估任务
        future_to_judge = {}
        for judge_name, judge_info in self.judges.items():
            future = executor.submit(
                self._evaluate_with_judge,
                judge_name,
                judge_info,
                output,
                category,
                prompt,
                model_name,
                test_name
            )
            future_to_judge[future] = judge_name

        # 收集结果
        for future in as_completed(future_to_judge):
            judge_name = future_to_judge[future]
            try:
                evaluation = future.result()
                if evaluation:
                    evaluations[judge_name] = evaluation
            except Exception as e:
                print(f"Judge {judge_name} 评估失败: {e}")

    return evaluations
```

**单个 Judge 评估流程**：
```python
def _evaluate_with_judge(self, judge_name, judge_info, output, category, prompt, model_name, test_name):
    # 1. 获取评分标准
    rubric = ScoringRubric.get_rubric(category)

    # 2. 构建评估提示词
    evaluation_prompt = self._build_evaluation_prompt(
        prompt=prompt,
        output=output,
        category=category,
        rubric=rubric,
        blind=config.get("blind_evaluation", True)
    )

    # 3. 调用 Judge API
    response_text = self._call_judge_api(client, evaluation_prompt, config)

    # 4. 解析评估结果
    evaluation_result = self._parse_evaluation_response(
        response_text,
        rubric["criteria"],
        category
    )

    # 5. 计算总体分数
    overall_score = ScoringRubric.calculate_overall_score(
        category, evaluation_result["scores"]
    )

    # 6. 创建 JudgeEvaluation 对象
    return JudgeEvaluation(
        judge_name=judge_name,
        scores=evaluation_result["scores"],
        overall_score=overall_score,
        strengths=evaluation_result.get("strengths", []),
        weaknesses=evaluation_result.get("weaknesses", []),
        reasoning=evaluation_result.get("reasoning", "")
    )
```

### 步骤 8：数据聚合和统计

**文件**: `src/benchmark/metrics_collector.py`

**类**: `MetricsCollector`

**收集的数据**：
```python
class MetricsCollector:
    def __init__(self):
        self.results: List[TestResult] = []  # 原始测试结果
        self.start_time = datetime.now()

    def add_result(self, result: TestResult):
        """添加单个测试结果"""
        self.results.append(result)
```

**汇总统计计算**：
```python
def calculate_category_summary(self, model_name, category):
    """计算特定模型和类别的汇总统计"""
    results = self.get_results_by_model_and_category(model_name, category)

    # 提取各项指标
    ttfts = [r.ttft_ms for r in results if r.success]
    speeds = [r.tokens_per_second for r in results if r.success]
    total_times = [r.total_time_ms for r in results if r.success]

    # 使用 numpy 计算统计量
    return CategorySummary(
        model_name=model_name,
        category=category,
        test_count=len(results),
        success_count=len([r for r in results if r.success]),

        # TTFT 统计
        ttft_mean=float(np.mean(ttfts)) if ttfts else 0.0,
        ttft_median=float(np.median(ttfts)) if ttfts else 0.0,
        ttft_std=float(np.std(ttfts)) if ttfts else 0.0,
        ttft_min=float(np.min(ttfts)) if ttfts else 0.0,
        ttft_max=float(np.max(ttfts)) if ttfts else 0.0,

        # 生成速度统计
        speed_mean=float(np.mean(speeds)) if speeds else 0.0,
        speed_median=float(np.median(speeds)) if speeds else 0.0,
        speed_std=float(np.std(speeds)) if speeds else 0.0,
        speed_min=float(np.min(speeds)) if speeds else 0.0,
        speed_max=float(np.max(speeds)) if speeds else 0.0,

        # 总时间统计
        total_time_mean=float(np.mean(total_times)) if total_times else 0.0,
        total_time_median=float(np.median(total_times)) if total_times else 0.0,
    )
```

### 步骤 9：报告生成

**文件**：
- `src/utils/json_saver.py` - JSON 保存
- `src/report/markdown_generator.py` - Markdown 报告
- `src/report/generator.py` - HTML 报告

**生成内容**：
```python
# 1. 保存 JSON 数据
json_saver = BenchmarkJSONSaver()
json_path = json_saver.save_evaluation_data(
    statistics=statistics,
    quality_scores=quality_scores,
    summaries=[s.to_dict() for s in summaries],
    raw_results=raw_results,
    dimension_weights=dimension_weights,
    quality_evaluations=quality_evaluations,
    config=config
)

# 2. 从 JSON 生成 Markdown 报告
md_generator = MarkdownReportGenerator()
md_path = md_generator.generate_from_json(json_path)

# 3. 生成 HTML 报告
report_generator = MiniMaxReportGenerator(config.get("report", {}))
report_path = report_generator.generate_minimax_report(
    statistics=statistics,
    quality_scores=quality_scores,
    performance_data=raw_results,
    model_names=model_names,
    dimension_weights=dimension_weights
)
```

## 数据流转

### 数据结构

```
配置 (config.yaml)
  │
  ▼
TestResult (单次测试)
  │
  ├─ model_name: str
  ├─ test_name: str
  ├─ test_category: str
  ├─ run_number: int
  ├─ ttft_ms: float
  ├─ total_time_ms: float
  ├─ generation_time_ms: float
  ├─ output_tokens: int
  ├─ tokens_per_second: float
  ├─ inter_token_latency_ms: float
  ├─ output_text: str
  ├─ success: bool
  ├─ error_message: Optional[str]
  ├─ parameters: Dict[str, Any]
  └─ quality_evaluations: Dict[str, JudgeEvaluation]
  │
  ▼
MetricsCollector (聚合)
  │
  ├─ results: List[TestResult]
  ├─ start_time: datetime
  ├─ calculate_category_summary()
  └─ get_statistics()
  │
  ▼
CategorySummary (类别汇总)
  │
  ├─ model_name: str
  ├─ category: str
  ├─ test_count: int
  ├─ ttft_mean/median/std/min/max
  ├─ speed_mean/median/std/min/max
  └─ total_time_mean/median
  │
  ▼
报告
  ├─ JSON (原始数据)
  ├─ Markdown (可读报告)
  └─ HTML (可视化报告)
```

## 关键配置参数

### 预热配置
```yaml
benchmark:
  warmup_runs: 2  # 预热次数
```

**建议值**：
- 快速测试：1-2 次
- 标准测试：2-3 次
- 精确测试：3-5 次

### 测试配置
```yaml
benchmark:
  test_runs: 3  # 每个测试的运行次数
```

**建议值**：
- 快速测试：1-2 次
- 标准测试：3 次（推荐）
- 精确测试：5 次

### 质量评估配置
```yaml
quality:
  enabled: true
  judges:
    deepseek_judge:
      enabled: true
      weight: 0.30
    glm_judge:
      enabled: true
      weight: 0.30
    minimax_judge:
      enabled: true
      weight: 0.40
  evaluation_strategy:
    mode: parallel  # parallel 或 sequential
```

**模式选择**：
- `parallel`: 并行评估，速度快（推荐）
- `sequential`: 顺序评估，更稳定

## 性能考虑

### 并行化

**Judge 评估**：
- 默认并行模式
- 使用 `ThreadPoolExecutor`
- 最大并发数 = Judge 数量

**测试执行**：
- 默认顺序执行
- 可配置为并行（future enhancement）

### 内存管理

**原始结果存储**：
```python
# 所有结果存储在内存中
self.results: List[TestResult] = []

# 可选保存到磁盘
if config.get("benchmark", {}).get("save_raw_responses", False):
    self._save_raw_responses()
```

**大规模测试**：
- 100+ 测试用例：约 100-200 MB 内存
- 1000+ 测试用例：考虑流式写入磁盘

### 错误恢复

**单个测试失败**：
- 不影响其他测试
- 错误信息记录在 `TestResult.error_message`
- 失败测试不计入统计

**部分结果返回**：
- API 调用失败时返回已收集的部分结果
- 确保有数据可用于分析

## 完整示例

### 运行标准评测

```bash
# 1. 设置环境变量
export DEEPSEEK_API_KEY="your_deepseek_key"
export GLM_API_KEY="your_glm_key"
export MINIMAX_API_KEY="your_minimax_key"

# 2. 运行标准评测
python run_benchmark.py --mode standard

# 3. 查看输出
# - 控制台：实时进度
# - JSON: results/data/raw_data_*.json
# - Markdown: results/reports/benchmark_report_*.md
# - HTML: results/minimax_reports/report_*.html
```

### 输出示例

```
===============================================================================
DeepSeek vs GLM - MiniMax 标准评测（100个用例）
开始时间: 2024-01-16 20:00:00
===============================================================================

加载配置文件...
✓ 配置加载成功

✓ 加载 MiniMax 标准测试用例: 100 个

测试用例分布:
  - basic_performance: 25 个
  - core_capabilities: 25 个
  - practical_scenarios: 25 个
  - advanced_features: 25 个

验证 API 连接...
验证 deepseek 连接...
deepseek: ✓ 成功
验证 glm 连接...
glm: ✓ 成功

===============================================================================
开始基准测试
===============================================================================

运行测试: 100%|████████████████████| 100/100 [10:23<00:00,  6.23s/it]

✓ 基准测试完成

测试完成:
  - 总测试数: 600
  - 成功: 598
  - 失败: 2
  - 成功率: 99.7%

===============================================================================
开始三模型交叉评价...
===============================================================================

质量评估完成:
  - 总评估数: 598
  - 成功评估: 595

===============================================================================
保存评测数据到JSON...
===============================================================================
✅ JSON数据已保存: results/data/raw_data_20240116_203500.json

===============================================================================
从JSON生成Markdown报告...
===============================================================================
✅ Markdown报告已生成: results/reports/benchmark_report_20240116_203500.md

===============================================================================
生成HTML报告...
===============================================================================
✅ 报告已生成: results/minimax_reports/report_20240116_203500.html

===============================================================================
✅ MiniMax 标准评测完成！
结束时间: 2024-01-16 20:35:00
===============================================================================

评测总结:

deepseek:
  综合得分: 8.45/10
  等级: 良好

glm:
  综合得分: 8.20/10
  等级: 良好
```

## 总结

基准测试系统的执行流程设计合理，具有以下特点：

1. **模块化设计**：每个步骤职责清晰，易于维护
2. **灵活配置**：支持多种运行模式和参数配置
3. **错误恢复**：单个测试失败不影响整体流程
4. **性能优化**：预热、并行评估、高精度计时
5. **完整数据**：保存原始结果，支持后续分析

通过这个流程，系统能够准确、公平地对比不同 LLM 的性能和质量。
