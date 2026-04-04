"""
集中式 CI 管线。

一次运行所有质量检查：架构合规 → 代码风格 → 文档健康 → 测试 → 覆盖率。
可通过 `python -m harness.ci` 运行。

退出码：0 = 全部通过，1 = 存在失败。
"""
from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class StageResult:
    name: str
    passed: bool
    output: str
    duration: float


def run_stage(name: str, cmd: list[str]) -> StageResult:
    """运行单个检查阶段。"""
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=120,
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        passed = False
        output = f"超时（120s）"
    except FileNotFoundError:
        passed = False
        output = f"命令未找到: {' '.join(cmd)}"
    duration = time.time() - start
    return StageResult(name, passed, output.strip(), duration)


def main() -> int:
    python = sys.executable
    stages: list[StageResult] = []

    # --- 阶段 1：架构合规 ---
    stages.append(run_stage(
        "架构合规",
        [python, "-m", "harness.lint.check_architecture"],
    ))

    # --- 阶段 2：代码风格 ---
    stages.append(run_stage(
        "代码风格",
        [python, "-m", "harness.lint.check_style"],
    ))

    # --- 阶段 3：文档健康 ---
    stages.append(run_stage(
        "文档健康",
        [python, "-m", "harness.lint.check_docs"],
    ))

    # --- 阶段 4：单元测试 ---
    stages.append(run_stage(
        "单元测试",
        [python, "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
    ))

    # --- 阶段 5：测试覆盖率 ---
    stages.append(run_stage(
        "测试覆盖率",
        [python, "-m", "pytest", "tests/", "--cov=src", "--cov-report=term-missing", "-q", "--no-header"],
    ))

    # --- 输出报告 ---
    print("=" * 60)
    print("CI 管线报告")
    print("=" * 60)

    all_passed = True
    for s in stages:
        icon = "PASS" if s.passed else "FAIL"
        print(f"\n[{icon}] {s.name} ({s.duration:.1f}s)")
        if not s.passed:
            all_passed = False
            # 输出失败详情（限制行数避免刷屏）
            lines = s.output.splitlines()
            for line in lines[:20]:
                print(f"      {line}")
            if len(lines) > 20:
                print(f"      ... ({len(lines) - 20} 行省略)")

    print("\n" + "=" * 60)
    if all_passed:
        print("结果：全部通过")
    else:
        failed = [s.name for s in stages if not s.passed]
        print(f"结果：{len(failed)} 项失败 — {', '.join(failed)}")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
