"""
文档健康检查器。

验证 docs/ 知识库的完整性、链接有效性和内容一致性。
可通过 `python -m harness.lint.check_docs` 运行。

检查项：
1. 必需文档存在
2. Markdown 内部链接有效（相对路径指向的文件存在）
3. 计划文档状态与目录一致（active/ 中无 completed 状态文档）
4. 模块是否有对应的规格文档
5. 规格文档与实际代码的一致性（接口名、模型名是否匹配）
6. 模块测试目录结构完整性（test_engine / test_scenarios / fixtures）
"""
from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
MODULES_DIR = PROJECT_ROOT / "src" / "modules"
TESTS_DIR = PROJECT_ROOT / "tests" / "modules"

REQUIRED_DOCS = [
    "docs/architecture.md",
    "docs/quality-standards.md",
    "docs/module-template.md",
]

_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
_STATUS_RE = re.compile(r"\*\*状态\*\*\s*:\s*(\w+)")


@dataclass
class Violation:
    file: str
    rule: str
    message: str
    fix_hint: str = ""


@dataclass
class DocsResult:
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def add(self, file: str, rule: str, message: str, fix_hint: str = "") -> None:
        self.violations.append(Violation(file, rule, message, fix_hint))

    def report(self) -> str:
        if self.passed:
            return "文档检查通过：0 问题"
        lines = [f"文档检查不通过：{len(self.violations)} 项问题\n"]
        for i, v in enumerate(self.violations, 1):
            lines.append(f"  [{i}] {v.rule}")
            lines.append(f"      文件: {v.file}")
            lines.append(f"      问题: {v.message}")
            if v.fix_hint:
                lines.append(f"      修复: {v.fix_hint}")
            lines.append("")
        return "\n".join(lines)


def check_required_docs(result: DocsResult) -> None:
    """检查必需文档是否存在。"""
    for doc in REQUIRED_DOCS:
        if not (PROJECT_ROOT / doc).exists():
            result.add(
                doc, "docs/missing-required",
                f"缺少必需文档: {doc}",
                f"创建 {doc}，参考已有文档格式",
            )


def check_internal_links(result: DocsResult) -> None:
    """检查 Markdown 文件中的相对链接是否有效。"""
    for md_file in DOCS_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(md_file.relative_to(PROJECT_ROOT))
        for match in _MD_LINK_RE.finditer(content):
            link_text, link_target = match.group(1), match.group(2)
            # 跳过外部链接和锚点
            if link_target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # 解析相对路径
            target_path = (md_file.parent / link_target.split("#")[0]).resolve()
            if not target_path.exists():
                result.add(
                    rel, "docs/broken-link",
                    f"链接 [{link_text}]({link_target}) 指向的文件不存在",
                    f"更新链接或创建目标文件: {link_target}",
                )

    # 也检查 CLAUDE.md 中的链接
    claude_md = PROJECT_ROOT / "CLAUDE.md"
    if claude_md.exists():
        try:
            content = claude_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        for match in _MD_LINK_RE.finditer(content):
            link_text, link_target = match.group(1), match.group(2)
            if link_target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = (PROJECT_ROOT / link_target.split("#")[0]).resolve()
            if not target_path.exists():
                result.add(
                    "CLAUDE.md", "docs/broken-link",
                    f"链接 [{link_text}]({link_target}) 指向的文件不存在",
                    f"更新链接或创建目标文件: {link_target}",
                )


def check_plan_status_consistency(result: DocsResult) -> None:
    """检查计划文档状态与所在目录是否一致。"""
    for subdir, expected_status in [("active", "active"), ("completed", "completed")]:
        plan_dir = DOCS_DIR / "plans" / subdir
        if not plan_dir.exists():
            continue
        for md_file in plan_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            match = _STATUS_RE.search(content)
            if match:
                actual_status = match.group(1)
                if actual_status != expected_status:
                    rel = str(md_file.relative_to(PROJECT_ROOT))
                    result.add(
                        rel, "docs/plan-status-mismatch",
                        f"文档状态为 '{actual_status}'，但位于 {subdir}/ 目录",
                        f"将文档移至 docs/plans/{actual_status}/ 或更新状态为 '{expected_status}'",
                    )


def check_module_spec_coverage(result: DocsResult) -> None:
    """检查每个已实现模块是否有对应的规格文档。"""
    if not MODULES_DIR.exists():
        return
    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        module_name = module_dir.name
        active = DOCS_DIR / "plans" / "active" / f"{module_name}.md"
        completed = DOCS_DIR / "plans" / "completed" / f"{module_name}.md"
        if not active.exists() and not completed.exists():
            result.add(
                f"src/modules/{module_name}/", "docs/missing-spec",
                f"模块 '{module_name}' 缺少规格文档",
                f"创建 docs/plans/active/{module_name}.md 或运行 /plan-module {module_name}",
            )


def check_spec_code_consistency(result: DocsResult) -> None:
    """检查规格文档中提到的类名是否在实际代码中存在。"""
    if not MODULES_DIR.exists():
        return

    class_name_re = re.compile(r"`(\w+Engine)`|`(I\w+)`|class\s+`?(\w+)`?\s*[:(（]")

    for plan_dir in [DOCS_DIR / "plans" / "active", DOCS_DIR / "plans" / "completed"]:
        if not plan_dir.exists():
            continue
        for spec_file in plan_dir.glob("*.md"):
            module_name = spec_file.stem
            module_dir = MODULES_DIR / module_name
            if not module_dir.exists():
                continue

            # 从规格中提取提到的类名
            try:
                spec_content = spec_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            spec_classes = set()
            for m in class_name_re.finditer(spec_content):
                name = m.group(1) or m.group(2) or m.group(3)
                if name:
                    spec_classes.add(name)

            if not spec_classes:
                continue

            # 从代码中提取实际定义的类名
            code_classes = set()
            for py_file in module_dir.rglob("*.py"):
                try:
                    tree = ast.parse(py_file.read_text(encoding="utf-8"))
                except (SyntaxError, OSError, UnicodeDecodeError):
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        code_classes.add(node.name)

            # 找出规格提到但代码中不存在的类
            missing = spec_classes - code_classes
            # 过滤掉明显不是本模块的类名（如公共层的类）
            common_classes = {"BaseModel", "ABC", "GameEngine", "EventBus", "Field"}
            missing -= common_classes

            for cls in sorted(missing):
                result.add(
                    str(spec_file.relative_to(PROJECT_ROOT)),
                    "docs/spec-code-drift",
                    f"规格中提到的类 `{cls}` 在模块代码中不存在",
                    f"在 src/modules/{module_name}/ 中实现 `{cls}`，或更新规格文档移除该引用",
                )


def check_test_structure(result: DocsResult) -> None:
    """检查模块测试目录是否包含必需的测试文件。"""
    if not MODULES_DIR.exists():
        return

    required_test_files = ["test_engine.py", "test_scenarios.py"]

    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        module_name = module_dir.name
        test_dir = TESTS_DIR / module_name

        if not test_dir.exists():
            result.add(
                f"tests/modules/{module_name}/", "docs/missing-test-dir",
                f"模块 '{module_name}' 缺少测试目录",
                f"创建 tests/modules/{module_name}/ 及必需的测试文件",
            )
            continue

        for test_file in required_test_files:
            if not (test_dir / test_file).exists():
                result.add(
                    f"tests/modules/{module_name}/", "docs/missing-test-file",
                    f"缺少必需测试文件: {test_file}",
                    f"创建 tests/modules/{module_name}/{test_file}，参考 docs/module-template.md",
                )

        # 检查 fixtures 目录
        fixtures_dir = test_dir / "fixtures"
        if not fixtures_dir.exists():
            result.add(
                f"tests/modules/{module_name}/", "docs/missing-fixtures",
                f"缺少 fixtures/ 测试数据目录",
                f"创建 tests/modules/{module_name}/fixtures/ 并添加场景配置数据",
            )


def run_checks() -> DocsResult:
    result = DocsResult()
    check_required_docs(result)
    check_internal_links(result)
    check_plan_status_consistency(result)
    check_module_spec_coverage(result)
    check_spec_code_consistency(result)
    check_test_structure(result)
    return result


def main() -> int:
    result = run_checks()
    print(result.report())
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
