# 雨停之前 / Before the Rain Stops

离线中文 Ren’Py 视觉小说。雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。

**v1.0.1 免费配音重听补丁版。** 六章、24 个叙事场景、四次选择、16 条路线与 Normal / True 两个完整结局。包含七表情、四背景、旧信 CG、17 句关键配音及原创程序音乐 / 环境音效。

关键配音使用免费开源 **Qwen3-TTS 1.7B CustomVoice / Serena**，预生成 OGG 随游戏提供，不需付费语音 API、账号、模型或运行时网络。当前有配音的台词提供“重听语音”；已读历史中有录音的条目提供“重播语音”，离开历史停止重播。自动播放会等待新一轮重播结束。

## 下载与运行

[v1.0.1 Release](https://github.com/AureliusWu/Test/releases/tag/v1.0.1) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v1.0.1/BeforeTheRainStops-1.0.1-win.zip) · [本次验收](docs/RELEASE_ACCEPTANCE_V101.md) · [统一真人后续](docs/HUMAN_HANDOFF.md) · [保留的 v1.0.0](https://github.com/AureliusWu/Test/releases/tag/v1.0.0)

1. 完整解压 `BeforeTheRainStops-1.0.1-win.zip` 到可写目录。
2. 双击 `BeforeTheRainStops.exe`。无需 Python、引擎或模型，可离线游玩。
3. 左键 / 空格 / Enter 推进，右键 / Esc 开菜单；下方提供回退、历史、快进、自动、存读档与设置。F 切换全屏。重听后可点击对白区域继续阅读。

原生 1920×1080、默认 1280×720 缩放窗口。v1 使用存档目录 `AureliusWu-BeforeTheRainStops-v1`；已实际检查 v1.0.0 的开局配音行和后半段存档读取。更早 v0.x 存档保留，跨阶段请从头开始。

游戏验收提交 `cfacee500c15498175f165f32ddfb6c70f7c9314` / [Windows CI 37496730978](https://github.com/AureliusWu/Test/actions/runs/37496730978)；原始 ZIP **56,364,666 字节**，SHA-256 `9238e2d06cb7820056912455765f42b74337bf857dacd5a213be4cc349843f36`。

Windows 113 项 Python、全部作者校验及 Ren’Py 8.5.3 lint 通过；源码和独立 EXE 各 **34/34 用例、404/404 断言**，新进程读档 **1/1 用例、10/10 断言**。精确的公开 v1.0.0 EXE 写档 **1/12**，新版 EXE 读取旧档 **2/20** 均通过；全部异常计数为 0，五个进程退出 0、未超时。

145 张 PNG 完整解码并检查尺寸 / SHA-256；42 个关键 EXE / 升级读取视图复核，其中 17 个直接查看当前图、25 个仅在 SHA-256 与此前直接审阅图一致时复用。85 包内资产、原始 ZIP CRC、版本、玩家说明和许可核验通过；原始包没有注入测试脚本。

全分支正文 15,065 字符，单路线 11,303–11,666。真人试听、Normal / True 阅读计时、普通电脑 / 中文路径 / DPI、最终创作定案与冻结继续待用户统一操作。Windows runner 使用 dummy 音频，自动执行耗时不等于阅读时长。

## 开发与验证

当前游戏验收提交 `cfacee500c15498175f165f32ddfb6c70f7c9314`。完整机器与图像证据见 [本次验收](docs/RELEASE_ACCEPTANCE_V101.md)，发布进度见 [当前断点](docs/WORK_CHECKPOINT.md)。

Python 3.12、Pillow、SoundFile / NumPy 只用于开发。模型与推理依赖不进入玩家包。

```bash
python -m pip install -r requirements-dev.txt
python -m tools.preflight
python -m tools.validate
python -m tools.build.sdk
```

Windows 使用固定并校验 SHA-256 的 Ren’Py 8.5.3 SDK：

升级构建先从已发布的 v1.0.0 ZIP 校验并保留原语句名；CI 自动完成。手工构建也应在 lint 前运行 `python -m tools.build.seed_release_names --previous-zip <已下载的完整v1.0.0-ZIP>`。标准 [old-game 机制](https://www.renpy.org/doc/html/build.html#old-game) 不进入玩家包；真实旧档加载另行测试。

```powershell
$sdk = ".runtime/renpy-8.5.3-sdk"
& "$sdk/lib/py3-windows-x86_64/python.exe" "$sdk/renpy.py" . lint --error-code --all-problems
python -m tools.build.display
python -m tools.build.verify_package --source-sdk $sdk --timeout 2400
python -m tools.build.package --sdk $sdk
python -m tools.build.verify_package --zip dist/BeforeTheRainStops-1.0.1-win.zip --timeout 2400
```

## 数据与来源

`game/data/story.json` 是剧情唯一事实来源，编译成原生 label / menu / if。仅 affection、trust、truth_known 三个状态，遍历全部 16 条可达路径。源码资产、Scene Prompt、录音文字、来源、许可证和 SHA-256 均保留；运行时没有 LLM、TTS 服务或服务器。

| 位置 | 内容 |
|---|---|
| `game/data/` | 剧情、资产及语音绑定 |
| `game/script/*_generated.rpy` | 自动生成的运行脚本 |
| `assets_source/`、`prompts/` | 原始资产、版本化请求与 Registry |
| `tools/`、`tests/` | 编译、完整性和回归工具 |
| `CREDITS.md`、`licenses/` | 署名、第三方许可与 AI 输出说明 |

[正文精修记录](docs/review/V10_PROSE_REVIEW.json) · [字数统计](docs/STORY_STATS_V10.md) · [项目约束](docs/PROJECT.md) · [测试计划](docs/TEST_PLAN.md)。最终主题、角色、美术与结局由用户决定。


## 正式发布记录

`release-v10.yml` 依据用户“完成后发布正式版”的独立授权，绑定 Windows 机器验收、17 句语音证据和真实 pending 人验表。使用成功 CI 已验收的原始 ZIP，发布并下载回读核对相同字节。v1.0.0 tag 指向包含验收记录的发行提交，CI 已验证与游戏验收提交仅有文档 / 发布工作流差异；后续文档提交不改变发行包。

[发行证据](docs/evidence/v10-publication.json) · [语音方案与来源](docs/VOICE_UPGRADE_V10.md) · [发布授权](docs/review/V10_PUBLICATION_AUTHORIZATION.json)。
