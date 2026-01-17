"""报告可视化生成器"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
import numpy as np


class ReportVisualizer:
    """报告可视化生成器"""

    def __init__(self):
        """初始化可视化生成器"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False

    def create_ttft_boxplot(
        self,
        summaries: List[Dict[str, Any]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建 TTFT 箱型图

        Args:
            summaries: 类别汇总数据列表
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        # 按类别组织数据
        categories = set(s['category'] for s in summaries)
        models = set(s['model_name'] for s in summaries)

        fig = go.Figure()

        for model in models:
            for category in categories:
                model_data = [s for s in summaries if s['model_name'] == model and s['category'] == category]
                if model_data and model_data[0]['ttft_mean'] > 0:
                    fig.add_trace(go.Box(
                        x=[category],
                        y=[model_data[0]['ttft_mean']],
                        name=model,
                        boxmean='sd'
                    ))

        fig.update_layout(
            title='TTFT (首次响应时间) 对比',
            xaxis_title='测试类别',
            yaxis_title='TTFT (毫秒)',
            barmode='group',
            height=600
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_generation_speed_bar(
        self,
        summaries: List[Dict[str, Any]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建生成速度柱状图

        Args:
            summaries: 类别汇总数据列表
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        categories = sorted(set(s['category'] for s in summaries))
        models = sorted(set(s['model_name'] for s in summaries))

        fig = go.Figure()

        for model in models:
            speeds = []
            for category in categories:
                model_data = [s for s in summaries if s['model_name'] == model and s['category'] == category]
                if model_data:
                    speeds.append(model_data[0]['speed_mean'])
                else:
                    speeds.append(0)

            fig.add_trace(go.Bar(
                x=categories,
                y=speeds,
                name=model,
                error_y=dict(
                    type='data',
                    array=[s['speed_std'] for s in summaries if s['model_name'] == model and s['category'] in categories][:len(categories)]
                ) if any(s['model_name'] == model for s in summaries) else None
            ))

        fig.update_layout(
            title='生成速度对比 (tokens/秒)',
            xaxis_title='测试类别',
            yaxis_title='生成速度',
            barmode='group',
            height=600
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_quality_radar(
        self,
        quality_scores: Dict[str, Dict[str, float]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建质量雷达图

        Args:
            quality_scores: 质量分数字典 {model: {criterion: score}}
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        criteria = list(next(iter(quality_scores.values())).keys())

        fig = go.Figure()

        for model, scores in quality_scores.items():
            fig.add_trace(go.Scatterpolar(
                r=list(scores.values()),
                theta=criteria,
                fill='toself',
                name=model
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            title='质量维度对比',
            height=600
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_latency_heatmap(
        self,
        summaries: List[Dict[str, Any]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建延迟热力图

        Args:
            summaries: 类别汇总数据列表
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        categories = sorted(set(s['category'] for s in summaries))
        models = sorted(set(s['model_name'] for s in summaries))

        # 创建矩阵
        z = []
        for model in models:
            row = []
            for category in categories:
                model_data = [s for s in summaries if s['model_name'] == model and s['category'] == category]
                if model_data:
                    row.append(model_data[0]['total_time_mean'])
                else:
                    row.append(0)
            z.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=categories,
            y=models,
            colorscale='Viridis'
        ))

        fig.update_layout(
            title='总响应时间热力图 (毫秒)',
            xaxis_title='测试类别',
            yaxis_title='模型',
            height=500
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_performance_scatter(
        self,
        summaries: List[Dict[str, Any]],
        quality_scores: Dict[str, float],
        output_path: str = None
    ) -> go.Figure:
        """
        创建性能-质量散点图

        Args:
            summaries: 类别汇总数据列表
            quality_scores: 质量分数 {model: score}
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        fig = go.Figure()

        for model in set(s['model_name'] for s in summaries):
            model_summaries = [s for s in summaries if s['model_name'] == model]
            x = [s['speed_mean'] for s in model_summaries]
            y = [quality_scores.get(model, 0)] * len(x)

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                name=model,
                marker=dict(size=10)
            ))

        fig.update_layout(
            title='性能 vs 质量权衡',
            xaxis_title='生成速度 (tokens/秒)',
            yaxis_title='质量分数',
            height=600
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    # ========== MiniMax 标准图表 ==========

    def create_dimension_radar(
        self,
        dimension_scores: Dict[str, Dict[str, float]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建四维度雷达图 (MiniMax 标准)

        Args:
            dimension_scores: 维度分数字典 {model: {dimension: score}}
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        dimensions = ["基础性能", "核心能力", "实用场景", "高级特性"]

        fig = go.Figure()

        for model, scores in dimension_scores.items():
            # 获取各维度分数
            model_scores = [
                scores.get("basic_performance", 0),
                scores.get("core_capabilities", 0),
                scores.get("practical_scenarios", 0),
                scores.get("advanced_features", 0)
            ]

            fig.add_trace(go.Scatterpolar(
                r=model_scores,
                theta=dimensions,
                fill='toself',
                name=model,
                opacity=0.7
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickvals=[0, 2, 4, 6, 8, 10]
                )),
            showlegend=True,
            title="四维度能力对比雷达图 (MiniMax 标准)",
            height=600
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_capability_heatmap(
        self,
        sub_dimension_scores: Dict[str, Dict[str, float]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建能力热力图 (MiniMax 标准)

        Args:
            sub_dimension_scores: 子维度分数字典 {model: {sub_dimension: score}}
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        # 12 个子维度
        sub_dimensions = [
            "实时响应", "吞吐量", "稳定性",
            "逻辑推理", "代码生成", "文本理解", "创意生成",
            "专业应用", "中文处理", "长文本", "结构化输出",
            "复杂推理", "指令遵循", "多模态", "创新思维"
        ]

        models = list(sub_dimension_scores.keys())

        # 构建评分矩阵
        z_values = []
        for model in models:
            row = []
            for sub_dim in sub_dimensions:
                row.append(sub_dimension_scores[model].get(sub_dim, 0))
            z_values.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=sub_dimensions,
            y=models,
            colorscale='Viridis',
            colorbar=dict(title="评分 (0-10)"),
            text=z_values,
            texttemplate="%{text:.1f}",
            textfont={"size": 9},
            zmin=0,
            zmax=10
        ))

        fig.update_layout(
            title="模型能力热力图 (MiniMax 标准)",
            xaxis_title="能力子维度",
            yaxis_title="模型",
            height=500,
            xaxis=dict(tickangle=-45)
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_score_distribution(
        self,
        quality_stats: Dict[str, Dict[str, int]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建评分等级分布图 (MiniMax 标准)

        Args:
            quality_stats: 质量统计字典 {model: {grade: count}}
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        grades = ["优秀", "良好", "合格", "不合格", "严重缺陷"]
        grade_ranges = ["9.0-10.0", "7.5-8.9", "6.0-7.4", "3.0-5.9", "0-2.9"]

        fig = go.Figure()

        for model, stats in quality_stats.items():
            counts = [
                stats.get("excellent_count", 0),
                stats.get("good_count", 0),
                stats.get("qualified_count", 0),
                stats.get("unqualified_count", 0),
                stats.get("critical_count", 0)
            ]

            # 根据模型选择颜色
            color = 'rgb(99, 110, 250)' if 'deepseek' in model.lower() else 'rgb(239, 85, 59)'

            fig.add_trace(go.Bar(
                x=grades,
                y=counts,
                name=model,
                marker_color=color,
                text=counts,
                textposition='outside'
            ))

        fig.update_layout(
            title="评分等级分布对比 (MiniMax 标准)",
            xaxis_title="评分等级",
            yaxis_title="维度数量",
            barmode='group',
            showlegend=True,
            height=600,
            annotations=[
                dict(x=0.5, y=-0.15, showarrow=False,
                     text=f"范围: {grade_ranges[0]}",
                     xref="paper", yref="paper"),
                dict(x=0.5, y=-0.2, showarrow=False,
                     text="|".join(grade_ranges),
                     xref="paper", yref="paper", font=dict(size=8))
            ]
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_confidence_interval_chart(
        self,
        statistics: Dict[str, Dict[str, float]],
        output_path: str = None
    ) -> go.Figure:
        """
        创建置信区间图 (MiniMax 标准)

        Args:
            statistics: 统计数据字典 {model: {mean, ci_lower, ci_upper}}
            output_path: 输出路径（可选）

        Returns:
            Figure: Plotly 图表对象
        """
        models = list(statistics.keys())

        mean_scores = [statistics[m]["mean_score"] for m in models]
        ci_lower = [statistics[m].get("ci_lower", m - 1) for m in models]
        ci_upper = [statistics[m].get("ci_upper", m + 1) for m in models]

        # 计算误差范围
        error_plus = [upper - mean for mean, upper in zip(mean_scores, ci_upper)]
        error_minus = [mean - lower for mean, lower in zip(mean_scores, ci_lower)]

        # 根据模型选择颜色
        colors = []
        for model in models:
            if 'deepseek' in model.lower():
                colors.append('rgb(99, 110, 250)')
            elif 'glm' in model.lower():
                colors.append('rgb(239, 85, 59)')
            else:
                colors.append('rgb(75, 192, 192)')

        fig = go.Figure()

        for i, model in enumerate(models):
            fig.add_trace(go.Scatter(
                x=[model],
                y=[mean_scores[i]],
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=[error_plus[i]],
                    arrayminus=[error_minus[i]]
                ),
                mode='markers',
                name=model,
                marker=dict(size=15, color=colors[i]),
                text=[f"{mean_scores[i]:.2f}"],
                textposition='top center'
            ))

        fig.update_layout(
            title="综合得分 95% 置信区间 (MiniMax 标准)",
            xaxis_title="模型",
            yaxis_title="综合得分",
            yaxis_range=[0, 10],
            showlegend=True,
            height=600
        )

        if output_path:
            fig.write_html(output_path)

        return fig

    def create_static_chart(self, fig: go.Figure, output_path: str, format: str = 'png'):
        """
        创建静态图表

        Args:
            fig: Plotly 图表
            output_path: 输出路径
            format: 格式 ('png', 'svg', 'pdf')
        """
        if format == 'png':
            fig.write_image(output_path, format='png', width=1200, height=600, scale=2)
        elif format == 'svg':
            fig.write_image(output_path, format='svg')
        elif format == 'pdf':
            fig.write_image(output_path, format='pdf')
