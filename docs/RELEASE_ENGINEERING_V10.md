# v1.0 发布工程补检 — 2026-10-06

发布检查已修复异常计数、布尔值计数、机器问题和不完整记录的误判。新增 6 项反例回归，发布检查共 14 项；本轮 Linux 全部 97 项 Python 测试、作者校验及 Ren’Py 8.5.3 lint 通过。

## 修复与证据

| 输入或触发条件 | 原行为 | 修复后的要求 |
|---|---|---|
| xfailed / xpassed 非零或未记录 | 发布检查遗漏这两个字段，原生报告摘要也未保留它们 | 原生报告保留全部异常计数；正式发布要求 failed / xfailed / xpassed / skipped / not_run 都是整数 0 |
| cases / assertions / Python 数量为布尔值、浮点或字符串 | True 可以被当作正数，部分错误类型会触发异常栈 | 数量必须为正整数；CI 与 artifact ID 同样检查类型，进程退出码必须为整数 0 |
| unresolved_machine_issues 非空或未记录 | passed 状态可能遮盖未解决的机器问题 | 必须有明确的空问题列表 |
| 源码与 EXE 用例 / 断言数量不同 | 两边各自为正数即可 | 主集合的两项数量必须一致，新进程读档另行检查 |
| JSON null、缺对象、真人证据为 null | 部分记录产生属性错误或异常栈 | 非零退出并给出明确的 Release blocked 原因，不写发布输出 |

[机器补检记录](evidence/v10-release-gate-followup.json) 保留工具文件 SHA-256、原始报告 SHA-256、包身份与实际人验阻止结果。[97 项完整作者校验日志](evidence/v10-release-tools-validation.txt) 和 [Linux 引擎 lint](evidence/v10-release-tools-lint.txt) 已保存。

## 候选身份与人工范围

游戏候选仍绑定 `7593a348bf28e196c2ee3a55fd1e14c837289ef3`，Windows 原运行 [37411258713](https://github.com/AureliusWu/Test/actions/runs/37411258713)。本轮改动为发布工具、报告字段和文档；游戏、源资产、Prompt、许可、VERSION 和玩家说明与该候选一致。Windows 游戏回归证据继续使用这次已验收运行的源码 / EXE 各 31/359、新进程 1/10；本轮 97 项结果是 Linux 作者工具验证。

三个原始 Windows 输出与既有报告 SHA-256 一致，已按该候选的测试计划重新解析，确认五类异常计数全部为零。`v10-acceptance.json` 补齐 xfailed / xpassed；原 CI 输出和已交付审阅包保留其当时报告格式。

原始游戏 ZIP `BeforeTheRainStops-1.0.0-win.zip` 为 56,354,657 字节，SHA-256 `4ecba6cea822947b08bc8a877af2d5eed4ccbb3ffdd367c92032c236f5dac048`，本轮按正式发布包检查重新通过大小、哈希、CRC、版本、许可及开发文件排除校验；实际 EXE 预览身份也一致。

真实 `V10_HUMAN_ACCEPTANCE.json` 内容保留，五组均为 pending。正式检查的实际结果仍为 `Release blocked: Human acceptance pending`；未创建 tag 或 Release。用户继续在已交付审阅包的 `REVIEW_RESULT_TEMPLATE.md` 统一填写试听、阅读计时、普通 Windows / DPI 和创作意见。

本轮提交标为 `[skip ci]`：已完成作者工具验证，继续绑定原游戏包与 Windows 证据。后续若修改游戏或资产，重新建立候选、完成 Windows 全链路并更新真实人工绑定。
