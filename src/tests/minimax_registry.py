"""MiniMax 标准测试用例注册表"""

from typing import List, Dict, Optional
from collections import Counter
from .base_test import TestCase
from .base_registry import BaseTestRegistry


class MiniMaxTestRegistry(BaseTestRegistry):
    """MiniMax 标准测试注册表"""

    def __init__(self):
        super().__init__()

    def register(self, test_case: TestCase):
        """
        注册测试用例（实现基类抽象方法）

        Args:
            test_case: 测试用例对象
        """
        self.register_test(test_case)

    def register_test(self, test_case: TestCase):
        """
        注册测试用例

        Args:
            test_case: 测试用例对象
        """
        self._register_test(test_case)

    def get_all_test_cases(self) -> List[TestCase]:
        """
        获取所有测试用例（实现基类抽象方法）

        Returns:
            List[TestCase]: 所有测试用例列表
        """
        return list(self._tests.values())

    def get_tests_by_dimension(self, dimension: str) -> List[TestCase]:
        """
        按维度获取测试用例

        Args:
            dimension: 维度名称

        Returns:
            List[TestCase]: 该维度的所有测试用例
        """
        return [tc for tc in self._tests.values() if tc.dimension == dimension]

    def get_test_by_id(self, minimax_id: str) -> Optional[TestCase]:
        """
        按 MiniMax ID 获取测试用例

        Args:
            minimax_id: MiniMax 用例 ID (如 "A1-001")

        Returns:
            Optional[TestCase]: 测试用例对象，如果未找到则返回 None
        """
        return next(
            (tc for tc in self._tests.values() if tc.minimax_id == minimax_id),
            None
        )

    def get_dimension_summary(self) -> Dict[str, int]:
        """
        获取各维度的测试用例数量统计

        Returns:
            Dict[str, int]: 维度名称到测试数量的映射
        """
        dimension_counts = Counter(tc.dimension for tc in self._tests.values())
        return dict(dimension_counts)

    def get_subdimension_summary(self, dimension: str = None) -> Dict[str, int]:
        """
        获取子维度的测试用例数量统计

        Args:
            dimension: 可选，指定维度名称，则只统计该维度的子维度

        Returns:
            Dict[str, int]: 子维度名称到测试数量的映射
        """
        if dimension:
            test_cases = [tc for tc in self._tests.values() if tc.dimension == dimension]
        else:
            test_cases = list(self._tests.values())

        subdimension_counts = Counter(
            tc.sub_dimension for tc in test_cases if tc.sub_dimension
        )
        return dict(subdimension_counts)


# 全局注册表实例
minimax_registry = MiniMaxTestRegistry()
