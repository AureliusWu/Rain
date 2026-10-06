# 当前断点：新配音验收完成，修复发布退出码后重试正式发行

提交 `dff19a6ecf516fa674e24fcb3481413efc25b849` / [Windows CI 37440590549](https://github.com/AureliusWu/Test/actions/runs/37440590549)；原始游戏 ZIP **56,359,988 字节**，SHA-256 `0d09a78a482e2ff0d34e14f51d49c89d5cc0d36b91506d44c6a3bcdcc678d3f1`。

113 项 Windows Python、全部作者校验与 Ren’Py 8.5.3 lint 通过。源码和独立 EXE 各 **31/31 用例、359/359 断言**（1089.606 / 739.611 秒）；退出首进程后重新启动 EXE，真实读档另 **1/1 用例、10/10 断言**（3.745 秒）。failed / xfailed / xpassed / skipped / not run 全为 0，三个进程退出 0、未超时。

17 句关键配音已替换为免费开源 Qwen3-TTS 1.7B CustomVoice / Serena。逐句保存语气指令，双遍响度处理目标 -20 LUFS / 真峰值 -2 dBTP；24 kHz 单声道、合计 57.360 秒。全部信号与独立 large-v3 ASR 校验通过：16 句归一化文字一致，1 句“哪 / 哪儿”儿化差异。旧 Kokoro 源录音与 OGG 历史保留。

用户已明确授权“完成后发布正式版”；真人后续统一由用户操作。35 个 EXE 关键画面复核、131 PNG 解码、85 包内资产和完整 ZIP 检查完成。人验表保持真实 pending，独立授权 JSON 绑定本次语音与同字节包。

下一步：提交本次 docs 与授权文件到 main，触发 `release-v10.yml` → 等待并核对非 prerelease / 非 draft 的 v1.0.0、tag 目标 `dff19a6ecf516fa674e24fcb3481413efc25b849` 与公开资产 SHA-256 → 保存发行回读记录并更新当前状态 → 交付原始同字节 Windows 包与两份新声音材料。

不要重跑已通过的游戏合集、重生成配音、复用旧 Kokoro 包、把真人 pending 伪改为 passed，或再次要求发布许可。当前 docs 的更新不改变已验收运行资产。若发布途中中断，先读取 Release / tag / workflow 的实际状态，不覆盖既有发布。

Windows CI 使用 dummy 音频。真人试听、两结局阅读计时、普通电脑 / 中文路径 / 100% 与 150% DPI、创作定案及内容冻结仍为 pending，由用户统一操作；ASR 与自动执行时间不能代替这些结论。

首轮发布 37444936017 的声音授权、artifact 下载、原 ZIP / 预览全部通过；创建 Release 前因 gh 预期 HTTP 404 返回码残留导致 step 6 失败，创建步骤 skipped。workflow 修复提交 0e2db075 使用 exit 0，仅在所有验证及两个不存在检查完成后返回成功。没有更换候选或安装包，重新提交授权文件以触发修复后的工作流。失败证据见 evidence/v10-publication-first-failure.json。
