"""MiniMax 标准测试用例模块

本模块包含 100 个 MiniMax 标准测试用例，分为四个维度：
- basic_performance: 基础性能测试 (25个)
- core_capabilities: 核心能力测试 (35个)
- practical_scenarios: 实用场景测试 (25个)
- advanced_features: 高级特性测试 (15个)
"""

# 导入所有测试类别（触发注册到 minimax_registry）
from .basic_performance import BasicPerformanceTests
from .core_capabilities import CoreCapabilitiesTests
from .practical_scenarios import PracticalScenariosTests
from .advanced_features import AdvancedFeaturesTests

__all__ = [
    "BasicPerformanceTests",
    "CoreCapabilitiesTests",
    "PracticalScenariosTests",
    "AdvancedFeaturesTests",
]
