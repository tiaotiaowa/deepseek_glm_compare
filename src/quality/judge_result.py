"""Judge 评估结果数据模型"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


@dataclass
class JudgeEvaluation:
    """单个 Judge 的评估结果"""

    judge_name: str  # Judge 名称 (如 "deepseek_judge", "glm_judge")
    judge_model: str  # Judge 使用的模型 (如 "deepseek-chat", "glm-4.7")

    # 被评估的信息
    test_name: str
    test_category: str
    model_evaluated: str  # 被评估的模型 (如 "deepseek", "glm")

    # 评估分数
    scores: Dict[str, float] = field(default_factory=dict)
    # 格式: {"accuracy": 4.5, "clarity": 4.0}
    overall_score: float = 0.0  # 总体分数

    # 详细评估
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    reasoning: str = ""  # 评估理由

    # 元数据
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    evaluation_time_ms: float = 0.0  # 评估耗时
    blind_evaluation: bool = True
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "judge_name": self.judge_name,
            "judge_model": self.judge_model,
            "test_name": self.test_name,
            "test_category": self.test_category,
            "model_evaluated": self.model_evaluated,
            "scores": self.scores,
            "overall_score": self.overall_score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
            "evaluation_time_ms": self.evaluation_time_ms,
            "blind_evaluation": self.blind_evaluation,
            "success": self.success,
            "error_message": self.error_message
        }

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JudgeEvaluation':
        """从字典创建实例"""
        return cls(
            judge_name=data.get("judge_name", ""),
            judge_model=data.get("judge_model", ""),
            test_name=data.get("test_name", ""),
            test_category=data.get("test_category", ""),
            model_evaluated=data.get("model_evaluated", ""),
            scores=data.get("scores", {}),
            overall_score=data.get("overall_score", 0.0),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            reasoning=data.get("reasoning", ""),
            timestamp=data.get("timestamp", ""),
            evaluation_time_ms=data.get("evaluation_time_ms", 0.0),
            blind_evaluation=data.get("blind_evaluation", True),
            success=data.get("success", True),
            error_message=data.get("error_message")
        )


@dataclass
class JudgeComparison:
    """多个 Judge 的评估对比"""

    test_name: str
    test_category: str
    model_evaluated: str

    # 各 Judge 的评估结果
    evaluations: Dict[str, JudgeEvaluation] = field(default_factory=dict)
    # 格式: {"deepseek_judge": JudgeEvaluation, "glm_judge": JudgeEvaluation}

    # Judge 间的一致性分析
    score_variance: float = 0.0  # 分数方差
    score_std: float = 0.0  # 分数标准差
    agreement_level: str = ""  # 一致性等级 (high/medium/low)

    # 差异分析
    criteria_disagreements: Dict[str, float] = field(default_factory=dict)
    # 格式: {"accuracy": 0.8}  # 表示 accuracy 标准的最大分数差异

    def calculate_agreement_metrics(self):
        """计算 Judge 间的一致性指标"""
        import statistics

        if len(self.evaluations) < 2:
            return

        # 计算总体分数的一致性
        overall_scores = [eval.overall_score for eval in self.evaluations.values()]
        self.score_variance = statistics.variance(overall_scores) if len(overall_scores) > 1 else 0.0
        self.score_std = statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0.0

        # 判断一致性等级
        if self.score_std < 0.5:
            self.agreement_level = "high"
        elif self.score_std < 1.0:
            self.agreement_level = "medium"
        else:
            self.agreement_level = "low"

        # 计算各标准的分歧
        all_criteria = set()
        for eval in self.evaluations.values():
            all_criteria.update(eval.scores.keys())

        for criterion in all_criteria:
            scores_for_criterion = []
            for eval in self.evaluations.values():
                if criterion in eval.scores:
                    scores_for_criterion.append(eval.scores[criterion])

            if len(scores_for_criterion) >= 2:
                max_diff = max(scores_for_criterion) - min(scores_for_criterion)
                self.criteria_disagreements[criterion] = max_diff

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "test_category": self.test_category,
            "model_evaluated": self.model_evaluated,
            "evaluations": {
                name: eval.to_dict()
                for name, eval in self.evaluations.items()
            },
            "score_variance": self.score_variance,
            "score_std": self.score_std,
            "agreement_level": self.agreement_level,
            "criteria_disagreements": self.criteria_disagreements
        }

    def get_agreement_description(self) -> str:
        """获取一致性等级的描述"""
        descriptions = {
            "high": "高一致性",
            "medium": "中等一致性",
            "low": "低一致性"
        }
        return descriptions.get(self.agreement_level, "未知")
