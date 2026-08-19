# docs

文档目录按“读者”严格分两层：

## `docs/agent/` —— 给智能体读的文档
- 每次运行会随会话复制进 mod 工作区。
- 只放运行期必须的、会被智能体 `read_file` / `grep` 的知识。
- 当前内容：
  - `ERROR_LIST.md` —— 已知错误与修复，智能体遇到编译/测试错误先查这里。
  - `TOOL_GUIDE.md` —— 工具手册、禁则、Forge 1.21.11 硬事实、自检流程。

## `docs/dev/` —— 给人/开发/交接看的内部文档
- 不复制进智能体会话，不进入智能体上下文。
- 当前内容：
  - `HANDOFF.md` —— 项目交接。
  - `DSH_ADAPTATION_PLAN.md` —— DSH 架构移植计划。
  - `PORTED_FROM_DSH.md` —— 已移植机制清单。
  - `DSH_SOURCE_AUDIT.md` —— DSH 源码逐文件阅读记录（历史证明）。
  - `dsh-tools-system-report.md` —— 子代理调研报告。

## 规则
- 凡是需要智能体在运行期遵守/查询的内容 → 放 `docs/agent/`。
- 凡是只给人类维护者看、或一次性的调研/计划/记录 → 放 `docs/dev/`。
- 不要把内部文档放项目根目录或 `docs/agent/`。