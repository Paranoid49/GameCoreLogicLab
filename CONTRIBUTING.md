# 贡献指南

感谢你对 GameCoreLogicLab 的关注！本项目欢迎以下类型的贡献：

- 新增游戏核心机制模块
- 为已有模块添加 v2_optimized 性能优化实现
- 改进 harness 工具和质量检查
- 修复 bug 和完善文档

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

## 添加新模块

### 推荐流程：使用 Claude Code

如果你使用 [Claude Code](https://github.com/anthropics/claude-code)，可以用内置的 P-G-E 流程：

```
/build-module "你的模块描述"
```

这会自动完成 规划→实现→评估→迭代 全流程。

### 手动流程

1. **创建规格文档**

   在 `docs/plans/active/{module_name}.md` 中编写规格，参考 [module-template.md](docs/module-template.md) 底部的规格模板。

2. **实现模块**

   按照 [architecture.md](docs/architecture.md) 的分层规则创建文件：

   ```
   src/modules/{module_name}/
   ├── __init__.py
   ├── models.py
   ├── interfaces.py
   └── v1_readable/
       ├── __init__.py
       └── engine.py

   tests/modules/{module_name}/
   ├── __init__.py
   ├── test_engine.py
   └── test_benchmark.py
   ```

3. **验证质量**

   ```bash
   python -m harness.ci
   ```

   确保全部 5 个阶段通过。

4. **提交 PR**

   PR 模板中包含质量 checklist，请逐项确认。

## 架构规则

务必遵守以下规则（CI 会自动检查）：

- **分层**：Models → Interfaces → Engine → Simulation，依赖方向单向向下
- **隔离**：模块间禁止直接 import，只通过 `src/common/` 通信
- **接口**：引擎类必须继承 `GameEngine` 基类或模块接口
- **不可变**：状态变更返回新对象，不修改原对象
- **命名**：类名 PascalCase，函数 snake_case，常量 UPPER_SNAKE_CASE
- **大小**：单函数 ≤ 50 行，单文件 ≤ 300 行

详见 [architecture.md](docs/architecture.md)。

## 质量标准

所有模块按四个维度评估：

| 维度 | 权重 | 阈值 |
|------|------|------|
| 正确性 | 40% | 100% 测试通过 |
| 架构合规 | 25% | 0 违规 |
| 代码质量 | 20% | ≥ 7/10 |
| 性能 | 15% | 基准达标 |

详见 [quality-standards.md](docs/quality-standards.md)。

## 提交规范

- 一个 PR 只做一件事（一个模块或一个修复）
- commit message 简洁明了，说明"做了什么"和"为什么"
- 提交前确保 `python -m harness.ci` 通过
