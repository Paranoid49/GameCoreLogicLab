"""
场景定义模型。

用于定义结构化的游戏测试场景，供场景测试使用。
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ScenarioStep(BaseModel):
    """场景中的一步操作。"""
    tick: int = Field(description="执行时机（第几个 tick）")
    description: str = Field(description="操作描述（人类可读）")
    actions: list[dict] = Field(description="该 tick 的动作列表（具体类型由模块定义）")


class Invariant(BaseModel):
    """场景需要验证的不变量。"""
    name: str = Field(description="不变量名称")
    description: str = Field(description="不变量描述")


class ExpectedOutcome(BaseModel):
    """场景的预期结果。"""
    description: str = Field(description="预期结果描述")
    check_field: str = Field(description="要检查的状态字段路径")
    operator: str = Field(description="比较运算符（eq/gt/lt/ge/le/ne/in/not_in）")
    value: object = Field(description="期望值")


class ScenarioDefinition(BaseModel):
    """
    游戏测试场景定义。

    一个场景模拟一段真实的游戏片段，如一场团战、一轮回合、一次技能连招。
    """
    name: str = Field(description="场景名称")
    description: str = Field(description="场景描述（模拟什么情况）")
    seed: int = Field(default=42, description="随机种子（确保可复现）")
    config: dict = Field(description="引擎初始化配置")
    steps: list[ScenarioStep] = Field(description="场景步骤序列")
    invariants: list[Invariant] = Field(default_factory=list, description="全程不变量")
    expected_outcomes: list[ExpectedOutcome] = Field(default_factory=list, description="最终结果预期")
