"""Judge LLM 质量评估器"""

import os
from typing import Dict, List, Any, Optional
from anthropic import Anthropic

from .scoring_rubric import ScoringRubric, ScoreLevel


class JudgeLLM:
    """使用 Judge LLM 评估输出质量"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Judge LLM

        Args:
            config: 质量评估配置
        """
        self.enabled = config.get("enabled", True)
        self.model = config.get("judge_model", "claude-sonnet-4-5-20250929")
        self.api_key_env = config.get("judge_api_key_env", "JUDGE_API_KEY")
        self.blind_evaluation = config.get("blind_evaluation", True)

        # 初始化客户端
        if self.enabled:
            api_key = os.getenv(self.api_key_env)
            if not api_key:
                print(f"警告: 未找到 Judge LLM API key ({self.api_key_env})")
                self.enabled = False
            else:
                self.client = Anthropic(api_key=api_key)

    def evaluate_single(
        self,
        output: str,
        category: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        评估单个输出

        Args:
            output: 模型输出
            category: 测试类别
            prompt: 原始提示词

        Returns:
            Dict: 评估结果
        """
        if not self.enabled:
            return {"enabled": False}

        rubric = ScoringRubric.get_rubric(category)

        evaluation_prompt = self._build_evaluation_prompt(
            prompt=prompt,
            output=output,
            category=category,
            rubric=rubric
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": evaluation_prompt}]
            )

            # 解析响应（简化版本）
            return self._parse_evaluation_response(
                response.content[0].text,
                rubric["criteria"],
                category
            )

        except Exception as e:
            print(f"Judge LLM 评估失败: {e}")
            return {"error": str(e)}

    def compare_outputs(
        self,
        output_a: str,
        output_b: str,
        category: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        比较两个输出（盲评）

        Args:
            output_a: 模型 A 的输出
            output_b: 模型 B 的输出
            category: 测试类别
            prompt: 原始提示词

        Returns:
            Dict: 比较结果
        """
        if not self.enabled:
            return {"enabled": False}

        rubric = ScoringRubric.get_rubric(category)

        comparison_prompt = self._build_comparison_prompt(
            prompt=prompt,
            output_a=output_a,
            output_b=output_b,
            category=category,
            rubric=rubric,
            blind=self.blind_evaluation
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": comparison_prompt}]
            )

            return self._parse_comparison_response(
                response.content[0].text,
                rubric["criteria"],
                category
            )

        except Exception as e:
            print(f"Judge LLM 比较失败: {e}")
            return {"error": str(e)}

    def _build_evaluation_prompt(
        self,
        prompt: str,
        output: str,
        category: str,
        rubric: Dict[str, Any]
    ) -> str:
        """构建评估提示词"""
        criteria_desc = "\n".join([
            f"- {c}: {ScoringRubric.get_criteria_description(c)}"
            for c in rubric["criteria"]
        ])

        return f"""你是一个专业的 AI 输出质量评估专家。

任务类别：{category}

原始提示词：
{prompt}

模型输出：
{output}

评估标准（每项 1-5 分）：
{criteria_desc}

评分标准：
- 5 分：优秀，超出预期
- 4 分：良好，很好地满足预期
- 3 分：达标，满足最低要求
- 2 分：较差，低于预期，有明显问题
- 1 分：很差，未达到要求

请提供 JSON 格式的评估结果：
{{
    "scores": {{
        "criterion1": {{"score": 4, "justification": "原因"}},
        "criterion2": {{"score": 3, "justification": "原因"}}
    }},
    "overall_score": 3.5,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["缺点1", "缺点2"]
}}
"""

    def _build_comparison_prompt(
        self,
        prompt: str,
        output_a: str,
        output_b: str,
        category: str,
        rubric: Dict[str, Any],
        blind: bool
    ) -> str:
        """构建比较提示词"""
        label_a = "模型 A" if blind else "DeepSeek"
        label_b = "模型 B" if blind else "GLM"

        criteria_desc = "\n".join([
            f"- {c}: {ScoringRubric.get_criteria_description(c)}"
            for c in rubric["criteria"]
        ])

        return f"""你是一个专业的 AI 模型输出比较专家。

任务类别：{category}

原始提示词：
{prompt}

{label_a} 的输出：
{output_a}

{label_b} 的输出：
{output_b}

评估标准：
{criteria_desc}

请比较两个输出的质量，并给出 JSON 格式结果：
{{
    "model_a_scores": {{"criterion1": 4, "criterion2": 3}, "overall": 3.5},
    "model_b_scores": {{"criterion1": 5, "criterion2": 4}, "overall": 4.2},
    "winner": "model_b" | "model_a" | "tie",
    "reasoning": "比较理由",
    "key_differences": ["差异1", "差异2"]
}}
"""

    def _parse_evaluation_response(
        self,
        response: str,
        criteria: List[str],
        category: str
    ) -> Dict[str, Any]:
        """解析评估响应（简化版本）"""
        # 在实际实现中，这里应该解析 JSON 响应
        # 为了简化，返回基本结构
        return {
            "category": category,
            "response_text": response,
            "criteria_evaluated": criteria
        }

    def _parse_comparison_response(
        self,
        response: str,
        criteria: List[str],
        category: str
    ) -> Dict[str, Any]:
        """解析比较响应（简化版本）"""
        # 在实际实现中，这里应该解析 JSON 响应
        return {
            "category": category,
            "response_text": response,
            "criteria_evaluated": criteria
        }
