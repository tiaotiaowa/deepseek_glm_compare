"""Markdown 报告生成器"""

from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import numpy as np

# 导入共享的格式化器
from .formatters import (
    ScoreFormatter,
    GradeFormatter,
    TableFormatter,
    ProgressFormatter,
    DimensionTranslator
)


class ReportGenerator:
    """Markdown 报告生成器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化报告生成器

        Args:
            config: 报告配置
        """
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 确保输出目录存在
        self.output_dir = Path("results/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ========== Markdown 格式辅助方法 ==========
    # 注意：以下方法已迁移到 formatters.py，这里保留为兼容性包装器

    def _format_winning_score(self, value: float, values: List[float],
                              is_lower_better: bool = False, add_trophy: bool = True) -> str:
        """为获胜分数添加格式化（使用 ScoreFormatter）"""
        return ScoreFormatter.format_winning_score(value, values, is_lower_better, add_trophy)

    def _format_winning_model(self, model: str, is_winner: bool) -> str:
        """使用格式化突出获胜模型（使用 ScoreFormatter）"""
        return ScoreFormatter.format_winning_model(model, is_winner)

    def _get_grade_emoji(self, score: float) -> str:
        """
        根据分数返回等级 emoji 和文字说明（使用 GradeFormatter）

        Args:
            score: 分数 (0-10 或 0-5)

        Returns:
            等级字符串，如 "🟢 优秀" 或 "🔴 不合格"
        """
        # 判断是 10 分制还是 5 分制
        is_10_scale = score > 5.0
        return GradeFormatter.format_grade_with_emoji(score, is_10_scale)

    def generate_report(
        self,
        statistics: Dict[str, Any],
        summaries: List[Any],
        raw_results: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str],
        quality_stats: Dict[str, Any] = None,
        minimax_stats: Dict[str, Any] = None
    ):
        """
        生成 Markdown 报告

        Args:
            statistics: 统计信息
            summaries: 类别汇总数据
            raw_results: 原始结果数据
            model_names: 模型名称列表
            test_categories: 测试类别列表
            quality_stats: 质量评估统计数据
            minimax_stats: MiniMax 评测统计数据
        """
        # 转换汇总数据为字典
        summaries_dict = [s.to_dict() for s in summaries]

        # 生成完整报告
        md_content = self._build_complete_report(
            statistics=statistics,
            summaries=summaries_dict,
            raw_results=raw_results,
            model_names=model_names,
            test_categories=test_categories,
            quality_stats=quality_stats,
            minimax_stats=minimax_stats
        )

        # 保存文件
        output_path = self.output_dir / f"benchmark_report_{self.timestamp}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\n[OK] Markdown report generated: {output_path}")

        # 同时保存原始数据（供参考）
        self._save_raw_data(statistics, summaries_dict, raw_results, quality_stats, minimax_stats)

        return output_path

    def _save_raw_data(
        self,
        statistics: Dict[str, Any],
        summaries: List[Dict[str, Any]],
        raw_results: List[Dict[str, Any]],
        quality_stats: Dict[str, Any] = None,
        minimax_stats: Dict[str, Any] = None
    ):
        """保存原始数据（用于后续分析）"""
        import json

        data_dir = Path("results/data")
        data_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "timestamp": self.timestamp,
            "statistics": statistics,
            "summaries": summaries,
            "raw_results": raw_results,
            "quality_stats": quality_stats,
            "minimax_stats": minimax_stats
        }

        output_path = data_dir / f"raw_data_{self.timestamp}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _build_complete_report(
        self,
        statistics: Dict[str, Any],
        summaries: List[Dict[str, Any]],
        raw_results: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str],
        quality_stats: Dict[str, Any] = None,
        minimax_stats: Dict[str, Any] = None
    ) -> str:
        """构建完整的 Markdown 报告"""

        md = ""

        # ========== 报告标题 ==========
        md += self._generate_header()

        # ========== 执行摘要 ==========
        md += self._generate_executive_summary(
            summaries, model_names, quality_stats, minimax_stats
        )

        # ========== 快速对比表 ==========
        md += self._generate_quick_comparison(
            summaries, model_names, test_categories, quality_stats, minimax_stats
        )

        # ========== 一、测试设计 ==========
        md += self._generate_test_design(model_names, test_categories)

        # ========== 二、测试过程 ==========
        md += self._generate_test_process(statistics, test_categories)

        # ========== 三、测试结果 ==========
        md += self._generate_test_results(
            statistics, summaries, raw_results, model_names, test_categories
        )

        # ========== 四、MiniMax 第三方评测（如果有）==========
        if minimax_stats:
            md += self._generate_minimax_judge_section(minimax_stats, model_names)

        # ========== 五、质量评估（如果有）==========
        if quality_stats:
            md += self._generate_quality_assessment(
                quality_stats, model_names, test_categories, raw_results,
                has_minimax=(minimax_stats is not None)
            )

        # ========== 六、意见建议 ==========
        md += self._generate_recommendations(
            statistics, summaries, model_names, quality_stats, minimax_stats
        )

        # ========== 报告尾部 ==========
        md += self._generate_footer()

        return md

    def _generate_header(self) -> str:
        """生成报告标题"""
        return f"""# DeepSeek-v3.2 vs GLM-4.7 API 性能对比测试报告

**报告生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

**测试目的**: 对比 DeepSeek-v3.2 和 GLM-4.7 两个模型在 Anthropic 协议下的 API 响应性能

---

"""

    def _generate_executive_summary(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        quality_stats: Dict[str, Any] = None,
        minimax_stats: Dict[str, Any] = None
    ) -> str:
        """生成执行摘要 - 关键指标一览表"""
        md = "## 执行摘要\n\n"
        md += "### 关键指标一览\n\n"

        # 计算总体性能统计
        overall_data = {}
        for model in model_names:
            model_summaries = [s for s in summaries if s['model_name'] == model and s['test_count'] > 0]
            if model_summaries:
                overall_data[model] = {
                    'ttft': sum(s['ttft_mean'] for s in model_summaries) / len(model_summaries),
                    'speed': sum(s['speed_mean'] for s in model_summaries) / len(model_summaries)
                }

        # 获取质量评分（如果有）
        quality_scores = {}
        if quality_stats and 'by_model' in quality_stats:
            for model in model_names:
                if model in quality_stats['by_model']:
                    model_quality = quality_stats['by_model'][model]
                    # 计算平均质量分数（所有 judge 的平均值）
                    scores = []
                    for judge_data in model_quality.values():
                        if isinstance(judge_data, dict) and 'avg_score' in judge_data:
                            scores.append(judge_data['avg_score'])
                    if scores:
                        quality_scores[model] = sum(scores) / len(scores)

        # 获取 MiniMax 评分（如果有）
        minimax_scores = {}
        if minimax_stats and 'by_model' in minimax_stats:
            for model in model_names:
                if model in minimax_stats['by_model'] and 'minimax_judge' in minimax_stats['by_model'][model]:
                    minimax_scores[model] = minimax_stats['by_model'][model]['minimax_judge']['overall_score']

        # 构建关键指标表
        md += "| 指标类别 | " + " | ".join(model_names) + " |\n"
        md += "|----------|" + "|".join(["----------"] * len(model_names)) + "|\n"

        # TTFT 行
        if overall_data:
            ttfts = [overall_data[m]['ttft'] for m in model_names if m in overall_data]
            ttft_row = ["**TTFT**（首次响应）"]
            for model in model_names:
                if model in overall_data:
                    ttft_row.append(self._format_winning_score(overall_data[model]['ttft'], ttfts, is_lower_better=True) + " ms")
                else:
                    ttft_row.append("N/A")
            md += "| " + " | ".join(ttft_row) + " |\n"

        # 生成速度行
        if overall_data:
            speeds = [overall_data[m]['speed'] for m in model_names if m in overall_data]
            speed_row = ["**生成速度**"]
            for model in model_names:
                if model in overall_data:
                    speed_row.append(self._format_winning_score(overall_data[model]['speed'], speeds, is_lower_better=False) + " t/s")
                else:
                    speed_row.append("N/A")
            md += "| " + " | ".join(speed_row) + " |\n"

        # MiniMax 总分行
        if minimax_scores:
            mm_scores = [minimax_scores[m] for m in model_names if m in minimax_scores]
            mm_row = ["**MiniMax 总分**"]
            for model in model_names:
                if model in minimax_scores:
                    mm_row.append(self._format_winning_score(minimax_scores[model], mm_scores, is_lower_better=False))
                else:
                    mm_row.append("N/A")
            md += "| " + " | ".join(mm_row) + " |\n"

        # 质量评分行
        if quality_scores:
            q_scores = [quality_scores[m] for m in model_names if m in quality_scores]
            q_row = ["**质量评分**"]
            for model in model_names:
                if model in quality_scores:
                    q_row.append(self._format_winning_score(quality_scores[model], q_scores, is_lower_better=False))
                else:
                    q_row.append("N/A")
            md += "| " + " | ".join(q_row) + " |\n"

        md += "\n*注：🏆 表示该指标最佳模型，粗体表示获胜。TTFT 越小越好，其他指标越大越好*\n\n"

        # 核心发现
        md += "### 核心发现\n\n"

        # 计算性能领先百分比
        if len(overall_data) >= 2:
            model1, model2 = model_names[0], model_names[1]
            if model1 in overall_data and model2 in overall_data:
                # TTFT 领先百分比
                ttft_pct = (overall_data[model2]['ttft'] - overall_data[model1]['ttft']) / overall_data[model2]['ttft'] * 100
                ttft_leader = model1 if ttft_pct > 0 else model2
                ttft_pct = abs(ttft_pct)

                # 速度领先百分比
                speed_pct = (overall_data[model1]['speed'] - overall_data[model2]['speed']) / overall_data[model2]['speed'] * 100
                speed_leader = model1 if speed_pct > 0 else model2
                speed_pct = abs(speed_pct)

                md += f"- 🚀 **性能领先**：{ttft_leader} 的首次响应时间快 {ttft_pct:.1f}%，生成速度快 {speed_pct:.1f}%\n"

        # 质量比较
        if quality_scores and len(quality_scores) >= 2:
            model1, model2 = model_names[0], model_names[1]
            if model1 in quality_scores and model2 in quality_scores:
                q_diff = quality_scores[model1] - quality_scores[model2]
                if abs(q_diff) > 0.1:
                    q_leader = model1 if q_diff > 0 else model2
                    q_pct = abs(q_diff) / min(quality_scores.values()) * 100
                    md += f"- 🎯 **质量优势**：{q_leader} 的质量评分高 {q_pct:.1f}%\n"

        # MiniMax 质量比较
        if minimax_scores and len(minimax_scores) >= 2:
            model1, model2 = model_names[0], model_names[1]
            if model1 in minimax_scores and model2 in minimax_scores:
                mm_diff = minimax_scores[model1] - minimax_scores[model2]
                if abs(mm_diff) > 0.1:
                    mm_leader = model1 if mm_diff > 0 else model2
                    md += f"- 🏆 **MiniMax 评测**：{mm_leader} 在第三方评测中表现更优\n"

        md += "\n---\n\n"
        return md

    def _generate_quick_comparison(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str],
        quality_stats: Dict[str, Any] = None,
        minimax_stats: Dict[str, Any] = None
    ) -> str:
        """生成快速对比表 - 按场景推荐"""
        md = "### 快速对比表\n\n"
        md += "| 场景 | 推荐模型 | 理由 | 置信度 |\n"
        md += "|------|----------|------|--------|\n"

        # 收集各场景的数据
        category_data = {}
        for category in test_categories:
            for model in model_names:
                model_data = [s for s in summaries if s['category'] == category and s['model_name'] == model]
                if model_data and model_data[0]['test_count'] > 0:
                    if category not in category_data:
                        category_data[category] = {}
                    category_data[category][model] = model_data[0]

        # 为每个场景生成推荐
        for category in test_categories:
            if category not in category_data or len(category_data[category]) < 2:
                continue

            models_in_category = list(category_data[category].keys())
            model1, model2 = models_in_category[0], models_in_category[1]
            data1, data2 = category_data[category][model1], category_data[category][model2]

            # 计算综合得分（TTFT 和速度的加权）
            # 归一化 TTFT（越小越好）
            ttft_sum = data1['ttft_mean'] + data2['ttft_mean']
            ttft_score1 = (ttft_sum - data1['ttft_mean']) / ttft_sum  # TTFT 越小分数越高
            ttft_score2 = (ttft_sum - data2['ttft_mean']) / ttft_sum

            # 归一化速度（越大越好）
            speed_sum = data1['speed_mean'] + data2['speed_mean']
            speed_score1 = data1['speed_mean'] / speed_sum
            speed_score2 = data2['speed_mean'] / speed_sum

            # 综合得分（TTFT 40%，速度 60%）
            score1 = ttft_score1 * 0.4 + speed_score1 * 0.6
            score2 = ttft_score2 * 0.4 + speed_score2 * 0.6

            winner = model1 if score1 > score2 else model2
            margin = abs(score1 - score2) * 100

            # 确定理由
            if data1['ttft_mean'] < data2['ttft_mean'] and data1['speed_mean'] > data2['speed_mean']:
                reason = f"TTFT 快 {abs(data1['ttft_mean'] - data2['ttft_mean']) / data2['ttft_mean'] * 100:.1f}%，速度快 {abs(data1['speed_mean'] - data2['speed_mean']) / data2['speed_mean'] * 100:.1f}%"
            elif data1['ttft_mean'] < data2['ttft_mean']:
                reason = f"TTFT 快 {abs(data1['ttft_mean'] - data2['ttft_mean']) / data2['ttft_mean'] * 100:.1f}%"
            elif data1['speed_mean'] > data2['speed_mean']:
                reason = f"速度快 {abs(data1['speed_mean'] - data2['speed_mean']) / data2['speed_mean'] * 100:.1f}%"
            else:
                reason = "综合性能更优"

            # 确定置信度
            if margin > 15:
                confidence = "*** 高度显著"
            elif margin > 8:
                confidence = "** 显著"
            elif margin > 3:
                confidence = "* 边缘显著"
            else:
                confidence = "相当"

            md += f"| {category} | **{winner}** | {reason} | {confidence} |\n"

        md += "\n*注：*** 高度显著（差异 >15%），** 显著（差异 >8%），* 边缘显著（差异 >3%）*\n\n"
        md += "---\n\n"
        return md

    def _generate_minimax_judge_section(self, minimax_stats: Dict[str, Any],
                                       model_names: List[str]) -> str:
        """
        生成 MiniMax 第三方评测章节

        Args:
            minimax_stats: 来自 JSON 的 MiniMax 评测统计数据
            model_names: 被评估的模型列表

        Returns:
            包含 MiniMax 结果的 Markdown 章节
        """
        # 检查是否有 MiniMax 数据
        if not minimax_stats or "by_judge" not in minimax_stats or "minimax_judge" not in minimax_stats.get("by_judge", {}):
            return ""

        md = "## 四、MiniMax 第三方评测\n\n"

        # 4.1 MiniMax 综合评分
        md += "### 4.1 MiniMax 综合评分 (0-10分制)\n\n"
        md += self._generate_minimax_overall_table(minimax_stats, model_names)

        # 4.2 四维度详细评分
        md += "### 4.2 四维度详细评分\n\n"
        md += self._generate_minimax_dimensions_table(minimax_stats, model_names)

        # 4.3 子维度能力矩阵
        md += "### 4.3 子维度能力矩阵\n\n"
        md += self._generate_minimax_subdimension_heatmap(minimax_stats, model_names)

        md += "\n---\n\n"
        return md

    def _generate_minimax_overall_table(self, minimax_stats: Dict, models: List[str]) -> str:
        """生成 MiniMax 综合评分表"""
        md = "| 模型 | 综合得分 | 等级 | 基础性能 | 核心能力 | 实用场景 | 高级特性 |\n"
        md += "|------|---------|------|----------|----------|----------|----------|\n"

        for model in models:
            if model not in minimax_stats.get("by_model", {}):
                continue
            if "minimax_judge" not in minimax_stats["by_model"][model]:
                continue

            model_data = minimax_stats["by_model"][model]["minimax_judge"]
            overall = model_data.get("overall_score", 0)
            dims = model_data.get("dimension_scores", {})

            # 获取等级 emoji
            grade = self._get_grade_emoji(overall)

            # 格式化获胜分数（使用粗体）
            all_overall_scores = []
            for m in models:
                if m in minimax_stats.get("by_model", {}) and "minimax_judge" in minimax_stats["by_model"][m]:
                    all_overall_scores.append(minimax_stats["by_model"][m]["minimax_judge"].get("overall_score", 0))

            overall_formatted = self._format_winning_score(overall, all_overall_scores, is_lower_better=False)

            # 格式化模型名称
            is_winner = all_overall_scores and overall == max(all_overall_scores)
            model_formatted = self._format_winning_model(model, is_winner)

            md += f"| {model_formatted} | {overall_formatted} | {grade} "

            # 四维度分数
            for dim in ["basic_performance", "core_capabilities",
                       "practical_scenarios", "advanced_features"]:
                score = dims.get(dim, 0)
                all_scores = []
                for m in models:
                    if m in minimax_stats.get("by_model", {}) and "minimax_judge" in minimax_stats["by_model"][m]:
                        all_scores.append(minimax_stats["by_model"][m]["minimax_judge"].get("dimension_scores", {}).get(dim, 0))
                md += f"| {self._format_winning_score(score, all_scores)} "

            md += "|\n"

        md += "\n*注：🏆 表示该指标最佳模型，粗体表示获胜*\n"
        return md

    def _generate_minimax_dimensions_table(self, minimax_stats: Dict, models: List[str]) -> str:
        """生成 MiniMax 四维度详细评分表"""
        md = "#### 各维度得分对比\n\n"

        dimensions_cn = {
            "basic_performance": "基础性能",
            "core_capabilities": "核心能力",
            "practical_scenarios": "实用场景",
            "advanced_features": "高级特性"
        }

        for dim_key, dim_name in dimensions_cn.items():
            md += f"**{dim_name}**\n\n"

            # 收集该维度的数据
            dim_data = {}
            for model in models:
                if model in minimax_stats.get("by_model", {}) and "minimax_judge" in minimax_stats["by_model"][model]:
                    dim_data[model] = minimax_stats["by_model"][model]["minimax_judge"].get("dimension_scores", {}).get(dim_key, 0)

            if not dim_data:
                continue

            # 找出最佳模型
            best_model = max(dim_data.items(), key=lambda x: x[1])

            md += f"- 最佳模型：**{best_model[0]}** ({best_model[1]:.2f}/10)\n"

            # 详细对比
            for model, score in dim_data.items():
                is_best = score == best_model[1]
                marker = " 🏆" if is_best else ""
                formatted_score = f"**{score:.2f}**{marker}" if is_best else f"{score:.2f}"
                md += f"  - {model}: {formatted_score}\n"

            md += "\n"

        return md

    def _generate_minimax_subdimension_heatmap(self, minimax_stats: Dict, models: List[str]) -> str:
        """生成 MiniMax 子维度能力热力图"""
        md = "#### 子维度能力热力图\n\n"

        # 定义子维度列表
        sub_dimensions = [
            ("实时响应", "real_time"),
            ("吞吐量", "throughput"),
            ("稳定性", "stability"),
            ("逻辑推理", "reasoning"),
            ("代码生成", "code"),
            ("文本理解", "understanding"),
            ("创意生成", "creativity"),
            ("专业应用", "professional"),
            ("中文处理", "chinese"),
            ("长文本", "long_text"),
            ("结构化输出", "structured"),
            ("创新思维", "innovation")
        ]

        md += "| 能力维度 | " + " | ".join(models) + " |\n"
        md += "|----------|" + "|".join(["---------"] * len(models)) + "|\n"

        for dim_name, _ in sub_dimensions:
            row = [dim_name]

            for model in models:
                if model in minimax_stats.get("by_model", {}) and "minimax_judge" in minimax_stats["by_model"][model]:
                    sub_scores = minimax_stats["by_model"][model]["minimax_judge"].get("sub_dimension_scores", {})
                    score = sub_scores.get(dim_name, 0)

                    # 创建进度条（10个字符）
                    bar_length = int(score / 10 * 10)
                    filled = "█" * bar_length
                    empty = "░" * (10 - bar_length)
                    row.append(f"{filled}{empty} {score:.1f}")
                else:
                    row.append("N/A")

            md += "| " + " | ".join(row) + " |\n"

        md += "\n**图例**: ██████████ (9-10分) ██████░░ (7-8分) ████░░░░ (5-6分) ██░░░░░░ (3-4分)\n"
        return md

    def _generate_test_design(self, model_names: List[str], test_categories: List[str]) -> str:
        """生成测试设计部分"""
        md = "## 一、测试设计\n\n"

        # 1.1 测试对象
        md += "### 1.1 测试对象\n\n"
        md += "本次测试对比以下两个模型：\n\n"
        for i, model in enumerate(model_names, 1):
            md += f"**{i}. {model}**\n\n"
        md += "\n"

        # 1.2 测试指标
        md += "### 1.2 测试指标\n\n"
        md += "本次测试主要关注以下性能指标：\n\n"
        md += "| 指标 | 说明 | 单位 |\n"
        md += "|------|------|------|\n"
        md += "| TTFT | Time to First Token，从发送请求到收到第一个 token 的时间 | 毫秒 (ms) |\n"
        md += "| 总响应时间 | 完整请求从发送到接收完成的总时间 | 毫秒 (ms) |\n"
        md += "| 生成速度 | 模型生成 token 的速度 | tokens/秒 |\n"
        md += "| Token 间延迟 | 连续 token 之间的平均时间 | 毫秒 (ms) |\n"
        md += "| 输出 Token 数 | 模型生成的 token 数量 | 个 |\n\n"

        # 1.3 测试场景
        md += "### 1.3 测试场景\n\n"
        md += "测试涵盖以下场景类别：\n\n"

        category_descriptions = {
            "qa_simple": "简单问答 - 事实性问题、定义查询、简单解释",
            "code_generation": "代码生成 - 算法实现、API 设计、调试场景",
            "reasoning_complex": "复杂推理 - 多步逻辑、数学证明、分析推理",
            "generation_long": "长文本生成 - 论文写作、故事生成、文章创作",
            "summarization": "文本摘要 - 长文档摘要、要点提取",
            "translation": "翻译任务 - 多语言对、上下文感知翻译",
            "math_reasoning": "数学推理 - 应用题、符号数学、统计学",
            "creative_writing": "创意写作 - 诗歌、小说、对话创作",
            "factual_accuracy": "事实准确性 - 事实验证、幻觉检测",
            "multi_turn": "多轮对话 - 上下文保持、对话一致性"
        }

        for category in test_categories:
            desc = category_descriptions.get(category, "其他测试场景")
            md += f"- **{category}**: {desc}\n"
        md += "\n"

        # 1.4 测试方法
        md += "### 1.4 测试方法\n\n"
        md += "**测试流程**：\n\n"
        md += "1. **预热阶段**: 每个模型先进行 2 次预热请求，确保连接建立\n"
        md += "2. **正式测试**: 每个测试用例运行 3 次，取平均值\n"
        md += "3. **流式响应**: 使用 Anthropic 协议的流式响应接口\n"
        md += "4. **高精度计时**: 使用 `time.perf_counter()` 进行纳秒级精度计时\n\n"

        md += "**性能指标计算方式**：\n\n"
        md += "```\n"
        md += "TTFT = 首个 token 到达时间 - 请求开始时间\n"
        md += "总响应时间 = 请求结束时间 - 请求开始时间\n"
        md += "生成时间 = 总响应时间 - TTFT\n"
        md += "生成速度 = token 数量 / 生成时间\n"
        md += "Token 间延迟 = 平均相邻 token 时间间隔\n"
        md += "```\n\n"

        md += "---\n\n"
        return md

    def _generate_test_process(
        self,
        statistics: Dict[str, Any],
        test_categories: List[str]
    ) -> str:
        """生成测试过程部分"""
        md = "## 二、测试过程\n\n"

        # 2.1 测试环境
        md += "### 2.1 测试环境\n\n"
        md += f"- **测试时间**: {statistics.get('start_time', 'N/A')} ~ {statistics.get('end_time', 'N/A')}\n"
        md += f"- **测试工具**: Python + Anthropic SDK\n"
        md += f"- **网络环境**: 标准互联网连接\n\n"

        # 2.2 测试执行
        md += "### 2.2 测试执行\n\n"
        total_tests = statistics.get('total_tests', 0)
        successful_tests = statistics.get('successful_tests', 0)
        failed_tests = statistics.get('failed_tests', 0)
        success_rate = statistics.get('success_rate', 0) * 100

        md += f"- **计划测试数**: {total_tests} 次\n"
        md += f"- **成功执行**: {successful_tests} 次\n"
        md += f"- **执行失败**: {failed_tests} 次\n"
        md += f"- **成功率**: {success_rate:.1f}%\n\n"

        # 按模型统计
        md += "**各模型执行情况**：\n\n"
        model_stats = statistics.get('model_stats', {})
        for model_name, stats in model_stats.items():
            md += f"- **{model_name}**:\n"
            md += f"  - 总计: {stats.get('total', 0)} 次\n"
            md += f"  - 成功: {stats.get('success', 0)} 次\n"
            md += f"  - 失败: {stats.get('failed', 0)} 次\n\n"

        md += "---\n\n"
        return md

    def _generate_test_results(
        self,
        statistics: Dict[str, Any],
        summaries: List[Dict[str, Any]],
        raw_results: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成测试结果部分"""
        md = "## 三、测试结果\n\n"

        # 3.1 总体性能对比
        md += "### 3.1 总体性能对比\n\n"
        md += self._generate_overall_comparison(summaries, model_names)

        # 3.2 各指标详细对比
        md += "### 3.2 各指标详细对比\n\n"

        # TTFT 对比
        md += "#### 3.2.1 TTFT (首次响应时间) 对比\n\n"
        md += self._generate_ttft_comparison(summaries, model_names, test_categories)

        # 生成速度对比
        md += "#### 3.2.2 生成速度对比\n\n"
        md += self._generate_speed_comparison(summaries, model_names, test_categories)

        # 总响应时间对比
        md += "#### 3.2.3 总响应时间对比\n\n"
        md += self._generate_total_time_comparison(summaries, model_names, test_categories)

        # 3.3 分场景性能分析
        md += "### 3.3 分场景性能分析\n\n"
        md += self._generate_category_analysis(summaries, model_names, test_categories)

        # 3.4 模型优势分析
        md += "### 3.4 模型优势分析\n\n"
        md += self._generate_model_advantages(summaries, model_names, test_categories)

        md += "---\n\n"
        return md

    def _generate_overall_comparison(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str]
    ) -> str:
        """生成总体对比表"""
        md = "**总体平均性能**：\n\n"

        # 计算总体平均值
        overall_data = {}
        for model in model_names:
            model_summaries = [s for s in summaries if s['model_name'] == model and s['test_count'] > 0]
            if model_summaries:
                avg_ttft = sum(s['ttft_mean'] for s in model_summaries) / len(model_summaries)
                avg_speed = sum(s['speed_mean'] for s in model_summaries) / len(model_summaries)
                avg_total_time = sum(s['total_time_mean'] for s in model_summaries) / len(model_summaries)

                overall_data[model] = {
                    'ttft': avg_ttft,
                    'speed': avg_speed,
                    'total_time': avg_total_time
                }

        # 收集所有值用于比较
        all_ttft = [overall_data[m]['ttft'] for m in model_names if m in overall_data]
        all_speeds = [overall_data[m]['speed'] for m in model_names if m in overall_data]
        all_times = [overall_data[m]['total_time'] for m in model_names if m in overall_data]

        # 创建表格
        md += "| 模型 | 平均 TTFT (ms) | 平均生成速度 (tokens/s) | 平均总时间 (ms) |\n"
        md += "|------|----------------|------------------------|---------------|\n"

        for model in model_names:
            if model in overall_data:
                data = overall_data[model]
                # 使用格式化方法突出获胜分数
                ttft_str = self._format_winning_score(data['ttft'], all_ttft, is_lower_better=True)
                speed_str = self._format_winning_score(data['speed'], all_speeds, is_lower_better=False)
                time_str = self._format_winning_score(data['total_time'], all_times, is_lower_better=True)
                md += f"| {model} | {ttft_str} | {speed_str} | {time_str} |\n"

        md += "\n"
        md += "*注：粗体表示该指标最佳模型。TTFT 和总时间越小越好，生成速度越大越好*\n\n"
        return md

    def _generate_ttft_comparison(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成 TTFT 对比表（使用 Markdown 粗体突出优势值）"""
        md = "| 测试类别 | " + " | ".join(model_names) + " |\n"
        md += "|---------|" + "|".join(["---------"] * len(model_names)) + "|\n"

        for category in test_categories:
            row = [category]

            # 获取各模型的 TTFT
            model_ttfts = {}
            for model in model_names:
                model_data = [s for s in summaries if s['category'] == category and s['model_name'] == model]
                if model_data and model_data[0]['test_count'] > 0:
                    ttft = model_data[0]['ttft_mean']
                    model_ttfts[model] = ttft

            # 格式化 TTFT 值，突出最佳值（🏆 会自动添加到获胜值）
            for model in model_names:
                if model in model_ttfts:
                    ttft_values = list(model_ttfts.values())
                    formatted_ttft = self._format_winning_score(model_ttfts[model], ttft_values, is_lower_better=True)
                    row.append(formatted_ttft)
                else:
                    row.append("N/A")

            md += "| " + " | ".join(row) + " |\n"

        md += "\n"
        md += "*注：TTFT 越小越好，表示响应越快。🏆 表示该指标最佳模型，粗体表示获胜*\n\n"
        return md

    def _generate_speed_comparison(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成生成速度对比表（使用 Markdown 粗体突出优势值）"""
        md = "| 测试类别 | " + " | ".join(model_names) + " |\n"
        md += "|---------|" + "|".join(["---------"] * len(model_names)) + "|\n"

        for category in test_categories:
            row = [category]

            # 获取各模型的生成速度
            model_speeds = {}
            for model in model_names:
                model_data = [s for s in summaries if s['category'] == category and s['model_name'] == model]
                if model_data and model_data[0]['test_count'] > 0:
                    speed = model_data[0]['speed_mean']
                    model_speeds[model] = speed

            # 格式化速度值，突出最佳值（🏆 会自动添加到获胜值）
            for model in model_names:
                if model in model_speeds:
                    speed_values = list(model_speeds.values())
                    formatted_speed = self._format_winning_score(model_speeds[model], speed_values, is_lower_better=False)
                    row.append(formatted_speed)
                else:
                    row.append("N/A")

            md += "| " + " | ".join(row) + " |\n"

        md += "\n"
        md += "*注：生成速度越大越好，表示生成越快。🏆 表示该指标最佳模型，粗体表示获胜*\n\n"
        return md

    def _generate_total_time_comparison(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成总响应时间对比表"""
        md = "| 测试类别 | " + " | ".join(model_names) + " |\n"
        md += "|---------|" + "|".join(["---------"] * len(model_names)) + "|\n"

        for category in test_categories:
            row = [category]

            # 获取各模型的总响应时间
            model_times = {}
            for model in model_names:
                model_data = [s for s in summaries if s['category'] == category and s['model_name'] == model]
                if model_data and model_data[0]['test_count'] > 0:
                    total_time = model_data[0]['total_time_mean']
                    model_times[model] = total_time
                else:
                    model_times[model] = None

            # 使用格式化方法突出获胜分数（总时间越短越好，🏆 会自动添加到获胜值）
            times = [t for t in model_times.values() if t is not None]
            for model in model_names:
                if model_times[model] is not None:
                    row.append(self._format_winning_score(model_times[model], times, is_lower_better=True))
                else:
                    row.append("N/A")

            md += "| " + " | ".join(row) + " |\n"

        md += "\n"
        md += "*注：总响应时间越短越好，表示响应越快。🏆 表示该指标最佳模型，粗体表示获胜*\n\n"
        return md

    def _generate_category_analysis(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成分场景分析"""
        md = ""

        for category in test_categories:
            md += f"#### {category}\n\n"

            # 获取该类别的数据
            category_data = {}
            for model in model_names:
                model_summaries = [s for s in summaries if s['category'] == category and s['model_name'] == model]
                if model_summaries and model_summaries[0]['test_count'] > 0:
                    category_data[model] = model_summaries[0]

            if len(category_data) < 2:
                md += "*数据不足，无法对比*\n\n"
                continue

            # 对比分析
            model1, model2 = model_names[0], model_names[1]

            if model1 in category_data and model2 in category_data:
                data1 = category_data[model1]
                data2 = category_data[model2]

                # TTFT 对比
                ttft_diff = data2['ttft_mean'] - data1['ttft_mean']
                ttft_better = model1 if ttft_diff > 0 else model2
                ttft_pct = abs(ttft_diff) / data2['ttft_mean'] * 100 if data2['ttft_mean'] > 0 else 0

                md += f"- **TTFT**: {ttft_better} 领先 {ttft_pct:.1f}% "
                md += f"({data1['ttft_mean']:.2f}ms vs {data2['ttft_mean']:.2f}ms)\n"

                # 生成速度对比
                speed_diff = data1['speed_mean'] - data2['speed_mean']
                speed_better = model1 if speed_diff > 0 else model2
                speed_pct = abs(speed_diff) / data2['speed_mean'] * 100 if data2['speed_mean'] > 0 else 0

                md += f"- **生成速度**: {speed_better} 领先 {speed_pct:.1f}% "
                md += f"({data1['speed_mean']:.2f} vs {data2['speed_mean']:.2f} tokens/s)\n"

                # 总时间对比
                time_diff = data2['total_time_mean'] - data1['total_time_mean']
                time_better = model1 if time_diff > 0 else model2
                time_pct = abs(time_diff) / data2['total_time_mean'] * 100 if data2['total_time_mean'] > 0 else 0

                md += f"- **总响应时间**: {time_better} 领先 {time_pct:.1f}% "
                md += f"({data1['total_time_mean']:.2f}ms vs {data2['total_time_mean']:.2f}ms)\n\n"

        return md

    def _generate_model_advantages(
        self,
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成模型优势分析"""
        md = ""

        # 统计各模型在各类别的优势次数
        advantages = {model: {'ttft': 0, 'speed': 0, 'time': 0} for model in model_names}

        for category in test_categories:
            category_data = {}
            for model in model_names:
                model_summaries = [s for s in summaries if s['category'] == category and s['model_name'] == model]
                if model_summaries and model_summaries[0]['test_count'] > 0:
                    category_data[model] = model_summaries[0]

            if len(category_data) == 2:
                model1, model2 = model_names[0], model_names[1]
                data1, data2 = category_data[model1], category_data[model2]

                # TTFT 优势
                if data1['ttft_mean'] < data2['ttft_mean']:
                    advantages[model1]['ttft'] += 1
                else:
                    advantages[model2]['ttft'] += 1

                # 生成速度优势
                if data1['speed_mean'] > data2['speed_mean']:
                    advantages[model1]['speed'] += 1
                else:
                    advantages[model2]['speed'] += 1

                # 总时间优势
                if data1['total_time_mean'] < data2['total_time_mean']:
                    advantages[model1]['time'] += 1
                else:
                    advantages[model2]['time'] += 1

        # 生成总结
        md += "**各模型优势场景统计**：\n\n"
        md += "| 模型 | TTFT 优势 | 生成速度优势 | 总时间优势 | 总计 |\n"
        md += "|------|----------|-------------|----------|------|\n"

        # 找出总体优胜者用于格式化
        model_totals = {model: advantages[model]['ttft'] + advantages[model]['speed'] + advantages[model]['time'] for model in model_names}
        max_total = max(model_totals.values()) if model_totals else 0
        all_totals = list(model_totals.values())

        for model in model_names:
            adv = advantages[model]
            total = model_totals[model]
            # 突出获胜模型的名称和总分数（🏆 在较高的总分旁边）
            model_formatted = self._format_winning_model(model, total == max_total)
            total_formatted = self._format_winning_score(total, all_totals, is_lower_better=False)
            md += f"| {model_formatted} | {adv['ttft']} | {adv['speed']} | {adv['time']} | {total_formatted} |\n"

        md += "\n"

        # 综合分析
        md += "**综合分析**：\n\n"

        model1_adv = advantages[model_names[0]]['ttft'] + advantages[model_names[0]]['speed'] + advantages[model_names[0]]['time']
        model2_adv = advantages[model_names[1]]['ttft'] + advantages[model_names[1]]['speed'] + advantages[model_names[1]]['time']

        if model1_adv > model2_adv:
            md += f"- **{model_names[0]}** 在 {model1_adv} 个场景中表现更好\n"
            md += f"- {model_names[1]} 在 {model2_adv} 个场景中表现更好\n\n"
        elif model2_adv > model1_adv:
            md += f"- **{model_names[1]}** 在 {model2_adv} 个场景中表现更好\n"
            md += f"- {model_names[0]} 在 {model1_adv} 个场景中表现更好\n\n"
        else:
            md += "- 两个模型各有优势，表现相当\n\n"

        return md

    def _generate_recommendations(
        self,
        statistics: Dict[str, Any],
        summaries: List[Dict[str, Any]],
        model_names: List[str],
        quality_stats: Dict[str, Any] = None,
        minimax_stats: Dict[str, Any] = None
    ) -> str:
        """生成意见建议部分"""
        # 根据是否有 MiniMax 数据决定章节标题编号
        section_num = "六" if minimax_stats else "四"
        md = f"## {section_num}、意见建议\n\n"

        # 4.1 性能总结
        md += "### 4.1 性能总结\n\n"

        # 计算总体统计
        overall_stats = {}
        for model in model_names:
            model_summaries = [s for s in summaries if s['model_name'] == model and s['test_count'] > 0]
            if model_summaries:
                overall_stats[model] = {
                    'avg_ttft': sum(s['ttft_mean'] for s in model_summaries) / len(model_summaries),
                    'avg_speed': sum(s['speed_mean'] for s in model_summaries) / len(model_summaries),
                    'avg_time': sum(s['total_time_mean'] for s in model_summaries) / len(model_summaries)
                }

        if len(overall_stats) == 2:
            model1, model2 = model_names[0], model_names[1]
            stats1 = overall_stats[model1]
            stats2 = overall_stats[model2]

            # TTFT 对比
            if stats1['avg_ttft'] < stats2['avg_ttft']:
                md += f"- **首次响应速度**: {model1} 更快，平均快 {((stats2['avg_ttft'] - stats1['avg_ttft']) / stats2['avg_ttft'] * 100):.1f}%\n"
            else:
                md += f"- **首次响应速度**: {model2} 更快，平均快 {((stats1['avg_ttft'] - stats2['avg_ttft']) / stats1['avg_ttft'] * 100):.1f}%\n"

            # 生成速度对比
            if stats1['avg_speed'] > stats2['avg_speed']:
                if stats2['avg_speed'] > 0:
                    md += f"- **生成速度**: {model1} 更快，平均快 {((stats1['avg_speed'] - stats2['avg_speed']) / stats2['avg_speed'] * 100):.1f}%\n"
                else:
                    md += f"- **生成速度**: {model1} 更快 ({stats1['avg_speed']:.2f} vs {stats2['avg_speed']:.2f} tokens/s)\n"
            else:
                if stats1['avg_speed'] > 0:
                    md += f"- **生成速度**: {model2} 更快，平均快 {((stats2['avg_speed'] - stats1['avg_speed']) / stats1['avg_speed'] * 100):.1f}%\n"
                else:
                    md += f"- **生成速度**: {model2} 更快 ({stats2['avg_speed']:.2f} vs {stats1['avg_speed']:.2f} tokens/s)\n"

            md += "\n"

        # 4.2 使用建议
        md += "### 4.2 使用建议\n\n"

        md += "**根据不同场景的推荐**：\n\n"

        # 简单问答场景
        qa_data = [s for s in summaries if s['category'] == 'qa_simple']
        if qa_data:
            md += "**简单问答场景**：\n\n"
            best_ttft = min(qa_data, key=lambda x: x['ttft_mean'])
            md += f"- 如果追求快速响应，推荐使用 **{best_ttft['model_name']}** (TTFT: {best_ttft['ttft_mean']:.2f}ms)\n\n"

        # 长文本生成场景
        long_data = [s for s in summaries if s['category'] == 'generation_long']
        if long_data:
            md += "**长文本生成场景**：\n\n"
            best_speed = max(long_data, key=lambda x: x['speed_mean'])
            md += f"- 如果需要生成大量内容，推荐使用 **{best_speed['model_name']}** (速度: {best_speed['speed_mean']:.2f} tokens/s)\n\n"

        # 代码生成场景
        code_data = [s for s in summaries if s['category'] == 'code_generation']
        if code_data:
            md += "**代码生成场景**：\n\n"
            best_time = min(code_data, key=lambda x: x['total_time_mean'])
            md += f"- 代码生成任务推荐使用 **{best_time['model_name']}** (总时间: {best_time['total_time_mean']:.2f}ms)\n\n"

        # 4.3 优化建议
        md += "### 4.3 优化建议\n\n"

        md += "**对于 API 使用方**：\n\n"
        md += "1. **预热连接**: 在正式请求前进行 1-2 次预热请求，可以显著改善首次响应时间\n"
        md += "2. **流式响应**: 对于长文本生成，务必使用流式响应接口，可以改善用户体验\n"
        md += "3. **模型选择**: 根据具体场景选择合适的模型，简单问答优先考虑 TTFT，长文本生成优先考虑生成速度\n\n"

        md += "**对于 API 提供方**：\n\n"
        md += "1. **持续优化 TTFT**: 首次响应时间是用户体验的关键指标\n"
        md += "2. **提升生成速度**: 特别是对于长文本生成场景，生成速度直接影响用户等待时间\n"
        md += "3. **保持稳定性**: 减少响应时间的波动，提升用户体验的一致性\n\n"

        md += "---\n\n"
        return md

    def _generate_quality_assessment(
        self,
        quality_stats: Dict[str, Any],
        model_names: List[str],
        test_categories: List[str],
        raw_results: List[Dict[str, Any]],
        has_minimax: bool = False
    ) -> str:
        """生成质量评估章节"""
        # 根据是否有 MiniMax 数据决定章节编号
        section_num = "五" if has_minimax else "四"
        md = f"## {section_num}、质量评估\n\n"

        # 4.1 评估概述
        md += "### 4.1 评估概述\n\n"
        md += f"本次测试使用 {len(quality_stats.get('by_judge', {}))} 个 Judge 模型进行质量评估：\n\n"

        for judge_name, judge_stats in quality_stats.get("by_judge", {}).items():
            md += f"- **{judge_name}** (模型: {judge_stats.get('judge_model', 'N/A')})\n"
            md += f"  - 评估次数: {judge_stats.get('total_evaluations', 0)}\n"
            md += f"  - 平均分数: {judge_stats.get('avg_score', 0):.2f}/5.0\n\n"

        # 4.2 各 Judge 评估结果
        md += "### 4.2 各 Judge 评估结果\n\n"

        for judge_name in quality_stats.get("by_judge", {}).keys():
            md += f"#### {judge_name} 的评估\n\n"
            md += self._generate_judge_results(
                judge_name, quality_stats, model_names, test_categories
            )

        # 4.3 Judge 间评估对比
        md += "### 4.3 Judge 间评估对比\n\n"
        md += self._generate_judge_comparison(quality_stats, model_names, test_categories)

        # 4.4 质量评估示例
        md += "### 4.4 质量评估示例\n\n"
        md += self._generate_quality_examples(raw_results, model_names)

        md += "---\n\n"
        return md

    def _generate_judge_results(
        self,
        judge_name: str,
        quality_stats: Dict[str, Any],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成单个 Judge 的评估结果"""
        md = ""

        # 按模型统计
        md += "**按模型统计**：\n\n"
        md += "| 模型 | 平均分数 | 评估次数 |\n"
        md += "|------|---------|----------|\n"

        for model_name in model_names:
            if model_name in quality_stats.get("by_model", {}):
                model_stats = quality_stats["by_model"][model_name]
                if judge_name in model_stats:
                    stats = model_stats[judge_name]
                    md += f"| {model_name} | {stats['avg_score']:.2f} | {stats['total_evaluations']} |\n"

        md += "\n"

        # 按类别统计
        md += "**按类别统计**：\n\n"
        md += "| 类别 | " + " | ".join(model_names) + " |\n"
        md += "|------|" + "|".join(["---------"] * len(model_names)) + "|\n"

        for category in test_categories:
            if category in quality_stats.get("by_category", {}):
                row = [category]
                for model_name in model_names:
                    if model_name in quality_stats["by_category"][category]:
                        model_stats = quality_stats["by_category"][category][model_name]
                        if judge_name in model_stats:
                            row.append(f"{model_stats[judge_name]['avg_score']:.2f}")
                        else:
                            row.append("N/A")
                    else:
                        row.append("N/A")
                md += "| " + " | ".join(row) + " |\n"

        md += "\n"
        return md

    def _generate_judge_comparison(
        self,
        quality_stats: Dict[str, Any],
        model_names: List[str],
        test_categories: List[str]
    ) -> str:
        """生成 Judge 间对比"""
        md = "**Judge 评估一致性分析**：\n\n"

        judges = list(quality_stats.get("by_judge", {}).keys())
        if len(judges) < 2:
            md += "*只有一个 Judge，无法进行对比*\n\n"
            return md

        # 按类别对比
        md += "| 测试类别 | " + " | ".join([f"{j} 评估 {m}" for j in judges for m in model_names]) + " |\n"
        md += "|---------|" + "|".join(["------------------"] * (len(judges) * len(model_names))) + "|\n"

        for category in test_categories:
            if category not in quality_stats.get("by_category", {}):
                continue

            row = [category]
            category_stats = quality_stats["by_category"][category]

            for judge_name in judges:
                for model_name in model_names:
                    if model_name in category_stats and judge_name in category_stats[model_name]:
                        score = category_stats[model_name][judge_name]['avg_score']
                        row.append(f"{score:.2f}")
                    else:
                        row.append("N/A")

            md += "| " + " | ".join(row) + " |\n"

        md += "\n"

        # 计算分数差异
        md += "**Judge 间分数差异**：\n\n"
        md += "| 模型 | 平均分数差异 |\n"
        md += "|------|-------------|\n"

        for model_name in model_names:
            if model_name in quality_stats.get("by_model", {}):
                model_stats = quality_stats["by_model"][model_name]
                scores = [judge_stats['avg_score'] for judge_stats in model_stats.values()]
                if len(scores) >= 2:
                    diff = max(scores) - min(scores)
                    md += f"| {model_name} | {diff:.2f} |\n"

        md += "\n"
        return md

    def _generate_quality_examples(
        self,
        raw_results: List[Dict[str, Any]],
        model_names: List[str]
    ) -> str:
        """生成质量评估示例"""
        md = "**典型评估案例**：\n\n"

        # 找出有质量评估的结果
        quality_results = [r for r in raw_results if r.get("quality_evaluations")]

        if not quality_results:
            md += "*暂无详细评估案例*\n\n"
            return md

        # 展示前 3 个案例
        for i, result in enumerate(quality_results[:3], 1):
            md += f"#### 案例 {i}: {result.get('test_name', 'Unknown')}\n\n"
            md += f"- **测试类别**: {result.get('test_category', 'N/A')}\n"
            md += f"- **被评估模型**: {result.get('model_name', 'N/A')}\n\n"

            # 展示各 Judge 的评估
            for judge_name, evaluation in result.get("quality_evaluations", {}).items():
                if not evaluation.get("success", False):
                    continue

                md += f"**{judge_name} 评估**：\n\n"
                md += f"- 总体分数: {evaluation.get('overall_score', 0):.2f}/5.0\n"

                # 展示各标准分数
                scores = evaluation.get('scores', {})
                if scores:
                    md += "- 各项分数:\n"
                    for criterion, score in scores.items():
                        md += f"  - {criterion}: {score:.1f}\n"

                # 展示优缺点
                if evaluation.get('strengths'):
                    md += f"- 优点: {', '.join(evaluation['strengths'][:3])}\n"

                if evaluation.get('weaknesses'):
                    md += f"- 缺点: {', '.join(evaluation['weaknesses'][:3])}\n"

                # 展示评估理由（截断）
                reasoning = evaluation.get('reasoning', '')
                if reasoning:
                    reasoning_short = reasoning[:200] + "..." if len(reasoning) > 200 else reasoning
                    md += f"- 评估理由: {reasoning_short}\n"

                md += "\n"

            md += "\n"

        return md

    def _generate_footer(self) -> str:
        """生成报告尾部"""
        return f"""---

## 附录

### 测试配置

- **预热运行次数**: 2 次
- **正式测试次数**: 每个测试 3 次
- **计时精度**: 纳秒级 (使用 `time.perf_counter()`)
- **API 协议**: Anthropic Messages API (流式响应)

### 数据说明

- 所有测试数据均为多次运行的平均值
- 测试结果可能受网络条件、服务器负载等因素影响
- 建议在不同时间段多次测试以获得更准确的结果

### 报告说明

本报告由自动化测试系统生成，测试时间戳：{self.timestamp}

完整原始数据已保存至 `results/data/raw_data_{self.timestamp}.json`

---

*报告生成工具: DeepSeek vs GLM API 基准测试系统 v1.0*
"""
