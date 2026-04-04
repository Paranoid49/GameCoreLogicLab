## 变更说明

<!-- 简述本 PR 做了什么，以及为什么 -->

## 变更类型

- [ ] 新模块（新增游戏核心机制实现）
- [ ] 模块增强（对已有模块的功能扩展或优化）
- [ ] Bug 修复
- [ ] Harness/工具改进
- [ ] 文档更新

## 质量自审 Checklist

### 正确性
- [ ] 所有测试通过（`pytest tests/`）
- [ ] 验收标准完整覆盖（每条标准有对应测试）
- [ ] 包含边界条件测试（空输入、极值、零值）
- [ ] 包含异常路径测试（无效参数、非法状态）

### 架构合规
- [ ] 架构检查通过（`python -m harness.lint.check_architecture`）
- [ ] 引擎类继承正确接口
- [ ] 无跨模块直接导入
- [ ] 依赖方向正确（Models → Interfaces → Engine）

### 代码质量
- [ ] 风格检查通过（`python -m harness.lint.check_style`）
- [ ] 命名符合约定（PascalCase / snake_case / UPPER_SNAKE_CASE）
- [ ] 单函数 ≤ 50 行，单文件 ≤ 300 行
- [ ] Pydantic 模型字段有类型约束

### 性能
- [ ] 基准测试存在且可运行
- [ ] 无明显的不必要 O(n²) 复杂度

### 文档
- [ ] 文档检查通过（`python -m harness.lint.check_docs`）
- [ ] 新模块有对应的规格文档（`docs/plans/`）

## 测试结果

```
<!-- 粘贴 python -m harness.ci 的输出 -->
```
