"""报告格式化器 - 提供共享的格式化逻辑

这个模块提取了三个报告生成器(generator.py, markdown_generator.py, minimax_generator.py)
中的共同格式化逻辑，包括：
- 分数格式化（突出获胜者）
- 等级判断
- 表格格式化
- 进度条生成
- 图表样式管理

使用示例:
    from src.report.formatters import ScoreFormatter, GradeFormatter, TableFormatter

    # 格式化获胜分数
    scores = [85.5, 92.3, 78.9]
    formatted = ScoreFormatter.format_winning_score(92.3, scores)

    # 判断等级
    grade = GradeFormatter.get_grade(8.5, is_10_scale=True)  # 返回 "良好"

    # 创建表格
    table = TableFormatter.create_comparison_table(
        row_labels=["TTFT", "Speed"],
        column_models=["DeepSeek", "GLM"],
        data={"TTFT": {"DeepSeek": 150, "GLM": 180}}
    )
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass


# =============================================================================
# 分数格式化器
# =============================================================================

class ScoreFormatter:
    """分数格式化器 - 统一的分数处理逻辑

    提供分数比较、百分比计算、获胜者突出显示等功能
    """

    @staticmethod
    def format_winning_score(
        value: float,
        values: List[float],
        is_lower_better: bool = False,
        add_trophy: bool = True,
        use_bold: bool = True
    ) -> str:
        """
        为获胜分数添加格式化

        Args:
            value: 当前要格式化的值
            values: 所有用于比较的值
            is_lower_better: True 表示越小越好（TTFT、时间）
                           False 表示越大越好（速度、分数）
            add_trophy: 是否添加 🏆 emoji（默认 True）
            use_bold: 是否使用粗体（默认 True）

        Returns:
            格式化字符串（粗体+🏆表示获胜）

        示例:
            >>> ScoreFormatter.format_winning_score(92.3, [85.5, 92.3, 78.9])
            '**92.30** 🏆'
            >>> ScoreFormatter.format_winning_score(150, [150, 180, 200], is_lower_better=True)
            '**150.00** 🏆'
        """
        if not values:
            return f"{value:.2f}"

        is_winner = (value == min(values) if is_lower_better else value == max(values))

        if is_winner:
            trophy = " 🏆" if add_trophy else ""
            formatted = f"**{value:.2f}**{trophy}" if use_bold else f"{value:.2f}{trophy}"
        else:
            formatted = f"{value:.2f}"

        return formatted

    @staticmethod
    def format_winning_model(model: str, is_winner: bool) -> str:
        """
        使用格式化突出获胜模型

        Args:
            model: 模型名称
            is_winner: 是否为获胜者

        Returns:
            格式化的模型名称

        示例:
            >>> ScoreFormatter.format_winning_model("DeepSeek", True)
            '**DeepSeek**'
            >>> ScoreFormatter.format_winning_model("GLM", False)
            'GLM'
        """
        if is_winner:
            return f"**{model}**"  # Markdown 粗体
        return model

    @staticmethod
    def calculate_percentage_diff(value1: float, value2: float) -> float:
        """
        计算两个值的百分比差异

        Args:
            value1: 第一个值
            value2: 第二个值（作为基准）

        Returns:
            百分比差异

        示例:
            >>> ScoreFormatter.calculate_percentage_diff(110, 100)
            10.0
            >>> ScoreFormatter.calculate_percentage_diff(90, 100)
            10.0
        """
        if value2 == 0:
            return 0.0
        return abs(value1 - value2) / value2 * 100

    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """
        格式化百分比

        Args:
            value: 百分比值（0-100）
            decimals: 小数位数

        Returns:
            格式化的百分比字符串

        示例:
            >>> ScoreFormatter.format_percentage(95.678)
            '95.7%'
        """
        return f"{value:.{decimals}f}%"


# =============================================================================
# 等级格式化器
# =============================================================================

class GradeFormatter:
    """等级格式化器 - 统一的等级判断逻辑

    支持10分制和5分制的等级判断
    """

    # 10分制等级阈值
    GRADE_THRESHOLDS_10 = {
        "优秀": 9.0,
        "良好": 7.5,
        "合格": 6.0,
        "不合格": 3.0,
        "严重缺陷": 0.0
    }

    # 5分制等级阈值
    GRADE_THRESHOLDS_5 = {
        "优秀": 4.5,
        "良好": 3.75,
        "合格": 3.0,
        "不合格": 1.5,
        "严重缺陷": 0.0
    }

    @staticmethod
    def get_grade(score: float, is_10_scale: bool = True) -> str:
        """
        根据分数返回等级

        Args:
            score: 分数 (0-10 或 0-5)
            is_10_scale: 是否为10分制（默认True）

        Returns:
            等级字符串，如 "优秀"、"良好"、"合格"等

        示例:
            >>> GradeFormatter.get_grade(9.2)
            '优秀'
            >>> GradeFormatter.get_grade(6.5)
            '合格'
            >>> GradeFormatter.get_grade(4.8, is_10_scale=False)
            '优秀'
        """
        thresholds = GradeFormatter.GRADE_THRESHOLDS_10 if is_10_scale else GradeFormatter.GRADE_THRESHOLDS_5

        if score >= thresholds["优秀"]:
            return "优秀"
        elif score >= thresholds["良好"]:
            return "良好"
        elif score >= thresholds["合格"]:
            return "合格"
        elif score >= thresholds["不合格"]:
            return "不合格"
        else:
            return "严重缺陷"

    @staticmethod
    def get_grade_emoji(grade: str) -> str:
        """
        获取等级对应的emoji

        Args:
            grade: 等级字符串

        Returns:
            emoji字符串

        示例:
            >>> GradeFormatter.get_grade_emoji("优秀")
            '🟢'
            >>> GradeFormatter.get_grade_emoji("合格")
            '🟡'
        """
        emoji_map = {
            "优秀": "🟢",
            "良好": "🟢",
            "合格": "🟡",
            "不合格": "🔴",
            "严重缺陷": "🔴"
        }
        return emoji_map.get(grade, "⚪")

    @staticmethod
    def format_grade_with_emoji(score: float, is_10_scale: bool = True) -> str:
        """
        返回带emoji的等级

        Args:
            score: 分数
            is_10_scale: 是否为10分制

        Returns:
            带emoji的等级字符串

        示例:
            >>> GradeFormatter.format_grade_with_emoji(9.2)
            '🟢 优秀'
        """
        grade = GradeFormatter.get_grade(score, is_10_scale)
        emoji = GradeFormatter.get_grade_emoji(grade)
        return f"{emoji} {grade}"

    @staticmethod
    def get_score_color(score: float, is_10_scale: bool = True) -> str:
        """
        根据分数获取颜色代码

        Args:
            score: 分数
            is_10_scale: 是否为10分制

        Returns:
            颜色代码（十六进制）
        """
        grade = GradeFormatter.get_grade(score, is_10_scale)
        color_map = {
            "优秀": "#10B981",      # 绿色
            "良好": "#3B82F6",      # 蓝色
            "合格": "#F59E0B",      # 黄色
            "不合格": "#EF4444",    # 红色
            "严重缺陷": "#DC2626"   # 深红色
        }
        return color_map.get(grade, "#6B7280")


# =============================================================================
# 表格格式化器
# =============================================================================

class TableFormatter:
    """表格格式化器 - Markdown表格生成

    提供统一的Markdown表格生成接口
    """

    @staticmethod
    def create_table_header(headers: List[str]) -> str:
        """
        创建Markdown表格头部

        Args:
            headers: 列标题列表

        Returns:
            Markdown表格头部字符串

        示例:
            >>> TableFormatter.create_table_header(["模型", "分数", "等级"])
            '| 模型 | 分数 | 等级 |\\n|---------|---------|------|\\n'
        """
        separator = "|" + "|".join(["---------"] * len(headers)) + "|"
        header = "| " + " | ".join(headers) + " |\n"
        header += separator + "\n"
        return header

    @staticmethod
    def create_table_row(cells: List[Any]) -> str:
        """
        创建Markdown表格行

        Args:
            cells: 单元格内容列表

        Returns:
            Markdown表格行字符串

        示例:
            >>> TableFormatter.create_table_row(["DeepSeek", "92.3", "优秀"])
            '| DeepSeek | 92.3 | 优秀 |\\n'
        """
        return "| " + " | ".join(str(cell) for cell in cells) + " |\n"

    @staticmethod
    def create_comparison_table(
        row_labels: List[str],
        column_models: List[str],
        data: Dict[str, Dict[str, float]],
        format_fn: Optional[Callable] = None,
        is_lower_better: Dict[str, bool] = None
    ) -> str:
        """
        创建对比表格

        Args:
            row_labels: 行标签列表
            column_models: 列模型列表
            data: 数据字典 {row_label: {model: value}}
            format_fn: 可选的格式化函数
            is_lower_better: 每行是否越小越好 {row_label: bool}

        Returns:
            Markdown表格字符串

        示例:
            >>> data = {
            ...     "TTFT": {"DeepSeek": 150, "GLM": 180},
            ...     "Speed": {"DeepSeek": 85, "GLM": 78}
            ... }
            >>> table = TableFormatter.create_comparison_table(
            ...     ["TTFT", "Speed"],
            ...     ["DeepSeek", "GLM"],
            ...     data,
            ...     is_lower_better={"TTFT": True, "Speed": False}
            ... )
        """
        md = TableFormatter.create_table_header(["指标"] + column_models)

        if is_lower_better is None:
            is_lower_better = {}

        for row_label in row_labels:
            row = [row_label]

            # 收集所有值用于比较
            all_values = [data.get(row_label, {}).get(m, 0) for m in column_models]

            for model in column_models:
                value = data.get(row_label, {}).get(model, 0)

                if format_fn:
                    lower_better = is_lower_better.get(row_label, False)
                    formatted = format_fn(value, all_values, is_lower_better=lower_better)
                else:
                    formatted = f"{value:.2f}"

                row.append(formatted)

            md += TableFormatter.create_table_row(row)

        return md


# =============================================================================
# 进度条格式化器
# =============================================================================

class ProgressFormatter:
    """进度条格式化器 - 文本进度条和ASCII图表生成"""

    @staticmethod
    def create_progress_bar(
        value: float,
        max_value: float = 10.0,
        width: int = 20,
        filled_char: str = "█",
        empty_char: str = "░"
    ) -> str:
        """
        创建文本进度条

        Args:
            value: 当前值
            max_value: 最大值
            width: 进度条宽度（字符数）
            filled_char: 已填充字符
            empty_char: 空字符

        Returns:
            进度条字符串

        示例:
            >>> ProgressFormatter.create_progress_bar(7.5, 10.0, 20)
            '███████████████░░░░'
        """
        if max_value == 0:
            percentage = 0
        else:
            percentage = min(1.0, max(0.0, value / max_value))

        filled_length = int(percentage * width)
        bar = filled_char * filled_length + empty_char * (width - filled_length)
        return bar

    @staticmethod
    def create_ascii_bar_chart(
        values: Dict[str, float],
        title: str = "",
        bar_width: int = 30,
        show_values: bool = True
    ) -> str:
        """
        创建ASCII柱状图

        Args:
            values: 标签到值的映射
            title: 图表标题
            bar_width: 柱子宽度
            show_values: 是否显示数值

        Returns:
            ASCII图表字符串

        示例:
            >>> chart = ProgressFormatter.create_ascii_bar_chart(
            ...     {"DeepSeek": 92.3, "GLM": 85.6},
            ...     title="模型对比"
            ... )
        """
        if not values:
            return ""

        lines = []
        if title:
            lines.append(f"\n### {title}\n")

        max_val = max(values.values())
        if max_val == 0:
            max_val = 1

        lines.append("```")

        # 数据条
        for label, value in values.items():
            bar_length = int(value / max_val * bar_width)

            # 根据密度选择字符
            if value >= max_val * 0.8:
                bar_char = "█"
            elif value >= max_val * 0.6:
                bar_char = "▓"
            elif value >= max_val * 0.4:
                bar_char = "▒"
            else:
                bar_char = "░"

            bar = bar_char * bar_length
            value_str = f"{value:.2f}" if show_values else ""
            lines.append(f"{'':>12} │{bar}│ {label}: {value_str}")

        lines.append("```")
        return "\n".join(lines)


# =============================================================================
# 维度翻译器
# =============================================================================

class DimensionTranslator:
    """维度名称翻译器 - 提供中英文维度名称映射"""

    DIMENSIONS_CN = {
        # 主要测试类别
        "qa_simple": "简单问答",
        "code_generation": "代码生成",
        "reasoning_complex": "复杂推理",
        "generation_long": "长文本生成",
        "summarization": "文本摘要",
        "translation": "翻译任务",
        "math_reasoning": "数学推理",
        "creative_writing": "创意写作",
        "factual_accuracy": "事实准确性",
        "multi_turn": "多轮对话",

        # MiniMax评测维度
        "basic_performance": "基础性能",
        "core_capabilities": "核心能力",
        "practical_scenarios": "实用场景",
        "advanced_features": "高级特性",

        # MiniMax子维度
        "real_time": "实时响应",
        "throughput": "吞吐量",
        "stability": "稳定性",
        "reasoning": "逻辑推理",
        "code": "代码生成",
        "understanding": "文本理解",
        "creativity": "创意生成",
        "professional": "专业应用",
        "chinese": "中文处理",
        "long_text": "长文本",
        "structured": "结构化输出",
        "innovation": "创新思维"
    }

    @staticmethod
    def translate(dim_name: str) -> str:
        """
        翻译维度名称为中文

        Args:
            dim_name: 英文维度名称

        Returns:
            中文维度名称

        示例:
            >>> DimensionTranslator.translate("basic_performance")
            '基础性能'
            >>> DimensionTranslator.translate("unknown")
            'unknown'
        """
        return DimensionTranslator.DIMENSIONS_CN.get(dim_name, dim_name)

    @staticmethod
    def get_all_dimensions() -> Dict[str, str]:
        """获取所有维度映射"""
        return DimensionTranslator.DIMENSIONS_CN.copy()


# =============================================================================
# 辅助函数
# =============================================================================

def format_metric_value(
    value: float,
    unit: str = "",
    decimals: int = 2
) -> str:
    """
    格式化指标值

    Args:
        value: 数值
        unit: 单位
        decimals: 小数位数

    Returns:
        格式化的字符串

    示例:
        >>> format_metric_value(150.567, "ms", 1)
        '150.6 ms'
    """
    formatted = f"{value:.{decimals}f}"
    if unit:
        formatted += f" {unit}"
    return formatted


def format_confidence_interval(
    mean: float,
    std: float,
    n: int,
    confidence: float = 0.95
) -> str:
    """
    格式化置信区间

    Args:
        mean: 均值
        std: 标准差
        n: 样本数
        confidence: 置信水平

    Returns:
        格式化的置信区间字符串
    """
    import math

    if n <= 1:
        return f"{mean:.2f}"

    # 简化的置信区间计算（实际应使用t分布）
    margin = 1.96 * std / math.sqrt(n)  # 95%置信区间
    lower = mean - margin
    upper = mean + margin

    return f"{mean:.2f} [{lower:.2f}, {upper:.2f}]"
