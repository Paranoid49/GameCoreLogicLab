# GameCoreLogicLab

纯 Python 游戏核心逻辑实验室。实现经典游戏机制的工程化实践与性能优化探索。

## 项目结构

```
src/common/          公共接口与数据模型（所有模块共享）
src/modules/{name}/  各游戏模块（回合制、MOBA、FPS 等）
tests/modules/       与 src/modules/ 镜像的测试
harness/lint/        架构合规检查工具
harness/benchmarks/  性能基准测试基础设施
docs/                知识库（架构、标准、计划）
```

## 架构规则

每个模块内部分层，依赖方向单向向下：

```
Models → Interfaces → Engine → Simulation
```

- 模块间禁止直接依赖，只通过 `src/common/` 通信
- 可有 `v1_readable/`（可读优先）和 `v2_optimized/`（性能优先）两种实现
- 两种实现必须遵循同一接口

## 新模块创建

使用 `/build-module "模块描述"` 启动完整 Planner→Generator→Evaluator 流程。
也可分步执行：`/plan-module` 仅规划，`/evaluate` 仅评估。

## 评估标准

| 维度 | 权重 | 阈值 |
|------|------|------|
| 正确性 | 40% | 100% 测试通过 |
| 架构合规 | 25% | 0 违规 |
| 代码质量 | 20% | ≥7/10 |
| 性能 | 15% | 基准达标 |

## 关键文档

- [架构规范](docs/architecture.md) — 分层规则、模块结构、依赖约束
- [质量标准](docs/quality-standards.md) — 四维评估体系详细说明
- [模块模板](docs/module-template.md) — 新模块文件结构与接口规范
- [活跃计划](docs/plans/active/) — 进行中的模块规格
- [已完成计划](docs/plans/completed/) — 归档的已完成规格

## 技术栈

- Python 3.12+, Pydantic 2.x
- pytest + pytest-benchmark
- 无前端，纯逻辑层

## 开发命令

```bash
pytest tests/                              # 运行全部测试
pytest tests/ --benchmark-only             # 仅运行性能基准
python -m harness.lint.check_architecture  # 架构合规检查
python -m harness.lint.check_style         # 代码风格检查
python -m harness.lint.check_docs          # 文档健康检查
python -m harness.ci                       # 一键运行完整 CI 管线
```
