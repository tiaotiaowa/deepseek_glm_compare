"""Judge 管理器 - 协调多个 Judge 的评估"""

import os
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .judge_result import JudgeEvaluation, JudgeComparison
from .scoring_rubric import ScoringRubric

# 导入新创建的模块
from .judge_factory import JudgeFactory
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser
from .minimax_scorer import MiniMaxScoreCalculator


class JudgeManager:
    """管理多个 Judge 的质量评估"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Judge Manager

        Args:
            config: 质量评估配置
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self.judges_config = config.get("judges", {})
        self.evaluation_strategy = config.get("evaluation_strategy", {})

        # 初始化 Judge 客户端
        self.judges: Dict[str, Any] = {}
        if self.enabled:
            self._init_judges()

    def _init_judges(self):
        """初始化所有启用的 Judge（使用 JudgeFactory）"""
        self.judges = JudgeFactory.create_all(self.config)

        if not self.judges:
            print("[WARNING] No Judge clients were initialized. Quality evaluation will be disabled.")

    def evaluate_single_output(
        self,
        output: str,
        category: str,
        prompt: str,
        model_name: str,
        test_name: str
    ) -> Dict[str, JudgeEvaluation]:
        """
        使用所有 Judge 评估单个输出

        Args:
            output: 模型输出
            category: 测试类别
            prompt: 原始提示词
            model_name: 被评估的模型名称
            test_name: 测试名称

        Returns:
            Dict[str, JudgeEvaluation]: 各 Judge 的评估结果
        """
        if not self.enabled or not self.judges:
            return {}

        evaluations = {}
        mode = self.evaluation_strategy.get("mode", "parallel")

        if mode == "parallel":
            # 并行评估
            evaluations = self._evaluate_parallel(
                output, category, prompt, model_name, test_name
            )
        else:
            # 顺序评估
            evaluations = self._evaluate_sequential(
                output, category, prompt, model_name, test_name
            )

        return evaluations

    def _evaluate_parallel(
        self,
        output: str,
        category: str,
        prompt: str,
        model_name: str,
        test_name: str
    ) -> Dict[str, JudgeEvaluation]:
        """并行评估"""
        evaluations = {}

        with ThreadPoolExecutor(max_workers=len(self.judges)) as executor:
            # 提交所有评估任务
            future_to_judge = {}
            for judge_name, judge_info in self.judges.items():
                future = executor.submit(
                    self._evaluate_with_judge,
                    judge_name,
                    judge_info,
                    output,
                    category,
                    prompt,
                    model_name,
                    test_name
                )
                future_to_judge[future] = judge_name

            # 收集结果
            for future in as_completed(future_to_judge):
                judge_name = future_to_judge[future]
                try:
                    evaluation = future.result()
                    if evaluation:
                        evaluations[judge_name] = evaluation
                except Exception as e:
                    print(f"Judge {judge_name} evaluation failed: {e}")

        return evaluations

    def _evaluate_sequential(
        self,
        output: str,
        category: str,
        prompt: str,
        model_name: str,
        test_name: str
    ) -> Dict[str, JudgeEvaluation]:
        """顺序评估"""
        evaluations = {}

        for judge_name, judge_info in self.judges.items():
            evaluation = self._evaluate_with_judge(
                judge_name, judge_info, output, category, prompt, model_name, test_name
            )
            if evaluation:
                evaluations[judge_name] = evaluation

        return evaluations

    def _evaluate_with_judge(
        self,
        judge_name: str,
        judge_info: Dict[str, Any],
        output: str,
        category: str,
        prompt: str,
        model_name: str,
        test_name: str
    ) -> Optional[JudgeEvaluation]:
        """使用单个 Judge 进行评估"""
        start_time = time.perf_counter()

        try:
            client = judge_info["client"]
            config = judge_info["config"]
            judge_type = judge_info["type"]
            judge_model = judge_info["model"]

            # 获取评分标准
            rubric = ScoringRubric.get_rubric(category)

            # 构建评估提示词
            evaluation_prompt = self._build_evaluation_prompt(
                prompt=prompt,
                output=output,
                category=category,
                rubric=rubric,
                blind=config.get("blind_evaluation", True)
            )

            # 调用 Judge API（使用流式接口但等待完整响应）
            response_text = self._call_judge_api(
                client, evaluation_prompt, config
            )

            # 解析评估结果
            evaluation_result = self._parse_evaluation_response(
                response_text,
                rubric["criteria"],
                category
            )

            # 计算总体分数
            overall_score = ScoringRubric.calculate_overall_score(
                category, evaluation_result["scores"]
            )

            end_time = time.perf_counter()

            # 创建 JudgeEvaluation 对象
            return JudgeEvaluation(
                judge_name=judge_name,
                judge_model=judge_model,
                test_name=test_name,
                test_category=category,
                model_evaluated=model_name,
                scores=evaluation_result["scores"],
                overall_score=overall_score,
                strengths=evaluation_result.get("strengths", []),
                weaknesses=evaluation_result.get("weaknesses", []),
                reasoning=evaluation_result.get("reasoning", ""),
                evaluation_time_ms=(end_time - start_time) * 1000,
                blind_evaluation=config.get("blind_evaluation", True),
                success=True
            )

        except Exception as e:
            end_time = time.perf_counter()
            print(f"Judge {judge_name} evaluation error: {e}")

            return JudgeEvaluation(
                judge_name=judge_name,
                judge_model=judge_info.get("model", ""),
                test_name=test_name,
                test_category=category,
                model_evaluated=model_name,
                scores={},
                overall_score=0.0,
                evaluation_time_ms=(end_time - start_time) * 1000,
                success=False,
                error_message=str(e)
            )

    def _call_judge_api(
        self,
        client: Any,
        prompt: str,
        config: Dict[str, Any]
    ) -> str:
        """
        调用 Judge API

        使用非流式请求进行质量评估，因为：
        1. 质量评估不需要实时流式输出
        2. 非流式请求更简单、更可靠
        3. 避免流式响应可能带来的额外错误处理

        Args:
            client: API 客户端
            prompt: 评估提示词
            config: Judge 配置

        Returns:
            str: Judge 的响应文本
        """
        messages = [{"role": "user", "content": prompt}]

        # 使用非流式请求
        response_text = client.chat(
            messages=messages,
            max_tokens=config.get("max_tokens", 2048),
            temperature=config.get("temperature", 0.3)
        )

        return response_text

    def _build_evaluation_prompt(
        self,
        prompt: str,
        output: str,
        category: str,
        rubric: Dict[str, Any],
        blind: bool
    ) -> str:
        """构建评估提示词（使用 PromptBuilder）"""
        return PromptBuilder.build_standard_evaluation(
            output=output,
            category=category,
            prompt=prompt,
            rubric=rubric,
            blind=blind
        )

    def _parse_evaluation_response(
        self,
        response: str,
        criteria: List[str],
        category: str
    ) -> Dict[str, Any]:
        """解析评估响应（使用 ResponseParser）"""
        return ResponseParser.parse_standard(response, criteria, category)

    def compare_outputs(
        self,
        output_a: str,
        output_b: str,
        category: str,
        prompt: str,
        test_name: str
    ) -> Dict[str, JudgeComparison]:
        """
        使用所有 Judge 比较两个输出

        Args:
            output_a: 模型 A 的输出
            output_b: 模型 B 的输出
            category: 测试类别
            prompt: 原始提示词
            test_name: 测试名称

        Returns:
            Dict[str, JudgeComparison]: 每个模型的对比结果
        """
        # 为每个模型生成对比结果
        comparisons = {}

        # 评估模型 A
        evals_a = self.evaluate_single_output(
            output_a, category, prompt, "model_a", test_name
        )

        # 评估模型 B
        evals_b = self.evaluate_single_output(
            output_b, category, prompt, "model_b", test_name
        )

        # 为每个模型创建对比对象
        for model_name, evaluations in [("model_a", evals_a), ("model_b", evals_b)]:
            if evaluations:
                comparison = JudgeComparison(
                    test_name=test_name,
                    test_category=category,
                    model_evaluated=model_name,
                    evaluations=evaluations
                )
                comparison.calculate_agreement_metrics()
                comparisons[model_name] = comparison

        return comparisons

    def get_enabled_judges(self) -> List[str]:
        """获取已启用的 Judge 列表"""
        return list(self.judges.keys())

    def is_enabled(self) -> bool:
        """检查是否启用了质量评估"""
        return self.enabled and len(self.judges) > 0

    # ========== MiniMax 标准评估方法 ==========

    def evaluate_minimax_standard(
        self,
        output_a: str,
        output_b: str,
        category: str,
        prompt: str,
        test_name: str,
        dimension: str,
        sub_dimension: str,
        quality_criteria: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        使用 MiniMax 标准进行评估（0-10 分制）

        三模型交叉评价：MiniMax 40% + DeepSeek 30% + GLM 30%

        Args:
            output_a: 模型A的输出
            output_b: 模型B的输出
            category: 测试类别
            prompt: 原始提示词
            test_name: 测试名称
            dimension: 评测维度
            sub_dimension: 子维度
            quality_criteria: 质量标准权重

        Returns:
            Dict containing:
                - model_a_scores: 各Judge对模型A的评分
                - model_b_scores: 各Judge对模型B的评分
                - weighted_scores: 加权总分
                - statistics: 统计信息
        """
        if not self.enabled or not self.judges:
            return {
                "model_a_scores": {},
                "model_b_scores": {},
                "weighted_scores": {},
                "statistics": {},
                "error": "Quality evaluation not enabled"
            }

        # 构建标准化的评估提示词
        evaluation_prompt = self._build_minimax_evaluation_prompt(
            output_a=output_a,
            output_b=output_b,
            category=category,
            prompt=prompt,
            dimension=dimension,
            sub_dimension=sub_dimension,
            quality_criteria=quality_criteria
        )

        # 并行调用所有judge进行评估
        results = {}
        enabled_judges = self.get_enabled_judges()

        with ThreadPoolExecutor(max_workers=len(enabled_judges)) as executor:
            futures = {
                executor.submit(
                    self._evaluate_single_judge_minimax,
                    judge_name,
                    evaluation_prompt
                ): judge_name
                for judge_name in enabled_judges
            }

            for future in as_completed(futures):
                judge_name = futures[future]
                try:
                    result = future.result()
                    if result:
                        results[judge_name] = result
                except Exception as e:
                    print(f"  {judge_name} evaluation failed: {e}")
                    results[judge_name] = None

        # 组织结果
        model_a_scores = {}
        model_b_scores = {}

        for judge_name, result in results.items():
            if result:
                model_a_scores[judge_name] = result.get("model_a_score", {})
                model_b_scores[judge_name] = result.get("model_b_score", {})

        # 计算加权评分
        from .minimax_scorer import MiniMaxScoreCalculator
        scorer = MiniMaxScoreCalculator()

        weighted_scores = self._calculate_minimax_weighted_scores(
            model_a_scores,
            model_b_scores,
            scorer
        )

        # 计算统计信息
        statistics = self._calculate_minimax_statistics(
            model_a_scores,
            model_b_scores,
            scorer
        )

        return {
            "model_a_scores": model_a_scores,
            "model_b_scores": model_b_scores,
            "weighted_scores": weighted_scores,
            "statistics": statistics
        }

    def _build_minimax_evaluation_prompt(
        self,
        output_a: str,
        output_b: str,
        category: str,
        prompt: str,
        dimension: str,
        sub_dimension: str,
        quality_criteria: Dict[str, float]
    ) -> str:
        """构建MiniMax标准评估提示词（使用 PromptBuilder）"""
        return PromptBuilder.build_minimax_evaluation(
            output_a=output_a,
            output_b=output_b,
            category=category,
            prompt=prompt,
            dimension=dimension,
            sub_dimension=sub_dimension,
            quality_criteria=quality_criteria
        )


    def _evaluate_single_judge_minimax(
        self,
        judge_name: str,
        prompt: str
    ) -> Optional[Dict[str, Any]]:
        """单个Judge评估（MiniMax标准）"""
        start_time = time.perf_counter()

        try:
            judge_info = self.judges.get(judge_name)
            if not judge_info:
                return None

            client = judge_info["client"]
            config = judge_info["config"]

            # 使用现有的_call_judge_api（保持调用方式不变）
            response_text = self._call_judge_api(
                client,
                prompt,
                config
            )

            # 解析JSON响应
            result = self._parse_minimax_evaluation(response_text)

            end_time = time.perf_counter()
            if result:
                result["evaluation_time"] = end_time - start_time
                result["judge_name"] = judge_name

            return result

        except Exception as e:
            print(f"Judge {judge_name} MiniMax evaluation error: {e}")
            return None

    def _parse_minimax_evaluation(self, response_text: str) -> Optional[Dict[str, Any]]:
        """解析MiniMax标准评估响应（0-10分）（使用 ResponseParser）"""
        return ResponseParser.parse_minimax(response_text)

    def _calculate_minimax_weighted_scores(
        self,
        model_a_scores: Dict[str, Dict],
        model_b_scores: Dict[str, Dict],
        scorer: Any
    ) -> Dict[str, Any]:
        """计算MiniMax加权分数"""

        # 提取各Judge的overall_score
        minimax_scores = []
        deepseek_scores = []
        glm_scores = []

        for judge_name in model_a_scores.keys():
            if "minimax" in judge_name.lower():
                score_a = model_a_scores[judge_name].get("overall_score", 0)
                score_b = model_b_scores.get(judge_name, {}).get("overall_score", 0)
                minimax_scores.append(score_a)
                minimax_scores.append(score_b)
            elif "deepseek" in judge_name.lower():
                score_a = model_a_scores[judge_name].get("overall_score", 0)
                score_b = model_b_scores.get(judge_name, {}).get("overall_score", 0)
                deepseek_scores.append(score_a)
                deepseek_scores.append(score_b)
            elif "glm" in judge_name.lower():
                score_a = model_a_scores[judge_name].get("overall_score", 0)
                score_b = model_b_scores.get(judge_name, {}).get("overall_score", 0)
                glm_scores.append(score_a)
                glm_scores.append(score_b)

        # 计算平均分
        avg_minimax = sum(minimax_scores) / len(minimax_scores) if minimax_scores else 0
        avg_deepseek = sum(deepseek_scores) / len(deepseek_scores) if deepseek_scores else 0
        avg_glm = sum(glm_scores) / len(glm_scores) if glm_scores else 0

        # 计算加权总分
        weighted_a = scorer.calculate_weighted_score(
            minimax_score=model_a_scores.get("minimax_judge", {}).get("overall_score", avg_minimax),
            deepseek_score=model_a_scores.get("deepseek_judge", {}).get("overall_score", avg_deepseek),
            glm_score=model_a_scores.get("glm_judge", {}).get("overall_score", avg_glm)
        )

        weighted_b = scorer.calculate_weighted_score(
            minimax_score=model_b_scores.get("minimax_judge", {}).get("overall_score", avg_minimax),
            deepseek_score=model_b_scores.get("deepseek_judge", {}).get("overall_score", avg_deepseek),
            glm_score=model_b_scores.get("glm_judge", {}).get("overall_score", avg_glm)
        )

        return {
            "model_a_weighted": weighted_a["weighted_score"],
            "model_b_weighted": weighted_b["weighted_score"],
            "model_a_breakdown": weighted_a,
            "model_b_breakdown": weighted_b
        }

    def _calculate_minimax_statistics(
        self,
        model_a_scores: Dict[str, Dict],
        model_b_scores: Dict[str, Dict],
        scorer: Any
    ) -> Dict[str, Any]:
        """计算MiniMax评估统计信息"""

        # 提取所有overall_score
        a_scores = [s.get("overall_score", 0) for s in model_a_scores.values()]
        b_scores = [s.get("overall_score", 0) for s in model_b_scores.values()]

        stats = {
            "model_a": scorer.calculate_statistics(a_scores),
            "model_b": scorer.calculate_statistics(b_scores)
        }

        # 计算Pearson相关系数
        if len(a_scores) == len(b_scores) and len(a_scores) > 1:
            correlation = scorer.calculate_pearson_correlation(a_scores, b_scores)
            stats["correlation"] = correlation
        else:
            stats["correlation"] = None

        # 评价者间信度
        all_ratings = {}
        for judge_name, scores in model_a_scores.items():
            all_ratings[judge_name] = [scores.get("overall_score", 0)]

        reliability = scorer.calculate_inter_rater_reliability(all_ratings)
        stats["inter_rater_reliability"] = reliability

        return stats

