"""MiniMax 标准评分系统

提供三模型交叉评价的评分计算功能:
- MiniMax 40% + DeepSeek 30% + GLM 30% 加权评分
- Z-score 标准化
- 95% 置信区间计算
- Pearson 相关系数
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional


class MiniMaxScoreCalculator:
    """MiniMax 标准评分计算器

    实现基于 MiniMax 标准的三模型交叉评价评分计算
    """

    @staticmethod
    def calculate_weighted_score(
        minimax_score: float,
        deepseek_score: float,
        glm_score: float,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        计算三模型加权评分

        默认权重：MiniMax 40% + DeepSeek 30% + GLM 30%

        Args:
            minimax_score: MiniMax 评分 (0-10)
            deepseek_score: DeepSeek 自评分数 (0-10)
            glm_score: GLM 评分 (0-10)
            weights: 可选的自定义权重

        Returns:
            Dict containing:
                - weighted_score: 加权总分
                - minimax_score: MiniMax 原始分数
                - deepseek_score: DeepSeek 原始分数
                - glm_score: GLM 原始分数
                - weights: 使用的权重
        """
        if weights is None:
            weights = {"minimax": 0.40, "deepseek": 0.30, "glm": 0.30}

        weighted_score = (
            minimax_score * weights["minimax"] +
            deepseek_score * weights["deepseek"] +
            glm_score * weights["glm"]
        )

        return {
            "weighted_score": round(weighted_score, 2),
            "minimax_score": round(minimax_score, 2),
            "deepseek_score": round(deepseek_score, 2),
            "glm_score": round(glm_score, 2),
            "weights": weights
        }

    @staticmethod
    def calculate_dimension_score(
        test_scores: List[Dict[str, float]],
        test_weights: List[float]
    ) -> Dict[str, Any]:
        """
        计算维度加权总分

        Args:
            test_scores: 每个测试的评分列表
            test_weights: 每个测试的权重列表

        Returns:
            Dict containing:
                - dimension_score: 维度总分
                - weighted_sum: 加权总和
                - total_weight: 总权重
                - test_count: 测试数量
        """
        if len(test_scores) != len(test_weights):
            raise ValueError("test_scores and test_weights must have the same length")

        weighted_sum = 0.0
        total_weight = 0.0

        for score_dict, weight in zip(test_scores, test_weights):
            # 使用加权分数
            weighted_score = score_dict.get("weighted_score", score_dict.get("overall_score", 0))
            weighted_sum += weighted_score * weight
            total_weight += weight

        dimension_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        return {
            "dimension_score": round(dimension_score, 2),
            "weighted_sum": round(weighted_sum, 2),
            "total_weight": round(total_weight, 2),
            "test_count": len(test_scores)
        }

    @staticmethod
    def calculate_overall_score(
        dimension_scores: Dict[str, float],
        dimension_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        计算综合总分

        Args:
            dimension_scores: 各维度得分字典
            dimension_weights: 各维度权重字典

        Returns:
            Dict containing:
                - overall_score: 综合总分
                - dimension_scores: 各维度原始得分
                - dimension_weights: 各维度权重
                - breakdown: 各维度贡献明细
        """
        weighted_sum = 0.0
        breakdown = {}

        for dimension, score in dimension_scores.items():
            weight = dimension_weights.get(dimension, 0.0)
            contribution = score * weight
            weighted_sum += contribution
            breakdown[dimension] = {
                "score": round(score, 2),
                "weight": weight,
                "contribution": round(contribution, 2)
            }

        # 计算总分，防止除零
        total_weight = sum(dimension_weights.values())
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        return {
            "overall_score": round(overall_score, 2),
            "dimension_scores": {k: round(v, 2) for k, v in dimension_scores.items()},
            "dimension_weights": dimension_weights,
            "breakdown": breakdown
        }

    @staticmethod
    def z_score_normalize(scores: List[float]) -> List[float]:
        """
        Z-score 标准化

        Args:
            scores: 原始分数列表

        Returns:
            标准化后的分数列表
        """
        scores_array = np.array(scores)
        mean = np.mean(scores_array)
        std = np.std(scores_array)

        if std == 0:
            return [0.0] * len(scores)

        z_scores = [(x - mean) / std for x in scores]
        return [round(z, 4) for z in z_scores]

    @staticmethod
    def min_max_normalize(scores: List[float]) -> List[float]:
        """
        Min-Max 标准化到 [0, 1] 区间

        Args:
            scores: 原始分数列表

        Returns:
            标准化后的分数列表
        """
        if not scores:
            return []

        min_val = min(scores)
        max_val = max(scores)

        if max_val == min_val:
            return [0.5] * len(scores)

        normalized = [(x - min_val) / (max_val - min_val) for x in scores]
        return [round(n, 4) for n in normalized]

    @staticmethod
    def calculate_confidence_interval(
        scores: List[float],
        confidence: float = 0.95
    ) -> Tuple[float, float, float, float]:
        """
        计算置信区间

        Args:
            scores: 分数列表
            confidence: 置信水平 (默认 0.95)

        Returns:
            Tuple of (mean, lower_bound, upper_bound, margin_of_error)
        """
        scores_array = np.array(scores)
        mean = np.mean(scores_array)
        std = np.std(scores_array)
        n = len(scores_array)

        # Z-score for confidence level
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z_score = z_scores.get(confidence, 1.96)

        # Standard error
        std_error = std / np.sqrt(n) if n > 0 else 0

        # Margin of error
        margin_of_error = z_score * std_error

        lower_bound = mean - margin_of_error
        upper_bound = mean + margin_of_error

        return (
            round(mean, 2),
            round(lower_bound, 2),
            round(upper_bound, 2),
            round(margin_of_error, 2)
        )

    @staticmethod
    def calculate_pearson_correlation(
        scores1: List[float],
        scores2: List[float]
    ) -> Dict[str, Any]:
        """
        计算 Pearson 相关系数

        Args:
            scores1: 第一组分数
            scores2: 第二组分数

        Returns:
            Dict containing:
                - correlation: 相关系数
                - p_value: p值 (如果scipy可用)
                - interpretation: 相关性解释
        """
        if len(scores1) != len(scores2):
            raise ValueError("scores1 and scores2 must have the same length")

        if len(scores1) < 2:
            return {
                "correlation": 0.0,
                "p_value": None,
                "interpretation": "Insufficient data"
            }

        # Calculate correlation
        try:
            from scipy import stats
            correlation, p_value = stats.pearsonr(scores1, scores2)
        except ImportError:
            # Fallback to manual calculation
            n = len(scores1)
            sum1 = sum(scores1)
            sum2 = sum(scores2)
            sum1_sq = sum(x**2 for x in scores1)
            sum2_sq = sum(x**2 for x in scores2)
            sum_products = sum(x * y for x, y in zip(scores1, scores2))

            numerator = n * sum_products - sum1 * sum2
            denominator = np.sqrt((n * sum1_sq - sum1**2) * (n * sum2_sq - sum2**2))

            correlation = numerator / denominator if denominator != 0 else 0
            p_value = None

        # Interpretation
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            interpretation = "Very strong positive" if correlation > 0 else "Very strong negative"
        elif abs_corr >= 0.6:
            interpretation = "Strong positive" if correlation > 0 else "Strong negative"
        elif abs_corr >= 0.4:
            interpretation = "Moderate positive" if correlation > 0 else "Moderate negative"
        elif abs_corr >= 0.2:
            interpretation = "Weak positive" if correlation > 0 else "Weak negative"
        else:
            interpretation = "Very weak or no correlation"

        return {
            "correlation": round(correlation, 3),
            "p_value": round(p_value, 4) if p_value is not None else None,
            "interpretation": interpretation
        }

    @staticmethod
    def calculate_inter_rater_reliability(
        ratings: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """
        计算评价者间信度

        Args:
            ratings: 评价者评分字典 {rater_name: [scores]}

        Returns:
            Dict containing:
                - average_correlation: 平均相关系数
                - correlations: 各评价者之间的相关系数矩阵
                - reliability: 信度评估
        """
        if len(ratings) < 2:
            return {
                "average_correlation": 0.0,
                "correlations": {},
                "reliability": "Insufficient raters"
            }

        rater_names = list(ratings.keys())
        correlations = {}
        correlation_values = []

        # Calculate pairwise correlations
        for i, rater1 in enumerate(rater_names):
            for rater2 in rater_names[i+1:]:
                scores1 = ratings[rater1]
                scores2 = ratings[rater2]

                if len(scores1) == len(scores2) and len(scores1) > 1:
                    corr_result = MiniMaxScoreCalculator.calculate_pearson_correlation(scores1, scores2)
                    key = f"{rater1}_vs_{rater2}"
                    correlations[key] = corr_result["correlation"]
                    correlation_values.append(corr_result["correlation"])

        # Average correlation
        avg_correlation = np.mean(correlation_values) if correlation_values else 0.0

        # Reliability assessment
        if avg_correlation >= 0.8:
            reliability = "Excellent"
        elif avg_correlation >= 0.6:
            reliability = "Good"
        elif avg_correlation >= 0.4:
            reliability = "Fair"
        else:
            reliability = "Poor"

        return {
            "average_correlation": round(avg_correlation, 3),
            "correlations": correlations,
            "reliability": reliability
        }

    @staticmethod
    def grade_score(score: float) -> str:
        """
        将分数转换为等级

        Args:
            score: 0-10 分数

        Returns:
            等级字符串
        """
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

    @staticmethod
    def calculate_statistics(scores: List[float]) -> Dict[str, float]:
        """
        计算基本统计量

        Args:
            scores: 分数列表

        Returns:
            Dict containing:
                - mean: 均值
                - median: 中位数
                - std: 标准差
                - min: 最小值
                - max: 最大值
                - q25: 第25百分位
                - q75: 第75百分位
                - cv: 变异系数
        """
        if not scores:
            return {}

        scores_array = np.array(scores)
        mean = np.mean(scores_array)
        std = np.std(scores_array)

        return {
            "mean": round(mean, 2),
            "median": round(float(np.median(scores_array)), 2),
            "std": round(std, 2),
            "min": round(float(np.min(scores_array)), 2),
            "max": round(float(np.max(scores_array)), 2),
            "q25": round(float(np.percentile(scores_array, 25)), 2),
            "q75": round(float(np.percentile(scores_array, 75)), 2),
            "cv": round(std / mean, 2) if mean != 0 else 0.0
        }
