"""响应解析器 - 统一的评估响应解析逻辑

这个模块从 judge_manager.py 中提取了响应解析的逻辑，
包括标准评估响应和 MiniMax 评估响应的解析。

使用示例:
    from src.quality.response_parser import ResponseParser

    # 解析标准评估响应
    result = ResponseParser.parse_standard(
        response_text='{"scores": {...}, "overall_score": 4.2}',
        criteria=["accuracy", "completeness"],
        category="qa_simple"
    )
"""

import json
import re
from typing import Dict, List, Any, Optional


class ResponseParser:
    """响应解析器 - 提供统一的响应解析接口

    从 judge_manager.py 中提取，用于解析各种评估场景的响应
    """

    @staticmethod
    def parse_standard(
        response: str,
        criteria: List[str],
        category: str
    ) -> Dict[str, Any]:
        """
        解析标准评估响应（1-5分制）

        Args:
            response: Judge的响应文本
            criteria: 评估标准列表
            category: 测试类别

        Returns:
            解析后的评估结果字典，包含：
            - scores: 各标准分数
            - overall_score: 总分
            - strengths: 优点列表
            - weaknesses: 缺点列表
            - reasoning: 评估理由
        """
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\\{[\\s\\S]*\\}', response)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)

                # 验证并返回
                if "scores" in result:
                    # 提取简单分数（从嵌套结构中提取）
                    simple_scores = ResponseParser._extract_simple_scores(
                        result["scores"], criteria
                    )
                    result["scores"] = simple_scores
                    return result

            # 如果解析失败，尝试从文本中提取分数
            return ResponseParser._extract_scores_from_text(response, criteria)

        except Exception as e:
            print(f"Failed to parse evaluation response: {e}")
            return ResponseParser._extract_scores_from_text(response, criteria)

    @staticmethod
    def parse_minimax(response_text: str) -> Optional[Dict[str, Any]]:
        """
        解析 MiniMax 标准评估响应（0-10分制）

        Args:
            response_text: Judge的响应文本

        Returns:
            包含model_a_score和model_b_score的字典，如果解析失败返回None
        """
        try:
            # 尝试直接解析JSON
            result = json.loads(response_text)

            # 验证必需字段
            if "model_a" in result and "model_b" in result:
                return {
                    "model_a_score": result["model_a"],
                    "model_b_score": result["model_b"]
                }

        except json.JSONDecodeError:
            pass

        # 尝试提取JSON代码块
        json_match = re.search(r'```json\\s*(\\{[\\s\\S]*\\})\\s*```', response_text)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                if "model_a" in result and "model_b" in result:
                    return {
                        "model_a_score": result["model_a"],
                        "model_b_score": result["model_b"]
                    }
            except json.JSONDecodeError:
                pass

        # 正则表达式提取分数
        model_a_scores = {}
        model_b_scores = {}
        required_fields = ["accuracy_score", "completeness_score", "logic_score", "creativity_score"]

        for field in required_fields:
            # 查找 model_a 的分数
            pattern_a = f'"model_a"\\\\s*:\\\\s*\\{{[^}}]*"{field}"\\\\s*:\\\\s*([0-9.]+)'
            match_a = re.search(pattern_a, response_text)
            if match_a:
                model_a_scores[field] = float(match_a.group(1))

            # 查找 model_b 的分数
            pattern_b = f'"model_b"\\\\s*:\\\\s*\\{{[^}}]*"{field}"\\\\s*:\\\\s*([0-9.]+)'
            match_b = re.search(pattern_b, response_text)
            if match_b:
                model_b_scores[field] = float(match_b.group(1))

        # 如果找到了足够的分数，计算总分
        if len(model_a_scores) >= 4 and len(model_b_scores) >= 4:
            weights = {
                "accuracy_score": 0.30,
                "completeness_score": 0.25,
                "logic_score": 0.25,
                "creativity_score": 0.20
            }

            # 计算model_a总分
            if "overall_score" not in model_a_scores:
                model_a_scores["overall_score"] = sum(
                    model_a_scores.get(f, 0) * w
                    for f, w in weights.items()
                )

            # 计算model_b总分
            if "overall_score" not in model_b_scores:
                model_b_scores["overall_score"] = sum(
                    model_b_scores.get(f, 0) * w
                    for f, w in weights.items()
                )

            return {
                "model_a_score": model_a_scores,
                "model_b_score": model_b_scores
            }

        # 解析失败
        return None

    @staticmethod
    def _extract_simple_scores(scores_data: Dict, criteria: List[str]) -> Dict[str, float]:
        """
        从嵌套的分数结构中提取简单分数

        Args:
            scores_data: 分数数据（可能是嵌套结构）
            criteria: 评估标准列表

        Returns:
            简单的分数字典 {criterion: score}
        """
        simple_scores = {}
        for criterion in criteria:
            if criterion in scores_data:
                if isinstance(scores_data[criterion], dict):
                    # 如果是嵌套结构，提取 score 字段
                    simple_scores[criterion] = scores_data[criterion].get("score", 3.0)
                else:
                    # 如果已经是数字
                    simple_scores[criterion] = float(scores_data[criterion])
            else:
                simple_scores[criterion] = 3.0  # 默认中等分数

        return simple_scores

    @staticmethod
    def _extract_scores_from_text(text: str, criteria: List[str]) -> Dict[str, Any]:
        """
        从文本中提取分数（备用解析方法）

        Args:
            text: 响应文本
            criteria: 评估标准列表

        Returns:
            评估结果字典
        """
        scores = {}
        for criterion in criteria:
            # 尝试在文本中找到该标准的分数
            pattern = rf'{criterion}.*?(\\d+(?:\\.\\d+)?)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                # 确保分数在 1-5 范围内
                scores[criterion] = max(1.0, min(5.0, score))
            else:
                # 默认给中等分数
                scores[criterion] = 3.0

        return {
            "scores": scores,
            "strengths": [],
            "weaknesses": [],
            "reasoning": text[:500] if len(text) > 500 else text,
            "overall_score": sum(scores.values()) / len(scores) if scores else 3.0
        }

    @staticmethod
    def validate_response(response: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        验证响应是否包含所有必需字段

        Args:
            response: 响应字典
            required_fields: 必需字段列表

        Returns:
            是否有效
        """
        if not isinstance(response, dict):
            return False

        return all(field in response for field in required_fields)

    @staticmethod
    def extract_overall_score(response: Dict[str, Any]) -> float:
        """
        从响应中提取总分

        Args:
            response: 响应字典

        Returns:
            总分（如果不存在返回0.0）
        """
        if not isinstance(response, dict):
            return 0.0

        # 尝试多种可能的字段名
        possible_keys = ["overall_score", "total_score", "score", "rating"]
        for key in possible_keys:
            if key in response:
                try:
                    return float(response[key])
                except (ValueError, TypeError):
                    continue

        # 如果没有找到，尝试从scores计算
        if "scores" in response and isinstance(response["scores"], dict):
            scores = [s for s in response["scores"].values() if isinstance(s, (int, float))]
            if scores:
                return sum(scores) / len(scores)

        return 0.0
