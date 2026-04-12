# 模块模板

新模块的标准文件结构和接口规范。Generator Agent 创建新模块时必须遵循此模板。

## 目录结构

```
src/modules/{module_name}/
├── __init__.py              # 导出公共 API
├── models.py                # Pydantic 数据模型
├── interfaces.py            # ABC 接口定义
└── engine.py                # 核心逻辑实现

tests/modules/{module_name}/
├── __init__.py
├── test_engine.py           # 单元测试（单个方法级别）
├── test_scenarios.py        # 场景测试（多组件交互、真实游戏片段）
├── test_benchmark.py        # 性能基准测试
└── fixtures/                # 测试数据
    └── scenarios.py         # 预定义场景配置
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
from abc import abstractmethod
from common.interfaces import GameEngine
from .models import ExampleState


class I{ModuleName}Engine(GameEngine):
    """引擎接口，继承 GameEngine 基类，定义模块特有操作。"""

    @abstractmethod
    def initialize(self, config: ...) -> ExampleState:
        """初始化模块状态。"""
        ...

    @abstractmethod
    def step(self, state: ExampleState, action: ...) -> ExampleState:
        """执行一步操作，返回新状态。"""
        ...
```

### engine.py

```python
"""
{ModuleName} 核心引擎实现。
"""
from .interfaces import I{ModuleName}Engine
from .models import ExampleState


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
from modules.{module_name}.engine import {ModuleName}Engine


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
from modules.{module_name}.engine import {ModuleName}Engine


@pytest.fixture
def engine():
    return {ModuleName}Engine()


@pytest.mark.benchmark
def test_step_performance(benchmark, engine):
    """单步操作性能基准。"""
    state = engine.initialize(...)
    benchmark(engine.step, state, ...)
```

### tests/test_scenarios.py

```python
"""
{ModuleName} 场景测试。

模拟真实游戏片段，验证多组件交互下的系统行为。
"""
import pytest
from pathlib import Path
from harness.sim.runner import GameSimulation
from modules.{module_name}.engine import {ModuleName}Engine

REPLAY_DIR = Path(__file__).parent / "replays"


@pytest.fixture
def sim():
    engine = {ModuleName}Engine()
    simulation = GameSimulation(engine, replay_dir=REPLAY_DIR)
    # 注册不变量检查
    # simulation.add_invariant("守恒量", lambda before, after, actions: ...)
    return simulation


class TestScenario连续操作:
    """场景：单实体连续操作。"""

    def test_basic_combo(self, sim):
        config = ...  # 初始化配置
        actions = [
            [...],  # tick 0
            [...],  # tick 1
        ]
        result = sim.run(config, actions, seed=42, scenario_name="连续操作")
        assert result.passed, result.invariant_violations
        # 回放 JSON 已自动写入 replays/ 目录


class TestScenario多实体交互:
    """场景：多实体交互。"""

    def test_multi_entity_interaction(self, sim):
        # 多个实体同时行动
        ...


class TestScenario确定性:
    """场景：确定性验证。"""

    def test_determinism(self, sim):
        config = ...
        actions = [...]
        assert sim.run_determinism_check(config, actions, seed=42, runs=5)
```

### tests/fixtures/scenarios.py

```python
"""
{ModuleName} 预定义场景配置。

集中管理测试用的实体属性、技能参数等配置数据。
变量命名规则：大写开头（UPPER_SNAKE_CASE），会被 harness.fixtures 自动收集。
"""
from modules.{module_name}.models import ...  # 导入模块的数据模型

# --- 实体配置 ---
# HERO_WARRIOR = HeroConfig(name="战士", hp=1000, attack=80, ...)
# HERO_MAGE = HeroConfig(name="法师", hp=600, attack=40, ...)

# --- 技能/行为配置 ---
# SKILL_FIREBALL = SkillConfig(name="火球术", damage=200, cooldown=10, ...)

# --- 场景配置 ---
# SCENARIO_1V1 = {"config": ..., "actions": [...], "seed": 42}
# SCENARIO_TEAMFIGHT = {"config": ..., "actions": [...], "seed": 42}
```

### tests/fixtures/__init__.py

```python
"""Fixtures 包，由 harness.fixtures.discover_fixtures() 自动加载。"""
```

### tests/conftest.py（模块级）

```python
"""
{ModuleName} 测试公共 fixtures。

加载 fixtures/ 目录下的预定义数据，提供给所有测试使用。
"""
import pytest
from harness.fixtures import discover_fixtures

_FIXTURES = discover_fixtures("{module_name}")

@pytest.fixture
def fixtures():
    """返回该模块所有预定义测试数据。"""
    return _FIXTURES
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

## 范围声明
明确列出本模块覆盖和不覆盖的范围：
- **覆盖**：[列出所有包含的变体/维度/场景]
- **不覆盖**：[列出明确排除的内容及排除原因]
- **维度**：2D / 3D / 两者皆有

## 核心概念
定义该模块的关键术语和概念。

## 功能分级
### 核心功能（必须实现，不可关闭）
- [功能 1]：说明
- [功能 2]：说明

### 可选功能（配置项启用/禁用，默认关闭）
- [可选功能 1]：说明，配置项名称 `enable_xxx`
- [可选功能 2]：说明，配置项名称 `enable_yyy`

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

## 集成场景
描述 2-3 个模拟真实游戏片段的场景，用于场景测试。每个场景包含：
- 场景名称和描述（模拟什么情况）
- 参与的实体和初始状态
- 按 tick 排列的动作序列
- 全程应保持的不变量（如守恒量、状态约束）
- 最终预期结果

示例场景设计思路：
- 场景1：单实体连续操作（验证状态连续变更的正确性）
- 场景2：多实体同时交互（验证并发操作、目标选择、优先级处理）
- 场景3：极端边界（零值/极值输入、非法状态下的操作、同时触发的冲突事件）

## 性能目标
定义基准测试场景和性能阈值。

## 评估侧重
本模块的四维评估权重分配（默认 正确性40/架构25/质量20/性能15）。
说明为什么某个维度更重要，Evaluator 将据此调整评估重心。
```
