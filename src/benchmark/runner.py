"""基准测试执行器"""

import os
import time
from typing import Dict, List, Any, Optional
from tqdm import tqdm
from dotenv import load_dotenv

from ..api.base_client import BaseClient
from ..api.openai_client import OpenAIClient
from ..api.anthropic_client import AnthropicClient
from .metrics_collector import MetricsCollector
from .test_result import TestResult
from ..quality.judge_manager import JudgeManager


class BenchmarkRunner:
    """基准测试执行器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化执行器

        Args:
            config: 配置字典
        """
        load_dotenv()

        self.config = config
        self.metrics_collector = MetricsCollector()
        self.clients: Dict[str, BaseClient] = {}

        # 初始化客户端
        self._init_clients()

        # 初始化质量评估
        quality_config = config.get("quality", {})
        self.judge_manager = JudgeManager(quality_config)
        self.quality_enabled = quality_config.get("enabled", False) and self.judge_manager.is_enabled()

        if self.quality_enabled:
            print(f"✓ 质量评估已启用 (Judge: {', '.join(self.judge_manager.get_enabled_judges())})")

    def _init_clients(self):
        """初始化所有 API 客户端"""
        api_configs = self.config.get("apis", {})

        for api_name, api_config in api_configs.items():
            # 从环境变量获取 API key
            api_key = os.getenv(api_config.get("api_key_env", ""))
            if not api_key:
                print(f"警告: 未找到 {api_name} 的 API key，跳过初始化")
                continue

            # 创建客户端 - 根据配置决定使用哪个协议
            # DeepSeek 使用 OpenAI 协议
            # GLM 使用 Anthropic 协议
            if api_name == "deepseek":
                client = OpenAIClient(
                    base_url=api_config["base_url"],
                    api_key=api_key,
                    model=api_config["model"],
                    max_retries=api_config.get("max_retries", 3),
                    timeout=api_config.get("timeout", 120)
                )
            elif api_name == "glm":
                client = AnthropicClient(
                    base_url=api_config["base_url"],
                    api_key=api_key,
                    model=api_config["model"],
                    max_retries=api_config.get("max_retries", 3),
                    timeout=api_config.get("timeout", 120)
                )
            else:
                print(f"警告: 未知的 API 名称: {api_name}")
                continue

            self.clients[api_name] = client
            print(f"✓ {api_name} 客户端初始化成功 (模型: {api_config['model']})")

        if not self.clients:
            raise ValueError("没有可用的 API 客户端，请检查配置和环境变量")

    def validate_connections(self) -> Dict[str, bool]:
        """
        验证所有客户端连接

        Returns:
            Dict: 每个客户端的连接状态
        """
        results = {}
        for name, client in self.clients.items():
            print(f"验证 {name} 连接...")
            results[name] = client.validate_connection()
            status = "✓ 成功" if results[name] else "✗ 失败"
            print(f"{name}: {status}")
        return results

    def run_test_case(
        self,
        test_case: Dict[str, Any],
        client_name: str,
        run_number: int
    ) -> TestResult:
        """
        运行单个测试用例

        Args:
            test_case: 测试用例字典
            client_name: 客户端名称
            run_number: 运行编号

        Returns:
            TestResult: 测试结果
        """
        client = self.clients[client_name]

        try:
            # 提取测试参数
            messages = [{"role": "user", "content": test_case["prompt"]}]
            parameters = test_case.get("parameters", {})

            # 运行流式请求
            metrics = client.stream_chat(
                messages=messages,
                **parameters
            )

            # 创建测试结果
            result = TestResult(
                model_name=client_name,
                test_name=test_case["name"],
                test_category=test_case["category"],
                run_number=run_number,
                ttft_ms=metrics.ttft_ms,
                total_time_ms=metrics.total_time_ms,
                generation_time_ms=metrics.generation_time_ms,
                output_tokens=metrics.output_tokens,
                tokens_per_second=metrics.tokens_per_second,
                inter_token_latency_ms=metrics.inter_token_latency_ms,
                output_text=metrics.text,
                success=True,
                parameters=parameters
            )

            # 质量评估（如果启用）
            if self.quality_enabled and result.success and result.output_text:
                try:
                    evaluations = self.judge_manager.evaluate_single_output(
                        output=result.output_text,
                        category=test_case["category"],
                        prompt=test_case["prompt"],
                        model_name=client_name,
                        test_name=test_case["name"]
                    )
                    result.quality_evaluations = evaluations
                except Exception as e:
                    print(f"  ⚠ 质量评估失败: {e}")

        except Exception as e:
            # 发生错误
            result = TestResult(
                model_name=client_name,
                test_name=test_case["name"],
                test_category=test_case["category"],
                run_number=run_number,
                ttft_ms=0.0,
                total_time_ms=0.0,
                generation_time_ms=0.0,
                output_tokens=0,
                tokens_per_second=0.0,
                inter_token_latency_ms=0.0,
                output_text="",
                success=False,
                error_message=str(e),
                parameters=test_case.get("parameters", {})
            )

        return result

    def run_benchmark(
        self,
        test_cases: List[Dict[str, Any]],
        show_progress: bool = True,
        progress_callback: Optional[callable] = None
    ) -> MetricsCollector:
        """
        运行完整基准测试

        Args:
            test_cases: 测试用例列表
            show_progress: 是否显示进度条
            progress_callback: 进度回调函数，参数为(已完成测试数, 总测试数)

        Returns:
            MetricsCollector: 指标收集器，包含所有结果
        """
        benchmark_config = self.config.get("benchmark", {})
        warmup_runs = benchmark_config.get("warmup_runs", 2)
        test_runs = benchmark_config.get("test_runs", 3)

        client_names = list(self.clients.keys())
        total_runs = len(test_cases) * len(client_names) * test_runs

        print(f"\n开始基准测试:")
        print(f"  - 测试用例: {len(test_cases)}")
        print(f"  - 模型: {', '.join(client_names)}")
        print(f"  - 预热运行: {warmup_runs} 次/模型")
        print(f"  - 正式运行: {test_runs} 次/测试")

        # 预热
        print("\n预热阶段...")
        for client_name in client_names:
            for i in range(warmup_runs):
                try:
                    client = self.clients[client_name]
                    client.stream_chat(
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=10
                    )
                    print(f"  {client_name} 预热 {i+1}/{warmup_runs} 完成")
                except Exception as e:
                    print(f"  {client_name} 预热 {i+1}/{warmup_runs} 失败: {e}")

        # 正式测试
        print(f"\n测试阶段 (共 {total_runs} 次运行)...")

        iterator = tqdm(
            enumerate(test_cases),
            desc="运行测试",
            disable=not show_progress
        )

        completed_tests = 0
        for idx, test_case in iterator:
            test_name = test_case["name"]
            category = test_case["category"]

            if show_progress:
                iterator.set_description(f"测试: {test_name}")

            for client_name in client_names:
                for run_num in range(1, test_runs + 1):
                    # 运行测试
                    result = self.run_test_case(test_case, client_name, run_num)

                    # 添加到收集器
                    self.metrics_collector.add_result(result)

                    # 如果失败，打印警告
                    if not result.success:
                        print(
                            f"  ✗ {client_name} - {test_name} (运行 {run_num}/{test_runs}) 失败: "
                            f"{result.error_message}"
                        )

            # 更新已完成测试数
            completed_tests += 1

            # 调用进度回调
            if progress_callback:
                progress_callback(completed_tests, len(test_cases), self.metrics_collector)

        print("\n✓ 基准测试完成")
        return self.metrics_collector

    def get_results(self) -> MetricsCollector:
        """
        获取指标收集器

        Returns:
            MetricsCollector: 指标收集器
        """
        return self.metrics_collector

    def get_model_names(self) -> List[str]:
        """
        获取所有模型名称

        Returns:
            List[str]: 模型名称列表
        """
        return list(self.clients.keys())
