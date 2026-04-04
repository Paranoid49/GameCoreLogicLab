# /evaluate 命令

单独执行模块评估，对已实现的模块运行四维质量检查。

## 输入

用户提供模块名称：$ARGUMENTS

## 执行

派生 evaluator Agent：

> 请评估模块 `$ARGUMENTS` 的实现质量。如果 `docs/plans/active/$ARGUMENTS.md` 或 `docs/plans/completed/$ARGUMENTS.md` 存在，以其为规格基准进行评估；否则根据代码本身的接口定义和测试进行独立评估。

完成后向用户展示完整评估报告。

如果评估不通过且用户希望修复，可以手动处理或运行 `/build-module` 触发 Generator 迭代。
