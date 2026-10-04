# v0.6 音频制作与接入

保留既有剧情、美术与 zf_001 音色。本轮仅补充关键台词，17 句合计 58.048 秒；原有六句与全部 66 个既有游戏资产字节保持一致。新增资产仍是可试听候选，最终音色和音乐审美由用户决定。

## 场景音轨

| 声音 | 接入位置 | 制作方式 |
|---|---|---|
| rain_theme | 开场、第四章回忆 | 原有原创程序 BGM |
| unspoken_theme | 旧信与坦白至第三章 | 新增原创音符与程序合成 |
| next_message_theme | 离站及两个结局 | 新增原创音符与程序合成 |
| rain_ambience | 开场至第四章 | 原有程序雨声 |
| rain_light_ambience | 第五章雨势减小 | 固定随机种子与低通程序合成 |
| paper_rustle | 递信、True 结局放照片 | 短噪声包络合成 |
| message_ping | 第三章发送句号、Normal 结局收消息 | 两音短提示，不引用产品提示音 |

True 在 s07_true_l006 小店坐下时淡出雨声；Normal 在 s08_normal_l010“雨停了”时淡出。结局卡停止 music 与 ambient。music / ambient 使用 if_changed，换曲淡出淡入各 1 秒；sound 使用原生单次播放，voice 使用原生语音语句。所有设置、回退和存读档由 Ren'Py 负责。

## 配音复现

继续使用 requirements-voice.txt 中固定依赖和原有三份模型 SHA-256。生成工具在任何推理导入前设置 ORT_DISABLE_TELEMETRY=1，并关闭事件 API。模型与声音库是制作缓存，不随游戏发布。

```bash
python -m pip install -r requirements-voice.txt
ORT_DISABLE_TELEMETRY=1 python -m tools.audio_process.generate_voice --model /path/kokoro-v1.1-zh.int8.onnx --voices /path/voices-v1.1-zh.bin --config /path/config.json
python -m tools.audio_process.render_soundtrack --dry-run
python -m tools.audio_process.render_soundtrack
python -m tools.compile_story
python -m tools.compile_tests
python -m tools.validate
```

新台词的准确文本、line_id、声音、语速、Prompt、处理策略及固定模型配置形成 generation_sha256。已有录音必须同时匹配请求、源 WAV 与游戏 OGG 的哈希及解码元数据；配置或文件变更时拒绝静默覆盖，应审阅新的 voice_id / version。全部请求匹配时返回 0 changes，不初始化模型。原 v0.2 录音保留原处理策略；新录音有 15ms 边缘淡入淡出与 .89 峰值上限，未提高音量或增加虚构情绪控制。

程序谱曲和音效的方向、音符、种子、幅度与输出位置记录在 prompts/audio/soundtrack_v1.json；配音方向记录在 prompts/voice/heroine_v2.md，均登记 Registry。音乐是 AI 辅助创作和程序合成，未调用音乐生成模型。工具先在临时目录生成并解码全部新输出，再导入；已有文件哈希改变时拒绝覆盖。制作过程不声称具备断电恢复或跨进程事务保证。

## 自动验证与试听

SoundFile 0.14.0 仅用于开发校验，依赖见 requirements-dev.txt；播放器不需要它。24 个 OGG 和对应 WAV 必须全量解码、非静音、有限样本，记录格式、声道、采样率、帧数、时长、峰值及未加权 RMS。源与游戏文件帧数匹配；PNG 和原有图片重建检查继续执行。

```bash
python -m tools.audio_validator --report reports/audio.json
```

15 个新增 Python 用例覆盖假 OGG 头、静音、削波、非有限样本、长度／元数据差异、错误音效与配置缓存失效。三个新增原生用例检查纸张／消息播放、坦白与结局语音、音乐切换和雨声淡出；旧存读档用例追加音轨恢复，全静音追加 sfx / voice 断言。

试听重点是汉语停顿与发音、两种信任回应、Normal 消息朗读、True 结尾、循环边缘和音效是否抢对白。信号测量与 dummy 输出自动测试不等于已经完成真人试听或普通 Windows 电脑双击体验。当前已测最大 OGG 峰值 .420157，语音 RMS -24.043～-22.833 dBFS；实际平台结果见 STATUS.md。
