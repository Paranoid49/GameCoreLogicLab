# 模块模板

新模块的标准文件结构和接口规范。Generator Agent 创建新模块时必须遵循此模板。

## 目录结构

```
src/modules/{module_name}/
├── __init__.py              # 导出公共 API
├── models.py                # Pydantic 数据模型
├── interfaces.py            # ABC 接口定义
└── v1_readable/
    ├── __init__.py
    └── engine.py            # 可读性优先实现

tests/modules/{module_name}/
├── __init__.py
├── test_engine.py           # 功能测试
└── test_benchmark.py        # 性能基准测试
```

## 文件模板

### models.py

```python
"""
{ModuleName} 数据模型。

定义该模块使用的所有数据结构。
"""
from pydantic import BaseModel, Field
from common.models import EntityId  # 按需导入公共类型


class ExampleState(BaseModel):
    """描述该模型的用途。"""
    id: EntityId
    # 字段定义...
```

### interfaces.py

```python
"""
{ModuleName} 接口定义。

定义引擎必须实现的契约。
"""
from abc import ABC, abstractmethod
from .models import ExampleState


class I{ModuleName}Engine(ABC):
    """引擎接口，定义核心操作。"""

    @abstractmethod
    def initialize(self, config: ...) -> ExampleState:
        """初始化模块状态。"""
        ...

    @abstractmethod
    def step(self, state: ExampleState, action: ...) -> ExampleState:
        """执行一步操作，返回新状态。"""
        ...
```

### v1_readable/engine.py

```python
"""
{ModuleName} 引擎 — 可读性优先实现。

优先考虑代码清晰度和可理解性。
"""
from ..interfaces import I{ModuleName}Engine
from ..models import ExampleState


class {ModuleName}Engine(I{ModuleName}Engine):
    """可读性优先的引擎实现。"""

    def initialize(self, config: ...) -> ExampleState:
        # 清晰的实现...
        ...

    def step(self, state: ExampleState, action: ...) -> ExampleState:
        # 清晰的实现...
        ...
```

### tests/test_engine.py

```python
"""
{ModuleName} 引擎功能测试。
"""
import pytest
from modules.{module_name}.v1_readable.engine import {ModuleName}Engine


@pytest.fixture
def engine():
    return {ModuleName}Engine()


class TestInitialize:
    def test_basic_initialization(self, engine):
        # 基本初始化测试...
        ...

    def test_edge_case(self, engine):
        # 边界条件测试...
        ...


class TestStep:
    def test_normal_step(self, engine):
        # 正常操作测试...
        ...

    def test_invalid_action(self, engine):
        # 异常输入测试...
        ...
```

### tests/test_benchmark.py

```python
"""
{ModuleName} 性能基准测试。
"""
import pytest
from modules.{module_name}.v1_readable.engine import {ModuleName}Engine


@pytest.fixture
def engine():
    return {ModuleName}Engine()


@pytest.mark.benchmark
def test_step_performance(benchmark, engine):
    """单步操作性能基准。"""
    state = engine.initialize(...)
    benchmark(engine.step, state, ...)
```

## 模块规格文档模板

Planner Agent 生成的规格文档应包含以下章节（存放于 `docs/plans/active/{module_name}.md`）：

```markdown
# {模块名称} 规格

- **创建日期**: YYYY-MM-DD
- **状态**: active
- **一句话描述**: ...

## 概述
该模块实现什么机制，用于什么类型的游戏，解决什么问题。

## 核心概念
定义该模块的关键术语和概念。

## 数据模型
列出所有 Pydantic 模型及其字段定义。

## 接口定义
列出引擎接口的所有方法签名及语义。

## 核心算法
描述关键算法的逻辑（伪代码或文字描述）。

## 边界条件与异常处理
列举所有需要处理的边界情况。

## 验收标准
具体的、可测试的验收条件列表。

## 性能目标
定义基准测试场景和性能阈值。

## 评估侧重
本模块的四维评估权重分配（默认 正确性40/架构25/质量20/性能15）。
说明为什么某个维度更重要，Evaluator 将据此调整评估重心。
```
