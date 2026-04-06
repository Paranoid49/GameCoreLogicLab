# 架构规范

## 总体原则

GameCoreLogicLab 的每个游戏模块是一个独立的逻辑单元，模块间通过 `src/common/` 提供的公共接口和数据模型通信，禁止直接跨模块导入。

## 分层结构

每个模块内部必须遵循以下分层，依赖方向严格单向向下：

```
┌─────────────────────┐
│   Simulation 模拟    │  ← 可选，用于验证和演示
├─────────────────────┤
│   Engine 引擎        │  ← 核心逻辑实现
├─────────────────────┤
│   Interfaces 接口    │  ← 抽象基类，定义引擎契约
├─────────────────────┤
│   Models 数据模型    │  ← Pydantic 模型，纯数据定义
└─────────────────────┘
```

- **Models**：使用 Pydantic BaseModel，定义该模块的数据结构。可依赖 `src/common/models.py` 中的公共类型。
- **Interfaces**：使用 ABC，定义引擎必须实现的方法签名。可依赖本模块 Models 和 `src/common/interfaces.py`。
- **Engine**：核心逻辑实现。实现本模块的 Interfaces。可依赖本模块 Models、Interfaces。
- **Simulation**：可选。用于运行模拟、演示或交互式验证。可依赖本模块所有层。

## 模块目录结构

```
src/modules/{module_name}/
├── __init__.py
├── models.py              # 数据模型
├── interfaces.py          # 接口定义
├── v1_readable/
│   ├── __init__.py
│   └── engine.py          # 可读性优先实现
└── v2_optimized/          # 可选：性能优先实现
    ├── __init__.py
    └── engine.py
```

## 依赖规则

### 允许的依赖

| 源 | 可依赖 |
|---|---|
| 任何模块 | `src/common/*` |
| Models | `src/common/models` |
| Interfaces | 本模块 Models, `src/common/interfaces` |
| Engine | 本模块 Models + Interfaces |
| Simulation | 本模块任意层 |
| Tests | 本模块任意层, `src/common/*`, `pytest`, `harness/benchmarks` |

### 禁止的依赖

- `src/modules/A/` → `src/modules/B/`（模块间禁止直接导入）
- Engine → Simulation（下层不可依赖上层）
- `src/` → `harness/`（业务代码不可依赖工具代码）
- `src/` → `tests/`（业务代码不可依赖测试代码）

## 公共层 src/common/

公共层提供跨模块共享的基础设施：

- `models.py`：公共数据类型（如 EntityId、Timestamp、Position 等）
- `interfaces.py`：公共抽象基类（如 GameEngine 基类、EventBus 接口）

公共层应保持精简，只放真正被多个模块共享的内容。单个模块独有的类型应定义在模块内部。

### 公共层演进规则

当新模块需要与已有模块交互时，**共享接口必须提升到 common/**：

1. **识别依赖**：Planner 在规划阶段扫描已有模块，识别新模块需要的外部能力
2. **提升接口**：将共享的数据类型或接口从具体模块提升到 `common/`
3. **不破坏现有**：提升操作不可修改已有模块的行为，只提取接口

示例：技能系统（skill_system）需要伤害计算能力
- 错误做法：`from modules.damage_calc import calc_damage`（跨模块直接导入）
- 正确做法：在 `common/interfaces.py` 定义 `IDamageCalculator` 接口，两个模块各自实现或依赖该接口

### 模块间通信模式

模块间交互只允许以下两种方式：

**方式 1：共享数据模型**
- 两个模块使用 `common/models.py` 中的相同类型
- 模块 A 输出 common 类型，模块 B 接受 common 类型
- 模块间无直接依赖，通过数据流解耦

**方式 2：依赖注入**
- 在 `common/interfaces.py` 定义抽象接口
- 模块 A 实现该接口，模块 B 的引擎接受接口实例作为参数
- 组合在使用侧（测试或模拟运行器中）完成

## 确定性要求

游戏核心逻辑必须满足确定性：**相同输入 + 相同种子 = 完全相同的输出**。

规则：
- 含随机性的逻辑（暴击、闪避、掉落）必须接受 `random.Random` 实例或种子参数
- 禁止使用 `random` 模块的全局函数（`random.random()`、`random.choice()` 等）
- 禁止依赖 `time.time()`、`datetime.now()` 等时间源
- 禁止依赖 `set()` 遍历顺序作为逻辑依据（虽然 Python 3.7+ dict 有序，但 set 无序）
- 引擎的 `step()` 方法必须是纯函数风格：只依赖输入参数和内部状态，不依赖外部环境

## 可观测性约定

### 回放数据

模拟运行器（`harness/sim/runner.py`）自动记录每个 tick 的状态快照和事件描述，支持导出为标准 JSON 回放文件。

- **事件描述来源**：Action 模型的 `__str__` 方法。建议所有 Action 模型实现 `__str__`，返回人类可读的事件描述
- **状态序列化**：Pydantic 的 `model_dump()` 自动处理，无需额外代码
- **回放文件位置**：`tests/modules/{name}/replays/`（已 .gitignore 排除）

### 可视化层级

回放查看器（`harness/viewer/template.html`）自动检测状态数据类型，渐进渲染：

1. **基础层**（始终存在）：时间轴 + 播放控制 + 事件日志 + 状态面板
2. **数值层**（自动检测 int/float 字段）：折线图展示数值随 tick 变化
3. **空间层**（自动检测 Position 字段）：2D 画布渲染实体位置和运动轨迹
4. **自定义层**（可选）：模块提供 `render.js` 扩展渲染逻辑

### Action 模型的 `__str__` 建议

```python
class SomeAction(BaseModel):
    action_type: str
    source: EntityId
    target: EntityId

    def __str__(self) -> str:
        return f"{self.source} 对 {self.target} 执行 {self.action_type}"
```

未实现 `__str__` 时，回放日志回退到 `repr()` 输出（类名 + 字段值），可用但可读性较差。

## 命名约定

- 模块目录名：`snake_case`（如 `turn_order`、`skill_system`）
- 类名：`PascalCase`
- 函数/方法：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 引擎类命名：`{ModuleName}Engine`（如 `TurnOrderEngine`）
- 接口命名：`I{InterfaceName}` 或 `{InterfaceName}Protocol`（如 `ITurnOrderEngine`）
