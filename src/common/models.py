"""
公共数据模型。

定义跨模块共享的基础数据类型。模块专有类型应定义在各模块内部。
"""
from __future__ import annotations

from enum import Enum
from typing import NewType

from pydantic import BaseModel, Field

# --- 基础类型 ---

EntityId = NewType("EntityId", str)
Timestamp = NewType("Timestamp", int)


# --- 公共枚举 ---

class DamageType(str, Enum):
    """伤害类型。"""
    PHYSICAL = "physical"
    MAGICAL = "magical"
    TRUE = "true"
    PURE = "pure"


# --- 公共数据结构 ---

class Position(BaseModel):
    """2D 坐标位置。"""
    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other: Position) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class StatBlock(BaseModel):
    """通用属性数值块。"""
    hp: int = Field(ge=0, description="生命值")
    max_hp: int = Field(gt=0, description="最大生命值")
    attack: int = Field(ge=0, default=0, description="攻击力")
    defense: int = Field(ge=0, default=0, description="防御力")
    speed: int = Field(ge=0, default=0, description="速度")

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> StatBlock:
        """返回受到伤害后的新 StatBlock（不可变风格）。"""
        return self.model_copy(update={"hp": max(0, self.hp - amount)})

    def heal(self, amount: int) -> StatBlock:
        """返回治疗后的新 StatBlock。"""
        return self.model_copy(update={"hp": min(self.max_hp, self.hp + amount)})
