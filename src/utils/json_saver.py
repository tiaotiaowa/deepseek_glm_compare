"""评测数据JSON保存器

在维度得分计算后将完整评测结果保存到JSON文件
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class BenchmarkJSONSaver:
    """评测数据JSON保存器"""

    def __init__(self, output_dir: str = "results/json"):
        """
        初始化保存器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # 创建增量保存目录
        self.incremental_dir = self.output_dir / "incremental"
        self.incremental_dir.mkdir(parents=True, exist_ok=True)

    def save_evaluation_data(
        self,
        statistics: Dict[str, Any],
        quality_scores: Dict[str, Any],
        summaries: List[Any],
        raw_results: List[Dict[str, Any]],
        dimension_weights: Dict[str, float],
        quality_evaluations: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """
        保存完整评测数据到JSON

        Args:
            statistics: 测试统计信息
            quality_scores: 质量评估得分
            summaries: 性能汇总数据
            raw_results: 原始测试结果
            dimension_weights: 维度权重
            quality_evaluations: 质量评估详情
            config: 配置快照

        Returns:
            str: JSON文件路径
        """
        # 构建完整的JSON数据结构
        json_data = self._build_evaluation_json(
            statistics=statistics,
            quality_scores=quality_scores,
            summaries=summaries,
            raw_results=raw_results,
            dimension_weights=dimension_weights,
            quality_evaluations=quality_evaluations,
            config=config
        )

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"minimax_evaluation_{timestamp}.json"
        filepath = self.output_dir / filename

        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def save_incremental_data(
        self,
        completed_count: int,
        total_count: int,
        statistics: Dict[str, Any],
        quality_scores: Dict[str, Any],
        summaries: List[Any],
        incremental_results: List[Dict[str, Any]],
        dimension_weights: Dict[str, float],
        config: Dict[str, Any]
    ) -> str:
        """
        保存增量评测数据到JSON

        Args:
            completed_count: 已完成的测试用例数
            total_count: 总测试用例数
            statistics: 测试统计信息
            quality_scores: 质量评估得分
            summaries: 性能汇总数据
            incremental_results: 新增的原始测试结果
            dimension_weights: 维度权重
            config: 配置快照

        Returns:
            str: JSON文件路径
        """
        # 构建增量JSON数据结构
        json_data = {
            "metadata": {
                "type": "incremental",
                "completed_count": completed_count,
                "total_count": total_count,
                "progress_percentage": f"{completed_count/total_count*100:.1f}%",
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "dimension_weights": dimension_weights
            },
            "statistics": statistics,
            "quality_scores": quality_scores,
            "performance_summaries": self._build_performance_summaries(
                self._process_summaries(summaries), dimension_weights
            ),
            "incremental_results": incremental_results,
            "new_results_count": len(incremental_results)
        }

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"incremental_{completed_count}of{total_count}_{timestamp}.json"
        filepath = self.incremental_dir / filename

        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def _build_evaluation_json(
        self,
        statistics: Dict[str, Any],
        quality_scores: Dict[str, Any],
        summaries: List[Any],
        raw_results: List[Dict[str, Any]],
        dimension_weights: Dict[str, float],
        quality_evaluations: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建完整的JSON数据结构"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 构建metadata
        metadata = {
            "timestamp": timestamp,
            "report_id": f"minimax_eval_{timestamp}",
            "evaluation_mode": config.get("minimax_standard", {}).get("evaluation_mode", "standard"),
            "start_time": statistics.get("start_time"),
            "end_time": statistics.get("end_time"),
            "models_tested": list(quality_scores.keys()),
            "total_tests": statistics.get("total_tests", 0)
        }

        # 处理summaries数据
        summaries_dict = self._process_summaries(summaries)

        # 构建performance_summaries
        performance_summaries = self._build_performance_summaries(
            summaries_dict, dimension_weights
        )

        # 计算模型排名
        rankings = self._calculate_model_rankings(quality_scores)

        # 生成使用建议
        recommendations = self._generate_recommendations(quality_scores)

        # 为quality_scores添加排名和建议
        enhanced_quality_scores = self._enhance_quality_scores(
            quality_scores, rankings, recommendations
        )

        # 构建完整JSON
        json_data = {
            "metadata": metadata,
            "statistics": statistics,
            "dimension_weights": dimension_weights,
            "quality_scores": enhanced_quality_scores,
            "performance_summaries": performance_summaries,
            "quality_evaluations": self._process_quality_evaluations(quality_evaluations),
            "raw_results": raw_results,
            "config_snapshot": self._create_config_snapshot(config)
        }

        return json_data

    def _process_summaries(self, summaries: List[Any]) -> Dict[str, Dict]:
        """处理summaries数据，转换为字典格式"""
        summaries_dict = {}

        for summary in summaries:
            if hasattr(summary, 'to_dict'):
                summary_dict = summary.to_dict()
            else:
                summary_dict = summary

            category = summary_dict.get("category")
            model_name = summary_dict.get("model_name")

            if category not in summaries_dict:
                summaries_dict[category] = {}

            summaries_dict[category][model_name] = summary_dict

        return summaries_dict

    def _build_performance_summaries(
        self,
        summaries_dict: Dict[str, Dict],
        dimension_weights: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """构建性能汇总数据"""

        performance_summaries = []

        for dimension, models_data in summaries_dict.items():
            summary_entry = {
                "dimension": dimension,
                "category": dimension,
                "model_summaries": {},
                "comparison": {}
            }

            # 提取各模型数据
            for model_name, model_data in models_data.items():
                summary_entry["model_summaries"][model_name] = {
                    "test_count": model_data.get("test_count", 0),
                    "ttft_mean": model_data.get("ttft_mean", 0),
                    "ttft_median": model_data.get("ttft_median", 0),
                    "ttft_std": model_data.get("ttft_std", 0),
                    "ttft_min": model_data.get("ttft_min", 0),
                    "ttft_max": model_data.get("ttft_max", 0),
                    "speed_mean": model_data.get("speed_mean", 0),
                    "speed_median": model_data.get("speed_median", 0),
                    "speed_std": model_data.get("speed_std", 0),
                    "total_time_mean": model_data.get("total_time_mean", 0),
                    "total_time_median": model_data.get("total_time_median", 0),
                    "success_rate": model_data.get("success_count", 0) / max(model_data.get("test_count", 1), 1)
                }

            # 计算对比数据
            if len(models_data) >= 2:
                model_names = list(models_data.keys())
                if len(model_names) == 2:
                    model1, model2 = model_names
                    data1 = summary_entry["model_summaries"][model1]
                    data2 = summary_entry["model_summaries"][model2]

                    # TTFT对比
                    ttft_winner = model1 if data1["ttft_mean"] < data2["ttft_mean"] else model2
                    ttft_improvement = abs(data1["ttft_mean"] - data2["ttft_mean"]) / max(data1["ttft_mean"], data2["ttft_mean"]) * 100

                    # 速度对比
                    speed_winner = model1 if data1["speed_mean"] > data2["speed_mean"] else model2
                    speed_improvement = abs(data1["speed_mean"] - data2["speed_mean"]) / min(data1["speed_mean"], data2["speed_mean"]) * 100

                    summary_entry["comparison"] = {
                        "ttft_winner": ttft_winner,
                        "ttft_improvement": f"{ttft_improvement:.1f}%",
                        "speed_winner": speed_winner,
                        "speed_improvement": f"{speed_improvement:.1f}%"
                    }

            performance_summaries.append(summary_entry)

        return performance_summaries

    def _process_quality_evaluations(
        self,
        quality_evaluations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理质量评估数据"""

        if not quality_evaluations:
            return {
                "judges_used": [],
                "judge_weights": {},
                "evaluations_by_dimension": {}
            }

        # 提取Judge信息
        judges_used = []
        judge_weights = {}

        overall = quality_evaluations.get("overall", {})
        for judge_name, judge_data in overall.items():
            judges_used.append(judge_name)
            # 假设权重存储在某个地方，这里使用默认值
            judge_weights[judge_name] = 0.33  # 默认均等权重

        # 按维度组织评估数据
        evaluations_by_dimension = {}
        by_dimension = quality_evaluations.get("by_dimension", {})

        for dimension, dim_data in by_dimension.items():
            evaluations_by_dimension[dimension] = {
                "total_evaluations": dim_data.get("total_evaluations", 0),
                "successful_evaluations": dim_data.get("successful_evaluations", 0),
                "judge_consistency": dim_data.get("consistency", 0.0),
                "average_scores": dim_data.get("average_scores", {})
            }

        return {
            "judges_used": judges_used,
            "judge_weights": judge_weights,
            "evaluations_by_dimension": evaluations_by_dimension
        }

    def _calculate_model_rankings(self, quality_scores: Dict) -> Dict[str, int]:
        """计算模型排名"""
        rankings = {}

        # 按总分排序
        sorted_models = sorted(
            quality_scores.items(),
            key=lambda x: x[1]["overall_score"],
            reverse=True
        )

        for rank, (model_name, _) in enumerate(sorted_models, start=1):
            rankings[model_name] = rank

        return rankings

    def _generate_recommendations(self, quality_scores: Dict) -> Dict[str, Dict]:
        """生成使用建议"""

        recommendations = {}

        for model_name, scores in quality_scores.items():
            overall_score = scores["overall_score"]
            dimension_scores = scores["dimension_scores"]

            # 识别优势维度
            strengths = []
            weaknesses = []

            for dim_name, score in dimension_scores.items():
                if score >= 9.0:
                    strengths.append(f"{self._translate_dimension(dim_name)}优秀 ({score:.1f}分)")
                elif score <= 7.0:
                    weaknesses.append(f"{self._translate_dimension(dim_name)}有待提升 ({score:.1f}分)")

            # 生成推荐场景
            model_recommendations = []
            if overall_score >= 8.5:
                model_recommendations.append("适合作为主要模型")
                model_recommendations.append("推荐用于核心业务场景")
            elif overall_score >= 7.0:
                model_recommendations.append("可作为辅助模型")
                model_recommendations.append("适合特定场景使用")
            else:
                model_recommendations.append("建议谨慎使用")
                model_recommendations.append("需要进一步优化")

            recommendations[model_name] = {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": model_recommendations
            }

        return recommendations

    def _enhance_quality_scores(
        self,
        quality_scores: Dict,
        rankings: Dict[str, int],
        recommendations: Dict[str, Dict]
    ) -> Dict:
        """增强quality_scores，添加排名和建议"""

        enhanced = {}

        for model_name, scores in quality_scores.items():
            overall_score = scores["overall_score"]

            # 计算等级
            if overall_score >= 9.0:
                grade = "优秀"
                grade_color = "#10B981"
            elif overall_score >= 7.5:
                grade = "良好"
                grade_color = "#34D399"
            elif overall_score >= 6.0:
                grade = "合格"
                grade_color = "#FBBF24"
            else:
                grade = "不合格"
                grade_color = "#F87171"

            enhanced[model_name] = {
                **scores,
                "rank": rankings[model_name],
                "grade": grade,
                "grade_color": grade_color,
                "strengths": recommendations[model_name]["strengths"],
                "weaknesses": recommendations[model_name]["weaknesses"],
                "recommendations": recommendations[model_name]["recommendations"]
            }

        return enhanced

    def _create_config_snapshot(self, config: Dict) -> Dict[str, Any]:
        """创建配置快照"""
        return {
            "apis": {
                name: {
                    "model": api_config.get("model"),
                    "base_url": api_config.get("base_url")
                }
                for name, api_config in config.get("apis", {}).items()
            },
            "benchmark": {
                "warmup_runs": config.get("benchmark", {}).get("warmup_runs", 2),
                "test_runs": config.get("benchmark", {}).get("test_runs", 3)
            },
            "quality": {
                "enabled": config.get("quality", {}).get("enabled", False),
                "judges": list(config.get("quality", {}).get("judges", {}).keys())
            }
        }

    def _translate_dimension(self, dim_name: str) -> str:
        """翻译维度名称"""
        translations = {
            "basic_performance": "基础性能",
            "core_capabilities": "核心能力",
            "practical_scenarios": "实用场景",
            "advanced_features": "高级特性"
        }
        return translations.get(dim_name, dim_name)
