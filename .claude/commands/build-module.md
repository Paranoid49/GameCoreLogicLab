# /build-module 编排命令

完整的 Planner → Generator → Evaluator 模块构建流程。

## 输入

用户提供模块的简短描述，例如：`/build-module 回合制战斗排轴系统`

描述内容：$ARGUMENTS

## 执行流程

按以下步骤严格顺序执行，每步完成后报告进度：

### 阶段 1：规划（Planner）

派生 planner Agent，传入用户描述：

> 请为以下游戏核心机制生成完整的模块规格文档：「$ARGUMENTS」

等待 Planner 完成，向用户展示规格概要（模块名、核心概念、验收标准数量）。

**暂停等待用户确认**：用户可以提出修改意见或确认继续。如果用户要求修改，重新派生 Planner 修订规格。

### 阶段 2：实现（Generator）

用户确认规格后，派生 generator Agent：

> 请根据规格文档 `docs/plans/active/{module_name}.md` 实现完整的模块代码和测试。

等待 Generator 完成，向用户报告：创建了哪些文件、测试是否通过、架构检查是否通过。

### 阶段 3：评估（Evaluator）

派生 evaluator Agent：

> 请评估模块 `{module_name}` 的实现质量，规格文档在 `docs/plans/active/{module_name}.md`。

等待 Evaluator 完成，向用户展示评估报告。

### 阶段 4：迭代（如需要）

如果 Evaluator 报告不通过：
1. 提取 Evaluator 的改进建议
2. 重新派生 generator Agent，附带改进反馈
3. 再次派生 evaluator Agent 重新评估
4. 最多迭代 3 轮

### 阶段 5：归档

评估通过后：
1. 将规格文档从 `docs/plans/active/` 移动到 `docs/plans/completed/`
2. 向用户报告最终结果：模块名、文件列表、评估总分

## 失败处理

- 如果 3 轮迭代后仍未通过，停止自动迭代，向用户报告当前状态和未解决的问题，请求人工介入
- 如果任何阶段的 Agent 出错，向用户报告错误并等待指示
