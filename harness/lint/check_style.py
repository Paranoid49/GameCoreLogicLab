"""
代码风格检查器。

检查命名约定、文件大小、函数长度等代码风格规则。
可通过 `python -m harness.lint.check_style` 运行。

检查项：
1. 类名必须 PascalCase
2. 函数/方法名必须 snake_case
3. 模块目录名必须 snake_case
4. 常量必须 UPPER_SNAKE_CASE
5. 单文件不超过 300 行
6. 单函数不超过 50 行
"""
from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
MODULES_DIR = SRC_DIR / "modules"

MAX_FILE_LINES = 300
MAX_FUNC_LINES = 50

_PASCAL_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
_SNAKE_RE = re.compile(r"^_?[a-z][a-z0-9_]*$")
_UPPER_SNAKE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
# 豁免：常见的 dunder 方法和测试名
_SNAKE_EXEMPT = {"__init__", "__str__", "__repr__", "__eq__", "__hash__", "__post_init__"}


@dataclass
class Violation:
    file: str
    line: int
    rule: str
    message: str
    fix_hint: str = ""


@dataclass
class StyleResult:
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def add(self, file: str, line: int, rule: str, message: str, fix_hint: str = "") -> None:
        self.violations.append(Violation(file, line, rule, message, fix_hint))

    def report(self) -> str:
        if self.passed:
            return "风格检查通过：0 违规"
        lines = [f"风格检查不通过：{len(self.violations)} 项违规\n"]
        for i, v in enumerate(self.violations, 1):
            lines.append(f"  [{i}] {v.rule} (行 {v.line})")
            lines.append(f"      文件: {v.file}")
            lines.append(f"      问题: {v.message}")
            if v.fix_hint:
                lines.append(f"      修复: {v.fix_hint}")
            lines.append("")
        return "\n".join(lines)


def check_file_size(file_path: Path, result: StyleResult) -> None:
    """检查文件行数是否超限。"""
    try:
        line_count = len(file_path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return
    if line_count > MAX_FILE_LINES:
        rel = file_path.relative_to(PROJECT_ROOT)
        result.add(
            str(rel), 1, "size/file-too-long",
            f"文件 {line_count} 行，超过 {MAX_FILE_LINES} 行上限",
            f"将文件拆分为多个职责单一的模块，例如把辅助函数提取到 utils.py",
        )


def check_naming_and_length(file_path: Path, result: StyleResult) -> None:
    """检查命名约定和函数长度。"""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, OSError, UnicodeDecodeError):
        return

    rel = str(file_path.relative_to(PROJECT_ROOT))

    for node in ast.walk(tree):
        # 类名: PascalCase
        if isinstance(node, ast.ClassDef):
            if not _PASCAL_RE.match(node.name) and not node.name.startswith("I"):
                # 允许 I 前缀的接口名如 ITurnOrderEngine
                if not (node.name.startswith("I") and _PASCAL_RE.match(node.name[1:])):
                    result.add(
                        rel, node.lineno, "naming/class-pascal-case",
                        f"类名 '{node.name}' 不符合 PascalCase 约定",
                        f"重命名为 '{''.join(w.capitalize() for w in node.name.split('_'))}'",
                    )

        # 函数/方法名: snake_case + 长度检查
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if name not in _SNAKE_EXEMPT and not name.startswith("__"):
                if not _SNAKE_RE.match(name):
                    result.add(
                        rel, node.lineno, "naming/func-snake-case",
                        f"函数名 '{name}' 不符合 snake_case 约定",
                        f"重命名为 '{_to_snake_case(name)}'",
                    )

            # 函数长度
            end_line = node.end_lineno or node.lineno
            func_lines = end_line - node.lineno + 1
            if func_lines > MAX_FUNC_LINES:
                result.add(
                    rel, node.lineno, "size/func-too-long",
                    f"函数 '{name}' 有 {func_lines} 行，超过 {MAX_FUNC_LINES} 行上限",
                    f"将 '{name}' 拆分为多个职责单一的小函数",
                )

        # 模块级常量: UPPER_SNAKE_CASE
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("_"):
                    continue  # 跳过私有变量
                if isinstance(target, ast.Name) and target.id.isupper():
                    if not _UPPER_SNAKE_RE.match(target.id):
                        result.add(
                            rel, node.lineno, "naming/const-upper-snake",
                            f"常量 '{target.id}' 不符合 UPPER_SNAKE_CASE 约定",
                            f"重命名为符合 UPPER_SNAKE_CASE 的形式",
                        )


def check_module_dir_names(result: StyleResult) -> None:
    """检查模块目录名是否为 snake_case。"""
    if not MODULES_DIR.exists():
        return
    for module_dir in MODULES_DIR.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        if not _SNAKE_RE.match(module_dir.name):
            result.add(
                str(module_dir.relative_to(PROJECT_ROOT)), 0,
                "naming/module-dir-snake-case",
                f"模块目录名 '{module_dir.name}' 不符合 snake_case 约定",
                f"重命名为 '{_to_snake_case(module_dir.name)}'",
            )


def _to_snake_case(name: str) -> str:
    """PascalCase/camelCase → snake_case。"""
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def run_checks() -> StyleResult:
    result = StyleResult()
    check_module_dir_names(result)

    for py_file in sorted(SRC_DIR.rglob("*.py")):
        check_file_size(py_file, result)
        check_naming_and_length(py_file, result)

    return result


def main() -> int:
    result = run_checks()
    print(result.report())
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
