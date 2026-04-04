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

## 命名约定

- 模块目录名：`snake_case`（如 `turn_order`、`skill_system`）
- 类名：`PascalCase`
- 函数/方法：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 引擎类命名：`{ModuleName}Engine`（如 `TurnOrderEngine`）
- 接口命名：`I{InterfaceName}` 或 `{InterfaceName}Protocol`（如 `ITurnOrderEngine`）
