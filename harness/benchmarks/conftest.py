"""
性能基准测试公共 fixtures。

提供基准测试所需的通用配置和工具。
"""
import pytest


@pytest.fixture
def benchmark_config():
    """基准测试默认配置。"""
    return {
        "min_rounds": 100,
        "warmup": True,
        "warmup_iterations": 10,
    }
