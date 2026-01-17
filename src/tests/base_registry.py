"""测试用例注册表基类"""

from abc import ABC, abstractmethod
from typing import List, Dict
from collections import Counter
from .base_test import TestCase


class BaseTestRegistry(ABC):
    """测试用例注册表抽象基类，提供通用功能"""

    def __init__(self):
        """初始化注册表"""
        self._tests: Dict[str, TestCase] = {}

    @abstractmethod
    def register(self, test_case):
        """
        注册测试用例（子类实现）

        Args:
            test_case: 测试用例对象
        """
        pass

    @abstractmethod
    def get_all_test_cases(self) -> List[TestCase]:
        """
        获取所有测试用例（子类实现）

        Returns:
            List[TestCase]: 所有测试用例列表
        """
        pass

    def get_test_by_name(self, name: str) -> TestCase:
        """
        按名称获取测试用例（通用方法）

        Args:
            name: 测试用例名称

        Returns:
            TestCase: 测试用例对象，如果未找到则返回 None
        """
        return self._tests.get(name)

    def count_test_cases(self) -> int:
        """
        统计总测试用例数量（通用方法）

        Returns:
            int: 总测试用例数量
        """
        return len(self._tests)

    def get_statistics_summary(self) -> Dict[str, int]:
        """
        获取统计摘要（通用方法）

        Returns:
            Dict[str, int]: 统计信息
        """
        return {
            "total_tests": len(self._tests),
            "unique_names": len(set(tc.name for tc in self._tests.values()))
        }

    def _register_test(self, test_case: TestCase):
        """
        内部方法：注册测试用例到字典（通用实现）

        Args:
            test_case: 测试用例对象
        """
        self._tests[test_case.name] = test_case
