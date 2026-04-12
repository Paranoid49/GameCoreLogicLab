# GameCoreLogicLab

专注于研究和实现各类游戏核心逻辑系统的开源实验室。不关注前端渲染，只聚焦经典游戏机制的工程化实践与性能优化探索。

## 覆盖方向

| 游戏类型 | 核心机制示例 |
|----------|------------|
| 回合制 RPG | 回合排轴、伤害公式、状态系统 |
| MOBA | 技能系统、冷却管理、目标选择 |
| FPS | 射击判定、弹道计算、命中扣血 |
| RTS | 寻路算法、资源管理、单位 AI |
| Roguelike | 地图生成、物品掉落、随机事件 |

每个机制作为独立模块实现，可单独运行和测试。

## 架构

```
src/
├── common/                  # 公共接口与数据模型
│   ├── interfaces.py        #   GameEngine 泛型基类、EventBus
│   └── models.py            #   EntityId、Position、StatBlock 等
└── modules/                 # 各游戏模块
    └── {module_name}/
        ├── models.py        #   模块数据模型
        ├── interfaces.py    #   模块引擎接口
        └── engine.py        #   核心逻辑实现
```

**分层规则**：Models → Interfaces → Engine → Simulation，依赖方向严格单向向下，模块间禁止直接依赖。

## Harness Engineering

本项目内建了一套 AI Agent 驱动的开发体系，受 [Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps) 和 [OpenAI](https://openai.com/index/harness-engineering/) 的 harness engineering 实践启发：

```
用户输入: "回合制排轴系统"
    │
    ▼
[Planner] → 生成完整模块规格
    ▼
[Generator] → 实现代码 + 测试 + 自审
    ▼
[Evaluator] → 四维质量评估（正确性/架构/质量/性能）
    │
    ├─ 通过 → 归档
    └─ 不通过 → 反馈迭代（最多 3 轮）
```

**质量门禁**：
- 3 个自定义 linter（架构合规、代码风格、文档健康）
- Generator 自审 16 项 checklist
- 独立 Evaluator Agent 四维评分
- GitHub Actions CI 自动运行
- Pre-commit hooks 本地拦截

## 快速开始

```bash
# 克隆项目
git clone https://github.com/your-username/GameCoreLogicLab.git
cd GameCoreLogicLab

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -e ".[dev]"

# 运行 CI 检查
python -m harness.ci

# （可选）安装 pre-commit hooks
pip install pre-commit
pre-commit install
```

## 开发命令

```bash
# 质量检查
python -m harness.ci                       # 一键运行完整 CI 管线
python -m harness.lint.check_architecture  # 架构合规检查
python -m harness.lint.check_style         # 代码风格检查
python -m harness.lint.check_docs          # 文档健康检查

# 测试
pytest tests/                              # 运行全部测试
pytest tests/ --benchmark-only             # 仅运行性能基准
pytest tests/ --cov=src                    # 带覆盖率
```

## Claude Code 命令

如果你使用 [Claude Code](https://github.com/anthropics/claude-code) 开发本项目：

| 命令 | 作用 |
|------|------|
| `/build-module "描述"` | 完整 Planner→Generator→Evaluator 流程 |
| `/plan-module "描述"` | 仅生成模块规格文档 |
| `/evaluate 模块名` | 对已实现模块运行四维评估 |
| `/ci` | 运行完整 CI 管线 |

## 项目文档

| 文档 | 内容 |
|------|------|
| [architecture.md](docs/architecture.md) | 分层规则、依赖约束、命名约定 |
| [quality-standards.md](docs/quality-standards.md) | 四维评估体系详细说明 |
| [module-template.md](docs/module-template.md) | 新模块文件结构与代码模板 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |

## 技术栈

- **语言**：Python 3.12+
- **数据建模**：Pydantic 2.x
- **测试**：pytest + pytest-benchmark + pytest-cov
- **CI**：GitHub Actions
- **协议**：MIT License
