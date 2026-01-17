"""评分标准化工具

提供评分数据标准化、置信区间计算、相关性分析等功能
用于 MiniMax 标准评测体系
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from scipy import stats


class ScoreNormalizer:
    """评分标准化工具类"""

    @staticmethod
    def z_score_normalize(scores: List[float]) -> List[float]:
        """
        Z-score 标准化
        Z = (X - μ) / σ

        Args:
            scores: 原始分数列表

        Returns:
            List[float]: 标准化后的分数列表
        """
        if not scores:
            return []

        scores_array = np.array(scores, dtype=float)
        mean = np.mean(scores_array)
        std = np.std(scores_array)

        if std == 0:
            # 所有分数相同，返回 0
            return [0.0] * len(scores)

        return [(x - mean) / std for x in scores]

    @staticmethod
    def min_max_normalize(scores: List[float]) -> List[float]:
        """
        Min-Max 标准化
        Z = (X - X_min) / (X_max - X_min)

        Args:
            scores: 原始分数列表

        Returns:
            List[float]: 标准化到 [0, 1] 的分数列表
        """
        if not scores:
            return []

        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:
            # 所有分数相同，返回 0.5
            return [0.5] * len(scores)

        return [(x - min_score) / (max_score - min_score) for x in scores]

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
            Tuple[float, float, float, float]: (均值, 下限, 上限, 误差范围)
        """
        if not scores:
            return 0.0, 0.0, 0.0, 0.0

        scores_array = np.array(scores, dtype=float)
        mean = np.mean(scores_array)
        std = np.std(scores_array, ddof=1)  # 使用样本标准差
        n = len(scores_array)

        # 95% 置信区间使用 1.96，99% 使用 2.58
        z_score = 1.96 if confidence >= 0.95 else 1.645
        margin_of_error = z_score * std / np.sqrt(n)

        lower = mean - margin_of_error
        upper = mean + margin_of_error

        return mean, lower, upper, margin_of_error

    @staticmethod
    def calculate_pearson_correlation(
        scores1: List[float],
        scores2: List[float]
    ) -> Tuple[float, float]:
        """
        计算 Pearson 相关系数

        Args:
            scores1: 第一组分数
            scores2: 第二组分数

        Returns:
            Tuple[float, float]: (相关系数, p值)
        """
        if len(scores1) != len(scores2) or len(scores1) < 2:
            return 0.0, 1.0

        try:
            correlation, p_value = stats.pearsonr(scores1, scores2)
            return float(correlation), float(p_value)
        except Exception as e:
            print(f"计算 Pearson 相关系数时出错: {e}")
            return 0.0, 1.0

    @staticmethod
    def calculate_descriptive_stats(scores: List[float]) -> Dict[str, float]:
        """
        计算描述性统计量

        Args:
            scores: 分数列表

        Returns:
            Dict[str, float]: 包含均值、中位数、标准差、最小值、最大值等统计量
        """
        if not scores:
            return {
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0,
                "cv": 0.0  # 变异系数
            }

        scores_array = np.array(scores, dtype=float)
        mean = np.mean(scores_array)
        std = np.std(scores_array, ddof=1)

        return {
            "mean": float(mean),
            "median": float(np.median(scores_array)),
            "std": float(std),
            "min": float(np.min(scores_array)),
            "max": float(np.max(scores_array)),
            "count": len(scores),
            "cv": float(std / mean) if mean != 0 else 0.0,  # 变异系数
            "q25": float(np.percentile(scores_array, 25)),
            "q75": float(np.percentile(scores_array, 75)),
        }

    @staticmethod
    def grade_score(
        score: float,
        grade_thresholds: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> str:
        """
        根据分数给出等级

        Args:
            score: 分数 (0-10)
            grade_thresholds: 自定义等级阈值

        Returns:
            str: 等级名称
        """
        if grade_thresholds is None:
            # 默认阈值
            grade_thresholds = {
                "excellent": (9.0, 10.0),
                "good": (7.5, 8.9),
                "qualified": (6.0, 7.4),
                "unqualified": (3.0, 5.9),
                "critical": (0, 2.9)
            }

        if score >= grade_thresholds["excellent"][0]:
            return "优秀"
        elif score >= grade_thresholds["good"][0]:
            return "良好"
        elif score >= grade_thresholds["qualified"][0]:
            return "合格"
        elif score >= grade_thresholds["unqualified"][0]:
            return "不合格"
        else:
            return "严重缺陷"

    @staticmethod
    def calculate_cohens_d(
        scores1: List[float],
        scores2: List[float]
    ) -> float:
        """
        计算 Cohen's d 效应量

        Args:
            scores1: 第一组分数
            scores2: 第二组分数

        Returns:
            float: Cohen's d 值
        """
        if not scores1 or not scores2:
            return 0.0

        arr1 = np.array(scores1, dtype=float)
        arr2 = np.array(scores2, dtype=float)

        mean1, mean2 = np.mean(arr1), np.mean(arr2)
        std1, std2 = np.std(arr1, ddof=1), np.std(arr2, ddof=1)

        n1, n2 = len(arr1), len(arr2)

        # 合并标准差
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

        if pooled_std == 0:
            return 0.0

        return abs(mean1 - mean2) / pooled_std

    @staticmethod
    def interpret_cohens_d(d: float) -> str:
        """
        解释 Cohen's d 效应量

        Args:
            d: Cohen's d 值

        Returns:
            str: 效应量等级
        """
        if d >= 0.8:
            return "大效应"
        elif d >= 0.5:
            return "中等效应"
        elif d >= 0.2:
            return "小效应"
        else:
            return "极小效应"

    @staticmethod
    def calculate_inter_rater_reliability(
        ratings: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """
        计算评价者间信度

        Args:
            ratings: 评价者评分字典 {judge_name: [scores]}

        Returns:
            Dict[str, float]: 包含平均相关系数和一致性指标
        """
        judge_names = list(ratings.keys())

        if len(judge_names) < 2:
            return {
                "avg_correlation": 1.0,
                "consistency_level": "高一致性",
                "pairwise_correlations": {}
            }

        # 计算所有评价者对之间的相关性
        correlations = []
        pairwise = {}

        for i in range(len(judge_names)):
            for j in range(i + 1, len(judge_names)):
                judge1, judge2 = judge_names[i], judge_names[j]
                scores1 = ratings[judge1]
                scores2 = ratings[judge2]

                if len(scores1) == len(scores2) and len(scores1) > 1:
                    corr, _ = ScoreNormalizer.calculate_pearson_correlation(scores1, scores2)
                    correlations.append(corr)
                    pairwise[f"{judge1}_vs_{judge2}"] = corr

        if not correlations:
            return {
                "avg_correlation": 0.0,
                "consistency_level": "无法计算",
                "pairwise_correlations": pairwise
            }

        avg_corr = np.mean(correlations)

        # 一致性等级
        if avg_corr > 0.8:
            consistency = "高一致性"
        elif avg_corr > 0.5:
            consistency = "中一致性"
        else:
            consistency = "低一致性"

        return {
            "avg_correlation": float(avg_corr),
            "consistency_level": consistency,
            "pairwise_correlations": pairwise
        }
