"""测试用例基类和数据结构"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class TestCase:
    """测试用例数据结构"""

    # ========== 保留原有字段（向后兼容） ==========
    name: str  # 测试用例唯一标识符
    category: str  # 测试类别
    priority: str  # 优先级: "primary" 或 "secondary"
    prompt: str  # 发送给模型的提示词
    parameters: Dict[str, Any] = field(default_factory=dict)  # 模型参数
    expected_tokens_range: Optional[tuple] = None  # 预期 token 范围 (min, max)
    evaluation_criteria: List[str] = field(default_factory=list)  # 评估标准
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    # ========== 新增 MiniMax 标准字段（Optional） ==========
    dimension: Optional[str] = None  # 评测维度
    sub_dimension: Optional[str] = None  # 子维度
    dimension_weight: Optional[float] = None  # 维度权重
    test_weight: Optional[float] = None  # 测试用例权重
    score_range: Optional[tuple] = None  # 评分范围 (0, 10)
    quality_criteria: Optional[Dict[str, float]] = None  # 质量标准权重
    minimax_id: Optional[str] = None  # MiniMax 用例 ID (如 "A1-001")
    expected_score_range: Optional[tuple] = None  # 预期得分范围

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "category": self.category,
            "priority": self.priority,
            "prompt": self.prompt,
            "parameters": self.parameters,
            "expected_tokens_range": self.expected_tokens_range,
            "evaluation_criteria": self.evaluation_criteria,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """从字典创建"""
        return cls(**data)


class BaseTestCategory:
    """测试类别基类"""

    def __init__(self, category_name: str):
        """
        初始化测试类别

        Args:
            category_name: 类别名称
        """
        self.category_name = category_name
        self.test_cases: List[TestCase] = []

    def get_test_cases(self) -> List[TestCase]:
        """
        获取该类别的所有测试用例

        Returns:
            List[TestCase]: 测试用例列表
        """
        return self.test_cases

    def add_test_case(self, test_case: TestCase):
        """
        添加测试用例

        Args:
            test_case: 测试用例
        """
        test_case.category = self.category_name
        self.test_cases.append(test_case)

    def create_test_case(
        self,
        name: str,
        prompt: str,
        priority: str = "primary",
        max_tokens: int = 500,
        temperature: float = 0.7,
        expected_tokens_range: Optional[tuple] = None,
        evaluation_criteria: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TestCase:
        """
        创建测试用例

        Args:
            name: 测试名称
            prompt: 提示词
            priority: 优先级
            max_tokens: 最大 token 数
            temperature: 温度参数
            expected_tokens_range: 预期 token 范围
            evaluation_criteria: 评估标准
            metadata: 元数据

        Returns:
            TestCase: 创建的测试用例
        """
        test_case = TestCase(
            name=name,
            category=self.category_name,
            priority=priority,
            prompt=prompt,
            parameters={
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            expected_tokens_range=expected_tokens_range,
            evaluation_criteria=evaluation_criteria or [],
            metadata=metadata or {}
        )

        self.add_test_case(test_case)
        return test_case
