"""
回放数据处理与 CLI 入口。

支持文本回放和 HTML 可视化生成。
用法：
    python -m harness.sim.replay path/to/replay.json          # 终端文本回放
    python -m harness.sim.replay path/to/replay.json --html    # 生成 HTML 并打开浏览器
"""
from __future__ import annotations

import json
import sys
import webbrowser
from pathlib import Path

_VIEWER_TEMPLATE = Path(__file__).parent.parent / "viewer" / "template.html"


def load_replay(path: str | Path) -> dict:
    """加载回放 JSON 文件。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def text_replay(data: dict) -> str:
    """将回放数据转为人类可读的文本战报。"""
    lines = []
    lines.append(f"=== 回放：共 {data['total_ticks']} ticks ===\n")

    for tick in data["ticks"]:
        lines.append(f"[tick {tick['tick']}]")

        # 事件描述
        for event in tick.get("events", []):
            lines.append(f"  > {event}")

        # 状态变化 diff
        before = tick["state_before"]
        after = tick["state_after"]
        diffs = _diff_dict(before, after)
        for diff in diffs:
            lines.append(f"  {diff}")

        lines.append("")

    # 不变量违反
    violations = data.get("invariant_violations", [])
    if violations:
        lines.append("!!! 不变量违反 !!!")
        for v in violations:
            lines.append(f"  - {v}")
        lines.append("")

    status = "通过" if data.get("passed", True) else "未通过"
    lines.append(f"=== 结果：{status} ===")
    return "\n".join(lines)


def _diff_dict(before: dict, after: dict, prefix: str = "") -> list[str]:
    """递归 diff 两个字典，返回变化描述列表。"""
    diffs = []
    all_keys = set(list(before.keys()) + list(after.keys()))
    for key in sorted(all_keys):
        path = f"{prefix}.{key}" if prefix else key
        val_b = before.get(key)
        val_a = after.get(key)
        if val_b == val_a:
            continue
        if isinstance(val_b, dict) and isinstance(val_a, dict):
            diffs.extend(_diff_dict(val_b, val_a, path))
        else:
            diffs.append(f"  {path}: {val_b} → {val_a}")
    return diffs


def generate_html(data: dict, output_path: str | Path) -> Path:
    """将回放数据注入 HTML 模板，生成自包含的可视化文件。"""
    output_path = Path(output_path)
    template = _VIEWER_TEMPLATE.read_text(encoding="utf-8")
    json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    html = template.replace("/*__REPLAY_DATA__*/", f"const REPLAY_DATA = {json_str};")
    output_path.write_text(html, encoding="utf-8")
    return output_path


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="游戏回放查看器")
    parser.add_argument("file", help="回放 JSON 文件路径")
    parser.add_argument("--html", action="store_true", help="生成 HTML 并在浏览器中打开")
    args = parser.parse_args()

    replay_path = Path(args.file)
    if not replay_path.exists():
        print(f"文件不存在：{replay_path}", file=sys.stderr)
        return 1

    data = load_replay(replay_path)

    if args.html:
        html_path = replay_path.with_suffix(".html")
        generate_html(data, html_path)
        print(f"已生成：{html_path}")
        webbrowser.open(str(html_path.resolve()))
    else:
        print(text_replay(data))

    return 0


if __name__ == "__main__":
    sys.exit(main())
