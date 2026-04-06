"""
测试 Fixtures 加载器。

自动发现并加载各模块 tests/modules/{name}/fixtures/ 下的测试数据。
提供统一的 fixture 注册和访问机制。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TESTS_DIR = _PROJECT_ROOT / "tests" / "modules"


def discover_fixtures(module_name: str) -> dict[str, Any]:
    """
    加载指定模块的 fixtures 数据。

    查找 tests/modules/{module_name}/fixtures/ 下所有 .py 文件，
    收集其中所有大写开头的变量作为 fixture 数据。

    返回：
        {"HERO_WARRIOR": {...}, "SKILL_FIREBALL": {...}, ...}
    """
    fixtures_dir = _TESTS_DIR / module_name / "fixtures"
    if not fixtures_dir.exists():
        return {}

    collected: dict[str, Any] = {}
    for py_file in sorted(fixtures_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue

        # 动态导入 fixture 模块
        module_path = f"tests.modules.{module_name}.fixtures.{py_file.stem}"
        # 确保 src/ 在 sys.path 中
        src_dir = str(_PROJECT_ROOT / "src")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        try:
            mod = importlib.import_module(module_path)
        except ImportError:
            # 尝试直接从文件加载
            spec = importlib.util.spec_from_file_location(module_path, py_file)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            else:
                continue

        # 收集大写开头的变量（约定为 fixture 数据）
        for name in dir(mod):
            if name[0].isupper() and not name.startswith("__"):
                collected[name] = getattr(mod, name)

    return collected
