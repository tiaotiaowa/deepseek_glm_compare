"""统一评测脚本 - 支持 MiniMax 标准评测和原始对比测试

支持四种运行模式：
- --mode standard: 运行完整 MiniMax 标准评测（100个用例）
  ✅ 保存JSON
  ✅ 生成Markdown报告
  ✅ 生成HTML报告

- --mode preview: 运行预测试（每个维度1个用例，共4个）
  ✅ 保存JSON
  ✅ 生成Markdown报告
  ✅ 生成HTML报告

- --mode single: 运行单用例测试（1个用例）
  ✅ 保存JSON
  ✅ 生成Markdown报告
  ✅ 生成HTML报告

- --mode original: 运行原始对比测试（每类别1个用例，共4个）
  ✅ 保存JSON
  ✅ 生成Markdown报告
  ❌ 不生成HTML报告（简化模式）

使用示例：
    python run_benchmark.py                    # 默认：标准模式
    python run_benchmark.py --mode preview     # 预测试模式
    python run_benchmark.py --mode single      # 单用例测试
    python run_benchmark.py --mode original    # 原始对比测试模式
"""

import sys
import os
import io
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

# 设置 UTF-8 编码（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 验证 MINIMAX_API_KEY 已设置
if not os.environ.get("MINIMAX_API_KEY"):
    print("警告: 未设置 MINIMAX_API_KEY 环境变量")
    print("请在 .env 文件中设置: MINIMAX_API_KEY=your_api_key_here")
    print("MiniMax Judge 将无法参与质量评估。\n")

from src.utils.config_loader import load_config, validate_config
from src.benchmark.runner import BenchmarkRunner
from src.quality.judge_manager import JudgeManager
from src.quality.minimax_scorer import MiniMaxScoreCalculator
from src.report.minimax_generator import MiniMaxReportGenerator
from src.report.generator import ReportGenerator
from src.utils.json_saver import BenchmarkJSONSaver
from src.report.markdown_generator import MarkdownReportGenerator


# ============ MiniMax 标准评测模式 ============

def run_minimax_standard(config):
    """运行完整的 MiniMax 标准评测（100个用例）"""
    from src.tests.cases_minimax import (
        BasicPerformanceTests,
        CoreCapabilitiesTests,
        PracticalScenariosTests,
        AdvancedFeaturesTests
    )
    from src.tests.minimax_registry import minimax_registry

    print("=" * 80)
    print("DeepSeek vs GLM - MiniMax 标准评测（100个用例）")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # 加载配置
    print("加载配置文件...")
    if not validate_config(config):
        print("❌ 配置验证失败")
        sys.exit(1)
    print("✓ 配置加载成功\n")

    # MiniMax Judge 提前验证
    quality_config = config.get("quality", {})
    if quality_config.get("enabled", False):
        validate_minimax_judge(config)

    # 获取所有测试用例
    all_test_cases = minimax_registry.get_all_test_cases()
    print(f"✓ 加载 MiniMax 标准测试用例: {len(all_test_cases)} 个")

    dimension_counts = Counter(tc.dimension for tc in all_test_cases)
    print("\n测试用例分布:")
    for dimension, count in dimension_counts.items():
        print(f"  - {dimension}: {count} 个")
    print()

    # 阶段性保存配置 - 暂时禁用增量保存（存在除零错误bug）
    incremental_saves = []  # 禁用增量保存，只在最后保存完整结果

    # 创建进度回调函数 - 只显示进度里程碑
    def progress_callback(completed, total, metrics_collector):
        # 每10个测试用例显示一次进度
        if completed % 10 == 0 and completed > 0:
            statistics = metrics_collector.get_statistics()
            model_names = list(statistics.get('model_stats', {}).keys())

            print(f"\n{'=' * 80}")
            print(f"📊 进度里程碑: 已完成 {completed}/{total} 个测试用例")
            print(f"{'=' * 80}")
            print(f"  - 成功率: {statistics['success_rate']*100:.1f}%")
            for model_name in model_names:
                model_stats = statistics['model_stats'][model_name]
                print(f"  - {model_name}: {model_stats['success']}/{model_stats['total']} 测试成功")
            print()

    # 运行基准测试
    runner = BenchmarkRunner(config)
    print("\n验证 API 连接...")
    connection_status = runner.validate_connections()
    for api_name, status in connection_status.items():
        print(f"{api_name}: {'✓ 成功' if status else '✗ 失败'}")
    print()

    # 执行测试
    print("\n" + "=" * 80)
    print("开始基准测试")
    print("=" * 80 + "\n")

    metrics_collector = runner.run_benchmark(
        test_cases=[tc.to_dict() for tc in all_test_cases],
        show_progress=True,
        progress_callback=progress_callback
    )

    # 获取结果
    statistics = metrics_collector.get_statistics()
    print(f"\n测试完成:")
    print(f"  - 总测试数: {statistics['total_tests']}")
    print(f"  - 成功: {statistics['successful_tests']}")
    print(f"  - 失败: {statistics['failed_tests']}")
    print(f"  - 成功率: {statistics['success_rate']*100:.1f}%")

    # 计算维度得分
    model_names = runner.get_model_names()
    print(f"\n对比的模型: {', '.join(model_names)}")

    dimension_weights = {
        "basic_performance": 0.25,
        "core_capabilities": 0.35,
        "practical_scenarios": 0.25,
        "advanced_features": 0.15
    }

    categories = list(dimension_counts.keys())
    summaries = metrics_collector.calculate_all_summaries(
        model_names=model_names,
        categories=categories
    )

    # 三模型交叉评价
    if quality_config.get("enabled", False):
        print("\n" + "=" * 80)
        print("开始三模型交叉评价...")
        print("=" * 80 + "\n")

        judge_manager = JudgeManager(config)
        scorer = MiniMaxScoreCalculator()
        quality_stats = metrics_collector.get_quality_statistics()
        print(f"质量评估完成:")
        print(f"  - 总评估数: {quality_stats['overall']['total_evaluations']}")
        print(f"  - 成功评估: {quality_stats['overall']['successful_evaluations']}")
    else:
        scorer = None
        quality_stats = None

    # 计算维度得分
    print("\n计算 MiniMax 标准维度得分...")
    quality_scores = calculate_dimension_scores(model_names, summaries, dimension_weights, metrics_collector)

    # 保存评测数据到JSON
    print("\n" + "=" * 80)
    print("保存评测数据到JSON...")
    print("=" * 80)
    raw_results = metrics_collector.export_results()
    json_saver = BenchmarkJSONSaver()
    json_path = json_saver.save_evaluation_data(
        statistics=statistics,
        quality_scores=quality_scores,
        summaries=[s.to_dict() for s in summaries],
        raw_results=raw_results,
        dimension_weights=dimension_weights,
        quality_evaluations=metrics_collector.get_quality_statistics() if quality_config.get("enabled", False) else {},
        config=config
    )
    print(f"✅ JSON数据已保存: {json_path}")

    # 从JSON生成Markdown报告
    print("\n" + "=" * 80)
    print("从JSON生成Markdown报告...")
    print("=" * 80)
    md_generator = MarkdownReportGenerator()
    md_path = md_generator.generate_from_json(json_path)
    print(f"✅ Markdown报告已生成: {md_path}")

    # 生成HTML报告（保留原有功能）
    print("\n" + "=" * 80)
    print("生成HTML报告...")
    print("=" * 80 + "\n")

    report_generator = MiniMaxReportGenerator(config.get("report", {}))

    report_path = report_generator.generate_minimax_report(
        statistics=statistics,
        quality_scores=quality_scores,
        performance_data=raw_results,
        model_names=model_names,
        dimension_weights=dimension_weights
    )

    print(f"✅ 报告已生成: {report_path}")

    # 打印总结
    print("\n" + "=" * 80)
    print(f"✅ MiniMax 标准评测完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    print("评测总结:")
    for model_name in model_names:
        overall_score = quality_scores[model_name]["overall_score"]
        grade = scorer.grade_score(overall_score) if scorer else "N/A"
        print(f"\n{model_name}:")
        print(f"  综合得分: {overall_score:.2f}/10")
        print(f"  等级: {grade}")

    print(f"\n报告路径: {report_path}")


def run_minimax_preview(config):
    """运行预测试（每个维度1个用例，共4个）"""
    from src.tests.cases_minimax import (
        BasicPerformanceTests,
        CoreCapabilitiesTests,
        PracticalScenariosTests,
        AdvancedFeaturesTests
    )
    from src.tests.minimax_registry import minimax_registry

    print("=" * 80)
    print("MiniMax 标准评测 - 预测试（每个维度1个用例）")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # 加载配置
    if not validate_config(config):
        print("❌ 配置验证失败")
        sys.exit(1)
    print("✓ 配置加载成功\n")

    # MiniMax Judge 验证
    quality_config = config.get("quality", {})
    if quality_config.get("enabled", False):
        validate_minimax_judge(config)

    # 获取测试用例
    all_test_cases = minimax_registry.get_all_test_cases()

    # 选择每个维度的第一个用例
    selected_tests = []
    dimensions = ["basic_performance", "core_capabilities", "practical_scenarios", "advanced_features"]
    for dimension in dimensions:
        for tc in all_test_cases:
            if tc.dimension == dimension:
                selected_tests.append(tc)
                break

    print(f"✓ 加载预测试用例: {len(selected_tests)} 个（每个维度1个）")
    for tc in selected_tests:
        print(f"  - {tc.minimax_id}: {tc.sub_dimension}")
    print()

    # 运行测试
    runner = BenchmarkRunner(config)
    metrics_collector = runner.run_benchmark(
        test_cases=[tc.to_dict() for tc in selected_tests],
        show_progress=True
    )

    statistics = metrics_collector.get_statistics()
    print(f"\n预测试完成:")
    print(f"  - 总测试数: {statistics['total_tests']}")
    print(f"  - 成功: {statistics['successful_tests']}")
    print(f"  - 成功率: {statistics['success_rate']*100:.1f}%")

    # 计算维度得分
    model_names = runner.get_model_names()
    print(f"\n对比的模型: {', '.join(model_names)}")

    dimension_weights = {
        "basic_performance": 0.25,
        "core_capabilities": 0.35,
        "practical_scenarios": 0.25,
        "advanced_features": 0.15
    }

    categories = list(dimension_weights.keys())
    summaries = metrics_collector.calculate_all_summaries(
        model_names=model_names,
        categories=categories
    )

    # 三模型交叉评价（如果启用）
    if quality_config.get("enabled", False):
        print("\n" + "=" * 80)
        print("开始三模型交叉评价...")
        print("=" * 80 + "\n")

        from src.quality.judge_manager import JudgeManager
        from src.quality.minimax_scorer import MiniMaxScoreCalculator

        judge_manager = JudgeManager(config)
        scorer = MiniMaxScoreCalculator()
        quality_stats = metrics_collector.get_quality_statistics()
        print(f"质量评估完成:")
        print(f"  - 总评估数: {quality_stats['overall']['total_evaluations']}")
        print(f"  - 成功评估: {quality_stats['overall']['successful_evaluations']}")
    else:
        scorer = None
        quality_stats = None

    # 计算维度得分
    print("\n计算 MiniMax 标准维度得分...")
    quality_scores = calculate_dimension_scores(model_names, summaries, dimension_weights, metrics_collector)

    # 保存评测数据到JSON
    print("\n" + "=" * 80)
    print("保存评测数据到JSON...")
    print("=" * 80)
    raw_results = metrics_collector.export_results()
    json_saver = BenchmarkJSONSaver()
    json_path = json_saver.save_evaluation_data(
        statistics=statistics,
        quality_scores=quality_scores,
        summaries=[s.to_dict() for s in summaries],
        raw_results=raw_results,
        dimension_weights=dimension_weights,
        quality_evaluations=metrics_collector.get_quality_statistics() if quality_config.get("enabled", False) else {},
        config=config
    )
    print(f"✅ JSON数据已保存: {json_path}")

    # 从JSON生成Markdown报告
    print("\n" + "=" * 80)
    print("从JSON生成Markdown报告...")
    print("=" * 80)
    md_generator = MarkdownReportGenerator()
    md_path = md_generator.generate_from_json(json_path)
    print(f"✅ Markdown报告已生成: {md_path}")

    # 生成HTML报告（保留原有功能）
    print("\n" + "=" * 80)
    print("生成HTML报告...")
    print("=" * 80 + "\n")

    from src.report.minimax_generator import MiniMaxReportGenerator
    report_generator = MiniMaxReportGenerator(config.get("report", {}))

    report_path = report_generator.generate_minimax_report(
        statistics=statistics,
        quality_scores=quality_scores,
        performance_data=raw_results,
        model_names=model_names,
        dimension_weights=dimension_weights
    )

    print(f"✅ 报告已生成: {report_path}")

    # 打印总结
    print("\n" + "=" * 80)
    print("预测试评测总结:")
    print("=" * 80)
    for model_name in model_names:
        overall_score = quality_scores[model_name]["overall_score"]
        grade = scorer.grade_score(overall_score) if scorer else "N/A"
        print(f"\n{model_name}:")
        print(f"  综合得分: {overall_score:.2f}/10")
        print(f"  等级: {grade}")

    print("\n" + "=" * 80)
    print(f"✅ 预测试完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def run_single_test(config):
    """运行单用例测试（只运行第一个测试用例）"""
    from src.tests.cases_minimax import BasicPerformanceTests
    from src.tests.minimax_registry import minimax_registry

    print("=" * 80)
    print("MiniMax 标准评测 - 单用例测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # 加载配置
    if not validate_config(config):
        print("❌ 配置验证失败")
        sys.exit(1)
    print("✓ 配置加载成功\n")

    # MiniMax Judge 验证
    quality_config = config.get("quality", {})
    if quality_config.get("enabled", False):
        validate_minimax_judge(config)

    # 只选择第一个测试用例
    all_test_cases = minimax_registry.get_all_test_cases()
    if not all_test_cases:
        print("❌ 未找到测试用例")
        sys.exit(1)

    selected_tests = [all_test_cases[0]]  # 只取第一个

    print(f"✓ 加载单用例测试: 1 个")
    print(f"  - {selected_tests[0].minimax_id}: {selected_tests[0].sub_dimension}")
    print(f"  - 提示词: {selected_tests[0].prompt[:100]}...")
    print()

    # 运行测试
    runner = BenchmarkRunner(config)
    metrics_collector = runner.run_benchmark(
        test_cases=[tc.to_dict() for tc in selected_tests],
        show_progress=True
    )

    statistics = metrics_collector.get_statistics()
    print(f"\n单用例测试完成:")
    print(f"  - 总测试数: {statistics['total_tests']}")
    print(f"  - 成功: {statistics['successful_tests']}")
    print(f"  - 成功率: {statistics['success_rate']*100:.1f}%")

    # 计算维度得分
    model_names = runner.get_model_names()
    print(f"\n对比的模型: {', '.join(model_names)}")

    dimension_weights = {
        "basic_performance": 1.0,  # 单用例，权重为1
    }

    categories = list(dimension_weights.keys())
    summaries = metrics_collector.calculate_all_summaries(
        model_names=model_names,
        categories=categories
    )

    # 三模型交叉评价（如果启用）
    if quality_config.get("enabled", False):
        print("\n" + "=" * 80)
        print("开始三模型交叉评价...")
        print("=" * 80 + "\n")

        from src.quality.judge_manager import JudgeManager
        from src.quality.minimax_scorer import MiniMaxScoreCalculator

        judge_manager = JudgeManager(config)
        scorer = MiniMaxScoreCalculator()
        quality_stats = metrics_collector.get_quality_statistics()
        print(f"质量评估完成:")
        print(f"  - 总评估数: {quality_stats['overall']['total_evaluations']}")
        print(f"  - 成功评估: {quality_stats['overall']['successful_evaluations']}")
    else:
        scorer = None
        quality_stats = None

    # 计算维度得分
    print("\n计算 MiniMax 标准维度得分...")
    quality_scores = calculate_dimension_scores(model_names, summaries, dimension_weights, metrics_collector)

    # 保存评测数据到JSON
    print("\n" + "=" * 80)
    print("保存评测数据到JSON...")
    print("=" * 80)
    raw_results = metrics_collector.export_results()
    json_saver = BenchmarkJSONSaver()
    json_path = json_saver.save_evaluation_data(
        statistics=statistics,
        quality_scores=quality_scores,
        summaries=[s.to_dict() for s in summaries],
        raw_results=raw_results,
        dimension_weights=dimension_weights,
        quality_evaluations=metrics_collector.get_quality_statistics() if quality_config.get("enabled", False) else {},
        config=config
    )
    print(f"✅ JSON数据已保存: {json_path}")

    # 从JSON生成Markdown报告
    print("\n" + "=" * 80)
    print("从JSON生成Markdown报告...")
    print("=" * 80)
    md_generator = MarkdownReportGenerator()
    md_path = md_generator.generate_from_json(json_path)
    print(f"✅ Markdown报告已生成: {md_path}")

    print("\n" + "=" * 80)
    print("单用例测试评测总结:")
    print("=" * 80)

    for model_name in model_names:
        model_score = quality_scores.get(model_name, {})
        overall_score = model_score.get("overall_score", 0)
        print(f"\n{model_name}:")
        print(f"  综合得分: {overall_score:.2f}/10")

    # 生成HTML报告（保持与其他模式一致）
    print("\n" + "=" * 80)
    print("生成HTML报告...")
    print("=" * 80 + "\n")

    from src.report.minimax_generator import MiniMaxReportGenerator
    html_report_generator = MiniMaxReportGenerator(config.get("report", {}))

    html_report_path = html_report_generator.generate_minimax_report(
        statistics=statistics,
        quality_scores=quality_scores,
        performance_data=raw_results,
        model_names=model_names,
        dimension_weights=dimension_weights
    )

    print(f"✅ HTML报告已生成: {html_report_path}")

    print(f"\n✅ 单用例测试完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def run_original_test(config):
    """运行原始对比测试（每类别1个用例）"""
    from src.tests.test_registry import registry
    from src.utils.logger import setup_logger

    print("=" * 80)
    print("DeepSeek vs GLM - 每类别1用例对比测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # 选择的测试用例（单用例测试）
    SELECTED_TESTS = {
        "qa_simple": "qa_capital_france"
    }

    print(f"选择的测试类别数量: {len(SELECTED_TESTS)}")
    for category, test_name in SELECTED_TESTS.items():
        print(f"  - {category}: {test_name}")
    print()

    # 加载配置
    if not validate_config(config):
        print("❌ 配置验证失败")
        sys.exit(1)
    print("✓ 配置加载成功\n")

    # MiniMax Judge 验证
    quality_config = config.get("quality", {})
    if quality_config.get("enabled", False):
        validate_minimax_judge(config)

    # 获取选定的测试用例
    test_cases = []
    for category, test_name in SELECTED_TESTS.items():
        # 获取该类别的所有测试用例
        category_tests = registry.get_test_cases_by_category(category)
        # 找到指定名称的测试用例
        for test in category_tests:
            if test.name == test_name:
                test_cases.append(test)
                break

    print(f"✓ 加载测试用例: {len(test_cases)} 个\n")

    # 运行测试
    runner = BenchmarkRunner(config)
    metrics_collector = runner.run_benchmark(
        test_cases=[tc.to_dict() for tc in test_cases],
        show_progress=True
    )

    # 生成报告
    statistics = metrics_collector.get_statistics()
    model_names = runner.get_model_names()
    summaries = metrics_collector.calculate_all_summaries(
        model_names=model_names,
        categories=list(SELECTED_TESTS.keys())
    )
    raw_results = metrics_collector.export_results()
    quality_stats = metrics_collector.get_quality_statistics() if config.get("quality", {}).get("enabled", False) else None

    # 保存评测数据到JSON（统一流程）
    print("\n" + "=" * 80)
    print("保存评测数据到JSON...")
    print("=" * 80)

    # 为original模式构建简化的质量评分结构
    quality_scores_simple = {}
    for model_name in model_names:
        model_summaries = [s for s in summaries if s.model_name == model_name]
        if model_summaries:
            # 基于平均速度计算简化的质量评分
            avg_speed = sum(s.speed_mean for s in model_summaries) / len(model_summaries)
            overall_score = min(10.0, avg_speed / 10.0)

            # 构建维度得分（使用测试类别作为维度）
            dimension_scores = {}
            for summary in model_summaries:
                if summary.test_count > 0:
                    dim_score = min(10.0, summary.speed_mean / 10.0)
                    dimension_scores[summary.category] = dim_score

            quality_scores_simple[model_name] = {
                "overall_score": overall_score,
                "dimension_scores": dimension_scores,
                "grade": "N/A",  # 简化模式不计算等级
                "rank": 0
            }

    # 导入并使用 JSONSaver
    from src.utils.json_saver import BenchmarkJSONSaver
    json_saver = BenchmarkJSONSaver()

    json_path = json_saver.save_evaluation_data(
        statistics=statistics,
        quality_scores=quality_scores_simple,
        summaries=[s.to_dict() for s in summaries],
        raw_results=raw_results,
        dimension_weights={},  # original模式不使用维度权重
        quality_evaluations=quality_stats if quality_stats else {},
        config=config
    )
    print(f"✅ JSON数据已保存: {json_path}")

    # 从JSON生成Markdown报告（统一流程）
    print("\n" + "=" * 80)
    print("从JSON生成Markdown报告...")
    print("=" * 80)

    from src.report.markdown_generator import MarkdownReportGenerator
    md_generator = MarkdownReportGenerator()
    md_path = md_generator.generate_from_json(json_path)
    print(f"✅ Markdown报告已生成: {md_path}")
    print("\n" + "=" * 80)
    print(f"✅ 对比测试完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


# ============ 辅助函数 ============

def validate_minimax_judge(config):
    """验证 MiniMax Judge API 连接"""
    print("\n" + "=" * 80)
    print("🔍 MiniMax Judge 提前验证")
    print("=" * 80 + "\n")

    from src.api.minimax_client import MiniMaxClient

    minimax_api_key = os.environ.get("MINIMAX_API_KEY")
    minimax_base_url = os.environ.get("MINIMAX_BASE_URL", "https://api.minimaxi.com/anthropic")
    minimax_model = os.environ.get("MINIMAX_MODEL", "MiniMax-M2.1")

    if not minimax_api_key:
        print("❌ MiniMax API Key 未配置")
        return False

    print("✓ 从环境变量读取 MiniMax API Key")

    print("初始化 MiniMax 客户端...")
    try:
        # 使用项目中的 MiniMaxClient，它使用正确的认证格式
        client = MiniMaxClient(
            base_url=minimax_base_url,
            api_key=minimax_api_key,
            model=minimax_model,
            timeout=120
        )

        print("发送预热请求...")

        # 预热请求 1
        print("  预热 1/2（非流式请求）...")
        output1 = client.chat(
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10
        )
        print(f"    ✓ 响应: {output1[:50]}...")

        # 预热请求 2
        print("  预热 2/2（多轮对话）...")
        messages2 = [
            {"role": "user", "content": "我叫小明"},
            {"role": "assistant", "content": "你好小明！"},
            {"role": "user", "content": "请用一句话介绍你自己"}
        ]
        output2 = client.chat(
            messages=messages2,
            max_tokens=50
        )
        print(f"    ✓ 响应: {output2[:50]}...")

        print("\n✅ MiniMax Judge API 验证成功！可以正常参与质量评估。\n")
        return True

    except Exception as e:
        print(f"\n❌ MiniMax Judge API 验证失败: {e}")
        print("\n⚠️  MiniMax Judge 将无法参与质量评估，但其他 Judge 仍可正常工作。\n")
        return False


def calculate_dimension_scores(model_names, summaries, dimension_weights, metrics_collector):
    """计算维度得分"""
    quality_scores = {}

    for model_name in model_names:
        model_summaries = [s for s in summaries if s.model_name == model_name]

        dimension_scores = {}
        for dimension in dimension_weights.keys():
            dimension_summaries = [s for s in model_summaries if s.category == dimension]
            if dimension_summaries:
                avg_speed = sum(s.speed_mean for s in dimension_summaries) / len(dimension_summaries)
                score = min(10.0, avg_speed / 10.0)
                dimension_scores[dimension] = score
            else:
                dimension_scores[dimension] = 0.0

        overall_score = sum(
            dimension_scores[d] * dimension_weights[d]
            for d in dimension_weights
        )

        quality_scores[model_name] = {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores
        }

        print(f"\n{model_name}:")
        print(f"  综合得分: {overall_score:.2f}/10")
        for dimension, score in dimension_scores.items():
            print(f"  - {dimension}: {score:.2f}/10")

    return quality_scores


# ============ 主函数 ============

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="统一评测脚本 - 支持 MiniMax 标准评测和原始对比测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行模式示例：
  python run_benchmark.py                    # 默认：标准模式（100个用例）
  python run_benchmark.py --mode preview     # 预测试模式（4个用例）
  python run_benchmark.py --mode original    # 原始对比测试模式（4个用例）
        """
    )

    parser.add_argument(
        '--mode',
        choices=['standard', 'preview', 'original', 'single'],
        default='standard',
        help='运行模式: standard(100个用例), preview(4个用例), original(原始对比), single(单用例)'
    )

    args = parser.parse_args()

    # 加载配置
    config = load_config("config.yaml")

    # 根据模式运行不同的测试
    if args.mode == 'standard':
        run_minimax_standard(config)
    elif args.mode == 'preview':
        run_minimax_preview(config)
    elif args.mode == 'original':
        run_original_test(config)
    elif args.mode == 'single':
        run_single_test(config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
