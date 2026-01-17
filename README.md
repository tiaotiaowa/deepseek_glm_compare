# DeepSeek vs GLM API 基准测试系统

一个全面的 API 基准测试系统，用于对比 DeepSeek 和 GLM 模型在不同协议下的性能和质量。

## 📚 文档导航

### 核心文档
- **[API 架构文档](docs/api_architecture.md)** - API 客户端架构设计和实现
- **[执行流程文档](docs/execution_flow.md)** - 完整的测试执行流程说明
- **[质量评价体系文档](docs/quality_evaluation_system.md)** - 质量评估机制和评分标准

### 项目文档
- **[CLAUDE.md](CLAUDE.md)** - 项目概述和开发指南（Claude Code 使用）
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 完整的项目架构说明

## 功能特性

### 性能指标
- **TTFT (Time to First Token)**: 首次响应时间
- **总响应时间**: 完整请求持续时间
- **生成速度**: Tokens/秒
- **端到端延迟**: 包含网络开销的总时间
- **Token 间延迟**: 连续 token 之间的平均时间

### 质量评估
- 使用 Judge LLM 框架评估输出质量
- 盲评设计，减少偏差
- 多维度评分标准

### 测试场景
- **主要任务**: 简单问答、长文本生成、复杂推理、代码生成
- **次要任务**: 文本摘要、翻译、数学推理、创意写作、事实准确性、多轮对话

### 可视化报告
- 生成详细的 Markdown 格式测试报告
- 包含测试设计、测试过程、测试结果、意见建议四个部分
- 自动对比分析，标注优势模型
- 保存原始 JSON 数据供后续分析

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GLM_API_KEY=your_glm_api_key_here
```

### 3. 运行基准测试

```bash
# 运行预测试模式（每个维度1个用例，快速验证）
python run_benchmark.py --mode preview

# 运行完整标准评测（100个MiniMax测试用例）
python run_benchmark.py --mode standard

# 运行原始对比测试
python run_benchmark.py --mode original
```

### 4. 查看报告

测试完成后，报告将生成在 `results/reports/` 目录中：

- `benchmark_report_<timestamp>.md` - 详细的测试报告
- `results/data/raw_data_<timestamp>.json` - 原始数据（供分析）

报告包含以下内容：
- 一、测试设计（测试对象、指标、场景、方法）
- 二、测试过程（环境、执行情况）
- 三、测试结果（性能对比、详细分析）
- 四、意见建议（性能总结、使用建议、优化建议）

## 项目结构

```
ds_glm_compare/
├── src/
│   ├── api/                    # API 客户端
│   ├── benchmark/              # 基准测试引擎
│   ├── tests/                  # 测试用例
│   │   └── cases/              # 具体测试类别
│   ├── quality/                # 质量评估
│   ├── utils/                  # 工具函数
│   └── report/                 # 报告生成
├── data/                       # 测试数据
├── results/                    # 测试结果
├── config.yaml                 # 配置文件
├── run_benchmark.py            # 主程序入口
├── requirements.txt            # Python 依赖
└── .env                        # 环境变量
```

完整的架构说明请查看 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 配置说明

`config.yaml` 包含所有配置选项：

```yaml
apis:
  deepseek:
    base_url: "https://api.deepseek.com/v1"
    model: "deepseek-v3.2"
  glm:
    base_url: "https://open.bigmodel.cn/api/paas/v4"
    model: "glm-4.7"

benchmark:
  warmup_runs: 2      # 预热运行次数
  test_runs: 3        # 每个测试运行次数

quality:
  enabled: true       # 是否启用质量评估
```

## 添加新测试

在 `src/tests/cases/` 中创建新的测试类别文件：

```python
from ..base_test import BaseTestCategory
from ..test_registry import registry

class MyTests(BaseTestCategory):
    def __init__(self):
        super().__init__("my_category")
        self.create_test_case(
            name="test_1",
            prompt="你的提示词",
            priority="primary",
            max_tokens=500
        )

registry.register_category(MyTests())
```

## 测试类别说明

| 类别 | 描述 | 测试数量 |
|------|------|----------|
| `qa_simple` | 简单问答 | 12 |
| `generation_long` | 长文本生成 | 8 |
| `reasoning_complex` | 复杂推理 | 15 |
| `code_generation` | 代码生成 | 15 |
| `summarization` | 文本摘要 | - |
| `translation` | 翻译 | - |
| `math_reasoning` | 数学推理 | - |
| `creative_writing` | 创意写作 | - |
| `factual_accuracy` | 事实准确性 | - |
| `multi_turn` | 多轮对话 | - |

## 性能指标解释

### TTFT (Time to First Token)
从发送请求到收到第一个 token 的时间。这是用户体验的关键指标，TTFT 越短，用户感觉响应越快。

### 生成速度 (Tokens/Second)
模型生成 token 的速度。速度越快，长文本生成的等待时间越短。

### 总响应时间
完整请求从发送到接收完成的总时间。

## 质量评估

系统使用 Judge LLM 方法评估输出质量：

1. **盲评**: 裁判不知道哪个模型生成哪个输出
2. **多维度评分**: 准确性、清晰度、完整性等
3. **对比分析**: 直接对比两个模型的输出

## 开发

### 运行特定测试

```bash
# 运行预测试模式（快速验证）
python run_benchmark.py --mode preview

# 运行完整MiniMax标准评测
python run_benchmark.py --mode standard

# 运行原始对比测试
python run_benchmark.py --mode original
```

### 调试模式

```bash
# 查看帮助信息
python run_benchmark.py --help
```

## 常见问题

### Q: 测试失败怎么办？

A: 检查以下几点：
1. API 密钥是否正确配置
2. 网络连接是否正常
3. API 端点是否可访问
4. 查看日志文件获取详细错误信息

### Q: 如何调整测试参数？

A: 编辑 `config.yaml` 文件中的 `benchmark` 部分。

### Q: 报告在哪里？

A: 报告生成在 `results/reports/` 目录，文件名格式为 `benchmark_report_时间戳.md`

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请提交 Issue。
