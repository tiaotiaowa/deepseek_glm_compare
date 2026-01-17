"""测试结果数据模型"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


@dataclass
class TestResult:
    """单个测试结果"""

    model_name: str  # 模型名称
    test_name: str  # 测试名称
    test_category: str  # 测试类别
    run_number: int  # 运行编号

    # 性能指标
    ttft_ms: float  # Time to First Token (毫秒)
    total_time_ms: float  # 总响应时间 (毫秒)
    generation_time_ms: float  # 生成时间 (毫秒)
    output_tokens: int  # 输出 token 数量
    tokens_per_second: float  # 生成速度 (tokens/秒)
    inter_token_latency_ms: float  # 平均 token 间延迟 (毫秒)

    # 响应内容
    output_text: str  # 完整响应文本

    # 元数据
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True  # 是否成功
    error_message: Optional[str] = None  # 错误信息

    # 测试参数
    parameters: Dict[str, Any] = field(default_factory=dict)

    # 质量评估结果（支持多个 Judge）
    quality_evaluations: Dict[str, Any] = field(default_factory=dict)
    # 格式: {"deepseek_judge": JudgeEvaluation对象, "glm_judge": JudgeEvaluation对象}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "model_name": self.model_name,
            "test_name": self.test_name,
            "test_category": self.test_category,
            "run_number": self.run_number,
            "ttft_ms": self.ttft_ms,
            "total_time_ms": self.total_time_ms,
            "generation_time_ms": self.generation_time_ms,
            "output_tokens": self.output_tokens,
            "tokens_per_second": self.tokens_per_second,
            "inter_token_latency_ms": self.inter_token_latency_ms,
            "output_text": self.output_text,
            "timestamp": self.timestamp,
            "success": self.success,
            "error_message": self.error_message,
            "parameters": self.parameters,
            "quality_evaluations": {}
        }

        # 转换质量评估结果
        for judge_name, evaluation in self.quality_evaluations.items():
            if hasattr(evaluation, 'to_dict'):
                result["quality_evaluations"][judge_name] = evaluation.to_dict()
            else:
                result["quality_evaluations"][judge_name] = evaluation

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResult":
        """从字典创建"""
        return cls(**data)


@dataclass
class CategorySummary:
    """测试类别汇总统计"""

    category: str  # 类别名称
    model_name: str  # 模型名称

    # TTFT 统计
    ttft_mean: float
    ttft_median: float
    ttft_std: float
    ttft_min: float
    ttft_max: float

    # 生成速度统计
    speed_mean: float
    speed_median: float
    speed_std: float
    speed_min: float
    speed_max: float

    # 总时间统计
    total_time_mean: float
    total_time_median: float
    total_time_std: float

    # 测试数量
    test_count: int
    success_count: int

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "category": self.category,
            "model_name": self.model_name,
            "ttft_mean": self.ttft_mean,
            "ttft_median": self.ttft_median,
            "ttft_std": self.ttft_std,
            "ttft_min": self.ttft_min,
            "ttft_max": self.ttft_max,
            "speed_mean": self.speed_mean,
            "speed_median": self.speed_median,
            "speed_std": self.speed_std,
            "speed_min": self.speed_min,
            "speed_max": self.speed_max,
            "total_time_mean": self.total_time_mean,
            "total_time_median": self.total_time_median,
            "total_time_std": self.total_time_std,
            "test_count": self.test_count,
            "success_count": self.success_count
        }
