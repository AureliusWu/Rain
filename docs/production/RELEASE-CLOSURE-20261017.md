# 雨停之前 v1.2.2 更新与推送闭环 — 2026-10-17

当前更新的源码推送、构建、发行附件和网页部署已完成核验，版本为 **v1.2.2（正式版）**。[发行页](https://github.com/AureliusWu/Rain/releases/tag/v1.2.2) · [在线游玩](https://aureliuswu.github.io/Rain/) · [机器回执](RELEASE-CLOSURE-20261017.json)。

| 环节 | 核验结果 |
| --- | --- |
| 主线 | 已审计 `main` 提交 `073b5bc8b58fc98b2709e8d04c7de2a7f634b381`；无开放 PR，无尚未发布的玩家程序差异 |
| 发行身份 | `v1.2.2` → `15d87ef4455b95feb6069e044a1d3a6456f75e0c`；公开且非草稿，prerelease 为 `false` |
| 下载 | 全部 4 份附件的字节数、SHA-256 与当前 GitHub digest 一致；3 条 checksum 记录一致 |
| 压缩包 | 2 个 ZIP 完整 CRC、路径和重复项检查通过 |
| 线上 | index.html 与离线 worker 共 2 份文件均为 HTTP 200，字节与已验证构建一致 |

Web ZIP 使用已下载的公开字节重新计算摘要，其余三份匿名重新下载。逐份附件 ID、大小、摘要、检验方法及压缩包条目数保存在机器回执。入口与 worker 均与本版本公开 Web/PWA ZIP 中对应文件逐字节一致。

本轮及原版本的程序验证：本轮 172 项 Python、完整作者校验、5 项输入控件和公开原官方 WASM 包的 14 项真实浏览器检查通过；Windows 完整执行与旧档升级沿用原版本的已通过回执。证据见 [PUBLISHED-v1.2.2.json](PUBLISHED-v1.2.2.json) 和 [本轮实现/复验记录](MAINTENANCE-20261017.json)。

| 必需工作流 | 结论 | 已验证提交 |
| --- | --- | --- |
| [Game validation](https://github.com/AureliusWu/Rain/actions/runs/38828604885) | success | `15d87ef4455b` |
| [Native RenPy PWA and shared materials](https://github.com/AureliusWu/Rain/actions/runs/38828604848) | success | `15d87ef4455b` |
| [Publish exact verified v1.2.2 Windows and PWA](https://github.com/AureliusWu/Rain/actions/runs/38861929614) | success | `a5f0fdf2342e` |

该回执是在表中已审计主线之后追加的文档提交；原版本 tag、发行附件及玩家程序保持原有身份。闭环范围为本轮工程更新、推送、发行和线上一致性。真人试听、逐图审阅、阅读计时、普通物理设备/DPI 与创作冻结保持原验收状态；本轮未重新执行 Windows。
