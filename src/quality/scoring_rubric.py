"""评分标准定义"""

from typing import Dict, List, Any


class ScoringRubric:
    """评分标准类"""

    # 各类别的评分标准和权重
    CATEGORY_RUBRICS = {
        "qa_simple": {
            "criteria": ["accuracy", "conciseness", "clarity"],
            "weights": {"accuracy": 0.4, "conciseness": 0.3, "clarity": 0.3}
        },
        "reasoning_complex": {
            "criteria": ["reasoning_quality", "completeness", "clarity"],
            "weights": {"reasoning_quality": 0.4, "completeness": 0.3, "clarity": 0.3}
        },
        "code_generation": {
            "criteria": ["code_correctness", "code_style", "efficiency", "documentation"],
            "weights": {"code_correctness": 0.5, "code_style": 0.2, "efficiency": 0.2, "documentation": 0.1}
        },
        "generation_long": {
            "criteria": ["structure", "content_quality", "creativity", "clarity"],
            "weights": {"structure": 0.25, "content_quality": 0.35, "creativity": 0.2, "clarity": 0.2}
        },
        "summarization": {
            "criteria": ["completeness", "conciseness", "accuracy"],
            "weights": {"completeness": 0.4, "conciseness": 0.3, "accuracy": 0.3}
        },
        "translation": {
            "criteria": ["accuracy", "fluency", "cultural_appropriateness"],
            "weights": {"accuracy": 0.5, "fluency": 0.3, "cultural_appropriateness": 0.2}
        },
        "math_reasoning": {
            "criteria": ["accuracy", "reasoning_quality", "clarity"],
            "weights": {"accuracy": 0.5, "reasoning_quality": 0.3, "clarity": 0.2}
        },
        "creative_writing": {
            "criteria": ["creativity", "coherence", "emotional_impact", "originality"],
            "weights": {"creativity": 0.3, "coherence": 0.3, "emotional_impact": 0.2, "originality": 0.2}
        },
        "factual_accuracy": {
            "criteria": ["accuracy", "completeness", "citation_quality"],
            "weights": {"accuracy": 0.5, "completeness": 0.3, "citation_quality": 0.2}
        },
        "multi_turn": {
            "criteria": ["context_retention", "relevance", "coherence"],
            "weights": {"context_retention": 0.4, "relevance": 0.3, "coherence": 0.3}
        }
    }

    @classmethod
    def get_rubric(cls, category: str) -> Dict[str, Any]:
        """
        获取特定类别的评分标准

        Args:
            category: 类别名称

        Returns:
            Dict: 评分标准
        """
        return cls.CATEGORY_RUBRICS.get(category, {
            "criteria": ["relevance", "accuracy", "clarity"],
            "weights": {"relevance": 0.4, "accuracy": 0.3, "clarity": 0.3}
        })

    @classmethod
    def get_criteria_description(cls, criterion: str) -> str:
        """
        获取评分标准的描述

        Args:
            criterion: 标准名称

        Returns:
            str: 标准描述
        """
        descriptions = {
            "accuracy": "事实正确性，信息准确无误",
            "conciseness": "简洁性，用最少的话表达完整意思",
            "clarity": "清晰度，结构清楚，易于理解",
            "reasoning_quality": "推理质量，逻辑严密，论证合理",
            "completeness": "完整性，涵盖所有必需方面",
            "code_correctness": "代码正确性，能正常运行",
            "code_style": "代码风格，遵循最佳实践",
            "efficiency": "效率，算法复杂度合理",
            "documentation": "文档质量，注释和说明清晰",
            "structure": "结构，组织有序，逻辑清晰",
            "content_quality": "内容质量，有实质内容",
            "creativity": "创造力，有独特见解",
            "fluency": "流畅性，语言自然流畅",
            "cultural_appropriateness": "文化适应性，符合文化背景",
            "coherence": "连贯性，前后一致",
            "emotional_impact": "情感冲击，能引起共鸣",
            "originality": "原创性，不落俗套",
            "citation_quality": "引用质量，来源可靠",
            "context_retention": "上下文保持，记住之前的对话",
            "relevance": "相关性，切合主题"
        }

        return descriptions.get(criterion, criterion)

    @classmethod
    def calculate_overall_score(
        cls,
        category: str,
        scores: Dict[str, float]
    ) -> float:
        """
        计算总体得分

        Args:
            category: 类别名称
            scores: 各标准得分

        Returns:
            float: 总体得分
        """
        rubric = cls.get_rubric(category)
        weights = rubric["weights"]

        overall_score = 0.0
        for criterion, weight in weights.items():
            if criterion in scores:
                overall_score += scores[criterion] * weight

        return round(overall_score, 2)


class ScoreLevel:
    """评分等级"""

    EXCELLENT = 5
    GOOD = 4
    ADEQUATE = 3
    POOR = 2
    VERY_POOR = 1

    @classmethod
    def get_description(cls, level: int) -> str:
        """
        获取等级描述

        Args:
            level: 等级分数

        Returns:
            str: 等级描述
        """
        descriptions = {
            5: "优秀：超出预期",
            4: "良好：很好地满足预期",
            3: "达标：满足最低要求",
            2: "较差：低于预期，有明显问题",
            1: "很差：未达到要求"
        }
        return descriptions.get(level, "未知")
