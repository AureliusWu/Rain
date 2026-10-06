# v1.0 配音升级验收与正式发布

新版配音及工程验收已完成，按用户明确指令进入正式发布。本页绑定本次 Qwen 配音的游戏包；旧 Kokoro 候选机器、画面及人验表另保留在 `evidence/v10-kokoro-acceptance.json`、`evidence/v10-kokoro-visual-review.json` 与 `review/V10_KOKORO_HUMAN_ACCEPTANCE.json`。

## 当前机器验收

提交 `dff19a6ecf516fa674e24fcb3481413efc25b849` / [Windows CI 37440590549](https://github.com/AureliusWu/Test/actions/runs/37440590549)；原始游戏 ZIP **56,359,988 字节**，SHA-256 `0d09a78a482e2ff0d34e14f51d49c89d5cc0d36b91506d44c6a3bcdcc678d3f1`。

113 项 Windows Python、全部作者校验与 Ren’Py 8.5.3 lint 通过。源码和独立 EXE 各 **31/31 用例、359/359 断言**（1089.606 / 739.611 秒）；退出首进程后重新启动 EXE，真实读档另 **1/1 用例、10/10 断言**（3.745 秒）。failed / xfailed / xpassed / skipped / not run 全为 0，三个进程退出 0、未超时。

131 张原生 PNG 完整解码并核对尺寸 / SHA-256。35 张实际 EXE 关键画面由当前原图直接查看或匹配既有直接审阅图的相同 SHA-256 复核，方法逐图记录；未发现遗留机器问题。85 个包内资产、ZIP CRC、版本、玩家说明、Qwen 等许可及文件排除均通过；原始 ZIP 未注入测试脚本，未含推理模型。

17 句关键配音已替换为免费开源 Qwen3-TTS 1.7B CustomVoice / Serena。逐句保存语气指令，双遍响度处理目标 -20 LUFS / 真峰值 -2 dBTP；24 kHz 单声道、合计 57.360 秒。全部信号与独立 large-v3 ASR 校验通过：16 句归一化文字一致，1 句“哪 / 哪儿”儿化差异。旧 Kokoro 源录音与 OGG 历史保留。 模型和推理代码为 Apache-2.0，固定模型 revision 与依赖、每句种子、请求、来源和哈希均有记录；模型仅在作者侧运行。

Windows CI 使用 dummy 音频。真人试听、两结局阅读计时、普通电脑 / 中文路径 / 100% 与 150% DPI、创作定案及内容冻结仍为 pending，由用户统一操作；ASR 与自动执行时间不能代替这些结论。

## 发布依据与同字节验证

用户最新指令为“优化角色语音……搞点免费的语音引擎……完成后发布正式版”。此明确授权更新先前等待真人全部完成才发布的安排。

`review/V10_PUBLICATION_AUTHORIZATION.json` 绑定上述指令、语音证据 SHA-256、当前提交与包哈希，并披露五组 pending。`review/V10_HUMAN_ACCEPTANCE.json` 仅更新包身份，真人结果保持真实 pending、证据为空、实测分钟为 null。

`release-v10.yml` 检查机器验收、语音和用户授权，从成功 CI 的原始 `windows-<commit>` artifact 取包，核对原始 SHA-256 / 大小 / CRC / 许可 / 预览后创建非预发行 v1.0.0，随后下载公开发行资产核对同一字节。任何现存同名 tag / Release 均拒绝覆盖；不会重新构建另一份包。

目前处于正式发布执行前；成功回读后的公开 URL、发行资产与运行身份补记于 `evidence/v10-publication.json`。真人后续统一见 [HUMAN_HANDOFF](HUMAN_HANDOFF.md)，语音来源与自动校验限制见 [VOICE_UPGRADE_V10](VOICE_UPGRADE_V10.md)。
