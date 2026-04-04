# 贡献指南

感谢你对 GameCoreLogicLab 的关注！本项目欢迎以下类型的贡献：

- 新增游戏核心机制模块
- 为已有模块添加 v2_optimized 性能优化实现
- 改进 harness 工具和质量检查
- 修复 bug 和完善文档

## 核心原则：人类掌舵，Agent 执行

**本项目不接受手写代码贡献。** 所有代码必须通过 AI Agent 的 Planner-Generator-Evaluator 流程生成。

这不是限制，而是本项目的核心实验：验证 harness engineering 能否驱动 AI 自主产出高质量的游戏核心逻辑代码。人类的职责是设计环境、明确意图、构建反馈回路——而非直接编码。

贡献者的工作：
- **定义需求**：描述要实现的游戏机制（一句话即可）
- **审查规格**：确认 Planner 生成的规格文档符合预期
- **验收结果**：确认最终产出满足质量标准
- **改进 harness**：优化 Agent 定义、评估标准、质量检查工具

## 环境准备

```bash
git clone https://github.com/your-username/GameCoreLogicLab.git
cd GameCoreLogicLab
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 安装 pre-commit hooks
pip install pre-commit
pre-commit install
```

本项目使用 [Claude Code](https://github.com/anthropics/claude-code) 作为 AI Agent 运行时。

## 贡献流程

### 添加新模块

1. **提出需求**：运行 `/build-module "你的模块描述"`，启动完整的 P-G-E 流程
2. **审查规格**：Planner 生成规格文档后会暂停等待确认，审查并提出修改意见
3. **等待实现**：Generator 根据规格实现代码和测试，Evaluator 自动评估
4. **验收结果**：评估通过后检查最终产出，确认 CI 全绿

也可以分步操作：
- `/plan-module "描述"` — 仅生成规格，用于先讨论再实现
- `/evaluate 模块名` — 对已有模块重新评估

### 改进已有模块

对已有模块的 bug 修复、功能增强、性能优化，同样通过 Agent 执行。向 Claude Code 描述问题或目标，由 Agent 修改代码并通过 Evaluator 验证。

### 改进 harness 工具

以下 harness 组件本身的改进可以手动进行（因为它们是 Agent 的支撑环境，不是 Agent 的产出）：

- `.claude/agents/` 中的 Agent 定义
- `.claude/commands/` 中的编排命令
- `harness/lint/` 中的质量检查器
- `docs/` 中的规范文档

改进 harness 后需运行 `/ci` 验证不破坏现有检查。

## Harness 规范

贡献时必须遵循以下 harness 工程规范：

### 1. 仓库即唯一真相来源

- 所有上下文必须存在于仓库内（代码、文档、规格、计划）
- 不依赖外部文档、聊天记录或口头约定
- Agent 无法访问的信息 = 不存在的信息

### 2. 严格的架构约束由工具执行

- 架构规则不靠约定，靠自动化检查器机械执行
- 每个 linter 的报错信息必须包含可操作的修复指令（`fix_hint`）
- 新增架构规则时必须同步更新 `harness/lint/` 中的检查器

### 3. P-G-E 流程不可跳过

- 新模块必须有 Planner 生成的规格文档（`docs/plans/`）
- 代码必须由 Generator 生成并通过自审 checklist
- 代码必须经过独立 Evaluator 的四维评估
- 评估不通过必须迭代修复，不可强行合并

### 4. 评估标准公开透明

所有代码按四维标准评估（详见 [quality-standards.md](docs/quality-standards.md)）：

| 维度 | 权重 | 通过阈值 |
|------|------|---------|
| 正确性 | 40% | 100% 测试通过 |
| 架构合规 | 25% | 0 违规 |
| 代码质量 | 20% | ≥ 7/10 |
| 性能 | 15% | 基准达标 |

### 5. 质量门禁层层递进

```
本地开发：pre-commit hooks（架构 + 风格 + 文档检查）
     ↓
Agent 自审：Generator 16 项 checklist 逐项确认
     ↓
独立评估：Evaluator 四维评分 + 具体反馈
     ↓
CI 管线：GitHub Actions 全量检查（架构 + 风格 + 文档 + 测试 + 覆盖率）
     ↓
PR 审查：质量 checklist 模板 + 人工验收
```

### 6. 知识持续沉淀

- 完成的模块规格归档至 `docs/plans/completed/`
- 新发现的架构约束编码为 linter 规则
- Agent 评估中发现的模式问题反馈到 Agent 定义中

## 架构规则速查

- **分层**：Models → Interfaces → Engine → Simulation，依赖方向单向向下
- **隔离**：模块间禁止直接 import，只通过 `src/common/` 通信
- **接口**：引擎类必须继承 `GameEngine` 基类
- **不可变**：状态变更返回新对象，不修改原对象
- **命名**：类名 PascalCase，函数 snake_case，常量 UPPER_SNAKE_CASE
- **大小**：单函数 ≤ 50 行，单文件 ≤ 300 行

详见 [architecture.md](docs/architecture.md)。

## 提交规范

- 一个 PR 只做一件事（一个模块或一个修复）
- commit message 简洁明了，说明"做了什么"和"为什么"
- 提交前确保 `python -m harness.ci` 通过
- PR 描述中粘贴 CI 输出作为质量证据
