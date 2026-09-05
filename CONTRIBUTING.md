# 贡献指南 (Contributing to TiKu)

首先，非常感谢你花时间来为 TiKu 贡献代码！🎉

作为一个探索 AI 辅助开发的项目，我们欢迎任何形式的贡献，包括但不限于提交 Bug、增加新功能、完善文档或提供宝贵的建议。

为了让合作更加顺畅，请在贡献前阅读以下指南：

## 🚨 重要前置约定

如果你计划使用 AI 辅助工具（如 Cursor, GitHub Copilot 等）来协助开发本项目，**请务必首先阅读项目根目录下的 [`agent.md`](./agent.md) 文件**。该文件是我们项目最高的规则指导，为了防止出现“文档打架”或历史逻辑被覆盖的情况，所有的 AI Prompt 和 Agent 行为都必须遵循该文档中的约定。

## 提交 Issue

如果你发现了一个 Bug 或有一个新功能的好主意，请先在 GitHub/Gitee 上搜索是否已经有相关的 Issue。如果没有，请创建一个新的 Issue，并尽量提供以下信息：
- **Bug 报告**：重现步骤、预期的结果、实际的结果、相关的截图或报错日志、你所使用的环境（OS, 浏览器版本, Docker 版本等）。
- **功能请求**：该功能解决什么痛点、具体的使用场景、你期望的实现方式。

## 本地开发与 Pull Request 流程

1. **Fork 本仓库** 到你自己的 GitHub/Gitee 账号下。
2. **克隆 (Clone)** 你 Fork 的仓库到本地。
3. **创建分支 (Branch)**：强烈建议基于 `main` 分支创建一个新的分支来进行开发。
   - `git checkout -b feat/your-feature-name` (用于新功能)
   - `git checkout -b fix/your-bugfix-name` (用于修复 Bug)
4. **提交代码 (Commit)**：我们遵循 [Angular 提交规范](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines)。
   常用的前缀包括：
   - `feat:` 新功能
   - `fix:` 修复 Bug
   - `docs:` 文档修改
   - `style:` 代码格式修改（不影响逻辑）
   - `refactor:` 代码重构
   - `test:` 添加或修改测试用例
   - `chore:` 构建过程或辅助工具的变动
5. **保持同步并解决冲突**：在提交 PR 之前，请确保你的分支与官方仓库的 `main` 分支保持同步。
6. **提交 Pull Request**：推送你的分支到远程仓库，然后发起一个 Pull Request。请在 PR 描述中清晰地说明你的修改内容，如果关联了某个 Issue，请使用 `Closes #Issue号` 的格式将其关联。

## 代码规范

- **前端**：遵循 Vue 官方风格指南，使用 Prettier 和 ESLint 保持代码风格统一。
- **后端**：遵循 PEP 8 规范，建议使用 `black` 进行代码格式化。所有新增的 API 端点必须添加详细的 Type Hint，并能在 Swagger 中正确展示。
- **文档一致性**：如果你修改了功能或 API，请务必同步更新 [`product.md`](./product.md), [`tech-spec.md`](./tech-spec.md), 或 [`api-contract.md`](./api-contract.md)，保持代码与文档同源。

感谢你让 TiKu 变得更好！🚀
