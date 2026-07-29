---
name: git-workflow
description: Git 提交与分支规范
---

## 提交信息格式

使用 Conventional Commits 规范：
```
<type>(<scope>): <subject>

<body>

<footer>
```

### type 取值
- `feat` — 新功能
- `fix` — 修复 bug
- `docs` — 文档变更
- `style` — 代码格式（不影响逻辑）
- `refactor` — 重构（非新功能、非修 bug）
- `test` — 测试相关
- `chore` — 构建/工具/依赖

### 示例
```
feat(user-api): 新增用户删除接口

DELETE /api/users/:id，含 404 处理和软删除标记。
关联 issue #42
```

## 分支策略

- `main` — 生产分支，只接收 PR，禁止直接 push
- `develop` — 开发集成分支
- `feature/<name>` — 功能分支，从 develop 拉出
- `fix/<name>` — 修复分支，从 main 或 develop 拉出
- `hotfix/<name>` — 紧急修复，从 main 拉出，合并回 main 和 develop

## 提交粒度

- 一次提交只做一件事
- 提交前跑 `git diff --cached` 自查
- 禁止 `git commit -m "update"` 这种无意义信息
- 禁止 `git add .`，按文件添加

## 合并规范

- PR 标题遵循 Conventional Commits
- 至少 1 人 review 后才能合并
- 合并前 rebase 到最新 develop，解决冲突
- 禁止 merge commit 除非是 release 分支