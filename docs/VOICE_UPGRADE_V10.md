# v1.0 关键配音升级

用户要求优化角色语音、研究免费引擎，并在完成后发布正式版。继续保留真人体验集中由用户操作的安排。此指令允许工程通过后正式发布，不等同于真人试听、计时或创作定案已经完成。

## 选型

选用 **Qwen3-TTS-12Hz-1.7B-CustomVoice / Serena / Chinese**。官方将 Serena 描述为温暖、轻柔的年轻中文女声；1.7B CustomVoice 支持自然语言语气指令。模型与推理代码使用 Apache-2.0，下载后可以自行推理，不需要付费语音 API。

| 方案 | 本项目判断 | 官方来源 |
|---|---|---|
| Qwen3-TTS 1.7B CustomVoice | 有合适的中文预设女声和语气指令；本次采用 | https://github.com/QwenLM/Qwen3-TTS ，https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice |
| CosyVoice3 | 开源候选，支持零样本和指令能力；本次采用预设音色较直接的 Qwen 方案 | https://github.com/FunAudioLLM/CosyVoice |
| IndexTTS2 | 代码与模型许可需分别看；模型有单独使用协议，本次优先采用 Apache-2.0 模型 | https://github.com/index-tts/index-tts ，https://github.com/index-tts/index-tts/blob/main/INDEX_MODEL_LICENSE |

固定模型提交 `0c0e3051f131929182e2c023b9537f8b1c68adfe`，固定 `qwen-tts==0.1.1` 和 CPU PyTorch 2.9.1。模型仅在作者侧运行，不进入玩家包；游戏无新增账号、服务器或实时语音请求。

## 制作与绑定

- 17 句台词文字、角色与 voice ID 保持原身份，音频资产版本升为 2。保存 17 条具体表演指令和随机种子，使用同一 Serena 音色。
- 输出源 WAV 和游戏 OGG；双遍 EBU R128 响度处理目标为 -20 LUFS、真峰值 -2 dBTP，24 kHz 单声道。另检查完整解码、WAV/OGG 帧数、峰值和 RMS。
- Whisper small 先做诊断，Whisper large-v3 CPU int8 对全部录音独立复核，不向识别器提供期望台词。标点与繁简统一后逐句检查字符错误率，并检查“不”“没”计数与首次识别出现歧义的“我还不知道”“句号”“拍歪”；通过条件不代替人类对错读或表演的判断。
- 所有新文件在整批绑定、哈希和音频元数据预检通过后才替换；源请求与旧 voice manifest 的哈希必须一致。保留旧源 WAV，旧游戏 OGG 转入作者侧历史目录。
- 根据新版实际时长重新生成自动播放测试，继续验证语音播放、音量、结局配音和存读档恢复。

生成状态及逐句证据见 `evidence/voice-qwen-generation.json`，模型文件与参数出处见 `game/data/voice_provider_qwen.json`。Windows 包与本次验收身份见 `evidence/v10-acceptance.json`；生成证据出现前，本文只说明实施方案。

## 正式发布与真人后续

工程检查、Windows 实际执行和画面检查完成后，按照本次明确指令发布同一份验收 ZIP。`review/V10_PUBLICATION_AUTHORIZATION.json` 单独记录用户的发布指令、条件、目标提交、包哈希和仍未完成的人类检查。`review/V10_HUMAN_ACCEPTANCE.json` 保留真实 pending 状态，不能伪填 passed。

普通 Windows / DPI、完整试听、两结局阅读计时、最终创作定案仍由用户统一操作。不能将 ASR、虚拟音频设备或机器执行时长称为真人听感与阅读时长。
