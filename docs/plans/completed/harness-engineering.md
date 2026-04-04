# Harness Engineering 实施计划

- **创建日期**: 2026-04-04
- **状态**: completed
- **完成日期**: 2026-04-04
- **目标**: 构建基于 Claude Code CLI 原生能力的 Planner-Generator-Evaluator harness 工程体系

## 背景

参考两篇 harness engineering 实践文章，为 GameCoreLogicLab（纯 Python 游戏核心逻辑实验室）构建 Agent 驱动的开发体系：

- **Anthropic** — *Harness Design for Long-Running Apps*：GAN 启发的三 Agent 架构（Planner-Generator-Evaluator），通过独立评估 Agent 解决自我评价失真问题，迭代反馈提升输出质量。
- **OpenAI** — *Harness Engineering*：仓库即唯一真相来源，AGENTS.md 作目录而非百科，严格架构约束 + 自定义 Linter 机械执行，Agent 可读性优先。

## 设计理念

| 文章思想 | 本项目实现 |
|---|---|
| AGENTS.md 是目录不是百科 | 项目级 `CLAUDE.md` ~100行索引 → 指向 `docs/` |
| 仓库即唯一真相来源 | `docs/` 结构化知识库，版本控制 |
| 严格架构 + 自定义 Linter | `harness/lint/check_architecture.py` + Hooks 自动执行 |
| Planner-Generator-Evaluator | `.claude/agents/` 三个 Agent 定义 |
| Sprint Contract | `/build-module` 命令编排完整 P→G→E 流程 |
| 评估标准 | `docs/quality-standards.md` 四维评分体系 |

## 目标目录结构

```
GameCoreLogicLab/
├── CLAUDE.md                           # Agent 索引地图（~100行）
├── docs/
│   ├── architecture.md                 # 分层规则与依赖约束
│   ├── quality-standards.md            # 四维评估标准
│   ├── module-template.md              # 新模块规范模板
│   └── plans/
│       ├── active/                     # 进行中的模块规格
│       └── completed/                  # 已完成的规格归档
├── src/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── interfaces.py              # 公共抽象基类
│   │   └── models.py                  # 公共数据模型
│   └── modules/                       # 各游戏模块（按规范创建）
├── tests/
│   ├── conftest.py
│   └── modules/                       # 与 src/modules/ 镜像
├── harness/
│   ├── lint/
│   │   └── check_architecture.py      # 架构合规检查脚本
│   └── benchmarks/
│       └── conftest.py                # 性能基准测试基础设施
├── .claude/
│   ├── agents/
│   │   ├── planner.md                 # Planner Agent
│   │   ├── generator.md               # Generator Agent
│   │   └── evaluator.md               # Evaluator Agent
│   ├── commands/
│   │   ├── build-module.md            # 完整 P→G→E 编排
│   │   ├── plan-module.md             # 单独规划
│   │   └── evaluate.md                # 单独评估
│   └── settings.local.json            # 权限 + Hooks
├── pyproject.toml                     # 项目配置 + 依赖
└── README.md
```

## 架构分层规则

每个游戏模块内部遵循严格分层，依赖方向单向向下：

```
Models（数据模型）→ Interfaces（接口）→ Engine（引擎实现）→ Simulation（模拟运行）
```

- 模块间**不允许**直接依赖，只能通过 `src/common/` 的公共接口通信
- 每个模块可有 `v1_readable/`（可读优先）和 `v2_optimized/`（性能优先）两种实现
- 两种实现必须遵循同一接口

## 四维评估标准

| 维度 | 权重 | 通过阈值 | 说明 |
|---|---|---|---|
| **正确性** | 40% | 100% 测试通过 | 核心逻辑、边界条件、异常处理 |
| **架构合规** | 25% | 0 违规 | 分层规则、接口使用、无跨模块依赖 |
| **代码质量** | 20% | ≥7/10 | 命名、结构、可读性、类型标注 |
| **性能** | 15% | 达到基准 | 基准测试通过目标阈值 |

## P-G-E 编排流程

```
用户输入: "回合制排轴系统"
    │
    ▼
[Planner Agent] → docs/plans/active/{module_name}.md
    │                 (完整规格：目的、数据模型、算法、边界、验收标准)
    ▼
  用户确认规格
    │
    ▼
[Generator Agent] → src/modules/{module_name}/ + tests/modules/{module_name}/
    │                  (按架构规则实现 v1_readable + 测试)
    ▼
[Evaluator Agent] → 运行测试 + 架构检查 + 代码审查
    │                  输出评估报告（四维评分）
    │
    ├─ 通过 → 完成，规格移入 plans/completed/
    │
    └─ 不通过 → 具体反馈发回 Generator → 迭代（最多 3 轮）
```

## 实施步骤

| 步骤 | 内容 | 产出文件 |
|---|---|---|
| 1 | 项目基础设施 | `pyproject.toml`, pytest 配置, `__init__.py` |
| 2 | CLAUDE.md 索引 | 项目级 Agent 地图（~100行） |
| 3 | docs/ 知识库 | architecture.md, quality-standards.md, module-template.md |
| 4 | src/common/ 公共层 | interfaces.py, models.py（抽象基类和公共类型） |
| 5 | harness/ 质量工具 | check_architecture.py + benchmark 基础设施 |
| 6 | .claude/agents/ | planner.md, generator.md, evaluator.md |
| 7 | .claude/commands/ | build-module.md, plan-module.md, evaluate.md |
| 8 | Hooks + 权限 | settings.local.json 更新 |

## 决策记录

- **为什么不用 Anthropic API 编排**：Claude Code CLI 原生已有 Agent 派生、Team/Task、Hooks 能力，零外部依赖，上下文在 CLI 内闭环管理。
- **为什么先不实现游戏模块**：harness 体系应独立于业务逻辑，先验证工程流程可行，再用 `/build-module` 驱动实际模块开发。
- **为什么选择四维评估而非二元通过/失败**：游戏逻辑虽然有客观正确性，但代码质量和性能优化属于程度问题，需要分维度量化才能给出可操作的迭代反馈。
