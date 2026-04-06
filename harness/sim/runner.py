"""
游戏模拟运行器。

提供 tick-by-tick 的游戏循环基础设施，用于场景测试。
模块的场景测试通过继承 GameSimulation 并提供引擎实例来运行。
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from common.interfaces import GameEngine

TState = TypeVar("TState", bound=BaseModel)
TAction = TypeVar("TAction", bound=BaseModel)
TConfig = TypeVar("TConfig", bound=BaseModel)


@dataclass
class TickRecord:
    """单个 tick 的记录。"""
    tick: int
    actions: list
    events: list[str]
    state_before: BaseModel
    state_after: BaseModel


@dataclass
class SimulationResult:
    """模拟运行结果。"""
    total_ticks: int
    final_state: BaseModel
    history: list[TickRecord]
    invariant_violations: list[str] = field(default_factory=list)
    passed: bool = True

    def add_violation(self, description: str) -> None:
        self.invariant_violations.append(description)
        self.passed = False

    def to_replay_dict(self) -> dict[str, Any]:
        """将结果转为可序列化的回放字典。"""
        ticks = []
        for record in self.history:
            ticks.append({
                "tick": record.tick,
                "events": record.events,
                "state_before": record.state_before.model_dump(),
                "state_after": record.state_after.model_dump(),
            })
        return {
            "total_ticks": self.total_ticks,
            "final_state": self.final_state.model_dump(),
            "ticks": ticks,
            "invariant_violations": self.invariant_violations,
            "passed": self.passed,
        }

    def export_json(self, path: str | Path) -> Path:
        """导出回放 JSON 文件。"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_replay_dict(), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        return path


class GameSimulation(Generic[TState, TAction, TConfig]):
    """
    游戏模拟基类。

    提供 tick-by-tick 的游戏循环，支持：
    - 种子化随机数（确保确定性）
    - 状态历史记录（含人类可读事件描述）
    - 不变量验证
    - 回放数据自动导出

    用法：
        engine = MyEngine()
        sim = GameSimulation(engine, replay_dir="tests/modules/xxx/replays")
        result = sim.run(config, action_sequence, seed=42, scenario_name="基础场景")
        # 回放 JSON 自动写入 replay_dir
    """

    def __init__(
        self,
        engine: GameEngine[TState, TAction, TConfig],
        replay_dir: str | Path | None = None,
    ) -> None:
        self.engine = engine
        self.replay_dir = Path(replay_dir) if replay_dir else None
        self._invariant_checks: list[tuple[str, callable]] = []

    def add_invariant(self, name: str, check_fn: callable) -> None:
        """
        注册不变量检查函数。

        check_fn 接收 (state_before, state_after, actions) 三个参数，
        返回 True 表示不变量成立，返回 False 或抛出异常表示违反。
        """
        self._invariant_checks.append((name, check_fn))

    def run(
        self,
        config: TConfig,
        action_sequence: list[list[TAction]],
        seed: int = 0,
        scenario_name: str = "default",
    ) -> SimulationResult:
        """
        运行完整模拟。

        参数：
            config: 引擎初始化配置
            action_sequence: 每个 tick 的动作列表
            seed: 随机种子（确保确定性）
            scenario_name: 场景名称（用于回放文件命名）

        返回：
            SimulationResult 包含历史、不变量违反和最终状态。
            如果设置了 replay_dir，回放 JSON 自动写入。
        """
        rng = random.Random(seed)  # noqa: F841 — 供子类使用
        state = self.engine.initialize(config)
        history: list[TickRecord] = []

        for tick_idx, actions in enumerate(action_sequence):
            state_before = state.model_copy(deep=True)

            # 采集事件描述：优先 __str__，fallback 到 repr
            events = [str(action) for action in actions]

            for action in actions:
                state = self.engine.step(state, action)

            record = TickRecord(
                tick=tick_idx,
                actions=actions,
                events=events,
                state_before=state_before,
                state_after=state.model_copy(deep=True),
            )
            history.append(record)

        result = SimulationResult(
            total_ticks=len(action_sequence),
            final_state=state,
            history=history,
        )

        # 逐 tick 验证不变量
        for record in history:
            for inv_name, check_fn in self._invariant_checks:
                try:
                    ok = check_fn(record.state_before, record.state_after, record.actions)
                    if not ok:
                        result.add_violation(
                            f"tick {record.tick}: 不变量 '{inv_name}' 违反"
                        )
                except Exception as e:
                    result.add_violation(
                        f"tick {record.tick}: 不变量 '{inv_name}' 检查异常 — {e}"
                    )

        # 自动导出回放 JSON
        if self.replay_dir:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            replay_path = self.replay_dir / f"{scenario_name}_{ts}.json"
            result.export_json(replay_path)

        return result

    def run_determinism_check(
        self,
        config: TConfig,
        action_sequence: list[list[TAction]],
        seed: int = 0,
        runs: int = 3,
    ) -> bool:
        """
        确定性验证：相同输入运行多次，结果必须完全一致。

        返回 True 表示确定性成立。
        """
        results = []
        for _ in range(runs):
            result = self.run(config, action_sequence, seed=seed)
            results.append(result.final_state.model_dump())

        baseline = results[0]
        return all(r == baseline for r in results[1:])
