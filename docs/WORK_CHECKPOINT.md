# 当前断点：v1.0.1 配音重听候选，待本批 Windows 验证

用户继续开发后，本批增加当前台词和历史的语音重播，使用引擎原生接口。沿用现有正文、17 句 Qwen 录音、台词 ID 和 v1 存档目录；只提升补丁版本。历史退出停止重播，下一句无语音时隐藏当前重听入口。

本地 113 Python、全部作者校验与 Ren'Py 8.5.3 lint 通过。Windows 新功能、全套路线 / 存读档、源码 / EXE / 新进程，以及旧正式 v1.0.0 的真实存档升级检查尚待当前提交执行；下一步完成当前 Windows 结果和新截图审阅，不复用历史结果证明新功能。

已完成的 v1.0.0 免费配音升级和正式发行保持，下方为已发布版本身份；新候选不能覆盖 v1.0.0 或重跑已完成的语音生成。真人试听、计时、普通电脑 / DPI、创作定案继续由用户统一操作。

---

# v1.0.0 正式版已发布

[正式 Release](https://github.com/AureliusWu/Test/releases/tag/v1.0.0) · [Windows 下载](https://github.com/AureliusWu/Test/releases/download/v1.0.0/BeforeTheRainStops-1.0.0-win.zip)

游戏验收提交 `dff19a6ecf516fa674e24fcb3481413efc25b849`；发行 tag 指向 `b4f06f89eebb73ff0494cb18fc4cfc38192c84ce`，仅增加文档与发布工作流差异，游戏内容完全一致。原始 ZIP **56,359,988 字节**，SHA-256 `0d09a78a482e2ff0d34e14f51d49c89d5cc0d36b91506d44c6a3bcdcc678d3f1`。

Windows 113 项 Python、全部作者校验与 Ren’Py 8.5.3 lint 通过；源码和独立 EXE 各 31 用例 / 359 断言，退出后新进程读档 1 用例 / 10 断言通过。全部异常计数为 0，三个进程退出 0、未超时；131 PNG 完整解码、35 个 EXE 关键视图复核、85 包内资产与 ZIP CRC / 许可检查通过。

17 句关键配音已替换为免费开源 Qwen3-TTS 1.7B / Serena，合计 57.360 秒；逐句指令、固定 revision / 种子、响度处理、信号及 large-v3 独立 ASR 完成，旧录音历史保留。语音证据 SHA-256：`5180a9ca16c7a01f502350dcdfadf073da06edcb9b054350d7fdec8c3af7336a`。

发布 workflow **37446100720** 已 success，tag 目标包含验收文档且游戏内容与验收提交完全一致；Release 非 draft、非 prerelease，原始 ZIP 发布后下载回读通过。实际发行资产及 SHA-256 见 `evidence/v10-publication.json`。

真人试听、Normal / True 阅读计时、普通电脑 / 中文路径 / DPI、最终创作定案与冻结仍待用户统一操作。ASR、dummy 音频与自动测试耗时不代表这些项目通过。

后续若收到真人结果，按实际问题修复并发行新版本；不要覆盖 v1.0.0、重跑已完成开发、伪填人验表，或再次请求本次发布许可。旧候选与旧发声引擎证据有独立历史归档。
