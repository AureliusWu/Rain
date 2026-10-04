# 音频规范

优先级：环境声 → BGM → 关键语音。所有声音支持独立混音，voice / music / sfx 使用 Ren'Py 原生音量设置。

声音运行时离线；模型、API 密钥、联网服务不随游戏发布。所有合成台词与 line_id、voice_id、文字、角色、模型/声音、情绪、源文件、版本和游戏文件绑定。

BGM：原创简单主题，安静、低音量、不模仿现成音乐。环境声：雨声。源 WAV 与游戏 OGG 分离。源代码辅助谱曲和程序合成明确注明，不冒称为音乐模型输出。

v0.1 为原创程序合成 BGM 与雨声，无语音。v0.2 仅制作关键台词，试听后再决定是否扩大配音。音色选择与艺术效果待用户审阅。

## v0.2 配音复现

Kokoro-82M v1.1-zh ONNX int8、zf_001、speed 0.95、24kHz。6 句合计 19.759 秒；源 WAV 保存，游戏使用 Vorbis OGG。emotion=calm 只是制作方向，模型没有接收情绪条件，不声称具备情绪控制。

可选依赖见 requirements-voice.txt。下载 model-files-v1.1 的 kokoro-v1.1-zh.int8.onnx、voices-v1.1-zh.bin，以及官方模型 config.json，放入仓库外的模型目录；生成工具核验三个文件的固定 SHA-256。FFmpeg 需要在 PATH。

```bash
python -m pip install -r requirements-voice.txt
ORT_DISABLE_TELEMETRY=1 python -m tools.audio_process.generate_voice --model /path/kokoro-v1.1-zh.int8.onnx --voices /path/voices-v1.1-zh.bin --config /path/config.json
python -m tools.compile_story
python -m tools.validate
```

ONNX Runtime 1.30 的非 Windows 官方构建默认启用联网遥测。本项目在任何相关导入前固定 ORT_DISABLE_TELEMETRY=1，并调用 disable_telemetry_events；使用官方完整关闭机制，不依赖网络请求被拒绝来实现离线。依据：[官方隐私说明](https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md)。模型下载是独立步骤；台词合成不需要在线服务。播放器包不含推理库。

自动检查覆盖文本绑定、音频存在、哈希、非零时长、播放通道和静音切换。无削波源文件峰值已检查；最终发音、混音听感和情绪仍需要真人试听。
