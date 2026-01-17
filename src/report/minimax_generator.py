"""MiniMax 标准报告生成器

生成符合 MiniMax 标准的评测报告，包括：
- 多维度雷达图
- 详细评分矩阵
- 能力对比分析
- 应用建议矩阵
- 扩展可视化图表（箱型图、小提琴图、散点图等）
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 尝试导入 plotly，如果不可用则跳过可视化功能
try:
    import plotly.graph_objects as go
    import numpy as np
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None
    np = None

from .generator import ReportGenerator
from .color_schemes import ColorSchemes, get_model_color, get_score_color

# 导入共享的格式化器
from .formatters import (
    ScoreFormatter,
    GradeFormatter,
    DimensionTranslator
)


class MiniMaxReportGenerator(ReportGenerator):
    """MiniMax 标准报告生成器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 MiniMax 报告生成器

        Args:
            config: 报告配置
        """
        super().__init__(config)
        self.output_dir = Path(config.get("output_dir", "results/minimax_reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_minimax_report(
        self,
        statistics: Dict[str, Any],
        quality_scores: Dict[str, Any],
        performance_data: List[Dict[str, Any]],
        model_names: List[str],
        dimension_weights: Dict[str, float]
    ) -> str:
        """
        生成 MiniMax 标准完整报告

        Args:
            statistics: 基准测试统计信息
            quality_scores: 质量评估分数
            performance_data: 性能数据
            model_names: 模型名称列表
            dimension_weights: 维度权重

        Returns:
            str: 生成的报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"minimax_report_{timestamp}"

        # 生成各部分
        summary = self._generate_summary(
            statistics, quality_scores, model_names
        )

        performance_analysis = self._generate_performance_analysis(
            performance_data, model_names
        )

        quality_analysis = self._generate_quality_analysis(
            quality_scores, model_names
        )

        dimension_analysis = self._generate_dimension_analysis(
            quality_scores, dimension_weights, model_names
        )

        recommendations = self._generate_recommendations(
            statistics, quality_scores, model_names
        )

        # 组合完整报告
        report = self._assemble_report(
            summary=summary,
            performance_analysis=performance_analysis,
            quality_analysis=quality_analysis,
            dimension_analysis=dimension_analysis,
            recommendations=recommendations,
            model_names=model_names
        )

        # 保存报告
        report_path = self._save_report(report_name, report)

        return report_path

    def _generate_summary(
        self,
        statistics: Dict[str, Any],
        quality_scores: Dict[str, Any],
        model_names: List[str]
    ) -> str:
        """生成执行摘要"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        summary = f"""# MiniMax 标准评测 - 执行摘要

**评测时间**: {timestamp}
**评测模型**: {', '.join(model_names)}
**评测标准**: MiniMax 标准评测体系 v3.0

---

## 总体结论

"""

        # 计算总体得分
        for model_name in model_names:
            model_quality = quality_scores.get(model_name, {})
            overall_score = model_quality.get("overall_score", 0)
            grade = self._get_grade(overall_score)

            summary += f"""### {model_name}

- **综合得分**: {overall_score:.2f}/10
- **等级**: {grade}
- **测试成功率**: {statistics.get('model_stats', {}).get(model_name, {}).get('success', 0)}/{statistics.get('model_stats', {}).get(model_name, {}).get('total', 0)}

"""

        summary += "\n---\n\n"
        return summary

    def _generate_performance_analysis(
        self,
        performance_data: List[Dict[str, Any]],
        model_names: List[str]
    ) -> str:
        """生成性能分析"""
        analysis = "## 性能指标分析\n\n"

        # 按模型组织数据
        model_performance = {}
        for result in performance_data:
            model = result.get("model_name")
            if model and model in model_names:
                if model not in model_performance:
                    model_performance[model] = []
                model_performance[model].append(result)

        # 计算各模型性能统计
        for model_name in model_names:
            if model_name not in model_performance:
                continue

            results = model_performance[model_name]

            ttft_values = [r.get("ttft_ms", 0) for r in results if r.get("success")]
            speed_values = [r.get("tokens_per_second", 0) for r in results if r.get("success")]

            if ttft_values:
                avg_ttft = sum(ttft_values) / len(ttft_values)
                min_ttft = min(ttft_values)
                max_ttft = max(ttft_values)
            else:
                avg_ttft = min_ttft = max_ttft = 0

            if speed_values:
                avg_speed = sum(speed_values) / len(speed_values)
                min_speed = min(speed_values)
                max_speed = max(speed_values)
            else:
                avg_speed = min_speed = max_speed = 0

            analysis += f"""### {model_name}

**首次响应时间 (TTFT)**
- 平均: {avg_ttft:.2f} ms
- 范围: {min_ttft:.2f} - {max_ttft:.2f} ms

**生成速度**
- 平均: {avg_speed:.2f} tokens/s
- 范围: {min_speed:.2f} - {max_speed:.2f} tokens/s

**成功运行**: {len([r for r in results if r.get("success")])}/{len(results)}

---

"""

        return analysis

    def _generate_quality_analysis(
        self,
        quality_scores: Dict[str, Any],
        model_names: List[str]
    ) -> str:
        """生成质量分析"""
        analysis = "## 质量评估分析\n\n"

        for model_name in model_names:
            model_scores = quality_scores.get(model_name, {})

            analysis += f"""### {model_name}

**各维度得分**:

"""

            # 按维度显示得分
            dimension_scores = model_scores.get("dimension_scores", {})
            for dimension, score in dimension_scores.items():
                grade = self._get_grade(score)
                analysis += f"- **{dimension}**: {score:.2f}/10 ({grade})\n"

            analysis += "\n"

        return analysis

    def _generate_dimension_analysis(
        self,
        quality_scores: Dict[str, Any],
        dimension_weights: Dict[str, float],
        model_names: List[str]
    ) -> str:
        """生成维度分析"""
        analysis = "## 维度对比分析\n\n"

        analysis += "| 维度 | 权重 | " + " | ".join(model_names) + " | 优胜者 |\n"
        analysis += "|------|------| " + " | ".join(["---"] * len(model_names)) + " | ------ |\n"

        for dimension, weight in dimension_weights.items():
            row = [dimension, f"{weight*100:.0f}%"]

            scores = []
            for model_name in model_names:
                score = quality_scores.get(model_name, {}).get("dimension_scores", {}).get(dimension, 0)
                scores.append(score)
                row.append(f"{score:.2f}")

            # 判断优胜者
            if len(scores) == 2:
                winner = model_names[0] if scores[0] > scores[1] else model_names[1]
                if abs(scores[0] - scores[1]) < 0.1:
                    winner = "平局"
            else:
                winner = "-"

            row.append(winner)
            analysis += "| " + " | ".join(row) + " |\n"

        return analysis

    def _generate_recommendations(
        self,
        statistics: Dict[str, Any],
        quality_scores: Dict[str, Any],
        model_names: List[str]
    ) -> str:
        """生成应用建议"""
        recommendations = "## 应用建议\n\n"

        # 分析各模型的优势场景
        recommendations += "### 模型优势分析\n\n"

        for model_name in model_names:
            model_scores = quality_scores.get(model_name, {})
            dimension_scores = model_scores.get("dimension_scores", {})

            # 找出得分最高的维度
            if dimension_scores:
                best_dimension = max(dimension_scores.items(), key=lambda x: x[1])
                recommendations += f"""**{model_name}**

- 最强维度: {best_dimension[0]} ({best_dimension[1]:.2f}/10)
- 适用场景: {self._get_scenario_recommendation(best_dimension[0])}

"""

        # 添加使用建议
        recommendations += "\n### 使用建议\n\n"

        if len(model_names) == 2:
            model1, model2 = model_names
            score1 = quality_scores.get(model1, {}).get("overall_score", 0)
            score2 = quality_scores.get(model2, {}).get("overall_score", 0)

            if abs(score1 - score2) < 0.5:
                recommendations += f"两个模型整体表现相当，建议根据具体应用场景选择。"
            elif score1 > score2:
                recommendations += f"**{model1}** 整体表现优于 **{model2}**，建议优先选择 {model1}。"
            else:
                recommendations += f"**{model2}** 整体表现优于 {model1}，建议优先选择 {model2}。"

        return recommendations

    def _assemble_report(
        self,
        summary: str,
        performance_analysis: str,
        quality_analysis: str,
        dimension_analysis: str,
        recommendations: str,
        model_names: List[str]
    ) -> str:
        """组装完整报告"""
        report = f"""# MiniMax 标准评测报告

{summary}
{performance_analysis}
{quality_analysis}
{dimension_analysis}
{recommendations}

---

## 评测方法论

本评测基于 MiniMax 标准评测体系 v3.0，采用三模型交叉评价方式：

### 评价维度
- **基础性能** (25%): TTFT、吞吐量、稳定性
- **核心能力** (35%): 逻辑推理、代码生成、文本理解、创意生成
- **实用场景** (25%): 专业应用、中文处理、长文本、结构化输出
- **高级特性** (15%): 复杂推理、指令遵循、多模态、创新思维

### 评分标准
- **9-10 分**: 优秀，超出预期
- **7.5-8.9 分**: 良好，很好地满足预期
- **6-7.4 分**: 合格，满足最低要求
- **3-5.9 分**: 不合格，低于预期
- **0-2.9 分**: 严重缺陷，未达到要求

### 三模型交叉评价
- MiniMax 40% + DeepSeek 30% + GLM 30% 加权评分

---

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**评测模型**: {', '.join(model_names)}
"""

        return report

    def _save_report(self, report_name: str, report_content: str) -> str:
        """保存报告到文件"""
        # 保存 Markdown 格式
        md_path = self.output_dir / f"{report_name}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # 保存 JSON 格式（原始数据）
        json_path = self.output_dir / f"{report_name}.json"
        # 这里可以添加更多元数据
        report_data = {
            "report_name": report_name,
            "timestamp": datetime.now().isoformat(),
            "content": report_content
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return str(md_path)

    def _get_grade(self, score: float) -> str:
        """将分数转换为等级（使用 GradeFormatter）"""
        return GradeFormatter.get_grade(score, is_10_scale=True)

    def _get_scenario_recommendation(self, dimension: str) -> str:
        """获取维度对应的应用场景建议"""
        scenarios = {
            "basic_performance": "对实时性要求高的场景，如在线对话、实时响应",
            "core_capabilities": "需要复杂推理和代码生成的场景，如编程辅助、问题解决",
            "practical_scenarios": "专业领域的实际应用，如咨询、分析、文档处理",
            "advanced_features": "需要创新思维和复杂推理的高级应用场景"
        }
        return scenarios.get(dimension, "通用场景")

    # ========== 扩展可视化图表生成方法 ==========

    def generate_extended_visualizations(
        self,
        dimension_scores: Dict[str, Any],
        metrics: List[Dict[str, Any]],
        quality_stats: Dict[str, Any]
    ) -> Dict[str, str]:
        """生成扩展可视化图表

        Args:
            dimension_scores: 各维度评分
            metrics: 性能指标数据
            quality_stats: 质量统计数据

        Returns:
            Dict[str, str]: 图表名称到 HTML 的映射
        """
        if not PLOTLY_AVAILABLE:
            print("⚠️  Plotly 未安装，无法生成可视化图表")
            return {}

        charts = {}

        # 原有图表（保留）
        # charts["radar"] = self._create_radar_chart(dimension_scores)
        # charts["heatmap"] = self._create_heatmap(dimension_scores)
        # charts["distribution"] = self._create_grade_distribution(quality_stats)
        # charts["confidence_interval"] = self._create_confidence_interval(dimension_scores)

        # 新增图表
        try:
            charts["box_plot"] = self._create_box_plot(dimension_scores)
        except Exception as e:
            print(f"⚠️  箱型图生成失败: {e}")

        try:
            charts["violin_plot"] = self._create_violin_plot(dimension_scores)
        except Exception as e:
            print(f"⚠️  小提琴图生成失败: {e}")

        try:
            charts["scatter_performance_quality"] = self._create_scatter_plot(metrics, quality_stats)
        except Exception as e:
            print(f"⚠️  散点图生成失败: {e}")

        try:
            charts["stacked_grade"] = self._create_stacked_grade_distribution(quality_stats)
        except Exception as e:
            print(f"⚠️  堆叠柱状图生成失败: {e}")

        try:
            charts["waterfall"] = self._create_waterfall_chart(dimension_scores)
        except Exception as e:
            print(f"⚠️  瀑布图生成失败: {e}")

        try:
            charts["sankey"] = self._create_sankey_diagram(quality_stats)
        except Exception as e:
            print(f"⚠️  桑基图生成失败: {e}")

        try:
            charts["cdf"] = self._create_cdf_chart(metrics)
        except Exception as e:
            print(f"⚠️  CDF图生成失败: {e}")

        try:
            charts["area_chart"] = self._create_area_chart(dimension_scores)
        except Exception as e:
            print(f"⚠️  面积图生成失败: {e}")

        return charts

    def _create_box_plot(self, dimension_scores: Dict[str, Any]) -> str:
        """创建评分分布箱型图"""
        categories = ["基础性能", "核心能力", "实用场景", "高级特性"]
        category_map = {
            "基础性能": "basic_performance",
            "核心能力": "core_capabilities",
            "实用场景": "practical_scenarios",
            "高级特性": "advanced_features"
        }

        fig = go.Figure()

        # DeepSeek 数据
        for category in categories:
            dim_key = category_map[category]
            score = dimension_scores.get("deepseek", {}).get(dim_key, 0)
            fig.add_trace(go.Box(
                x=[category],
                y=[score],
                name='DeepSeek',
                marker_color=get_model_color("deepseek"),
                boxmean='sd',
                jitter=0.3,
                pointpos=-1.8
            ))

        # GLM 数据
        for category in categories:
            dim_key = category_map[category]
            score = dimension_scores.get("glm", {}).get(dim_key, 0)
            fig.add_trace(go.Box(
                x=[category],
                y=[score],
                name='GLM',
                marker_color=get_model_color("glm"),
                boxmean='sd',
                jitter=0.3,
                pointpos=-1.8
            ))

        fig.update_layout(
            title="各维度评分分布箱型图",
            xaxis_title="评测维度",
            yaxis_title="评分 (0-10)",
            yaxis_range=[0, 10],
            boxmode='group'
        )

        return fig.to_html()

    def _create_violin_plot(self, dimension_scores: Dict[str, Any]) -> str:
        """创建小提琴图"""
        dimensions = ["基础性能", "核心能力", "实用场景", "高级特性"]
        dim_keys = ["basic_performance", "core_capabilities", "practical_scenarios", "advanced_features"]

        fig = go.Figure()

        # DeepSeek 小提琴
        for i, (dim, dim_key) in enumerate(zip(dimensions, dim_keys)):
            score = dimension_scores.get("deepseek", {}).get(dim_key, 0)
            fig.add_trace(go.Violin(
                x=[dim],
                y=[score],
                name='DeepSeek',
                line_color=get_model_color("deepseek"),
                fillcolor=f"{get_model_color('deepseek', 'rgba_medium').replace('0.3', '0.3')}",
                meanline_visible=True,
                showlegend=(i == 0)
            ))

        # GLM 小提琴
        for i, (dim, dim_key) in enumerate(zip(dimensions, dim_keys)):
            score = dimension_scores.get("glm", {}).get(dim_key, 0)
            fig.add_trace(go.Violin(
                x=[dim],
                y=[score],
                name='GLM',
                line_color=get_model_color("glm"),
                fillcolor=f"{get_model_color('glm', 'rgba_medium').replace('0.3', '0.3')}",
                meanline_visible=True,
                showlegend=(i == 0)
            ))

        fig.update_layout(
            title="评分概率密度分布（小提琴图）",
            xaxis_title="评测维度",
            yaxis_title="评分 (0-10)",
            yaxis_range=[0, 10],
            violinmode='group'
        )

        return fig.to_html()

    def _create_scatter_plot(self, metrics: List[Dict[str, Any]], quality_stats: Dict[str, Any]) -> str:
        """创建性能-质量散点图"""
        # 提取数据
        deepseek_ttft = []
        deepseek_quality = []
        glm_ttft = []
        glm_quality = []

        for metric in metrics:
            for model_name in ["deepseek", "glm"]:
                ttft = metric.get(model_name, {}).get("avg_ttft", 0) / 1000  # 转换为秒
                quality = quality_stats.get(model_name, {}).get("overall_score", 0)

                if model_name == "deepseek":
                    deepseek_ttft.append(ttft)
                    deepseek_quality.append(quality)
                else:
                    glm_ttft.append(ttft)
                    glm_quality.append(quality)

        fig = go.Figure()

        # DeepSeek 散点
        fig.add_trace(go.Scatter(
            x=deepseek_ttft,
            y=deepseek_quality,
            mode='markers',
            name='DeepSeek',
            marker=dict(
                size=12,
                color=get_model_color("deepseek"),
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
            text=[f"测试{i+1}" for i in range(len(deepseek_ttft))],
            hovertemplate='%{text}<br>TTFT: %{x:.2f}s<br>质量: %{y:.1f}分<extra></extra>'
        ))

        # GLM 散点
        fig.add_trace(go.Scatter(
            x=glm_ttft,
            y=glm_quality,
            mode='markers',
            name='GLM',
            marker=dict(
                size=12,
                color=get_model_color("glm"),
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
            text=[f"测试{i+1}" for i in range(len(glm_ttft))],
            hovertemplate='%{text}<br>TTFT: %{x:.2f}s<br>质量: %{y:.1f}分<extra></extra>'
        ))

        # 添加理想区域标注
        fig.add_shape(
            type="rect",
            x0=0, y0=8, x1=1.5, y1=10,
            fillcolor="rgba(16, 185, 129, 0.2)",
            line=dict(width=0),
            layer="below"
        )

        fig.update_layout(
            title="性能 vs 质量权衡分析",
            xaxis_title="TTFT (秒)",
            yaxis_title="质量评分 (0-10)",
            yaxis_range=[0, 10],
            hovermode='closest'
        )

        # 添加象限标注
        fig.add_annotation(
            x=0.75, y=9, text="理想区域<br>(快且好)",
            showarrow=False,
            font=dict(size=12, color="#059669")
        )

        return fig.to_html()

    def _create_stacked_grade_distribution(self, quality_stats: Dict[str, Any]) -> str:
        """创建评分等级堆叠柱状图"""
        grades = ["优秀 (9-10)", "良好 (7.5-8.9)", "合格 (6-7.4)", "不合格 (3-5.9)", "严重缺陷 (0-2.9)"]
        grade_keys = ["excellent", "good", "qualified", "unqualified", "critical"]

        fig = go.Figure()

        # DeepSeek 堆叠
        for i, (grade, key) in enumerate(zip(grades, grade_keys)):
            count = quality_stats.get("deepseek", {}).get(f"{key}_count", 0)
            color = ColorSchemes.GRADE_COLORS[key]
            fig.add_trace(go.Bar(
                x=['DeepSeek'],
                y=[count],
                name=grade,
                marker_color=color,
                text=[f"{count}"],
                textposition='inside'
            ))

        # GLM 堆叠
        for i, (grade, key) in enumerate(zip(grades, grade_keys)):
            count = quality_stats.get("glm", {}).get(f"{key}_count", 0)
            color = ColorSchemes.GRADE_COLORS[key]
            fig.add_trace(go.Bar(
                x=['GLM'],
                y=[count],
                name=grade,
                marker_color=color,
                text=[f"{count}"],
                textposition='inside',
                showlegend=False
            ))

        fig.update_layout(
            title="评分等级占比对比（堆叠图）",
            barmode='stack',
            yaxis_title="维度数量",
            xaxis_title="模型"
        )

        return fig.to_html()

    def _create_waterfall_chart(self, dimension_scores: Dict[str, Any]) -> str:
        """创建综合得分瀑布图"""
        dimensions = ["基础性能", "核心能力", "实用场景", "高级特性", "综合得分"]
        dim_keys = ["basic_performance", "core_capabilities", "practical_scenarios", "advanced_features"]
        weights = [0.25, 0.35, 0.25, 0.15, 0]

        # DeepSeek
        deepseek_values = []
        deepseek_total = 0
        for i, dim_key in enumerate(dim_keys):
            score = dimension_scores.get("deepseek", {}).get(dim_key, 0)
            weighted = score * weights[i]
            deepseek_values.append(weighted)
            deepseek_total += weighted
        deepseek_values.append(deepseek_total)

        # GLM
        glm_values = []
        glm_total = 0
        for i, dim_key in enumerate(dim_keys):
            score = dimension_scores.get("glm", {}).get(dim_key, 0)
            weighted = score * weights[i]
            glm_values.append(weighted)
            glm_total += weighted
        glm_values.append(glm_total)

        fig = go.Figure()

        # DeepSeek 瀑布
        fig.add_trace(go.Scatter(
            x=dimensions,
            y=deepseek_values,
            mode='lines+markers',
            name='DeepSeek',
            line=dict(color=get_model_color("deepseek"), width=2),
            marker=dict(size=10),
            connectgaps=True
        ))

        # GLM 瀑布
        fig.add_trace(go.Scatter(
            x=dimensions,
            y=glm_values,
            mode='lines+markers',
            name='GLM',
            line=dict(color=get_model_color("glm"), width=2),
            marker=dict(size=10),
            connectgaps=True
        ))

        # 添加权重标注
        annotations = []
        for i, (dim, weight) in enumerate(zip(dimensions[:-1], weights)):
            annotations.append(dict(
                x=dim, y=0,
                text=f"权重 {weight*100:.0f}%",
                showarrow=False,
                yshift=-20,
                font=dict(size=10)
            ))

        fig.update_layout(
            title="综合得分构成分析（瀑布图）",
            xaxis_title="评测维度",
            yaxis_title="加权得分贡献",
            annotations=annotations,
            hovermode='x unified'
        )

        return fig.to_html()

    def _create_sankey_diagram(self, quality_stats: Dict[str, Any]) -> str:
        """创建评价权重流向桑基图"""
        # 定义节点
        nodes = [
            "MiniMax Judge",
            "DeepSeek Judge",
            "GLM Judge",
            "DeepSeek 得分",
            "GLM 得分"
        ]

        # 定义链接
        links = {
            "source": [0, 0, 1, 1, 2, 2],  # MiniMax, DeepSeek Judge, GLM Judge
            "target": [3, 4, 3, 4, 3, 4],  # DeepSeek, GLM
            "value": [40, 40, 30, 30, 30, 30],  # 权重值
            "label": [
                "MiniMax → DeepSeek (40%)",
                "MiniMax → GLM (40%)",
                "DeepSeek Judge → DeepSeek (30%)",
                "DeepSeek Judge → GLM (30%)",
                "GLM Judge → DeepSeek (30%)",
                "GLM Judge → GLM (30%)"
            ]
        }

        # 颜色映射
        colors = {
            "MiniMax Judge": ColorSchemes.MINIMAX["primary"],
            "DeepSeek Judge": ColorSchemes.DEEPSEEK["primary"],
            "GLM Judge": ColorSchemes.GLM["primary"],
            "DeepSeek 得分": ColorSchemes.DEEPSEEK["secondary"],
            "GLM 得分": ColorSchemes.GLM["secondary"]
        }

        node_colors = [colors[node] for node in nodes]

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='white', width=2),
                label=nodes,
                color=node_colors
            ),
            link=dict(
                source=links["source"],
                target=links["target"],
                value=links["value"],
                label=links["label"],
                color='rgba(255, 255, 255, 0.2)'
            )
        )])

        fig.update_layout(
            title="三模型 Judge 评价权重流向（桑基图）",
            font=dict(size=12)
        )

        return fig.to_html()

    def _create_cdf_chart(self, metrics: List[Dict[str, Any]]) -> str:
        """创建 TTFT 累积分布函数图"""
        # 收集 TTFT 数据
        deepseek_ttft = sorted([
            m.get("deepseek", {}).get("avg_ttft", 0)
            for m in metrics if m.get("deepseek", {}).get("avg_ttft", 0) > 0
        ])

        glm_ttft = sorted([
            m.get("glm", {}).get("avg_ttft", 0)
            for m in metrics if m.get("glm", {}).get("avg_ttft", 0) > 0
        ])

        # 计算 CDF
        deepseek_cdf = np.arange(1, len(deepseek_ttft) + 1) / len(deepseek_ttft) if deepseek_ttft else []
        glm_cdf = np.arange(1, len(glm_ttft) + 1) / len(glm_ttft) if glm_ttft else []

        fig = go.Figure()

        if deepseek_ttft and deepseek_cdf is not None and len(deepseek_cdf) > 0:
            fig.add_trace(go.Scatter(
                x=deepseek_ttft,
                y=deepseek_cdf,
                mode='lines',
                name='DeepSeek',
                line=dict(color=get_model_color("deepseek"), width=3),
                fill='tozeroy',
                fillcolor=f"{get_model_color('deepseek', 'rgba_light').replace('0.1', '0.1')}"
            ))

        if glm_ttft and glm_cdf is not None and len(glm_cdf) > 0:
            fig.add_trace(go.Scatter(
                x=glm_ttft,
                y=glm_cdf,
                mode='lines',
                name='GLM',
                line=dict(color=get_model_color("glm"), width=3),
                fill='tozeroy',
                fillcolor=f"{get_model_color('glm', 'rgba_light').replace('0.1', '0.1')}"
            ))

        # 添加百分位线
        for percentile in [0.5, 0.9, 0.95]:
            fig.add_hline(
                y=percentile,
                line_dash="dash",
                line_color="gray",
                annotation_text=f"P{percentile*100:.0f}",
                annotation_position="right"
            )

        fig.update_layout(
            title="TTFT 累积分布函数 (CDF)",
            xaxis_title="TTFT (ms)",
            yaxis_title="累积概率",
            yaxis_range=[0, 1],
            hovermode='x unified'
        )

        return fig.to_html()

    def _create_area_chart(self, dimension_scores: Dict[str, Any]) -> str:
        """创建多维度面积图"""
        dimensions = ["基础性能", "核心能力", "实用场景", "高级特性"]
        dim_keys = ["basic_performance", "core_capabilities", "practical_scenarios", "advanced_features"]

        deepseek_scores = [
            dimension_scores.get("deepseek", {}).get(dim_key, 0)
            for dim_key in dim_keys
        ]

        glm_scores = [
            dimension_scores.get("glm", {}).get(dim_key, 0)
            for dim_key in dim_keys
        ]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dimensions,
            y=deepseek_scores,
            mode='lines+markers',
            name='DeepSeek',
            line=dict(color=get_model_color("deepseek"), width=2),
            fill='tozeroy',
            fillcolor=f"{get_model_color('deepseek', 'rgba_medium').replace('0.2', '0.2')}",
            stackgroup='one'
        ))

        fig.add_trace(go.Scatter(
            x=dimensions,
            y=glm_scores,
            mode='lines+markers',
            name='GLM',
            line=dict(color=get_model_color("glm"), width=2),
            fill='tozeroy',
            fillcolor=f"{get_model_color('glm', 'rgba_medium').replace('0.2', '0.2')}",
            stackgroup='two'
        ))

        fig.update_layout(
            title="多维度得分趋势对比（面积图）",
            xaxis_title="评测维度",
            yaxis_title="评分 (0-10)",
            yaxis_range=[0, 10],
            hovermode='x unified'
        )

        return fig.to_html()
