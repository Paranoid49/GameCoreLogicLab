"""
架构合规检查器。

验证项目代码是否遵循 docs/architecture.md 中定义的分层和依赖规则。
可通过 `python -m harness.lint.check_architecture` 运行。

检查项：
1. 模块目录结构完整性（必需文件存在）
2. 禁止的跨模块导入
3. 分层依赖方向正确性
4. 引擎类是否实现了对应接口
"""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
MODULES_DIR = SRC_DIR / "modules"

# 模块内必需文件
REQUIRED_FILES = ["__init__.py", "models.py", "interfaces.py", "engine.py"]

# 分层顺序（索引越小越底层）
LAYER_ORDER = {
    "models": 0,
    "interfaces": 1,
    "engine": 2,
    "simulation": 3,
}


@dataclass
class Violation:
    """单条违规记录。"""
    file: str
    rule: str
    message: str
    fix_hint: str = ""


@dataclass
class CheckResult:
    """检查结果。"""
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def add(self, file: str, rule: str, message: str, fix_hint: str = "") -> None:
        self.violations.append(Violation(file, rule, message, fix_hint))

    def report(self) -> str:
        if self.passed:
            return "架构检查通过：0 违规"
        lines = [f"架构检查不通过：{len(self.violations)} 项违规\n"]
        for i, v in enumerate(self.violations, 1):
            lines.append(f"  [{i}] {v.rule}")
            lines.append(f"      文件: {v.file}")
            lines.append(f"      问题: {v.message}")
            if v.fix_hint:
                lines.append(f"      修复: {v.fix_hint}")
            lines.append("")
        return "\n".join(lines)


def _get_imports(file_path: Path) -> list[str]:
    """解析 Python 文件，提取所有 import 的模块路径。"""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _classify_layer(file_path: Path) -> str | None:
    """根据文件路径判断所属层级。"""
    name = file_path.stem
    if name == "models":
        return "models"
    if name == "interfaces":
        return "interfaces"
    if name == "engine":
        return "engine"
    if name == "simulation" or name.startswith("sim_"):
        return "simulation"
    return None


def check_module_structure(module_dir: Path, result: CheckResult) -> None:
    """检查模块目录结构完整性。"""
    module_name = module_dir.name
    rel = module_dir.relative_to(PROJECT_ROOT)

    for required in REQUIRED_FILES:
        if not (module_dir / required).exists():
            result.add(
                str(rel),
                "structure/missing-file",
                f"缺少必需文件: {required}",
                f"创建 {rel / required}，参考 docs/module-template.md",
            )


def check_cross_module_imports(module_dir: Path, result: CheckResult) -> None:
    """检查是否存在跨模块直接导入。"""
    module_name = module_dir.name

    for py_file in module_dir.rglob("*.py"):
        rel = py_file.relative_to(PROJECT_ROOT)
        for imp in _get_imports(py_file):
            # 检查是否导入了其他模块
            if imp.startswith("modules.") or imp.startswith("src.modules."):
                parts = imp.replace("src.", "").split(".")
                if len(parts) >= 2 and parts[1] != module_name:
                    result.add(
                        str(rel),
                        "dependency/cross-module",
                        f"禁止跨模块导入: {imp}",
                        f"通过 src/common/ 的公共接口通信，不要直接导入 modules.{parts[1]}",
                    )


def check_layer_direction(module_dir: Path, result: CheckResult) -> None:
    """检查分层依赖方向是否正确（只允许上层依赖下层）。"""
    module_name = module_dir.name

    for py_file in module_dir.rglob("*.py"):
        source_layer = _classify_layer(py_file)
        if source_layer is None:
            continue

        source_order = LAYER_ORDER.get(source_layer, -1)
        rel = py_file.relative_to(PROJECT_ROOT)

        for imp in _get_imports(py_file):
            # 只检查模块内部的相对引用
            imp_parts = imp.split(".")
            for target_layer_name, target_order in LAYER_ORDER.items():
                if target_layer_name in imp_parts and target_order > source_order:
                    result.add(
                        str(rel),
                        "dependency/layer-direction",
                        f"{source_layer} 层不允许依赖 {target_layer_name} 层（依赖方向必须向下）",
                        f"重构代码，让 {target_layer_name} 的逻辑通过接口或参数传入",
                    )


def check_src_harness_boundary(result: CheckResult) -> None:
    """检查业务代码是否误依赖 harness/ 或 tests/。"""
    for py_file in SRC_DIR.rglob("*.py"):
        rel = py_file.relative_to(PROJECT_ROOT)
        for imp in _get_imports(py_file):
            if imp.startswith("harness"):
                result.add(
                    str(rel),
                    "dependency/src-harness",
                    f"业务代码不可依赖 harness: {imp}",
                    "将需要共享的工具移入 src/common/",
                )
            if imp.startswith("tests"):
                result.add(
                    str(rel),
                    "dependency/src-tests",
                    f"业务代码不可依赖 tests: {imp}",
                    "将测试工具移入 tests/conftest.py 或 harness/",
                )


def run_checks() -> CheckResult:
    """运行所有架构检查。"""
    result = CheckResult()

    if not MODULES_DIR.exists():
        return result

    # 全局检查
    check_src_harness_boundary(result)

    # 逐模块检查
    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        check_module_structure(module_dir, result)
        check_cross_module_imports(module_dir, result)
        check_layer_direction(module_dir, result)

    return result


def main() -> int:
    result = run_checks()
    print(result.report())
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
