# 雨停之前 / Before the Rain Stops

离线中文 Ren’Py 视觉小说。雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。

**v1.0.0 正式版已发布。** 六章、24 个叙事场景、四次选择、16 条路线与 Normal / True 两个完整结局。40 处正文精修、七表情、四背景、旧信 CG、17 句关键配音及原创程序音乐 / 环境音效。

关键配音升级为免费开源 **Qwen3-TTS 1.7B CustomVoice / Serena**，按台词设定语气并统一混音；预生成 OGG 随游戏提供，不需付费语音 API、账号、模型或运行时网络。

## 下载与运行

[正式 v1.0.0](https://github.com/AureliusWu/Test/releases/tag/v1.0.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v1.0.0/BeforeTheRainStops-1.0.0-win.zip) · [验收记录](docs/RELEASE_ACCEPTANCE_V10.md) · [统一真人后续](docs/HUMAN_HANDOFF.md)

1. 完整解压 `BeforeTheRainStops-1.0.0-win.zip` 到可写目录。
2. 双击 `BeforeTheRainStops.exe`。无需 Python、引擎或模型，可离线游玩。
3. 左键 / 空格 / Enter 推进，右键 / Esc 开菜单；下方提供回退、历史、快进、自动、存读档与设置。F 切换全屏。

原生 1920×1080、默认 1280×720 缩放窗口。v1 使用独立存档目录 `AureliusWu-BeforeTheRainStops-v1`，旧阶段存档保留，请从头开始。

游戏验收提交 `dff19a6ecf516fa674e24fcb3481413efc25b849`；发行 tag 指向 `b4f06f89eebb73ff0494cb18fc4cfc38192c84ce`，仅增加文档与发布工作流差异，游戏内容完全一致。原始 ZIP **56,359,988 字节**，SHA-256 `0d09a78a482e2ff0d34e14f51d49c89d5cc0d36b91506d44c6a3bcdcc678d3f1`。

Windows 113 项 Python、全部作者校验与 Ren’Py 8.5.3 lint 通过；源码和独立 EXE 各 31 用例 / 359 断言，退出后新进程读档 1 用例 / 10 断言通过。全部异常计数为 0，三个进程退出 0、未超时；131 PNG 完整解码、35 个 EXE 关键视图复核、85 包内资产与 ZIP CRC / 许可检查通过。

全分支正文 15,065 字符，单路线 11,303–11,666。真人试听、Normal / True 阅读计时、普通电脑 / 中文路径 / DPI、最终创作定案与冻结仍待用户统一操作。ASR、dummy 音频与自动测试耗时不代表这些项目通过。

## 开发与验证

`main` 正在验证 v1.0.1 配音重听小版本，公开正式版仍为上方 v1.0.0。新增当前台词和已读历史的重播，并检查已发布 v1.0.0 EXE 的真实存档升级；进度见 [当前断点](docs/WORK_CHECKPOINT.md)。

Python 3.12、Pillow、SoundFile / NumPy 只用于开发。模型与推理依赖不进入玩家包。

```bash
python -m pip install -r requirements-dev.txt
python -m tools.preflight
python -m tools.validate
python -m tools.build.sdk
```

Windows 使用固定并校验 SHA-256 的 Ren’Py 8.5.3 SDK：

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
