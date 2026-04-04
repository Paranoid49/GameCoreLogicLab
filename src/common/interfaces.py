"""
公共接口定义。

定义所有游戏模块引擎共享的抽象基类。各模块应继承这些接口并实现具体逻辑。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

# 泛型类型变量：状态、动作、配置
TState = TypeVar("TState", bound=BaseModel)
TAction = TypeVar("TAction", bound=BaseModel)
TConfig = TypeVar("TConfig", bound=BaseModel)


class GameEngine(ABC, Generic[TState, TAction, TConfig]):
    """
    游戏引擎基类。

    所有模块的引擎实现必须继承此基类。
    泛型参数：
        TState  — 游戏状态类型
        TAction — 玩家/系统动作类型
        TConfig — 引擎配置类型
    """

    @abstractmethod
    def initialize(self, config: TConfig) -> TState:
        """根据配置创建初始游戏状态。"""
        ...

    @abstractmethod
    def step(self, state: TState, action: TAction) -> TState:
        """执行一个动作，返回新状态。状态应为不可变风格（返回新对象）。"""
        ...

    @abstractmethod
    def is_terminal(self, state: TState) -> bool:
        """判断当前状态是否为终态（游戏结束）。"""
        ...

    @abstractmethod
    def get_valid_actions(self, state: TState) -> list[TAction]:
        """获取当前状态下所有合法动作。"""
        ...


class EventBus(ABC):
    """
    事件总线接口。

    用于模块内部的事件驱动通信。
    """

    @abstractmethod
    def emit(self, event_type: str, payload: Any = None) -> None:
        """发送事件。"""
        ...

    @abstractmethod
    def on(self, event_type: str, handler: Any) -> None:
        """注册事件处理器。"""
        ...

    @abstractmethod
    def off(self, event_type: str, handler: Any) -> None:
        """移除事件处理器。"""
        ...
