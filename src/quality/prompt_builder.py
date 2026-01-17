"""提示词构建器 - 统一的评估提示词构建逻辑

这个模块从 judge_manager.py 中提取了提示词构建的逻辑，
包括标准评估提示词和 MiniMax 评估提示词。

使用示例:
    from src.quality.prompt_builder import PromptBuilder

    # 构建标准评估提示词
    prompt = PromptBuilder.build_standard_evaluation(
        output="模型输出文本",
        category="code_generation",
        prompt="原始提示词",
        rubric=scoring_rubric,
        blind=True
    )
"""

import re
from typing import Dict, List, Any


class PromptBuilder:
    """提示词构建器 - 提供统一的评估提示词构建接口

    从 judge_manager.py 中提取，用于构建各种评估场景的提示词
    """

    @staticmethod
    def build_standard_evaluation(
        output: str,
        category: str,
        prompt: str,
        rubric: Dict[str, Any],
        blind: bool = True
    ) -> str:
        """
        构建标准评估提示词（1-5分制）

        Args:
            output: 模型输出
            category: 测试类别
            prompt: 原始提示词
            rubric: 评分标准字典
            blind: 是否盲评（True表示使用"模型A"，False使用实际模型名）

        Returns:
            完整的评估提示词字符串
        """
        model_label = "模型 A" if blind else "该模型"

        criteria_desc = "\\n".join([
            f"- {c}: {PromptBuilder._get_criteria_description(c)}"
            for c in rubric["criteria"]
        ])

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

    @staticmethod
    def build_minimax_evaluation(
        output_a: str,
        output_b: str,
        category: str,
        prompt: str,
        dimension: str,
        sub_dimension: str,
        quality_criteria: Dict[str, float]
    ) -> str:
        """
        构建 MiniMax 标准评估提示词（0-10分制）

        Args:
            output_a: 模型A的输出
            output_b: 模型B的输出
            category: 测试类别
            prompt: 原始提示词
            dimension: 评测维度（如"basic_performance"）
            sub_dimension: 子维度（如"real_time"）
            quality_criteria: 质量标准权重字典

        Returns:
            MiniMax标准评估提示词字符串
        """
        criteria_desc = "\\n".join([
            f"- {k} (权重 {v}): {PromptBuilder._get_criteria_description(k)}"
            for k, v in quality_criteria.items()
        ])

        return f"""你是一个专业的模型评测专家，基于 MiniMax 标准对模型输出进行评价。

评测维度：{dimension}
子维度：{sub_dimension}
测试类别：{category}

评分标准（0-10 分）：
- 9-10 分：优秀，超出预期
- 7.5-8.9 分：良好，很好地满足预期
- 6-7.4 分：合格，满足最低要求
- 3-5.9 分：不合格，低于预期
- 0-2.9 分：严重缺陷，未达到要求

评估标准及权重：
{criteria_desc}

请对以下两个模型的输出进行评价，返回 JSON 格式：

{{
    "model_a": {{
        "accuracy_score": <准确性得分 0-10>,
        "completeness_score": <完整性得分 0-10>,
        "logic_score": <逻辑性得分 0-10>,
        "creativity_score": <创造性得分 0-10>,
        "overall_score": <加权总分 0-10>,
        "strengths": ["优势1", "优势2"],
        "weaknesses": ["劣势1", "劣势2"],
        "reasoning": "<详细评价理由>"
    }},
    "model_b": {{
        "accuracy_score": <准确性得分 0-10>,
        "completeness_score": <完整性得分 0-10>,
        "logic_score": <逻辑性得分 0-10>,
        "creativity_score": <创造性得分 0-10>,
        "overall_score": <加权总分 0-10>,
        "strengths": ["优势1", "优势2"],
        "weaknesses": ["劣势1", "劣势2"],
        "reasoning": "<详细评价理由>"
    }}
}}

=== 模型 A 输出 ====
{output_a}

=== 模型 B 输出 ====
{output_b}

=== 原始提示词 ====
{prompt}

请确保输出有效的 JSON 格式，不要添加任何其他文字。
"""

    @staticmethod
    def _get_criteria_description(criteria: str) -> str:
        """
        获取评估标准的中文描述

        Args:
            criteria: 评估标准名称

        Returns:
            中文描述
        """
        descriptions = {
            # 通用标准
            "accuracy": "输出的正确性和准确度",
            "completeness": "对所有必需方面的覆盖程度",
            "logic": "思维的逻辑严密性",
            "creativity": "创新性和独特性",

            # MiniMax 特定标准
            "ttft_performance": "首次Token生成时间性能",
            "throughput_performance": "Token生成吞吐量性能",
            "stability_performance": "稳定性表现",
            "reasoning_quality": "推理质量",
            "code_correctness": "代码正确性",
            "code_style": "代码风格",
            "efficiency": "效率",
            "documentation": "文档完整性",
            "understanding_quality": "理解质量",
            "professional_quality": "专业质量",
            "chinese_quality": "中文处理质量",
            "format_correctness": "格式正确性",
            "structural_analysis": "结构分析能力"
        }
        return descriptions.get(criteria, criteria)

    @staticmethod
    def validate_prompt(prompt: str) -> bool:
        """
        验证提示词是否有效

        Args:
            prompt: 提示词字符串

        Returns:
            是否有效
        """
        if not prompt or len(prompt.strip()) == 0:
            return False

        # 检查是否包含必要的占位符
        required_patterns = ["{", "}", "model", "output"]
        return all(pattern in prompt.lower() for pattern in required_patterns)
