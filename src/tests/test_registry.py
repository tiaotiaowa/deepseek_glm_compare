"""测试用例注册表"""

from typing import Dict, List, Optional
from .base_test import BaseTestCategory, TestCase
from .base_registry import BaseTestRegistry


class TestRegistry(BaseTestRegistry):
    """测试用例注册表（标准测试用）"""

    def __init__(self):
        """初始化注册表"""
        super().__init__()
        self.categories: Dict[str, BaseTestCategory] = {}

    def register(self, category: BaseTestCategory):
        """
        注册测试类别（实现基类抽象方法）

        Args:
            category: 测试类别
        """
        self.register_category(category)

    def register_category(self, category: BaseTestCategory):
        """
        注册测试类别

        Args:
            category: 测试类别
        """
        self.categories[category.category_name] = category
        # 同时注册所有测试用例到基类的字典中
        for test_case in category.get_test_cases():
            self._register_test(test_case)

    def get_category(self, category_name: str) -> Optional[BaseTestCategory]:
        """
        获取测试类别

        Args:
            category_name: 类别名称

        Returns:
            BaseTestCategory: 测试类别，如果不存在则返回 None
        """
        return self.categories.get(category_name)

    def get_all_test_cases(self) -> List[TestCase]:
        """
        获取所有测试用例（实现基类抽象方法）

        Returns:
            List[TestCase]: 所有测试用例
        """
        return list(self._tests.values())

    def get_test_cases_by_category(self, category_name: str) -> List[TestCase]:
        """
        按类别获取测试用例

        Args:
            category_name: 类别名称

        Returns:
            List[TestCase]: 该类别的测试用例
        """
        category = self.get_category(category_name)
        if category:
            return category.get_test_cases()
        return []

    def get_test_cases_by_priority(self, priority: str) -> List[TestCase]:
        """
        按优先级获取测试用例

        Args:
            priority: 优先级 ("primary" 或 "secondary")

        Returns:
            List[TestCase]: 符合优先级的测试用例
        """
        all_cases = self.get_all_test_cases()
        return [case for case in all_cases if case.priority == priority]

    def get_categories(self) -> List[str]:
        """
        获取所有类别名称

        Returns:
            List[str]: 类别名称列表
        """
        return list(self.categories.keys())

    def count_test_cases_by_category(self) -> Dict[str, int]:
        """
        按类别统计测试用例数量

        Returns:
            Dict: 类别到测试数量的映射
        """
        return {
            category_name: len(category.get_test_cases())
            for category_name, category in self.categories.items()
        }

    # 保持向后兼容的别名
    def count_test_cases(self) -> Dict[str, int]:
        """
        统计测试用例数量（向后兼容方法）

        Returns:
            Dict: 类别到测试数量的映射
        """
        return self.count_test_cases_by_category()


# 全局注册表实例
registry = TestRegistry()
