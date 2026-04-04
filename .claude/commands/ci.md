# /ci 命令

运行完整的 CI 管线，一次检查所有质量维度。

## 执行

运行集中式 CI 脚本：

```bash
python -m harness.ci
```

该脚本依次运行以下阶段：
1. **架构合规** — `harness.lint.check_architecture`
2. **代码风格** — `harness.lint.check_style`
3. **文档健康** — `harness.lint.check_docs`
4. **单元测试** — `pytest tests/`
5. **测试覆盖率** — `pytest --cov`

运行完成后向用户展示统一报告。如有失败项，给出具体的修复建议。
