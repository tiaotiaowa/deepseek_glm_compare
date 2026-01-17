# 质量评价体系详解

## 概述

本系统使用**多模型交叉评价（Multi-Judge Evaluation）**机制，通过多个强大的 LLM 作为裁判，对模型输出进行客观、公正的质量评估。

**核心特性**：
- **多 Judge 评估**：使用 3 个独立的 LLM 作为裁判
- **盲评机制**：Judge 不知道评估的是哪个模型
- **加权综合**：根据 Judge 可靠性分配不同权重
- **标准化评分**：统一的评分标准和等级划分

## 评价体系架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                   模型输出                                │
│       (DeepSeek / GLM 的测试响应)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              JudgeManager (评价协调器)                    │
│  - 构建评价提示词                                         │
│  - 协调多个 Judge                                        │
│  - 并行/顺序控制                                          │
│  - 结果解析和验证                                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ DeepSeek     │ │ GLM          │ │ MiniMax      │
│ Judge        │ │ Judge        │ │ Judge        │
│ (30%)        │ │ (30%)        │ │ (40%)        │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │  1-5 分制      │  1-5 分制      │  0-10 分制
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  标准化和归一化  │
              │  (Z-score 等)   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  加权综合评分    │
              │  (0-10 分制)    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  等级划分       │
              │  (优秀/良好等)  │
              └─────────────────┘
```

## Judge 配置

### 1. DeepSeek Judge

**配置示例**：
```yaml
deepseek_judge:
  enabled: true
  type: "deepseek"
  model: "deepseek-chat"
  api_key_env: "DEEPSEEK_API_KEY"
  blind_evaluation: true
  max_tokens: 2048
  temperature: 0.3
  weight: 0.30
```

**特点**：
- **协议**：OpenAI 兼容协议
- **权重**：30%
- **温度**：0.3（低温度保证稳定性）
- **评分制**：1-5 分制

**适用场景**：
- 代码生成评估
- 技术文档评估
- 逻辑推理评估

### 2. GLM Judge

**配置示例**：
```yaml
glm_judge:
  enabled: true
  type: "glm"
  model: "glm-4.7"
  api_key_env: "GLM_API_KEY"
  blind_evaluation: true
  max_tokens: 2048
  temperature: 0.3
  weight: 0.30
```

**特点**：
- **协议**：Anthropic 兼容协议
- **权重**：30%
- **温度**：0.3
- **评分制**：1-5 分制

**适用场景**：
- 中文内容评估
- 创意写作评估
- 对话质量评估

### 3. MiniMax Judge

**配置示例**：
```yaml
minimax_judge:
  enabled: true
  type: "minimax"
  model: "MiniMax-M2.1"
  api_key_env: "MINIMAX_API_KEY"
  blind_evaluation: true
  max_tokens: 2048
  temperature: 0.3
  weight: 0.40
```

**特点**：
- **协议**：Anthropic 兼容协议（专用客户端）
- **权重**：40%（最高权重，作为主要参考）
- **温度**：0.3
- **评分制**：0-10 分制（更细粒度）

**适用场景**：
- 综合质量评估
- 中文内容评估
- MiniMax 标准评测

## 评价标准

### 标准分类

系统定义了 10 个测试类别，每个类别有特定的评价标准和权重：

#### 1. 简单问答 (qa_simple)

**标准**：accuracy, conciseness, clarity

**权重**：
- accuracy (准确性): 40%
- conciseness (简洁性): 30%
- clarity (清晰度): 30%

**评分细则**：

**准确性 (accuracy)**：
- 5分：信息完全准确，无错误
- 4分：基本准确，有轻微瑕疵
- 3分：部分准确，有明显错误
- 2分：大部分不准确
- 1分：完全错误

**简洁性 (conciseness)**：
- 5分：用最少的话完整表达
- 4分：简洁但稍显冗余
- 3分：适度简洁
- 2分：较为冗长
- 1分：非常冗长，包含无关信息

**清晰度 (clarity)**：
- 5分：结构清晰，易于理解
- 4分：较清晰
- 3分：基本清晰
- 2分：表达混乱
- 1分：难以理解

#### 2. 复杂推理 (reasoning_complex)

**标准**：reasoning_quality, completeness, clarity

**权重**：
- reasoning_quality (推理质量): 40%
- completeness (完整性): 30%
- clarity (清晰度): 30%

**推理质量 (reasoning_quality)**：
- 5分：逻辑严密，推理正确
- 4分：逻辑基本正确
- 3分：推理有瑕疵
- 2分：推理混乱
- 1分：无逻辑推理

#### 3. 代码生成 (code_generation)

**标准**：code_correctness, code_style, efficiency, documentation

**权重**：
- code_correctness (代码正确性): 50%
- code_style (代码风格): 20%
- efficiency (效率): 20%
- documentation (文档): 10%

**代码正确性 (code_correctness)**：
- 5分：完全正确，可直接运行
- 4分：基本正确，需微调
- 3分：部分正确，有明显错误
- 2分：大部分错误
- 1分：完全错误

#### 4. 长文本生成 (generation_long)

**标准**：structure, content_quality, creativity, clarity

**权重**：
- structure (结构): 25%
- content_quality (内容质量): 35%
- creativity (创造力): 20%
- clarity (清晰度): 20%

**结构 (structure)**：
- 5分：结构完整，逻辑清晰
- 4分：结构较好
- 3分：结构基本完整
- 2分：结构混乱
- 1分：无结构

#### 5. 摘要 (summarization)

**标准**：completeness, conciseness, accuracy

**权重**：
- completeness (完整性): 40%
- conciseness (简洁性): 30%
- accuracy (准确性): 30%

#### 6. 翻译 (translation)

**标准**：accuracy, fluency, cultural_appropriateness

**权重**：
- accuracy (准确性): 50%
- fluency (流畅性): 30%
- cultural_appropriateness (文化适应性): 20%

#### 7. 数学推理 (math_reasoning)

**标准**：accuracy, reasoning_quality, clarity

**权重**：
- accuracy (准确性): 50%
- reasoning_quality (推理质量): 30%
- clarity (清晰度): 20%

#### 8. 创意写作 (creative_writing)

**标准**：creativity, coherence, emotional_impact, originality

**权重**：
- creativity (创造力): 30%
- coherence (连贯性): 30%
- emotional_impact (情感冲击): 20%
- originality (原创性): 20%

#### 9. 事实准确性 (factual_accuracy)

**标准**：accuracy, completeness, citation_quality

**权重**：
- accuracy (准确性): 50%
- completeness (完整性): 30%
- citation_quality (引用质量): 20%

#### 10. 多轮对话 (multi_turn)

**标准**：context_retention, relevance, coherence

**权重**：
- context_retention (上下文保持): 40%
- relevance (相关性): 30%
- coherence (连贯性): 30%

## 盲评机制

### 目的

减少 Judge 的偏见，确保评价客观性。

### 实现方式

#### 1. 模型标记匿名化

```python
def _build_evaluation_prompt(self, prompt, output, category, rubric, blind):
    # 使用匿名标签
    model_label = "模型 A" if blind else self.model_name

    return f"""
    【原始提示词】
    {prompt}

    【{model_label}的输出】
    {output}

    请评估{model_label}的输出质量...
    """
```

#### 2. Judge 不知道的信息

- 哪个模型生成了输出
- 其他 Judge 的评分
- 测试用例的来源

#### 3. 可配置开关

```yaml
quality:
  judges:
    deepseek_judge:
      blind_evaluation: true  # 启用盲评
```

## 评分计算

### 单个 Judge 评分

#### 1-5 分制（DeepSeek, GLM）

```python
overall_score = sum(
    score[criterion] * weight[criterion]
    for criterion in criteria
)
```

**示例**（简单问答）：
```
accuracy = 4.5 * 0.40 = 1.80
conciseness = 4.0 * 0.30 = 1.20
clarity = 4.5 * 0.30 = 1.35
overall_score = 4.35
```

#### 0-10 分制（MiniMax）

```python
# MiniMax 直接返回 0-10 分
overall_score = judge_response["overall_score"]
```

### 多 Judge 加权综合

#### 标准化到 0-10 分制

```python
# 1-5 分制标准化
normalized_score = (score - 1) / 4 * 10

# 示例：4.35 分 → (4.35 - 1) / 4 * 10 = 8.375 分
```

#### 加权平均

```python
weighted_score = (
    minimax_score * 0.40 +
    deepseek_score * 0.30 +
    glm_score * 0.30
)
```

**示例**：
```
MiniMax: 8.5 * 0.40 = 3.40
DeepSeek: 8.0 * 0.30 = 2.40
GLM: 8.2 * 0.30 = 2.46
综合得分: 8.26
```

### MiniMax 标准评分（三模型交叉评价）

#### 维度得分计算

```python
dimension_score = sum(
    test_score * weight
    for test, weight in tests.items()
) / sum(weights)
```

**示例**（基础性能维度）：
```
测试1: 8.5 * 0.25 = 2.125
测试2: 8.0 * 0.25 = 2.000
测试3: 9.0 * 0.25 = 2.250
测试4: 8.7 * 0.25 = 2.175
维度得分: 8.55
```

#### 综合评分

```python
overall_score = sum(
    dimension_score * dimension_weight
    for dimension, score in dimension_scores.items()
)
```

**示例**：
```
基础性能: 8.55 * 0.25 = 2.1375
核心能力: 8.20 * 0.35 = 2.8700
实用场景: 8.40 * 0.25 = 2.1000
高级特性: 7.80 * 0.15 = 1.1700
综合得分: 8.28
```

## 评分等级

### MiniMax 标准（0-10 分制）

```python
def grade_score(score):
    if score >= 9.0:
        return "优秀"
    elif score >= 7.5:
        return "良好"
    elif score >= 6.0:
        return "合格"
    elif score >= 3.0:
        return "不合格"
    else:
        return "严重缺陷"
```

**等级分布**：
- **优秀** (9.0-10.0)：超出预期，表现卓越
- **良好** (7.5-8.9)：很好地满足预期
- **合格** (6.0-7.4)：满足最低要求
- **不合格** (3.0-5.9)：低于预期，有明显问题
- **严重缺陷** (0-2.9)：未达到要求

### 标准评分（1-5 分制）

- **5分**：优秀，超出预期
- **4分**：良好，很好地满足预期
- **3分**：达标，满足最低要求
- **2分**：较差，低于预期，有明显问题
- **1分**：很差，未达到要求

## 统计分析

### Z-score 标准化

```python
z_score = (x - mean) / std
```

**用途**：消除不同 Judge 之间的评分偏差

**示例**：
```
DeepSeek Judge 平均分: 4.2, 标准差: 0.5
GLM Judge 平均分: 3.8, 标准差: 0.6

某个测试的评分：
DeepSeek: 4.5 → z_score = (4.5 - 4.2) / 0.5 = 0.6
GLM: 4.2 → z_score = (4.2 - 3.8) / 0.6 = 0.67
```

### 置信区间

```python
confidence_interval = mean ± (z_value * std / sqrt(n))
```

**95% 置信水平**：z_value = 1.96

**示例**：
```
平均分: 8.26
标准差: 0.5
样本数: 100

置信区间 = 8.26 ± (1.96 * 0.5 / 10) = 8.26 ± 0.098 = [8.16, 8.36]
```

### Pearson 相关系数

```python
r = covariance(X, Y) / (std_X * std_Y)
```

**用途**：衡量 Judge 之间的一致性

**相关系数解释**：
- 0.9-1.0：极高一致性
- 0.7-0.9：高一致性
- 0.5-0.7：中等一致性
- 0.3-0.5：低一致性
- 0-0.3：极低一致性

### 评价者间信度

```python
def calculate_inter_rater_reliability(ratings):
    """
    计算评价者间信度（Krippendorff's Alpha）

    Args:
        ratings: {judge_name: [score1, score2, ...]}

    Returns:
        float: 信度系数 (0-1)
    """
    # 实现 Krippendorff's Alpha 算法
    pass
```

**信度解释**：
- 0.8-1.0：极高信度
- 0.6-0.8：高信度
- 0.4-0.6：中等信度
- 0.2-0.4：低信度
- 0-0.2：极低信度

## 评价流程

### 2026-01 架构更新

**模块化重构**: 质量评估系统已进行模块化重构，提升可维护性和可扩展性。

**新增模块**:
- `src/quality/judge_factory.py` - Judge客户端工厂（工厂模式）
- `src/quality/prompt_builder.py` - 提示词构建器（建造者模式）
- `src/quality/response_parser.py` - 响应解析器（策略模式）

**重构收益**:
- 消除约280行重复代码
- 平均模块大小降低63%
- 单一职责原则，每个模块功能清晰

### 架构组件

质量评估系统采用模块化设计，主要组件包括：

1. **JudgeFactory** (`src/quality/judge_factory.py`)
   - 负责创建不同类型的Judge客户端
   - 支持DeepSeek、GLM、MiniMax三种类型
   - 使用工厂模式统一创建流程

2. **JudgeManager** (`src/quality/judge_manager.py`)
   - 协调多个Judge的评估工作
   - 支持并行和顺序评估模式
   - 委托专门的模块进行提示词构建和响应解析

3. **PromptBuilder** (`src/quality/prompt_builder.py`)
   - 统一的提示词构建接口
   - 支持标准评估（1-5分）和MiniMax评估（0-10分）
   - 提供评估标准描述映射

4. **ResponseParser** (`src/quality/response_parser.py`)
   - 解析Judge的评估响应
   - 支持多种响应格式（JSON、代码块、文本）
   - 提供多层降级解析机制

---

### 1. 提示词构建

**文件**: `src/quality/prompt_builder.py` **[已重构]**

**类**: `PromptBuilder`

**方法**:
- `build_standard_evaluation()` - 构建标准评估提示词（1-5分制）
- `build_minimax_evaluation()` - 构建MiniMax评估提示词（0-10分制）

**使用示例**:
```python
from src.quality.prompt_builder import PromptBuilder

# 构建标准评估提示词
prompt = PromptBuilder.build_standard_evaluation(
    output="模型输出文本",
    category="code_generation",
    prompt="原始提示词",
    rubric=scoring_rubric,
    blind=True
)
```

**构建步骤**：
```python
def _build_evaluation_prompt(self, prompt, output, category, rubric, blind):
    # 1. 获取评分标准
    criteria_desc = "\n".join([
        f"- {c}: {ScoringRubric.get_criteria_description(c)}"
        for c in rubric["criteria"]
    ])

    # 2. 格式化提示词
    model_label = "模型 A" if blind else "该模型"

    # 3. 构建完整提示词
    return f"""你是一个专业的 AI 输出质量评估专家。

任务类别：{category}

原始提示词：
{prompt}

{model_label}的输出：
{output}

评估标准（每项 1-5 分）：
{criteria_desc}

评分标准：
- 5 分：优秀，超出预期
- 4 分：良好，很好地满足预期
- 3 分：达标，满足最低要求
- 2 分：较差，低于预期，有明显问题
- 1 分：很差，未达到要求

请严格按照以下 JSON 格式提供评估结果（不要添加任何其他文字）：
{{
    "scores": {{
        "criterion1": {{"score": 4, "justification": "原因"}},
        "criterion2": {{"score": 3, "justification": "原因"}}
    }},
    "overall_score": 3.5,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["缺点1", "缺点2"],
    "reasoning": "总体评估理由"
}}

请确保输出有效的 JSON 格式。
"""
```

### 2. Judge 调用

**方法**: `_call_judge_api()`

**执行方式**：
```python
def _call_judge_api(self, client, prompt, config):
    messages = [{"role": "user", "content": prompt}]

    # 使用非流式请求
    response_text = client.chat(
        messages=messages,
        max_tokens=config.get("max_tokens", 2048),
        temperature=config.get("temperature", 0.3)
    )

    return response_text
```

### 3. 结果解析

**文件**: `src/quality/response_parser.py` **[已重构]**

**类**: `ResponseParser`

**方法**:
- `parse_standard()` - 解析标准评估响应（1-5分制）
- `parse_minimax()` - 解析MiniMax评估响应（0-10分制）
- `validate_response()` - 验证响应格式
- `extract_overall_score()` - 提取总分

**使用示例**:
```python
from src.quality.response_parser import ResponseParser

# 解析标准评估响应
result = ResponseParser.parse_standard(
    response_text='{"scores": {...}, "overall_score": 4.2}',
    criteria=["accuracy", "completeness"],
    category="qa_simple"
)
```

**解析逻辑**（多层降级策略）：
```python
def _parse_evaluation_response(self, response, criteria, category):
    try:
        # 1. 尝试提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)

            # 2. 验证并返回
            if "scores" in result:
                # 提取简单分数
                simple_scores = {}
                scores_data = result["scores"]
                for criterion in criteria:
                    if criterion in scores_data:
                        if isinstance(scores_data[criterion], dict):
                            simple_scores[criterion] = scores_data[criterion].get("score", 3.0)
                        else:
                            simple_scores[criterion] = float(scores_data[criterion])
                    else:
                        simple_scores[criterion] = 3.0

                result["scores"] = simple_scores
                return result

        # 3. 如果解析失败，从文本中提取分数
        return self._extract_scores_from_text(response, criteria)

    except Exception as e:
        print(f"解析评估响应失败: {e}")
        return self._extract_scores_from_text(response, criteria)
```

**备用解析方法**：
```python
def _extract_scores_from_text(self, text, criteria):
    """从文本中提取分数（备用解析方法）"""
    scores = {}
    for criterion in criteria:
        # 尝试在文本中找到该标准的分数
        pattern = rf'{criterion}.*?(\d+(?:\.\d+)?)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            score = float(match.group(1))
            # 确保分数在 1-5 范围内
            scores[criterion] = max(1.0, min(5.0, score))
        else:
            scores[criterion] = 3.0

    return {
        "scores": scores,
        "strengths": [],
        "weaknesses": [],
        "reasoning": text[:500] if len(text) > 500 else text
    }
```

### 4. 并行控制

**方法**: `_evaluate_parallel()`

**实现**：
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def _evaluate_parallel(self, output, category, prompt, model_name, test_name):
    evaluations = {}

    with ThreadPoolExecutor(max_workers=len(self.judges)) as executor:
        # 提交所有评估任务
        future_to_judge = {}
        for judge_name, judge_info in self.judges.items():
            future = executor.submit(
                self._evaluate_with_judge,
                judge_name, judge_info, output, category, prompt, model_name, test_name
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

## 质量保证

### 一致性检查

```python
# 10% 的评估运行两次
consistency_check_rate = 0.1

if random.random() < consistency_check_rate:
    # 运行第二次评估
    evaluation_2 = self._evaluate_with_judge(...)

    # 计算相关性
    correlation = calculate_correlation(evaluation_1, evaluation_2)

    # 相关性 < 0.8 时警告
    if correlation < 0.8:
        print(f"警告：Judge 评估一致性低 ({correlation:.2f})")
```

### 异常检测

```python
def validate_evaluation(evaluation):
    """验证评估结果"""

    # 1. 评分范围检查
    for criterion, score in evaluation["scores"].items():
        if not (1 <= score <= 5):
            raise ValueError(f"{criterion} 评分超出范围: {score}")

    # 2. 必需字段检查
    required_fields = ["scores", "overall_score", "reasoning"]
    for field in required_fields:
        if field not in evaluation:
            raise ValueError(f"缺少必需字段: {field}")

    # 3. 评分一致性检查
    overall = evaluation["overall_score"]
    calculated = calculate_overall_score(evaluation["scores"])
    if abs(overall - calculated) > 0.5:
        print(f"警告：总体分数与计算值不一致 ({overall} vs {calculated})")
```

### 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2)
)
def evaluate_with_retry(self, ...):
    """带重试的评估"""
    return self._evaluate_with_judge(...)
```

## 扩展新 Judge

### 步骤

#### 1. 在 config.yaml 中添加配置

```yaml
quality:
  judges:
    new_judge:
      enabled: true
      type: "openai"  # 或 "anthropic", "minimax"
      model: "new-model-v1"
      api_key_env: "NEW_JUDGE_API_KEY"
      blind_evaluation: true
      max_tokens: 2048
      temperature: 0.3
      weight: 0.25
```

#### 2. 在 JudgeManager._init_judges() 中添加初始化逻辑

```python
def _init_judges(self):
    # ... 现有 Judge 初始化 ...

    elif judge_type == "openai":
        # 新的 OpenAI 兼容 Judge
        api_key = os.getenv(judge_config.get("api_key_env", ""))
        client = OpenAIClient(
            base_url="https://api.newjudge.com",
            api_key=api_key,
            model=judge_model,
            max_retries=3,
            timeout=120
        )

        self.judges[judge_name] = {
            "client": client,
            "config": judge_config,
            "type": judge_type,
            "model": judge_model
        }
```

#### 3. 调整权重分配

确保所有 Judge 的权重总和为 1.0：

```yaml
deepseek_judge: 0.25  # 从 0.30 降低
glm_judge: 0.25      # 从 0.30 降低
minimax_judge: 0.35   # 从 0.40 降低
new_judge: 0.15      # 新增
# 总计: 1.0
```

## 总结

质量评价体系通过以下设计实现了公正、准确的质量评估：

1. **多 Judge 评估**：使用 3 个独立的 LLM 作为裁判，减少单一 Judge 的偏见
2. **盲评机制**：Judge 不知道评估的是哪个模型，确保客观性
3. **加权综合**：根据 Judge 可靠性分配不同权重
4. **标准化评分**：统一的评分标准和等级划分
5. **统计分析**：Z-score 标准化、置信区间、相关系数等
6. **质量保证**：一致性检查、异常检测、重试机制

这种评价体系为基准测试提供了全面、客观的质量对比，帮助用户准确了解不同模型的优缺点。
