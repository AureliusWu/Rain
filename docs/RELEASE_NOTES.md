# 雨停之前 v1.0.0

雨夜旧车站，两位久未联系的旧友，一封没有寄出的信。六章、24 个叙事场景、四次选择、16 条路线，Normal / True 两个完整结局。

- 40 处正文精修已应用；全分支 15,065 字符，单路线 11,303–11,666。
- 原生 1920×1080、默认 1280×720 窗口；七表情、四背景、旧信 CG、三首原创程序音乐与环境音效。
- 17 句关键配音已替换为免费开源 Qwen3-TTS 1.7B CustomVoice / Serena。逐句保存语气指令，双遍响度处理目标 -20 LUFS / 真峰值 -2 dBTP；24 kHz 单声道、合计 57.360 秒。全部信号与独立 large-v3 ASR 校验通过：16 句归一化文字一致，1 句“哪 / 哪儿”儿化差异。旧 Kokoro 源录音与 OGG 历史保留。
- 存读档、退出后读档、历史、回退改选、快进、自动等待语音、音量、全屏与同进程新游戏均纳入回归。

下载 `BeforeTheRainStops-1.0.0-win.zip`，完整解压到可写目录后双击 `BeforeTheRainStops.exe`。无需安装引擎、Python 或模型，可离线游玩。v1 使用独立存档目录，旧阶段存档保留，请从头开始。

提交 `dff19a6ecf516fa674e24fcb3481413efc25b849` / [Windows CI 37440590549](https://github.com/AureliusWu/Test/actions/runs/37440590549)；原始游戏 ZIP **56,359,988 字节**，SHA-256 `0d09a78a482e2ff0d34e14f51d49c89d5cc0d36b91506d44c6a3bcdcc678d3f1`。

113 项 Windows Python、全部作者校验与 Ren’Py 8.5.3 lint 通过。源码和独立 EXE 各 **31/31 用例、359/359 断言**（1089.606 / 739.611 秒）；退出首进程后重新启动 EXE，真实读档另 **1/1 用例、10/10 断言**（3.745 秒）。failed / xfailed / xpassed / skipped / not run 全为 0，三个进程退出 0、未超时。

本次按用户“完成后发布正式版”的明确指令发布同一份验收 ZIP。Windows CI 使用 dummy 音频。真人试听、两结局阅读计时、普通电脑 / 中文路径 / 100% 与 150% DPI、创作定案及内容冻结仍为 pending，由用户统一操作；ASR 与自动执行时间不能代替这些结论。

[完整验收与包身份](https://github.com/AureliusWu/Test/blob/main/docs/RELEASE_ACCEPTANCE_V10.md) · [统一真人操作](https://github.com/AureliusWu/Test/blob/main/docs/HUMAN_HANDOFF.md) · [语音方案](https://github.com/AureliusWu/Test/blob/main/docs/VOICE_UPGRADE_V10.md) · [来源与许可](https://github.com/AureliusWu/Test/blob/main/CREDITS.md)。

发行 tag 基于包含验收记录的当前 main 提交。发布 CI 验证与上述游戏验收提交仅有文档 / 发布工作流差异，全部游戏与资产内容一致；安装包直接来自该成功验收，不重新构建。
