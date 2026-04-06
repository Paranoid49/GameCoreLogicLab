# /replay 命令

查看指定模块的最新回放文件。

## 输入

模块名称：$ARGUMENTS

## 执行

1. 查找 `tests/modules/$ARGUMENTS/replays/` 目录下最新的 `.json` 文件
2. 如果目录不存在或无回放文件，提示用户先运行 `/evaluate $ARGUMENTS` 或 `/build-module` 生成回放
3. 找到回放文件后：
   - 默认：运行 `python -m harness.sim.replay {json_path}` 输出文本回放
   - 如用户要求可视化：运行 `python -m harness.sim.replay {json_path} --html` 打开浏览器
4. 如有多个回放文件，列出供用户选择
