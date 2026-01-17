"""基础性能测试 (25个测试用例)

包含:
- A1: 实时响应能力测试 (10个)
- A2: 吞吐量能力测试 (10个)
- A3: 稳定性表现测试 (5个)
"""

from ..base_test import BaseTestCategory, TestCase
from ..minimax_registry import minimax_registry


class BasicPerformanceTests(BaseTestCategory):
    """基础性能测试（25个用例）"""

    def __init__(self):
        super().__init__("basic_performance")
        self._create_tests()

    def _create_tests(self):
        """创建基础性能测试用例"""

        # ========== A1. 实时响应能力测试 (10个) ==========

        self.add_test_case(TestCase(
            name="A1_001_simple_dialogue_ttft",
            category="basic_performance",
            priority="primary",
            prompt="你好，请简单介绍一下自己",
            parameters={"max_tokens": 50, "temperature": 0.7},
            expected_tokens_range=(10, 50),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "easy"},
            # MiniMax 标准字段
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-001",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_002_complex_question_ttft",
            category="basic_performance",
            priority="primary",
            prompt="请分析量子计算在人工智能领域的应用前景",
            parameters={"max_tokens": 300, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-002",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_003_long_text_ttft",
            category="basic_performance",
            priority="primary",
            prompt="请写一篇关于气候变化的详细分析报告",
            parameters={"max_tokens": 800, "temperature": 0.7},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-003",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_004_math_calculation_ttft",
            category="basic_performance",
            priority="primary",
            prompt="计算 1234 × 5678 的结果",
            parameters={"max_tokens": 100, "temperature": 0.0},
            expected_tokens_range=(10, 50),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "easy"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-004",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_005_code_generation_ttft",
            category="basic_performance",
            priority="primary",
            prompt="请写一个快速排序算法的Python实现",
            parameters={"max_tokens": 300, "temperature": 0.0},
            expected_tokens_range=(100, 300),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-005",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_006_chinese_understanding_ttft",
            category="basic_performance",
            priority="primary",
            prompt="请解释一下'人工智能'这个概念",
            parameters={"max_tokens": 200, "temperature": 0.7},
            expected_tokens_range=(100, 200),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "easy"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-006",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_007_creative_writing_ttft",
            category="basic_performance",
            priority="primary",
            prompt="请写一首关于春天的现代诗",
            parameters={"max_tokens": 300, "temperature": 0.8},
            expected_tokens_range=(100, 300),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-007",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_008_tech_consulting_ttft",
            category="basic_performance",
            priority="primary",
            prompt="什么是RESTful API设计原则？",
            parameters={"max_tokens": 400, "temperature": 0.7},
            expected_tokens_range=(200, 400),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-008",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_009_logic_reasoning_ttft",
            category="basic_performance",
            priority="primary",
            prompt="如果所有的鸟都会飞，企鹅是鸟，那么企鹅会飞吗？",
            parameters={"max_tokens": 200, "temperature": 0.0},
            expected_tokens_range=(50, 200),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-009",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A1_010_comprehensive_ttft",
            category="basic_performance",
            priority="primary",
            prompt="请分析区块链技术在金融行业的应用现状、挑战和未来趋势",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["response_quality", "ttft_performance"],
            metadata={"type": "ttft_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="实时响应能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"ttft_performance": 1.0},
            minimax_id="A1-010",
            expected_score_range=(6.0, 8.0)
        ))

        # ========== A2. 吞吐量能力测试 (10个) ==========

        self.add_test_case(TestCase(
            name="A2_001_standard_text_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成一篇500字的科技文章，主题为人工智能的发展",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-001",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_002_long_text_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成一篇2000字的学术论文摘要，主题为机器学习在医疗诊断中的应用",
            parameters={"max_tokens": 2200, "temperature": 0.7},
            expected_tokens_range=(1800, 2200),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-002",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_003_code_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成一个完整的Web应用后端API，包含用户认证、数据CRUD操作",
            parameters={"max_tokens": 1000, "temperature": 0.0},
            expected_tokens_range=(600, 1000),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-003",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_004_list_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请列出100个Python编程最佳实践条目",
            parameters={"max_tokens": 1500, "temperature": 0.7},
            expected_tokens_range=(1000, 1500),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-004",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_005_dialogue_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请模拟10轮深入的学术讨论，主题为量子计算的哲学意义",
            parameters={"max_tokens": 1500, "temperature": 0.7},
            expected_tokens_range=(1000, 1500),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-005",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_006_chinese_text_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成一篇1500字的商业分析报告，主题为电商行业发展趋势",
            parameters={"max_tokens": 1800, "temperature": 0.7},
            expected_tokens_range=(1200, 1800),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-006",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_007_tech_doc_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成完整的API文档，包含所有接口说明、参数、返回值、示例代码",
            parameters={"max_tokens": 1500, "temperature": 0.0},
            expected_tokens_range=(1000, 1500),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-007",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_008_creative_content_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成一个完整的科幻故事大纲和前3章内容",
            parameters={"max_tokens": 2000, "temperature": 0.8},
            expected_tokens_range=(1500, 2000),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.05,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-008",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_009_data_analysis_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成完整的用户行为分析报告，包含数据统计、趋势分析、优化建议",
            parameters={"max_tokens": 1200, "temperature": 0.7},
            expected_tokens_range=(800, 1200),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.05,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-009",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A2_010_comprehensive_output_generation_speed",
            category="basic_performance",
            priority="primary",
            prompt="请生成包含图表、数据、分析的综合商业计划书",
            parameters={"max_tokens": 2000, "temperature": 0.7},
            expected_tokens_range=(1500, 2000),
            evaluation_criteria=["response_quality", "throughput_performance"],
            metadata={"type": "throughput_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="吞吐量能力",
            dimension_weight=0.25,
            test_weight=0.05,
            score_range=(0, 10),
            quality_criteria={"throughput_performance": 1.0},
            minimax_id="A2-010",
            expected_score_range=(6.0, 8.0)
        ))

        # ========== A3. 稳定性表现测试 (5个) ==========

        self.add_test_case(TestCase(
            name="A3_001_concurrent_stability",
            category="basic_performance",
            priority="secondary",
            prompt="请同时回答以下5个问题：1. 什么是人工智能？2. 解释机器学习 3. 什么是深度学习？4. 什么是神经网络？5. 什么是自然语言处理？",
            parameters={"max_tokens": 800, "temperature": 0.7},
            expected_tokens_range=(500, 800),
            evaluation_criteria=["response_quality", "stability_performance"],
            metadata={"type": "stability_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="稳定性表现",
            dimension_weight=0.25,
            test_weight=0.30,
            score_range=(0, 10),
            quality_criteria={"stability_performance": 1.0},
            minimax_id="A3-001",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A3_002_long_running_stability",
            category="basic_performance",
            priority="secondary",
            prompt="请连续回答以下50个不同类型的问题（略，实际执行时会有详细问题列表）",
            parameters={"max_tokens": 5000, "temperature": 0.7},
            expected_tokens_range=(3000, 5000),
            evaluation_criteria=["response_quality", "stability_performance"],
            metadata={"type": "stability_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="稳定性表现",
            dimension_weight=0.25,
            test_weight=0.25,
            score_range=(0, 10),
            quality_criteria={"stability_performance": 1.0},
            minimax_id="A3-002",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A3_003_boundary_stability",
            category="basic_performance",
            priority="secondary",
            prompt="请处理以下特殊输入：空字符串、特殊符号、超长文本",
            parameters={"max_tokens": 1000, "temperature": 0.7},
            expected_tokens_range=(500, 1000),
            evaluation_criteria=["response_quality", "stability_performance"],
            metadata={"type": "stability_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="稳定性表现",
            dimension_weight=0.25,
            test_weight=0.20,
            score_range=(0, 10),
            quality_criteria={"stability_performance": 1.0},
            minimax_id="A3-003",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A3_004_memory_stability",
            category="basic_performance",
            priority="secondary",
            prompt="请连续执行100个复杂任务，包括代码生成、文本分析、数学计算等",
            parameters={"max_tokens": 8000, "temperature": 0.7},
            expected_tokens_range=(6000, 8000),
            evaluation_criteria=["response_quality", "stability_performance"],
            metadata={"type": "stability_test", "difficulty": "hard"},
            dimension="basic_performance",
            sub_dimension="稳定性表现",
            dimension_weight=0.25,
            test_weight=0.15,
            score_range=(0, 10),
            quality_criteria={"stability_performance": 1.0},
            minimax_id="A3-004",
            expected_score_range=(6.0, 8.0)
        ))

        self.add_test_case(TestCase(
            name="A3_005_error_recovery_stability",
            category="basic_performance",
            priority="secondary",
            prompt="请模拟处理网络中断、请求超时等异常情况，并展示错误恢复能力",
            parameters={"max_tokens": 600, "temperature": 0.7},
            expected_tokens_range=(400, 600),
            evaluation_criteria=["response_quality", "stability_performance"],
            metadata={"type": "stability_test", "difficulty": "medium"},
            dimension="basic_performance",
            sub_dimension="稳定性表现",
            dimension_weight=0.25,
            test_weight=0.10,
            score_range=(0, 10),
            quality_criteria={"stability_performance": 1.0},
            minimax_id="A3-005",
            expected_score_range=(6.0, 8.0)
        ))

        # 注册到 minimax_registry
        for test_case in self.get_test_cases():
            minimax_registry.register_test(test_case)


# 注册到全局 registry（保持兼容）
from ..test_registry import registry
registry.register_category(BasicPerformanceTests())
