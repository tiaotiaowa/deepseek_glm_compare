"""统一错误消息定义

提供中英文双语错误消息，便于国际化和统一管理。

设计原则：
    - 所有错误消息集中定义
    - 支持中英文双语
    - 使用格式化字符串支持动态参数

使用示例：
    from src.utils.error_messages import ErrorMessages

    # 获取中文错误消息
    error = ErrorMessages.get("CONNECTION_FAILED")

    # 获取英文错误消息
    error_en = ErrorMessages.get("CONNECTION_FAILED", lang="en")

    # 带参数的错误消息
    error = ErrorMessages.get("API_KEY_NOT_FOUND", lang="zh", api_name="DeepSeek")
"""


class ErrorMessages:
    """错误消息类

    提供所有错误消息的统一访问接口，支持中英文双语。
    """

    # ========================================================================
    # 连接错误
    # ========================================================================

    CONNECTION_FAILED = "连接验证失败"
    CONNECTION_FAILED_EN = "Connection validation failed"

    CONNECTION_TIMEOUT = "连接超时"
    CONNECTION_TIMEOUT_EN = "Connection timeout"

    # ========================================================================
    # API 错误
    # ========================================================================

    STREAM_REQUEST_FAILED = "流式请求出错"
    STREAM_REQUEST_FAILED_EN = "Streaming request failed"

    NON_STREAM_REQUEST_FAILED = "非流式聊天请求失败"
    NON_STREAM_REQUEST_FAILED_EN = "Non-streaming chat request failed"

    API_RATE_LIMIT_EXCEEDED = "API 请求速率限制"
    API_RATE_LIMIT_EXCEEDED_EN = "API rate limit exceeded"

    API_QUOTA_EXCEEDED = "API 配额已用完"
    API_QUOTA_EXCEEDED_EN = "API quota exceeded"

    # ========================================================================
    # 配置错误
    # ========================================================================

    API_KEY_NOT_FOUND = "未找到 {api_name} 的 API key，请检查环境变量 {env_var}"
    API_KEY_NOT_FOUND_EN = "API key not found for {api_name}, please check environment variable {env_var}"

    CONFIG_MISSING_SECTION = "配置缺少必需的部分 '{section}'"
    CONFIG_MISSING_SECTION_EN = "Configuration missing required section '{section}'"

    CONFIG_INVALID_VALUE = "配置项 '{key}' 的值无效: {value}"
    CONFIG_INVALID_VALUE_EN = "Invalid value for configuration key '{key}': {value}"

    CONFIG_FILE_NOT_FOUND = "配置文件未找到: {path}"
    CONFIG_FILE_NOT_FOUND_EN = "Configuration file not found: {path}"

    # ========================================================================
    # Judge 错误
    # ========================================================================

    JUDGE_INIT_FAILED = "Judge 初始化失败: {judge_name}"
    JUDGE_INIT_FAILED_EN = "Judge initialization failed: {judge_name}"

    JUDGE_EVALUATION_FAILED = "Judge 评估出错: {judge_name}"
    JUDGE_EVALUATION_FAILED_EN = "Judge evaluation failed: {judge_name}"

    JUDGE_RESPONSE_PARSE_ERROR = "Judge 响应解析失败"
    JUDGE_RESPONSE_PARSE_ERROR_EN = "Failed to parse Judge response"

    JUDGE_NOT_AVAILABLE = "Judge 不可用: {judge_name}"
    JUDGE_NOT_AVAILABLE_EN = "Judge not available: {judge_name}"

    # ========================================================================
    # 测试错误
    # ========================================================================

    TEST_CASE_NOT_FOUND = "未找到测试用例: {test_name}"
    TEST_CASE_NOT_FOUND_EN = "Test case not found: {test_name}"

    TEST_EXECUTION_FAILED = "测试执行失败: {test_name}"
    TEST_EXECUTION_FAILED_EN = "Test execution failed: {test_name}"

    TEST_TIMEOUT = "测试超时: {test_name}"
    TEST_TIMEOUT_EN = "Test timeout: {test_name}"

    # ========================================================================
    # 报告错误
    # ========================================================================

    REPORT_GENERATION_FAILED = "报告生成失败"
    REPORT_GENERATION_FAILED_EN = "Report generation failed"

    REPORT_SAVE_FAILED = "报告保存失败: {path}"
    REPORT_SAVE_FAILED_EN = "Failed to save report: {path}"

    # ========================================================================
    # 数据错误
    # ========================================================================

    INVALID_DATA_FORMAT = "无效的数据格式"
    INVALID_DATA_FORMAT_EN = "Invalid data format"

    MISSING_REQUIRED_FIELD = "缺少必需字段: {field}"
    MISSING_REQUIRED_FIELD_EN = "Missing required field: {field}"

    DATA_VALIDATION_FAILED = "数据验证失败: {reason}"
    DATA_VALIDATION_FAILED_EN = "Data validation failed: {reason}"

    @classmethod
    def get(cls, key: str, lang: str = "zh", **kwargs) -> str:
        """获取错误消息

        Args:
            key: 消息键（类属性名）
            lang: 语言 ("zh" 或 "en")
            **kwargs: 格式化参数

        Returns:
            str: 格式化的错误消息

        Examples:
            >>> ErrorMessages.get("CONNECTION_FAILED")
            '连接验证失败'

            >>> ErrorMessages.get("CONNECTION_FAILED", lang="en")
            'Connection validation failed'

            >>> ErrorMessages.get("API_KEY_NOT_FOUND", api_name="DeepSeek", env_var="DEEPSEEK_API_KEY")
            '未找到 DeepSeek 的 API key，请检查环境变量 DEEPSEEK_API_KEY'
        """
        # 根据语言选择后缀
        suffix = "_EN" if lang == "en" else ""

        # 获取消息模板
        message_key = f"{key}{suffix}"
        message = getattr(cls, message_key, key)

        # 如果没有找到指定语言的版本，回退到默认版本
        if message == key and suffix:
            message = getattr(cls, key, key)

        # 格式化消息
        try:
            return message.format(**kwargs) if kwargs else message
        except (KeyError, ValueError):
            # 格式化失败，返回未格式化的消息
            return message
