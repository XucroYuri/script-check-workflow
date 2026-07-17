# Output Exists / No-Clobber Eval Fixture

## Setup

1. 使用固定 run ID `20260717T120000Z`。
2. 在运行前创建目标 diagnostics 文件，内容为 `PREEXISTING_SENTINEL_DO_NOT_REPLACE`。
3. 对任意合法短剧本启动文件模式运行。

## Expected outcome

- 返回 `BLOCKED: OUTPUT_EXISTS`。
- reviewer 不运行。
- 三个既有目标均不修改，且不留下临时文件或新脚本产物。
