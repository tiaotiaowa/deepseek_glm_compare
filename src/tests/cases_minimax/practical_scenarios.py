"""实用场景测试 (25个测试用例)

包含:
- C1: 专业领域应用测试 (10个)
- C2: 中文处理能力测试 (8个)
- C3: 长文本处理测试 (4个)
- C4: 结构化输出测试 (3个)
"""

from ..base_test import BaseTestCategory, TestCase
from ..minimax_registry import minimax_registry


class PracticalScenariosTests(BaseTestCategory):
    """实用场景测试（25个用例）"""

    def __init__(self):
        super().__init__("practical_scenarios")
        self._create_tests()

    def _create_tests(self):
        """创建实用场景测试用例"""

        # ========== C1. 专业领域应用测试 (10个) ==========

        self.add_test_case(TestCase(
            name="C1_001_medical_consultation",
            category="practical_scenarios",
            priority="primary",
            prompt="患者出现持续发热、咳嗽、胸痛等症状，请分析可能的原因和应对措施",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["professional_quality", "accuracy", "completeness"],
            metadata={"type": "professional_application", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C1-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_002_legal_consultation",
            category="practical_scenarios",
            priority="primary",
            prompt="劳动合同到期后未续签，员工继续工作2个月，现公司要求员工离职。如何处理？",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["professional_quality", "accuracy", "legal_knowledge"],
            metadata={"type": "professional_application", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C1-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_003_financial_analysis",
            category="practical_scenarios",
            priority="primary",
            prompt="某公司年营收增长20%，但净利润下降15%，请分析可能的原因",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["professional_quality", "accuracy", "analysis_depth"],
            metadata={"type": "professional_application", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C1-003",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_004_education_planning",
            category="practical_scenarios",
            priority="primary",
            prompt="为高三学生制定大学专业选择和职业规划建议",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["professional_quality", "practicality", "completeness"],
            metadata={"type": "professional_application", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.40, "logic": 0.25},
            minimax_id="C1-004",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_005_investment_advice",
            category="practical_scenarios",
            priority="primary",
            prompt="当前经济环境下，普通投资者如何配置资产组合？",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["professional_quality", "risk_awareness", "practicality"],
            metadata={"type": "professional_application", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.35, "logic": 0.30},
            minimax_id="C1-005",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_006_engineering_design",
            category="practical_scenarios",
            priority="primary",
            prompt="设计一个小型风力发电系统，包含基本参数和实现方案",
            parameters={"max_tokens": 700, "temperature": 0.7},
            expected_tokens_range=(500, 700),
            evaluation_criteria=["professional_quality", "technical_feasibility", "completeness"],
            metadata={"type": "professional_application", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C1-006",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_007_hr_management",
            category="practical_scenarios",
            priority="primary",
            prompt="公司员工流失率居高不下，请制定改善方案",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["professional_quality", "practicality", "systematic_approach"],
            metadata={"type": "professional_application", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.09,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.40, "logic": 0.25},
            minimax_id="C1-007",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_008_marketing_strategy",
            category="practical_scenarios",
            priority="primary",
            prompt="为新推出的环保产品制定市场推广策略",
            parameters={"max_tokens": 600, "temperature": 0.8},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["professional_quality", "creativity", "feasibility"],
            metadata={"type": "professional_application", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.09,
            score_range=(0, 10),
            quality_criteria={"creativity": 0.35, "completeness": 0.35, "logic": 0.30},
            minimax_id="C1-008",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_009_data_science",
            category="practical_scenarios",
            priority="primary",
            prompt="电商平台用户购买行为数据分析，找出影响因素",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["professional_quality", "analytical_depth", "methodology"],
            metadata={"type": "professional_application", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.09,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C1-009",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C1_010_project_management",
            category="practical_scenarios",
            priority="primary",
            prompt="制定一个软件开发项目的完整管理计划",
            parameters={"max_tokens": 800, "temperature": 0.7},
            expected_tokens_range=(600, 800),
            evaluation_criteria=["professional_quality", "completeness", "structure"],
            metadata={"type": "professional_application", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="专业领域应用",
            dimension_weight=0.25,
            test_weight=0.09,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.40, "logic": 0.25},
            minimax_id="C1-010",
            expected_score_range=(7.0, 9.0)
        ))

        # ========== C2. 中文处理能力测试 (8个) ==========

        self.add_test_case(TestCase(
            name="C2_001_classical_poetry",
            category="practical_scenarios",
            priority="primary",
            prompt="请分析李白《静夜思》的艺术特色和思想感情",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["chinese_quality", "cultural_understanding", "literary_analysis"],
            metadata={"type": "chinese_processing", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C2-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C2_002_idiom_usage",
            category="practical_scenarios",
            priority="primary",
            prompt="在商务场合如何恰当地运用'相得益彰'这个成语？请举例说明",
            parameters={"max_tokens": 400, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["chinese_quality", "usage_accuracy", "context_appropriateness"],
            metadata={"type": "chinese_processing", "difficulty": "easy"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C2-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C2_003_chinese_character_culture",
            category="practical_scenarios",
            priority="primary",
            prompt="汉字从甲骨文到现代汉字的演变过程及其文化意义",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["chinese_quality", "cultural_knowledge", "historical_depth"],
            metadata={"type": "chinese_processing", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C2-003",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C2_004_dialect_understanding",
            category="practical_scenarios",
            priority="primary",
            prompt="请解释几个常见东北方言的含义和使用场景",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["chinese_quality", "cultural_knowledge", "regional_understanding"],
            metadata={"type": "chinese_processing", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C2-004",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C2_005_classical_chinese_translation",
            category="practical_scenarios",
            priority="primary",
            prompt="翻译并解释《论语》中'己所不欲，勿施于人'的含义",
            parameters={"max_tokens": 400, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["chinese_quality", "translation_accuracy", "philosophical_depth"],
            metadata={"type": "chinese_processing", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.45, "completeness": 0.35, "logic": 0.20},
            minimax_id="C2-005",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C2_006_chinese_rhetoric",
            category="practical_scenarios",
            priority="primary",
            prompt="分析朱自清《荷塘月色》中比喻修辞的运用",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["chinese_quality", "literary_analysis", "rhetoric_identification"],
            metadata={"type": "chinese_processing", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C2-006",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C2_007_modern_chinese_literature",
            category="practical_scenarios",
            priority="primary",
            prompt="分析鲁迅《狂人日记》的创作背景和主题思想",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["chinese_quality", "literary_analysis", "historical_context"],
            metadata={"type": "chinese_processing", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.12,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C2-007",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C2_008_language_comparison",
            category="practical_scenarios",
            priority="primary",
            prompt="中文和英文在表达逻辑和思维方式上有何差异？",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["chinese_quality", "comparative_analysis", "depth"],
            metadata={"type": "chinese_processing", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="中文处理能力",
            dimension_weight=0.25,
            test_weight=0.13,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.40, "logic": 0.25},
            minimax_id="C2-008",
            expected_score_range=(7.0, 9.0)
        ))

        # ========== C3. 长文本处理测试 (4个) ==========

        self.add_test_case(TestCase(
            name="C3_001_long_text_summarization",
            category="practical_scenarios",
            priority="primary",
            prompt="对一篇8000字的学术论文进行摘要，提取核心观点：[论文内容略，实际执行时会有完整内容]",
            parameters={"max_tokens": 800, "temperature": 0.7},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["completeness", "accuracy", "conciseness"],
            metadata={"type": "long_text_processing", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="长文本处理",
            dimension_weight=0.25,
            test_weight=0.30,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C3-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C3_002_long_text_structure",
            category="practical_scenarios",
            priority="primary",
            prompt="分析《红楼梦》前50回的主要情节结构",
            parameters={"max_tokens": 1000, "temperature": 0.7},
            expected_tokens_range=(700, 1000),
            evaluation_criteria=["completeness", "accuracy", "structural_analysis"],
            metadata={"type": "long_text_processing", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="长文本处理",
            dimension_weight=0.25,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C3-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C3_003_multi_document_integration",
            category="practical_scenarios",
            priority="primary",
            prompt="整合5篇不同角度的AI发展文章，形成综合分析：[文章内容略]",
            parameters={"max_tokens": 1000, "temperature": 0.7},
            expected_tokens_range=(700, 1000),
            evaluation_criteria=["completeness", "accuracy", "integration_quality"],
            metadata={"type": "long_text_processing", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="长文本处理",
            dimension_weight=0.25,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.40, "logic": 0.25},
            minimax_id="C3-003",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C3_004_long_dialogue_understanding",
            category="practical_scenarios",
            priority="primary",
            prompt="分析一场1小时学术讨论的关键观点和分歧点：[对话内容略]",
            parameters={"max_tokens": 800, "temperature": 0.7},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["completeness", "accuracy", "depth"],
            metadata={"type": "long_text_processing", "difficulty": "hard"},
            dimension="practical_scenarios",
            sub_dimension="长文本处理",
            dimension_weight=0.25,
            test_weight=0.20,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.40, "completeness": 0.35, "logic": 0.25},
            minimax_id="C3-004",
            expected_score_range=(7.0, 9.0)
        ))

        # ========== C4. 结构化输出测试 (3个) ==========

        self.add_test_case(TestCase(
            name="C4_001_json_output",
            category="practical_scenarios",
            priority="primary",
            prompt="将以下公司信息转换为标准JSON格式：腾讯公司，成立于1998年，主要业务包括社交、游戏、云计算等",
            parameters={"max_tokens": 300, "temperature": 0.0},
            expected_tokens_range=(150, 300),
            evaluation_criteria=["format_correctness", "data_accuracy", "structure_clarity"],
            metadata={"type": "structured_output", "difficulty": "easy"},
            dimension="practical_scenarios",
            sub_dimension="结构化输出",
            dimension_weight=0.25,
            test_weight=0.35,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.50, "completeness": 0.35, "logic": 0.15},
            minimax_id="C4-001",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C4_002_table_organizing",
            category="practical_scenarios",
            priority="primary",
            prompt="将以下销售数据整理成表格：Q1销售100万，Q2销售120万，Q3销售90万，Q4销售150万",
            parameters={"max_tokens": 300, "temperature": 0.0},
            expected_tokens_range=(150, 300),
            evaluation_criteria=["format_correctness", "data_accuracy", "readability"],
            metadata={"type": "structured_output", "difficulty": "easy"},
            dimension="practical_scenarios",
            sub_dimension="结构化输出",
            dimension_weight=0.25,
            test_weight=0.35,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.50, "completeness": 0.35, "logic": 0.15},
            minimax_id="C4-002",
            expected_score_range=(7.0, 9.0)
        ))

        self.add_test_case(TestCase(
            name="C4_003_workflow_description",
            category="practical_scenarios",
            priority="primary",
            prompt="详细描述用户注册登录的完整流程",
            parameters={"max_tokens": 500, "temperature": 0.7},
            expected_tokens_range=(300, 500),
            evaluation_criteria=["format_correctness", "completeness", "clarity"],
            metadata={"type": "structured_output", "difficulty": "medium"},
            dimension="practical_scenarios",
            sub_dimension="结构化输出",
            dimension_weight=0.25,
            test_weight=0.30,
            score_range=(0, 10),
            quality_criteria={"accuracy": 0.35, "completeness": 0.40, "logic": 0.25},
            minimax_id="C4-003",
            expected_score_range=(7.0, 9.0)
        ))

        # 注册到 minimax_registry
        for test_case in self.get_test_cases():
            minimax_registry.register_test(test_case)


# 注册到全局 registry（保持兼容）
from ..test_registry import registry
registry.register_category(PracticalScenariosTests())
