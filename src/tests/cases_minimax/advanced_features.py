"""高级特性测试 (15个测试用例)

包含:
- D1: 复杂推理链测试 (6个)
- D2: 指令遵循能力测试 (4个)
- D3: 多模态理解测试 (3个)
- D4: 创新思维能力测试 (2个)
"""

from ..base_test import BaseTestCategory, TestCase
from ..minimax_registry import minimax_registry


class AdvancedFeaturesTests(BaseTestCategory):
    """高级特性测试（15个用例）"""

    def __init__(self):
        super().__init__("advanced_features")
        self._create_tests()

    def _create_tests(self):
        """创建高级特性测试用例"""

        # ========== D1. 复杂推理链测试 (6个) ==========

        self.add_test_case(TestCase(
            name="D1_001_multi_step_reasoning",
            category="advanced_features",
            priority="primary",
            prompt="A、B、C三人中一人说谎。A说B在说谎，B说C在说谎，C说A和B都在说谎。请推理出谁在说谎？",
            parameters={"max_tokens": 600, "temperature": 0.0},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["reasoning_quality", "logic_chain", "accuracy"],
            metadata={"type": "complex_reasoning", "difficulty": "hard"},
            dimension="advanced_features",
            sub_dimension="复杂推理链",
            dimension_weight=0.15,
            test_weight=0.20,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.45, "completeness": 0.35, "logic": 0.20},
            minimax_id="D1-001",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D1_002_conditional_reasoning_chain",
            category="advanced_features",
            priority="primary",
            prompt="如果下雨，运动会取消。如果运动会取消，学生会失望。如果学生失望，家长会投诉。现在下雨了，请推理最终结果",
            parameters={"max_tokens": 500, "temperature": 0.0},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["reasoning_quality", "logic_chain", "accuracy"],
            metadata={"type": "complex_reasoning", "difficulty": "medium"},
            dimension="advanced_features",
            sub_dimension="复杂推理链",
            dimension_weight=0.15,
            test_weight=0.18,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.45, "completeness": 0.35, "logic": 0.20},
            minimax_id="D1-002",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D1_003_inductive_deductive",
            category="advanced_features",
            priority="primary",
            prompt="观察现象：铁能导电、铜能导电、铝能导电。请问所有金属都能导电吗？请进行推理",
            parameters={"max_tokens": 500, "temperature": 0.0},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["reasoning_quality", "logic_chain", "accuracy"],
            metadata={"type": "complex_reasoning", "difficulty": "medium"},
            dimension="advanced_features",
            sub_dimension="复杂推理链",
            dimension_weight=0.15,
            test_weight=0.16,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.45, "completeness": 0.35, "logic": 0.20},
            minimax_id="D1-003",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D1_004_analogy_chain",
            category="advanced_features",
            priority="primary",
            prompt="医生治病如同教师育人，如同工程师建造，如同...请完成这个类比链条并解释",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["reasoning_quality", "creativity", "accuracy"],
            metadata={"type": "complex_reasoning", "difficulty": "medium"},
            dimension="advanced_features",
            sub_dimension="复杂推理链",
            dimension_weight=0.15,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.35, "logic": 0.30},
            minimax_id="D1-004",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D1_005_counterfactual_reasoning",
            category="advanced_features",
            priority="primary",
            prompt="如果清朝没有闭关锁国，中国近代史会有什么不同？请进行反事实推理",
            parameters={"max_tokens": 700, "temperature": 0.8},
            expected_tokens_range=(500, 700),
            evaluation_criteria=["reasoning_quality", "historical_knowledge", "creativity"],
            metadata={"type": "complex_reasoning", "difficulty": "hard"},
            dimension="advanced_features",
            sub_dimension="复杂推理链",
            dimension_weight=0.15,
            test_weight=0.16,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.35, "logic": 0.30},
            minimax_id="D1-005",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D1_006_probability_chain",
            category="advanced_features",
            priority="primary",
            prompt="一个家庭有2个孩子，已知至少一个是男孩，求另一个也是男孩的概率",
            parameters={"max_tokens": 500, "temperature": 0.0},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["reasoning_quality", "math_accuracy", "logic_chain"],
            metadata={"type": "complex_reasoning", "difficulty": "hard"},
            dimension="advanced_features",
            sub_dimension="复杂推理链",
            dimension_weight=0.15,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.50, "completeness": 0.30, "logic": 0.20},
            minimax_id="D1-006",
            expected_score_range=(7.5, 9.5)
        ))

        # ========== D2. 指令遵循能力测试 (4个) ==========

        self.add_test_case(TestCase(
            name="D2_001_strict_instruction",
            category="advanced_features",
            priority="primary",
            prompt="请仅用3句话回答：什么是人工智能？每句话不超过20个字",
            parameters={"max_tokens": 100, "temperature": 0.7},
            expected_tokens_range=(50, 100),
            evaluation_criteria=["instruction_following", "constraint_compliance", "accuracy"],
            metadata={"type": "instruction_following", "difficulty": "easy"},
            dimension="advanced_features",
            sub_dimension="指令遵循能力",
            dimension_weight=0.15,
            test_weight=0.30,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.50, "completeness": 0.30, "logic": 0.20},
            minimax_id="D2-001",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D2_002_complex_instruction",
            category="advanced_features",
            priority="primary",
            prompt="先分析一下机器学习的基本概念，然后用Python写一个简单示例，最后解释运行结果",
            parameters={"max_tokens": 800, "temperature": 0.7},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["instruction_following", "completeness", "accuracy"],
            metadata={"type": "instruction_following", "difficulty": "medium"},
            dimension="advanced_features",
            sub_dimension="指令遵循能力",
            dimension_weight=0.15,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.40, "logic": 0.20},
            minimax_id="D2-002",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D2_003_instruction_correction",
            category="advanced_features",
            priority="primary",
            prompt="先解释量子计算，然后修正为用通俗语言解释，最后给一个生活化的比喻",
            parameters={"max_tokens": 700, "temperature": 0.7},
            expected_tokens_range=(400, 700),
            evaluation_criteria=["instruction_following", "adaptability", "clarity"],
            metadata={"type": "instruction_following", "difficulty": "medium"},
            dimension="advanced_features",
            sub_dimension="指令遵循能力",
            dimension_weight=0.15,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="D2-003",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D2_004_creative_instruction",
            category="advanced_features",
            priority="primary",
            prompt="请用诗歌的形式解释相对论，要押韵且朗朗上口",
            parameters={"max_tokens": 400, "temperature": 0.8},
            expected_tokens_range=(250, 400),
            evaluation_criteria=["instruction_following", "creativity", "accuracy"],
            metadata={"type": "instruction_following", "difficulty": "hard"},
            dimension="advanced_features",
            sub_dimension="指令遵循能力",
            dimension_weight=0.15,
            test_weight=0.20,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="D2-004",
            expected_score_range=(7.5, 9.5)
        ))

        # ========== D3. 多模态理解测试 (3个) ==========

        self.add_test_case(TestCase(
            name="D3_001_chart_understanding",
            category="advanced_features",
            priority="secondary",
            prompt="请描述这张图表显示的数据趋势并分析可能的原因：[图表描述：这是一张折线图，显示了2020-2024年某公司收入变化情况]",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["visual_understanding", "data_analysis", "reasoning"],
            metadata={"type": "multimodal", "difficulty": "medium"},
            dimension="advanced_features",
            sub_dimension="多模态理解",
            dimension_weight=0.15,
            test_weight=0.40,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.45, "completeness": 0.35, "logic": 0.20},
            minimax_id="D3-001",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D3_002_visual_analysis",
            category="advanced_features",
            priority="secondary",
            prompt="分析这张产品图片的设计风格、目标用户和使用场景：[图片描述：这是一款智能手表的产品图]",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["visual_understanding", "design_insight", "market_analysis"],
            metadata={"type": "multimodal", "difficulty": "medium"},
            dimension="advanced_features",
            sub_dimension="多模态理解",
            dimension_weight=0.15,
            test_weight=0.35,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="D3-002",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D3_003_cross_modal_creation",
            category="advanced_features",
            priority="secondary",
            prompt="根据这张风景照片，创作一首相关的诗歌：[照片描述：这是一张夕阳下的海滩照片]",
            parameters={"max_tokens": 400, "temperature": 0.8},
            expected_tokens_range=(250, 400),
            evaluation_criteria=["visual_understanding", "creativity", "emotional_depth"],
            metadata={"type": "multimodal", "difficulty": "hard"},
            dimension="advanced_features",
            sub_dimension="多模态理解",
            dimension_weight=0.15,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.45, "completeness": 0.30, "logic": 0.25},
            minimax_id="D3-003",
            expected_score_range=(7.5, 9.5)
        ))

        # ========== D4. 创新思维能力测试 (2个) ==========

        self.add_test_case(TestCase(
            name="D4_001_conceptual_innovation",
            category="advanced_features",
            priority="primary",
            prompt="如何重新定义'教育'概念以适应AI时代？提出创新观点",
            parameters={"max_tokens": 700, "temperature": 0.9},
            expected_tokens_range=(500, 700),
            evaluation_criteria=["innovation", "feasibility", "depth"],
            metadata={"type": "innovative_thinking", "difficulty": "hard"},
            dimension="advanced_features",
            sub_dimension="创新思维能力",
            dimension_weight=0.15,
            test_weight=0.50,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.50, "completeness": 0.30, "logic": 0.20},
            minimax_id="D4-001",
            expected_score_range=(7.5, 9.5)
        ))

        self.add_test_case(TestCase(
            name="D4_002_solution_innovation",
            category="advanced_features",
            priority="primary",
            prompt="传统交通方式面临哪些根本性挑战？提出颠覆性解决方案",
            parameters={"max_tokens": 800, "temperature": 0.9},
            expected_tokens_range=(600, 800),
            evaluation_criteria=["innovation", "feasibility", "impact"],
            metadata={"type": "innovative_thinking", "difficulty": "hard"},
            dimension="advanced_features",
            sub_dimension="创新思维能力",
            dimension_weight=0.15,
            test_weight=0.50,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.50, "completeness": 0.30, "logic": 0.20},
            minimax_id="D4-002",
            expected_score_range=(7.5, 9.5)
        ))

        # 注册到 minimax_registry
        for test_case in self.get_test_cases():
            minimax_registry.register_test(test_case)


# 注册到全局 registry（保持兼容）
from ..test_registry import registry
registry.register_category(AdvancedFeaturesTests())
