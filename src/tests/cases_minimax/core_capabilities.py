"""核心能力测试 (35个测试用例)

包含:
- B1: 逻辑推理能力测试 (12个)
- B2: 代码生成能力测试 (10个)
- B3: 文本理解能力测试 (8个)
- B4: 创意生成能力测试 (5个)
"""

from ..base_test import BaseTestCategory, TestCase
from ..minimax_registry import minimax_registry


class CoreCapabilitiesTests(BaseTestCategory):
    """核心能力测试（35个用例）"""

    def __init__(self):
        super().__init__("core_capabilities")
        self._create_tests()

    def _create_tests(self):
        """创建核心能力测试用例"""

        # ========== B1. 逻辑推理能力测试 (12个) ==========

        self.add_test_case(TestCase(
            name="B1_001_math_logic_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="一个袋子里有红球、蓝球、绿球各5个，至少要取出多少个球才能保证至少有两个同色的球？",
            parameters={"max_tokens": 300, "temperature": 0.0},
            expected_tokens_range=(100, 300),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_002_causal_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="如果下雨了，地会湿。地面湿了，路会滑。路滑了，交通事故会增加。现在下雨了，请推理出最终结果",
            parameters={"max_tokens": 300, "temperature": 0.0},
            expected_tokens_range=(100, 300),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "easy"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_003_analogy_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="医生之于医院，就像老师之于什么？请详细解释你的推理过程",
            parameters={"max_tokens": 300, "temperature": 0.0},
            expected_tokens_range=(100, 300),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "easy"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-003",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_004_logical_fallacy",
            category="core_capabilities",
            priority="primary",
            prompt="小明说吸烟对身体不好，但他自己也吸烟。所以吸烟对身体健康。请指出这段话的逻辑问题",
            parameters={"max_tokens": 400, "temperature": 0.0},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-004",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_005_syllogism",
            category="core_capabilities",
            priority="primary",
            prompt="所有A都是B，所有B都是C，因此所有A都是C。请问这个推理是否有效？请分析",
            parameters={"max_tokens": 400, "temperature": 0.0},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-005",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_006_conditional_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="如果今天下雨，我会带伞。如果我带伞，就不会迟到。如果我迟到，老板会生气。今天下雨了，请推理我会否会迟到？",
            parameters={"max_tokens": 400, "temperature": 0.0},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-006",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_007_inductive_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="观察到天鹅1是白的，天鹅2是白的，天鹅3是白的。请据此进行归纳推理",
            parameters={"max_tokens": 400, "temperature": 0.0},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-007",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_008_proof_by_contradiction",
            category="core_capabilities",
            priority="primary",
            prompt="请用反证法证明：质数是无穷多的",
            parameters={"max_tokens": 500, "temperature": 0.0},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-008",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_009_probability_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="抛硬币3次，至少出现一次正面的概率是多少？请详细计算",
            parameters={"max_tokens": 400, "temperature": 0.0},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-009",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_010_complex_logic",
            category="core_capabilities",
            priority="primary",
            prompt="在一个岛上住着说真话的人和说假话的人。甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。请分析每个人的真实身份",
            parameters={"max_tokens": 600, "temperature": 0.0},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["reasoning_quality", "accuracy"],
            metadata={"type": "logic_reasoning", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.3, "logic": 0.3},
            minimax_id="B1-010",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_011_philosophical_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="自由意志和决定论能否兼容？请从哲学角度分析",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["reasoning_quality", "accuracy", "creativity"],
            metadata={"type": "logic_reasoning", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.30, "logic": 0.35},
            minimax_id="B1-011",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B1_012_decision_reasoning",
            category="core_capabilities",
            priority="primary",
            prompt="公司面临市场萎缩，有三个选择：裁员、转型、降薪。请分析每个选择的利弊并推荐最优决策",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["reasoning_quality", "accuracy", "completeness"],
            metadata={"type": "logic_reasoning", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="逻辑推理能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.35, "logic": 0.30},
            minimax_id="B1-012",
            expected_score_range=(7.0, 9.0)
        ))

        # ========== B2. 代码生成能力测试 (10个) ==========

        self.add_test_case(TestCase(
            name="B2_001_basic_algorithm",
            category="core_capabilities",
            priority="primary",
            prompt="请实现快速排序算法，包含详细的注释和测试用例",
            parameters={"max_tokens": 500, "temperature": 0.0},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["code_correctness", "code_style", "documentation"],
            metadata={"type": "code_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "style": 0.25, "efficiency": 0.25},
            minimax_id="B2-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_002_data_structure",
            category="core_capabilities",
            priority="primary",
            prompt="请实现一个LRU缓存，支持get和put操作",
            parameters={"max_tokens": 500, "temperature": 0.0},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["code_correctness", "code_style", "efficiency"],
            metadata={"type": "code_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "style": 0.25, "efficiency": 0.25},
            minimax_id="B2-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_003_web_development",
            category="core_capabilities",
            priority="primary",
            prompt="请用Python Flask创建一个RESTful API，包含用户注册、登录、查询功能",
            parameters={"max_tokens": 800, "temperature": 0.0},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["code_correctness", "code_style", "security"],
            metadata={"type": "code_generation", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "style": 0.20, "efficiency": 0.20, "documentation": 0.10},
            minimax_id="B2-003",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_004_database_operations",
            category="core_capabilities",
            priority="primary",
            prompt="设计一个电商数据库，包含用户、商品、订单表，并编写相关SQL查询",
            parameters={"max_tokens": 800, "temperature": 0.0},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["code_correctness", "code_style", "database_design"],
            metadata={"type": "code_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "style": 0.25, "efficiency": 0.25},
            minimax_id="B2-004",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_005_frontend_development",
            category="core_capabilities",
            priority="primary",
            prompt="用React实现一个待办事项列表，支持添加、删除、编辑功能",
            parameters={"max_tokens": 800, "temperature": 0.0},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["code_correctness", "code_style", "ui_design"],
            metadata={"type": "code_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "style": 0.25, "efficiency": 0.25},
            minimax_id="B2-005",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_006_machine_learning",
            category="core_capabilities",
            priority="primary",
            prompt="请实现一个简单的神经网络分类器，包含前向传播和反向传播",
            parameters={"max_tokens": 800, "temperature": 0.0},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["code_correctness", "code_style", "math_accuracy"],
            metadata={"type": "code_generation", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "style": 0.25, "efficiency": 0.25},
            minimax_id="B2-006",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_007_system_design",
            category="core_capabilities",
            priority="primary",
            prompt="设计一个高并发的聊天系统架构，包含技术选型和关键实现",
            parameters={"max_tokens": 1000, "temperature": 0.7},
            expected_tokens_range=(700, 1000),
            evaluation_criteria=["architecture_quality", "technical_choice", "feasibility"],
            metadata={"type": "code_generation", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.4, "completeness": 0.35, "logic": 0.25},
            minimax_id="B2-007",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_008_test_code",
            category="core_capabilities",
            priority="secondary",
            prompt="为之前实现的快速排序算法编写完整的单元测试",
            parameters={"max_tokens": 500, "temperature": 0.0},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["code_correctness", "test_coverage", "edge_cases"],
            metadata={"type": "code_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "completeness": 0.30, "style": 0.20},
            minimax_id="B2-008",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_009_code_optimization",
            category="core_capabilities",
            priority="secondary",
            prompt="优化一个时间复杂度为O(n²)的查找算法到O(n log n)",
            parameters={"max_tokens": 600, "temperature": 0.0},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["code_correctness", "optimization_quality", "performance_gain"],
            metadata={"type": "code_generation", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "efficiency": 0.35, "style": 0.15},
            minimax_id="B2-009",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B2_010_code_refactoring",
            category="core_capabilities",
            priority="secondary",
            prompt="将一段冗余的代码重构为更优雅、可维护的版本",
            parameters={"max_tokens": 600, "temperature": 0.0},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["code_correctness", "refactoring_quality", "readability"],
            metadata={"type": "code_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="代码生成能力",
            dimension_weight=0.35,
            test_weight=0.08,
            score_range=(0, 10),
            quality_criteria={"correctness": 0.5, "style": 0.30, "efficiency": 0.20},
            minimax_id="B2-010",
            expected_score_range=(7.0, 9.0)
        ))

        # ========== B3. 文本理解能力测试 (8个) ==========

        self.add_test_case(TestCase(
            name="B3_001_reading_comprehension",
            category="core_capabilities",
            priority="primary",
            prompt="给予一段2000字的学术论文摘要，要求提取核心观点：[论文内容略，实际执行时会有完整内容]",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["understanding_quality", "accuracy", "completeness"],
            metadata={"type": "text_understanding", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.20},
            minimax_id="B3-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B3_002_sentiment_analysis",
            category="core_capabilities",
            priority="primary",
            prompt="分析以下文本的情感倾向：'这个产品让我既兴奋又失望，它的功能很强大，但使用体验却很糟糕'",
            parameters={"max_tokens": 300, "temperature": 0.7},
            expected_tokens_range=(150, 300),
            evaluation_criteria=["understanding_quality", "accuracy", "nuance"],
            metadata={"type": "text_understanding", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="B3-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B3_003_topic_extraction",
            category="core_capabilities",
            priority="primary",
            prompt="从多段新闻报道中提取共同主题：[新闻内容略]",
            parameters={"max_tokens": 400, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["understanding_quality", "accuracy", "abstraction"],
            metadata={"type": "text_understanding", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="B3-003",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B3_004_semantic_analysis",
            category="core_capabilities",
            priority="primary",
            prompt="'言外之意'和'弦外之音'在语境中的含义区别是什么？",
            parameters={"max_tokens": 400, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["understanding_quality", "accuracy", "depth"],
            metadata={"type": "text_understanding", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="B3-004",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B3_005_context_understanding",
            category="core_capabilities",
            priority="primary",
            prompt="'他很会说话'在不同语境中的含义变化是什么？",
            parameters={"max_tokens": 400, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["understanding_quality", "accuracy", "context_sensitivity"],
            metadata={"type": "text_understanding", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="B3-005",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B3_006_metaphor_understanding",
            category="core_capabilities",
            priority="primary",
            prompt="'时间如流水般消逝'这个比喻的含义和作用是什么？",
            parameters={"max_tokens": 300, "temperature": 0.7},
            expected_tokens_range=(150, 300),
            evaluation_criteria=["understanding_quality", "accuracy", "literary_analysis"],
            metadata={"type": "text_understanding", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="B3-006",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B3_007_implicit_info",
            category="core_capabilities",
            priority="primary",
            prompt="从以下看似中性的文本中提取隐含的态度倾向：[文本内容略]",
            parameters={"max_tokens": 400, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["understanding_quality", "accuracy", "depth"],
            metadata={"type": "text_understanding", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="B3-007",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B3_008_critical_reading",
            category="core_capabilities",
            priority="primary",
            prompt="对一篇观点文章进行批判性分析和评价：[文章内容略]",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["understanding_quality", "critical_thinking", "objectivity"],
            metadata={"type": "text_understanding", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="文本理解能力",
            dimension_weight=0.35,
            test_weight=0.13,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.35, "logic": 0.30},
            minimax_id="B3-008",
            expected_score_range=(7.0, 9.0)
        ))

        # ========== B4. 创意生成能力测试 (5个) ==========

        self.add_test_case(TestCase(
            name="B4_001_creative_writing",
            category="core_capabilities",
            priority="primary",
            prompt="以'时空穿越'为主题，创作一个1500字的科幻短篇故事",
            parameters={"max_tokens": 1800, "temperature": 0.9},
            expected_tokens_range=(1200, 1800),
            evaluation_criteria=["creativity", "story_quality", "writing_style"],
            metadata={"type": "creative_generation", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="创意生成能力",
            dimension_weight=0.35,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.5, "completeness": 0.30, "logic": 0.20},
            minimax_id="B4-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B4_002_product_innovation",
            category="core_capabilities",
            priority="primary",
            prompt="为老年人设计一款智能健康监测设备，详细描述功能和创新点",
            parameters={"max_tokens": 800, "temperature": 0.8},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["creativity", "practicality", "user_centricity"],
            metadata={"type": "creative_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="创意生成能力",
            dimension_weight=0.35,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.5, "completeness": 0.30, "logic": 0.20},
            minimax_id="B4-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B4_003_marketing_creativity",
            category="core_capabilities",
            priority="primary",
            prompt="为一个环保公益活动设计一套创意营销方案",
            parameters={"max_tokens": 800, "temperature": 0.8},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["creativity", "feasibility", "impact"],
            metadata={"type": "creative_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="创意生成能力",
            dimension_weight=0.35,
            test_weight=0.20,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.45, "completeness": 0.35, "logic": 0.20},
            minimax_id="B4-003",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B4_004_solution_innovation",
            category="core_capabilities",
            priority="primary",
            prompt="如何用创意方法解决城市交通拥堵问题？",
            parameters={"max_tokens": 800, "temperature": 0.8},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["creativity", "feasibility", "innovation"],
            metadata={"type": "creative_generation", "difficulty": "hard"},
            dimension="core_capabilities",
            sub_dimension="创意生成能力",
            dimension_weight=0.35,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.50, "completeness": 0.30, "logic": 0.20},
            minimax_id="B4-004",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="B4_005_artistic_creation",
            category="core_capabilities",
            priority="primary",
            prompt="创作一首关于'孤独'主题的现代诗",
            parameters={"max_tokens": 400, "temperature": 0.9},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["creativity", "emotional_depth", "literary_quality"],
            metadata={"type": "creative_generation", "difficulty": "medium"},
            dimension="core_capabilities",
            sub_dimension="创意生成能力",
            dimension_weight=0.35,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.50, "completeness": 0.25, "logic": 0.25},
            minimax_id="B4-005",
            expected_score_range=(7.0, 9.0)
        ))

        # 注册到 minimax_registry
        for test_case in self.get_test_cases():
            minimax_registry.register_test(test_case)


# 注册到全局 registry（保持兼容）
from ..test_registry import registry
registry.register_category(CoreCapabilitiesTests())
