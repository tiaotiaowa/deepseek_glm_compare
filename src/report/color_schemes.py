"""报告颜色主题配置

提供统一的颜色方案管理，支持多种主题和无障碍友好配色。
"""

class ColorSchemes:
    """颜色方案管理器

    提供模型、评分等级、热力图等的配色方案。
    所有颜色使用十六进制格式 (RRGGBB)。
    """

    # DeepSeek 配色方案（专业蓝色系）
    DEEPSEEK = {
        "primary": "#6366F1",      # Indigo 500
        "secondary": "#4F46E5",    # Indigo 600
        "dark": "#4338CA",         # Indigo 700
        "light": "#818CF8",        # Indigo 400
        "rgba": "rgba(99, 102, 241, 0.3)",
        "rgba_light": "rgba(99, 102, 241, 0.1)",
        "rgba_medium": "rgba(99, 102, 241, 0.2)"
    }

    # GLM 配色方案（活力橙红系）
    GLM = {
        "primary": "#F97316",      # Orange 500
        "secondary": "#EA580C",    # Orange 600
        "dark": "#C2410C",         # Orange 700
        "light": "#FB923C",        # Orange 400
        "rgba": "rgba(249, 115, 22, 0.3)",
        "rgba_light": "rgba(249, 115, 22, 0.1)",
        "rgba_medium": "rgba(249, 115, 22, 0.2)"
    }

    # MiniMax Judge 配色方案（紫罗兰系）
    MINIMAX = {
        "primary": "#8B5CF6",      # Violet 500
        "secondary": "#7C3AED",    # Violet 600
        "dark": "#6D28D9",         # Violet 700
        "light": "#A78BFA",        # Violet 400
        "rgba": "rgba(139, 92, 246, 0.3)",
        "rgba_light": "rgba(139, 92, 246, 0.1)",
        "rgba_medium": "rgba(139, 92, 246, 0.2)"
    }

    # 评分等级配色方案
    GRADE_COLORS = {
        "excellent": "#10B981",    # 翠绿 (9-10分)
        "good": "#34D399",         # 浅绿 (7.5-8.9分)
        "qualified": "#FBBF24",    # 琥珀 (6-7.4分)
        "unqualified": "#F87171",  # 浅红 (3-5.9分)
        "critical": "#EF4444"      # 深红 (0-2.9分)
    }

    # 评分等级详细信息
    GRADE_INFO = {
        "excellent": {"range": (9.0, 10.0), "label": "优秀", "color": "#10B981"},
        "good": {"range": (7.5, 8.9), "label": "良好", "color": "#34D399"},
        "qualified": {"range": (6.0, 7.4), "label": "合格", "color": "#FBBF24"},
        "unqualified": {"range": (3.0, 5.9), "label": "不合格", "color": "#F87171"},
        "critical": {"range": (0, 2.9), "label": "严重缺陷", "color": "#EF4444"}
    }

    # 热力图配色方案
    HEATMAP_PALETTES = {
        "viridis": "Viridis",      # 绿-黄渐变（默认，色盲友好）
        "plasma": "Plasma",        # 紫-黄渐变
        "inferno": "Inferno",      # 黑-红-黄渐变
        "magma": "Magma",          # 黑-紫-粉渐变
        "cividis": "Cividis",      # 色盲友好
        "blues": "Blues",          # 蓝色渐变
        "greens": "Greens"         # 绿色渐变
    }

    # 无障碍友好配色（Colorbrewer 方案）
    ACCESSIBILITY = {
        # 色盲友好配色（Wong palette）
        "colorblind_friendly": [
            "#0072B2",  # 蓝
            "#D55E00",  # 橙
            "#009E73",  # 绿
            "#CC79A7",  # 粉
            "#F0E442",  # 黄
            "#56B4E9"   # 浅蓝
        ],
        # 高对比度配色
        "high_contrast": {
            "background": "#FFFFFF",
            "text": "#000000",
            "border": "#333333",
            "grid": "#E5E5E5"
        },
        # 灰度方案（可打印）
        "grayscale": [
            "#000000",  # 黑
            "#333333",  # 深灰
            "#666666",  # 中灰
            "#999999",  # 浅灰
            "#CCCCCC",  # 极浅灰
            "#FFFFFF"   # 白
        ]
    }

    # 主题配色方案
    THEMES = {
        "default": {
            "background": "#FFFFFF",
            "text": "#1F2937",
            "border": "#E5E7EB",
            "grid": "#F3F4F6"
        },
        "dark": {
            "background": "#1F2937",
            "text": "#F9FAFB",
            "border": "#374151",
            "grid": "#374151"
        },
        "professional": {
            "background": "#FAFAFA",
            "text": "#111827",
            "border": "#D1D5DB",
            "grid": "#E5E7EB"
        }
    }

    @staticmethod
    def get_model_colors(model_name: str) -> dict:
        """获取模型配色方案

        Args:
            model_name: 模型名称 ("deepseek", "glm", "minimax")

        Returns:
            dict: 包含 primary, secondary, dark, light, rgba 等颜色的字典
        """
        model_colors = {
            "deepseek": ColorSchemes.DEEPSEEK,
            "glm": ColorSchemes.GLM,
            "minimax": ColorSchemes.MINIMAX
        }
        return model_colors.get(model_name.lower(), ColorSchemes.DEEPSEEK)

    @staticmethod
    def get_grade_color(score: float) -> str:
        """根据分数获取颜色

        Args:
            score: 评分 (0-10)

        Returns:
            str: 十六进制颜色代码
        """
        if score >= 9.0:
            return ColorSchemes.GRADE_COLORS["excellent"]
        elif score >= 7.5:
            return ColorSchemes.GRADE_COLORS["good"]
        elif score >= 6.0:
            return ColorSchemes.GRADE_COLORS["qualified"]
        elif score >= 3.0:
            return ColorSchemes.GRADE_COLORS["unqualified"]
        else:
            return ColorSchemes.GRADE_COLORS["critical"]

    @staticmethod
    def get_grade_info(score: float) -> dict:
        """根据分数获取评分等级完整信息

        Args:
            score: 评分 (0-10)

        Returns:
            dict: 包含 range, label, color 的字典
        """
        if score >= 9.0:
            return ColorSchemes.GRADE_INFO["excellent"]
        elif score >= 7.5:
            return ColorSchemes.GRADE_INFO["good"]
        elif score >= 6.0:
            return ColorSchemes.GRADE_INFO["qualified"]
        elif score >= 3.0:
            return ColorSchemes.GRADE_INFO["unqualified"]
        else:
            return ColorSchemes.GRADE_INFO["critical"]

    @staticmethod
    def get_heatmap_palette(name: str = "viridis") -> str:
        """获取热力图配色方案

        Args:
            name: 配色方案名称

        Returns:
            str: Plotly 支持的配色方案名称
        """
        return ColorSchemes.HEATMAP_PALETTES.get(name.lower(), "Viridis")

    @staticmethod
    def get_theme(theme_name: str = "default") -> dict:
        """获取主题配色

        Args:
            theme_name: 主题名称 ("default", "dark", "professional")

        Returns:
            dict: 包含 background, text, border, grid 的字典
        """
        return ColorSchemes.THEMES.get(theme_name.lower(), ColorSchemes.THEMES["default"])

    @staticmethod
    def get_colorblind_friendly_colors() -> list:
        """获取色盲友好配色列表

        Returns:
            list: 十六进制颜色代码列表
        """
        return ColorSchemes.ACCESSIBILITY["colorblind_friendly"]

    @staticmethod
    def get_contrast_colors() -> dict:
        """获取高对比度配色

        Returns:
            dict: 包含 background, text, border, grid 的字典
        """
        return ColorSchemes.ACCESSIBILITY["high_contrast"]

    @staticmethod
    def get_grayscale_colors() -> list:
        """获取灰度配色列表

        Returns:
            list: 从黑到白的十六进制颜色代码列表
        """
        return ColorSchemes.ACCESSIBILITY["grayscale"]


# 便捷函数
def get_model_color(model_name: str, shade: str = "primary") -> str:
    """获取模型的指定颜色

    Args:
        model_name: 模型名称
        shade: 颜色深浅 ("primary", "secondary", "dark", "light", "rgba")

    Returns:
        str: 十六进制或 rgba 颜色代码
    """
    colors = ColorSchemes.get_model_colors(model_name)
    return colors.get(shade, colors["primary"])


def get_score_color(score: float) -> str:
    """根据分数获取对应的颜色

    Args:
        score: 评分 (0-10)

    Returns:
        str: 十六进制颜色代码
    """
    return ColorSchemes.get_grade_color(score)


def get_theme_colors(theme_name: str = "default") -> dict:
    """获取主题配色

    Args:
        theme_name: 主题名称

    Returns:
        dict: 主题配色字典
    """
    return ColorSchemes.get_theme(theme_name)


# 预定义的颜色组合
COLOR_COMBINATIONS = {
    "deepseek_vs_glm": {
        "model_a": ColorSchemes.DEEPSEEK,
        "model_b": ColorSchemes.GLM,
        "judge": ColorSchemes.MINIMAX
    },
    "grades": ColorSchemes.GRADE_COLORS,
    "heatmap_default": ColorSchemes.HEATMAP_PALETTES["viridis"],
    "colorblind": ColorSchemes.ACCESSIBILITY["colorblind_friendly"]
}
