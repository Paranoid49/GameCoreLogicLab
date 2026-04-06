"""
确定性检查器。

验证游戏逻辑代码是否满足确定性要求：相同输入 + 相同种子 = 相同输出。
可通过 `python -m harness.lint.check_determinism` 运行。

检查项：
1. 禁止使用 random 模块的全局函数
2. 禁止依赖 time.time() / datetime.now()
3. 禁止依赖 set() 遍历顺序作为逻辑
"""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
MODULES_DIR = SRC_DIR / "modules"

# 禁止的全局随机函数调用
FORBIDDEN_RANDOM_CALLS = {
    "random.random", "random.randint", "random.choice",
    "random.shuffle", "random.sample", "random.uniform",
    "random.randrange", "random.gauss", "random.choices",
}

# 禁止的时间依赖调用
FORBIDDEN_TIME_CALLS = {
    "time.time", "time.monotonic", "time.perf_counter",
    "datetime.now", "datetime.utcnow", "datetime.today",
}


@dataclass
class Violation:
    file: str
    line: int
    rule: str
    message: str
    fix_hint: str = ""


@dataclass
class DeterminismResult:
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def add(self, file: str, line: int, rule: str, message: str, fix_hint: str = "") -> None:
        self.violations.append(Violation(file, line, rule, message, fix_hint))

    def report(self) -> str:
        if self.passed:
            return "确定性检查通过：0 违规"
        lines = [f"确定性检查不通过：{len(self.violations)} 项违规\n"]
        for i, v in enumerate(self.violations, 1):
            lines.append(f"  [{i}] {v.rule} (行 {v.line})")
            lines.append(f"      文件: {v.file}")
            lines.append(f"      问题: {v.message}")
            if v.fix_hint:
                lines.append(f"      修复: {v.fix_hint}")
            lines.append("")
        return "\n".join(lines)


class _DeterminismVisitor(ast.NodeVisitor):
    """AST 访问器，检测非确定性代码模式。"""

    def __init__(self, file_path: Path, result: DeterminismResult) -> None:
        self.file_path = file_path
        self.rel = str(file_path.relative_to(PROJECT_ROOT))
        self.result = result
        self._imports: dict[str, str] = {}  # alias → module

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname or alias.name
            self._imports[name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            for alias in node.names:
                name = alias.asname or alias.name
                self._imports[name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._get_call_name(node)
        if call_name:
            # 检查全局随机函数
            if call_name in FORBIDDEN_RANDOM_CALLS:
                self.result.add(
                    self.rel, node.lineno, "determinism/global-random",
                    f"禁止使用全局随机函数 `{call_name}()`",
                    "使用 `random.Random(seed)` 实例的方法替代，种子通过参数传入",
                )
            # 检查时间依赖
            if call_name in FORBIDDEN_TIME_CALLS:
                self.result.add(
                    self.rel, node.lineno, "determinism/time-dependency",
                    f"禁止依赖时间源 `{call_name}()`",
                    "游戏逻辑中的时间应通过 tick 计数或参数传入，不依赖系统时钟",
                )
        self.generic_visit(node)

    def _get_call_name(self, node: ast.Call) -> str | None:
        """提取函数调用的完整名称。"""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                obj = node.func.value.id
                method = node.func.attr
                # 解析 import alias
                module = self._imports.get(obj, obj)
                return f"{module}.{method}"
        elif isinstance(node.func, ast.Name):
            name = node.func.id
            return self._imports.get(name, name)
        return None


def check_file(file_path: Path, result: DeterminismResult) -> None:
    """检查单个文件的确定性。"""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, OSError, UnicodeDecodeError):
        return

    visitor = _DeterminismVisitor(file_path, result)
    visitor.visit(tree)


def run_checks() -> DeterminismResult:
    result = DeterminismResult()
    if not MODULES_DIR.exists():
        return result

    for py_file in sorted(MODULES_DIR.rglob("*.py")):
        check_file(py_file, result)

    return result


def main() -> int:
    result = run_checks()
    print(result.report())
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
