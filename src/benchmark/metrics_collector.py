"""性能指标收集器"""

import numpy as np
from typing import List, Dict, Any
from datetime import datetime

from .test_result import TestResult, CategorySummary


class MetricsCollector:
    """性能指标收集器和统计计算器"""

    def __init__(self):
        """初始化指标收集器"""
        self.results: List[TestResult] = []
        self.start_time: datetime = datetime.now()

    def add_result(self, result: TestResult):
        """
        添加测试结果

        Args:
            result: 测试结果
        """
        self.results.append(result)

    def get_results_by_model(self, model_name: str) -> List[TestResult]:
        """
        按模型获取结果

        Args:
            model_name: 模型名称

        Returns:
            List[TestResult]: 该模型的所有结果
        """
        return [r for r in self.results if r.model_name == model_name]

    def get_results_by_category(self, category: str) -> List[TestResult]:
        """
        按类别获取结果

        Args:
            category: 测试类别

        Returns:
            List[TestResult]: 该类别的所有结果
        """
        return [r for r in self.results if r.test_category == category]

    def get_results_by_model_and_category(
        self,
        model_name: str,
        category: str
    ) -> List[TestResult]:
        """
        按模型和类别获取结果

        Args:
            model_name: 模型名称
            category: 测试类别

        Returns:
            List[TestResult]: 符合条件的结果
        """
        return [
            r for r in self.results
            if r.model_name == model_name and r.test_category == category
        ]

    def calculate_category_summary(
        self,
        model_name: str,
        category: str
    ) -> CategorySummary:
        """
        计算类别汇总统计

        Args:
            model_name: 模型名称
            category: 测试类别

        Returns:
            CategorySummary: 汇总统计
        """
        results = self.get_results_by_model_and_category(model_name, category)

        if not results:
            # 如果没有结果，返回零值
            return CategorySummary(
                category=category,
                model_name=model_name,
                ttft_mean=0.0,
                ttft_median=0.0,
                ttft_std=0.0,
                ttft_min=0.0,
                ttft_max=0.0,
                speed_mean=0.0,
                speed_median=0.0,
                speed_std=0.0,
                speed_min=0.0,
                speed_max=0.0,
                total_time_mean=0.0,
                total_time_median=0.0,
                total_time_std=0.0,
                test_count=0,
                success_count=0
            )

        # 提取各项指标
        ttfts = [r.ttft_ms for r in results if r.success]
        speeds = [r.tokens_per_second for r in results if r.success]
        total_times = [r.total_time_ms for r in results if r.success]

        # 计算统计量
        return CategorySummary(
            category=category,
            model_name=model_name,
            # TTFT 统计
            ttft_mean=float(np.mean(ttfts)) if ttfts else 0.0,
            ttft_median=float(np.median(ttfts)) if ttfts else 0.0,
            ttft_std=float(np.std(ttfts)) if ttfts else 0.0,
            ttft_min=float(np.min(ttfts)) if ttfts else 0.0,
            ttft_max=float(np.max(ttfts)) if ttfts else 0.0,
            # 生成速度统计
            speed_mean=float(np.mean(speeds)) if speeds else 0.0,
            speed_median=float(np.median(speeds)) if speeds else 0.0,
            speed_std=float(np.std(speeds)) if speeds else 0.0,
            speed_min=float(np.min(speeds)) if speeds else 0.0,
            speed_max=float(np.max(speeds)) if speeds else 0.0,
            # 总时间统计
            total_time_mean=float(np.mean(total_times)) if total_times else 0.0,
            total_time_median=float(np.median(total_times)) if total_times else 0.0,
            total_time_std=float(np.std(total_times)) if total_times else 0.0,
            # 测试数量
            test_count=len(results),
            success_count=sum(1 for r in results if r.success)
        )

    def calculate_all_summaries(
        self,
        model_names: List[str],
        categories: List[str]
    ) -> List[CategorySummary]:
        """
        计算所有模型和类别的汇总统计

        Args:
            model_names: 模型名称列表
            categories: 类别列表

        Returns:
            List[CategorySummary]: 所有汇总统计
        """
        summaries = []

        for model_name in model_names:
            for category in categories:
                summary = self.calculate_category_summary(model_name, category)
                summaries.append(summary)

        return summaries

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取整体统计信息

        Returns:
            Dict: 统计信息
        """
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests

        # 按模型统计
        model_stats = {}
        for result in self.results:
            if result.model_name not in model_stats:
                model_stats[result.model_name] = {"total": 0, "success": 0, "failed": 0}
            model_stats[result.model_name]["total"] += 1
            if result.success:
                model_stats[result.model_name]["success"] += 1
            else:
                model_stats[result.model_name]["failed"] += 1

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
            "model_stats": model_stats,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat()
        }

    def export_results(self) -> List[Dict[str, Any]]:
        """
        导出所有结果为字典列表

        Returns:
            List[Dict]: 所有结果的字典表示
        """
        return [result.to_dict() for result in self.results]

    def clear(self):
        """清空所有结果"""
        self.results.clear()
        self.start_time = datetime.now()

    def get_quality_statistics(self) -> Dict[str, Any]:
        """
        获取质量评估统计信息

        Returns:
            Dict: 质量评估统计信息
        """
        quality_stats = {
            "by_judge": {},
            "by_model": {},
            "by_category": {},
            "overall": {
                "total_evaluations": 0,
                "successful_evaluations": 0
            }
        }

        for result in self.results:
            if not result.quality_evaluations:
                continue

            for judge_name, evaluation in result.quality_evaluations.items():
                # 跳过失败的评估
                if not evaluation.success:
                    continue

                # 按 Judge 统计
                if judge_name not in quality_stats["by_judge"]:
                    quality_stats["by_judge"][judge_name] = {
                        "total_evaluations": 0,
                        "scores": [],
                        "avg_score": 0.0,
                        "judge_model": evaluation.judge_model
                    }

                quality_stats["by_judge"][judge_name]["total_evaluations"] += 1
                quality_stats["by_judge"][judge_name]["scores"].append(evaluation.overall_score)

                # 按模型统计
                if result.model_name not in quality_stats["by_model"]:
                    quality_stats["by_model"][result.model_name] = {}

                if judge_name not in quality_stats["by_model"][result.model_name]:
                    quality_stats["by_model"][result.model_name][judge_name] = {
                        "total_evaluations": 0,
                        "scores": [],
                        "avg_score": 0.0
                    }

                quality_stats["by_model"][result.model_name][judge_name]["total_evaluations"] += 1
                quality_stats["by_model"][result.model_name][judge_name]["scores"].append(evaluation.overall_score)

                # 按类别统计（增加模型分组）
                if result.test_category not in quality_stats["by_category"]:
                    quality_stats["by_category"][result.test_category] = {}

                if result.model_name not in quality_stats["by_category"][result.test_category]:
                    quality_stats["by_category"][result.test_category][result.model_name] = {}

                if judge_name not in quality_stats["by_category"][result.test_category][result.model_name]:
                    quality_stats["by_category"][result.test_category][result.model_name][judge_name] = {
                        "total_evaluations": 0,
                        "scores": [],
                        "avg_score": 0.0
                    }

                quality_stats["by_category"][result.test_category][result.model_name][judge_name]["total_evaluations"] += 1
                quality_stats["by_category"][result.test_category][result.model_name][judge_name]["scores"].append(evaluation.overall_score)

                # 整体统计
                quality_stats["overall"]["total_evaluations"] += 1
                quality_stats["overall"]["successful_evaluations"] += 1

        # 计算平均分数
        for judge_name, judge_stats in quality_stats["by_judge"].items():
            if judge_stats["scores"]:
                judge_stats["avg_score"] = round(sum(judge_stats["scores"]) / len(judge_stats["scores"]), 2)

        for model_name, model_stats in quality_stats["by_model"].items():
            for judge_name, judge_stats in model_stats.items():
                if judge_stats["scores"]:
                    judge_stats["avg_score"] = round(sum(judge_stats["scores"]) / len(judge_stats["scores"]), 2)

        for category_name, category_stats in quality_stats["by_category"].items():
            for model_name, model_stats in category_stats.items():
                for judge_name, judge_stats in model_stats.items():
                    if judge_stats["scores"]:
                        judge_stats["avg_score"] = round(sum(judge_stats["scores"]) / len(judge_stats["scores"]), 2)

        return quality_stats
