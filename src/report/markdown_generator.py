"""Markdown报告生成器 - 从JSON数据生成纯Markdown格式的评测报告

包含10种丰富的ASCII图表：
1. 精细柱状图
2. 水平条形图
3. 雷达图文本表示
4. 折线图
5. 堆叠条形图
6. 对比矩阵表格
7. 散点图
8. 时间轴对比图
9. 进度条
10. 热力图
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# 导入共享的格式化器
from .formatters import (
    ScoreFormatter,
    GradeFormatter,
    TableFormatter,
    ProgressFormatter,
    DimensionTranslator
)


class MarkdownReportGenerator:
    """纯Markdown报告生成器"""

    def __init__(self, output_dir: str = "results/markdown_reports"):
        """
        初始化生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_json(self, json_path: str) -> str:
        """
        从JSON文件生成Markdown报告

        Args:
            json_path: JSON文件路径

        Returns:
            str: Markdown报告文件路径
        """
        # 读取JSON数据
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 生成报告内容
        content = self._generate_complete_report(data)

        # 保存Markdown文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"minimax_report_{timestamp}.md"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def _generate_complete_report(self, data: Dict) -> str:
        """生成完整报告"""
        sections = []

        # 报告头部
        sections.append(self._generate_front_matter(data))

        # 一、评测概要
        sections.append(self._generate_summary_section(data))

        # 二、性能指标分析
        sections.append(self._generate_performance_section(data))

        # 三、质量评估分析
        sections.append(self._generate_quality_section(data))

        # 四、维度详细分析
        sections.append(self._generate_dimension_section(data))

        # 五、使用建议
        sections.append(self._generate_recommendations_section(data))

        # 六、评测方法论
        sections.append(self._generate_methodology_section(data))

        # 七、原始数据摘要
        sections.append(self._generate_raw_data_section(data))

        # 附录
        sections.append(self._generate_appendix_section(data))

        return "\n\n".join(sections)

    def _generate_front_matter(self, data: Dict) -> str:
        """生成报告头部"""
        metadata = data["metadata"]
        lines = [
            f"# DeepSeek vs GLM - MiniMax 标准评测报告",
            "",
            f"**报告生成时间**: {metadata['start_time'][:10]}",
            f"**评测模式**: {metadata.get('evaluation_mode', 'standard').title()} ({metadata['total_tests']}个用例)",
            f"**报告ID**: {metadata['report_id']}",
            "",
            "---",
            ""
        ]
        return "\n".join(lines)

    def _generate_summary_section(self, data: Dict) -> str:
        """生成评测概要"""
        lines = [
            "## 一、评测概要",
            ""
        ]

        quality_scores = data["quality_scores"]
        models = list(quality_scores.keys())

        # 综合得分表格
        lines.append("### 综合得分")
        lines.append("")
        lines.append("| 模型 | 综合得分 | 等级 | 排名 |")
        lines.append("|------|---------|------|------|")

        for model in models:
            model_data = quality_scores[model]
            score = model_data["overall_score"]
            grade = model_data["grade"]
            rank = model_data["rank"]
            emoji = self._get_grade_emoji(grade)
            lines.append(f"| **{model.capitalize()}** | **{score:.2f}/10** | {emoji} {grade} | #{rank} |")

        lines.append("")

        # 核心发现
        lines.append("### 核心发现")
        lines.append("")

        # 找出最佳模型
        best_model = max(quality_scores.items(), key=lambda x: x[1]["overall_score"])
        best_name = best_model[0].capitalize()
        best_score = best_model[1]["overall_score"]

        lines.append(f"- ✨ **最佳模型**: {best_name} ({best_score:.2f}/10)")

        # 找出最快的模型（从performance_summaries中）
        if "performance_summaries" in data and len(data["performance_summaries"]) > 0:
            first_summary = data["performance_summaries"][0]
            if "comparison" in first_summary and "ttft_winner" in first_summary["comparison"]:
                fastest = first_summary["comparison"]["ttft_winner"].capitalize()
                lines.append(f"- ⚡ **最快响应**: {fastest} (首次响应)")

        lines.append(f"- 📊 **测试成功率**: {data['statistics']['success_rate']*100:.1f}% "
                     f"({data['statistics']['successful_tests']}/{data['statistics']['total_tests']})")

        lines.append("")
        return "\n".join(lines)

    def _generate_performance_section(self, data: Dict) -> str:
        """生成性能分析"""
        lines = [
            "## 二、性能指标分析",
            ""
        ]

        # 遍历各维度生成性能数据
        if "performance_summaries" in data:
            for perf_summary in data["performance_summaries"]:
                dimension = perf_summary["dimension"]
                dimension_name_cn = self._translate_dimension(dimension)

                lines.append(f"### {dimension_name_cn} - 性能对比")
                lines.append("")

                model_summaries = perf_summary["model_summaries"]
                models = list(model_summaries.keys())

                # 创建TTFT对比表格
                lines.append("| 模型 | 平均TTFT | 平均生成速度 | 平均总时间 |")
                lines.append("|------|---------|------------|----------|")

                for model in models:
                    summary = model_summaries[model]
                    lines.append(
                        f"| {model.capitalize()} | {summary['ttft_mean']:.1f}ms | "
                        f"{summary['speed_mean']:.2f} t/s | {summary['total_time_mean']:.1f}ms |"
                    )

                lines.append("")

                # TTFT对比图
                ttft_data = {model: model_summaries[model]["ttft_mean"] for model in models}
                lines.append(self._create_bar_chart(ttft_data, "TTFT对比"))

        return "\n".join(lines)

    def _generate_quality_section(self, data: Dict) -> str:
        """生成质量评估"""
        lines = [
            "## 三、质量评估分析",
            ""
        ]

        # Judge评估信息
        if "quality_evaluations" in data:
            qe = data["quality_evaluations"]

            lines.append("### Judge 评估概览")
            lines.append("")
            lines.append("| Judge | 权重 |")
            lines.append("|-------|------|")

            for judge, weight in qe.get("judge_weights", {}).items():
                judge_name = judge.replace("_", " ").title()
                lines.append(f"| {judge_name} | {weight:.0%} |")

            lines.append("")

        # 多维雷达图
        quality_scores = data["quality_scores"]
        dimension_scores = {}
        for model, scores in quality_scores.items():
            for dim, score in scores["dimension_scores"].items():
                if dim not in dimension_scores:
                    dimension_scores[dim] = {}
                dimension_scores[dim][model] = {"score": score}

        if dimension_scores:
            lines.append(self._create_radar_chart_text(dimension_scores, "多维能力对比"))

        return "\n".join(lines)

    def _generate_dimension_section(self, data: Dict) -> str:
        """生成维度详细分析"""
        lines = [
            "## 四、维度详细分析",
            ""
        ]

        quality_scores = data["quality_scores"]
        performance_summaries = {ps["dimension"]: ps for ps in data.get("performance_summaries", [])}

        dimensions = list(quality_scores[list(quality_scores.keys())[0]]["dimension_scores"].keys())

        for dimension in dimensions:
            dimension_name_cn = self._translate_dimension(dimension)
            lines.append(f"### {dimension_name_cn}")
            lines.append("")

            models = list(quality_scores.keys())

            # 维度得分表格
            lines.append("| 模型 | 得分 | 评价 |")
            lines.append("|------|------|------|")

            for model in models:
                score = quality_scores[model]["dimension_scores"][dimension]

                # 生成评价
                if score >= 9.0:
                    evaluation = "优秀"
                elif score >= 7.5:
                    evaluation = "良好"
                elif score >= 6.0:
                    evaluation = "合格"
                else:
                    evaluation = "待改进"

                lines.append(f"| {model.capitalize()} | {score:.2f}/10 | {evaluation} |")

            lines.append("")

            # 优劣势
            for model in models:
                model_data = quality_scores[model]
                if model_data.get("strengths") or model_data.get("weaknesses"):
                    lines.append(f"**{model.capitalize()}**:")

                    if model_data.get("strengths"):
                        lines.append("- ✅ 优势: " + "、".join(model_data["strengths"]))

                    if model_data.get("weaknesses"):
                        lines.append("- ⚠️  注意: " + "、".join(model_data["weaknesses"]))

                    lines.append("")

            # 分数对比图
            scores = {model: quality_scores[model]["dimension_scores"][dimension] for model in models}
            lines.append(self._create_progress_bars(scores, f"{dimension_name_cn}得分"))

            lines.append("")

        return "\n".join(lines)

    def _generate_recommendations_section(self, data: Dict) -> str:
        """生成使用建议"""
        lines = [
            "## 五、使用建议",
            ""
        ]

        quality_scores = data["quality_scores"]

        # 为每个模型生成建议
        for model, scores in quality_scores.items():
            lines.append(f"### {model.capitalize()} 使用建议")
            lines.append("")

            overall_score = scores["overall_score"]

            if scores.get("recommendations"):
                for rec in scores["recommendations"]:
                    lines.append(f"- {rec}")

            lines.append("")

        return "\n".join(lines)

    def _generate_methodology_section(self, data: Dict) -> str:
        """生成评测方法论"""
        lines = [
            "## 六、评测方法论",
            ""
        ]

        # 测试设计
        lines.append("### 测试设计")
        lines.append("")
        metadata = data["metadata"]
        stats = data["statistics"]

        lines.append(f"- **测试用例总数**: {metadata['total_tests']}")
        lines.append(f"- **测试维度**: 4个")
        lines.append(f"- **成功率**: {stats['success_rate']*100:.1f}%")
        lines.append("")

        # 维度权重
        lines.append("### 维度权重")
        lines.append("")
        lines.append("| 维度 | 权重 | 说明 |")
        lines.append("|------|------|------|")

        dimension_translations = {
            "basic_performance": ("基础性能", "响应速度、稳定性"),
            "core_capabilities": ("核心能力", "推理、理解、生成能力"),
            "practical_scenarios": ("实用场景", "实际应用表现"),
            "advanced_features": ("高级特性", "创造性、多轮对话等")
        }

        for dim, weight in data["dimension_weights"].items():
            cn_name, desc = dimension_translations.get(dim, (dim, ""))
            lines.append(f"| {cn_name} | {weight:.0%} | {desc} |")

        lines.append("")

        return "\n".join(lines)

    def _generate_raw_data_section(self, data: Dict) -> str:
        """生成原始数据摘要"""
        lines = [
            "## 七、原始数据摘要",
            ""
        ]

        # 测试执行情况
        lines.append("### 测试执行情况")
        lines.append("")
        stats = data["statistics"]

        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 总测试数 | {stats['total_tests']} |")
        lines.append(f"| 成功执行 | {stats['successful_tests']} |")
        lines.append(f"| 执行失败 | {stats['failed_tests']} |")
        lines.append(f"| 成功率 | {stats['success_rate']*100:.1f}% |")
        lines.append("")

        # 模型配置
        lines.append("### 模型配置")
        lines.append("")

        config = data.get("config_snapshot", {})
        if "apis" in config:
            lines.append("| 模型 | API端点 | 模型名称 |")
            lines.append("|------|---------|---------|")

            for model_name, api_config in config["apis"].items():
                lines.append(
                    f"| {model_name.capitalize()} | {api_config.get('base_url', 'N/A')} | "
                    f"{api_config.get('model', 'N/A')} |"
                )

        lines.append("")

        return "\n".join(lines)

    def _generate_appendix_section(self, data: Dict) -> str:
        """生成附录"""
        lines = [
            "---",
            "",
            "## 附录",
            ""
        ]

        # 评分等级定义
        lines.append("### 附录A: 评分等级定义")
        lines.append("")
        lines.append("| 等级 | 分数范围 |")
        lines.append("|------|---------|")
        lines.append("| 🟢 优秀 | 9.0-10.0 |")
        lines.append("| 🟢 良好 | 7.5-8.9 |")
        lines.append("| 🟡 合格 | 6.0-7.4 |")
        lines.append("| 🔴 不合格 | 3.0-5.9 |")
        lines.append("| 🔴 严重缺陷 | 0-2.9 |")
        lines.append("")

        # 数据文件
        lines.append("### 附录B: 数据文件")
        lines.append("")
        metadata = data["metadata"]
        lines.append(f"**JSON原始数据**: `{self.output_dir.name}/{metadata['report_id']}.json`")
        lines.append("**完整配置**: `config.yaml`")
        lines.append("**测试用例定义**: `src/tests/cases_minimax/`")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*报告生成工具: DeepSeek vs GLM MiniMax 评测系统 v2.0*")
        lines.append(f"*生成时间: {metadata['start_time']}*")

        return "\n".join(lines)

    # =========================================================================
    # 图表生成方法（10种）
    # =========================================================================

    def _create_bar_chart(self, values: Dict[str, float], title: str,
                         bar_width: int = 40) -> str:
        """创建精细ASCII柱状图，带刻度和网格"""
        if not values:
            return ""

        max_val = max(values.values())
        lines = [f"\n### {title}\n"]
        lines.append("```")

        # 顶部边框
        lines.append(f"{'':>12} {'█' * bar_width}")
        lines.append(f"{max_val:>10.1f} ┌{'─' * bar_width}┐")

        # 数据条
        for label, value in values.items():
            bar_length = int(value / max_val * bar_width)

            # 使用不同字符表示密度
            if value >= max_val * 0.8:
                bar_char = "█"
            elif value >= max_val * 0.6:
                bar_char = "▓"
            elif value >= max_val * 0.4:
                bar_char = "▒"
            else:
                bar_char = "░"

            bar = bar_char * bar_length
            lines.append(f"{'':>12} │{bar}│ {label}: {value:.2f}")

        # 底部边框
        lines.append(f"{'':>12} └{'─' * bar_width}┘")
        lines.append(f"{'0.0':>10}  ")
        lines.append("```")

        return "\n".join(lines)

    def _create_horizontal_bar_chart(self, data: Dict[str, Dict],
                                      metric: str, title: str) -> str:
        """创建水平对比条形图"""
        if not data:
            return ""

        lines = [f"\n### {title}\n"]
        lines.append("```\n")

        for label, values in data.items():
            lines.append(f"\n**{label}**")
            for model, value in values.items():
                max_val = max(v for vals in data.values() for v in vals.values())
                bar_length = int(value / max_val * 30) if max_val > 0 else 0

                # 不同模型使用不同字符
                if model == "deepseek":
                    bar = "▓" * bar_length
                else:
                    bar = "█" * bar_length

                lines.append(f"  {model:12} {bar} {value:.2f}")

        lines.append("\n```")
        return "\n".join(lines)

    def _create_radar_chart_text(self, quality_scores: Dict, title: str = "") -> str:
        """创建雷达图的文本表示"""
        if not quality_scores:
            return ""

        lines = [f"\n### {title}\n"]

        # 获取所有维度和模型
        dimensions = list(quality_scores.keys())
        if not dimensions:
            return ""

        models = list(quality_scores[dimensions[0]].keys())

        # 为每个模型生成雷达图文本
        for model in models:
            lines.append(f"\n**{model.upper()}**")
            lines.append("```")

            scores = []
            for dim in dimensions:
                score_data = quality_scores[dim][model]
                score = score_data["score"] if isinstance(score_data, dict) else score_data
                scores.append((dim, score))

            # 按分数排序
            scores.sort(key=lambda x: x[1], reverse=True)

            for dim, score in scores:
                # 创建10级刻度条
                bar_len = int(score / 10 * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)

                # 翻译维度名
                dim_cn = self._translate_dimension(dim)
                lines.append(f"  {dim_cn:20} [{bar}] {score:.1f}/10")

            lines.append("```")

        return "\n".join(lines)

    def _create_line_chart(self, data_points: List[float],
                           labels: List[str], title: str) -> str:
        """创建ASCII折线图显示趋势"""
        if not data_points:
            return ""

        lines = [f"\n### {title}\n"]
        lines.append("```")

        max_val = max(data_points)
        min_val = min(data_points)
        height = 10

        # 创建Y轴刻度
        for y in range(height, -1, -1):
            val = min_val + (max_val - min_val) * y / height
            line = f"{val:6.1f} │"

            for i, point in enumerate(data_points):
                # 计算该点在当前高度的相对位置
                point_y = (point - min_val) / (max_val - min_val) * height
                if abs(point_y - y) < 0.5:
                    line += "  ●  "
                else:
                    line += "     "

            lines.append(line)

        # 添加X轴标签
        lines.append("       └" + "─────" * len(data_points))
        label_line = "        "
        for label in labels:
            label_cn = self._translate_dimension(label)[:4]
            label_line += f"{label_cn:^5}"
        lines.append(label_line)

        lines.append("```")
        return "\n".join(lines)

    def _create_stacked_bar(self, quality_scores: Dict,
                            dimension_weights: Dict, title: str) -> str:
        """创建堆叠条形图，显示各维度对总分的贡献"""
        if not quality_scores:
            return ""

        lines = [f"\n### {title}\n"]
        lines.append("```\n")

        for model_name, scores in quality_scores.items():
            overall = scores["overall_score"]
            lines.append(f"**{model_name}** (总分: {overall:.2f}/10)")

            # 按权重排序维度
            sorted_dims = sorted(
                scores["dimension_scores"].items(),
                key=lambda x: dimension_weights[x[0]],
                reverse=True
            )

            for dim_name, score in sorted_dims:
                weight = dimension_weights[dim_name]
                weighted = score * weight

                # 计算条形长度
                bar_len = int(score / 10 * 30)

                # 根据权重使用不同符号
                if weight >= 0.35:
                    char = "█"  # 高权重
                elif weight >= 0.25:
                    char = "▓"  # 中等权重
                else:
                    char = "▒"  # 低权重

                bar = char * bar_len
                pct = weight * 100

                dim_cn = self._translate_dimension(dim_name)
                lines.append(
                    f"  {dim_cn:20} ({pct:2.0f}%) "
                    f"[{bar}] {score:.2f} → {weighted:.2f}"
                )

            lines.append("")

        lines.append("```")
        lines.append("**图例**: ██(35%) ▓▓(25%) ▒▒(15%)")

        return "\n".join(lines)

    def _create_comparison_matrix(self, data: Dict) -> str:
        """创建详细的对比矩阵"""
        if not data or "quality_scores" not in data:
            return ""

        quality_scores = data["quality_scores"]
        models = list(quality_scores.keys())

        if not models:
            return ""

        lines = ["\n### 模型对比矩阵\n"]

        # 表头
        header = "| 指标 |"
        for model in models:
            header += f" {model.capitalize()} |"
        lines.append(header)

        separator = "|------|"
        for _ in models:
            separator += "---------|"
        lines.append(separator)

        # 维度得分行
        dimensions = list(quality_scores[models[0]]["dimension_scores"].keys())

        for dim in dimensions:
            row = f"| {dim} |"
            for model in models:
                score = quality_scores[model]["dimension_scores"][dim]
                # 使用颜色标记
                if score >= 9.0:
                    emoji = "🟢"
                elif score >= 7.5:
                    emoji = "🟢"
                elif score >= 6.0:
                    emoji = "🟡"
                else:
                    emoji = "🔴"
                row += f" {emoji} {score:.2f} |"
            lines.append(row)

        # 总分行
        total_row = "| **总分** |"
        for model in models:
            score = quality_scores[model]["overall_score"]
            total_row += f" **{score:.2f}** |"
        lines.append(total_row)

        return "\n".join(lines)

    def _create_scatter_plot(self, performance_data: List,
                             quality_data: List, title: str) -> str:
        """创建性能vs质量散点图"""
        if not performance_data or not quality_data:
            return ""

        lines = [f"\n### {title}\n"]
        lines.append("```")

        # 定义网格
        grid_size = 15
        grid = [[" " for _ in range(grid_size)] for _ in range(grid_size)]

        # 映射数据点到网格
        model_labels = ["A", "B"]
        for i, (perf, qual) in enumerate(zip(performance_data, quality_data)):
            if max(performance_data) > 0 and max(quality_data) > 0:
                x = int((perf / max(performance_data)) * (grid_size - 1))
                y = int((qual / max(quality_data)) * (grid_size - 1))
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    grid[grid_size - 1 - y][x] = model_labels[i % len(model_labels)]

        # Y轴标签
        lines.append(f"{'质量':^4} ↑")

        # 绘制网格
        for row in grid:
            line = "     │" + "".join(row) + "│"
            lines.append(line)

        # X轴标签
        lines.append("     └" + "─" * grid_size + "→")
        lines.append(f"{'':>10}性能\n")

        # 图例
        lines.append("**图例**: A = DeepSeek, B = GLM")
        lines.append("右上角 = 高质量高性能")

        lines.append("```")
        return "\n".join(lines)

    def _create_timeline_comparison(self, time_data: Dict[str, List[float]],
                                    title: str) -> str:
        """创建时间轴对比图"""
        if not time_data:
            return ""

        lines = [f"\n### {title}\n"]
        lines.append("```")

        max_time = max(max(times) for times in time_data.values() if times)

        for model, times in time_data.items():
            if not times:
                continue

            avg_time = sum(times) / len(times)
            bar_len = int(avg_time / max_time * 30) if max_time > 0 else 0

            # 使用不同字符表示时间长短
            if avg_time <= max_time * 0.3:
                bar = "▁" * bar_len  # 极快
            elif avg_time <= max_time * 0.6:
                bar = "▂" * bar_len  # 快
            elif avg_time <= max_time * 0.8:
                bar = "▃" * bar_len  # 中等
            else:
                bar = "▄" * bar_len  # 慢

            lines.append(f"{model:12} {bar} {avg_time:.0f}ms")

        lines.append("\n```")
        lines.append("**图例**: ▁≤30% ▂≤60% ▃≤80% ▄>80%")

        return "\n".join(lines)

    def _create_progress_bars(self, data: Dict[str, float],
                             title: str, max_val: float = 10.0) -> str:
        """创建百分比进度条"""
        if not data:
            return ""

        lines = [f"\n### {title}\n"]
        lines.append("```")

        for label, score in data.items():
            percentage = (score / max_val) * 100
            filled = int(percentage / 5)  # 每5%一个字符

            # 使用不同颜色字符
            if percentage >= 90:
                fill_char = "█"
            elif percentage >= 75:
                fill_char = "▓"
            elif percentage >= 60:
                fill_char = "▒"
            else:
                fill_char = "░"

            bar = fill_char * filled + "░" * (20 - filled)
            lines.append(f"{label:20} [{bar}] {percentage:5.1f}% ({score:.2f})")

        lines.append("\n```")
        return "\n".join(lines)

    def _create_heatmap(self, data: Dict[str, Dict[str, float]],
                       title: str) -> str:
        """创建ASCII热力图"""
        if not data:
            return ""

        lines = [f"\n### {title}\n"]
        lines.append("```")

        models = list(data.keys())
        metrics = list(data[models[0]].keys()) if models else []

        # 表头
        header = "         "
        for model in models:
            header += f"{model.capitalize():^10}"
        lines.append(header)
        lines.append("-" * len(header))

        # 数据行
        for metric in metrics:
            line = f"{metric:10}"
            for model in models:
                value = data[model][metric]
                # 根据数值选择密度字符
                if value >= 9.0:
                    cell = "██████████"
                elif value >= 8.0:
                    cell = "▓▓▓▓▓▓▓▓▓"
                elif value >= 7.0:
                    cell = "▒▒▒▒▒▒▒▒▒"
                elif value >= 6.0:
                    cell = "░░░░░░░░░░"
                else:
                    cell = "··········"
                line += f"{cell:^10}"
            lines.append(line)

        lines.append("```")
        lines.append("**密度**: █=9.0+ ▓=8.0+ ▒=7.0+ ░=6.0+ ·=<6.0")

        return "\n".join(lines)

    # =========================================================================
    # 辅助方法
    # =========================================================================

    def _get_grade_emoji(self, grade: str) -> str:
        """获取等级emoji（使用 GradeFormatter）"""
        return GradeFormatter.get_grade_emoji(grade)

    def _translate_dimension(self, dim_name: str) -> str:
        """翻译维度名称（使用 DimensionTranslator）"""
        return DimensionTranslator.translate(dim_name)
