# 雨停之前 / Before the Rain Stops

离线中文 Ren’Py 视觉小说。雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。

**v1.1.0 离线鉴赏室版已正式发布。** 六章、24 个叙事场景、四次选择、16 条路线、Normal / True 两个结局，七表情、四背景、旧信 CG、17 句配音及原创音乐 / 环境音效。

主菜单新增“鉴赏室”：五张已有背景 / CG、三首音乐随真实剧情解锁，退出后保留进度。未解锁内容隐藏图片和标题；支持全图查看、播放 / 切曲 / 暂停 / 停止、共用音量与静音，离开页面停止播放。

关键配音使用免费开源 **Qwen3-TTS 1.7B CustomVoice / Serena**，预生成 OGG 随包提供；当前台词可重听，已读历史可重播，自动模式等待重播结束。

## 下载与运行

[v1.1.0 Release](https://github.com/AureliusWu/Test/releases/tag/v1.1.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v1.1.0/BeforeTheRainStops-1.1.0-win.zip) · [本次验收](docs/RELEASE_ACCEPTANCE_V11.md) · [统一真人后续](docs/HUMAN_HANDOFF.md)

1. 完整解压 `BeforeTheRainStops-1.1.0-win.zip` 到可写目录。
2. 双击 `BeforeTheRainStops.exe`，无需 Python、引擎、模型、账号或语音 API，可离线游玩。
3. 左键 / 空格 / Enter 推进，右键 / Esc 开菜单，F 切换全屏；下方有回退、历史、快进、自动、存读档与设置。
4. 主菜单进入鉴赏室，看过的图片与听过的音乐自动解锁。

原生 1920×1080、默认 1280×720；沿用 `AureliusWu-BeforeTheRainStops-v1` 存档目录，实际验证 v1.0.1 两个代表存档和原生已读记录。

游戏验收提交 `b1f4f180b7a315fcb9a195889389d5af5e7688d2` / [Windows CI 37610239212](https://github.com/AureliusWu/Test/actions/runs/37610239212)；原始 ZIP **56,379,987 字节**，SHA-256 `a6ce022d23e5e88e3666d9806ca69a30077d52c56bf74820f4863f9ddc66fca0`。

Windows **118 项 Python**、全部作者校验及 Ren’Py 8.5.3.26051504 lint 通过；源码和独立 EXE 各 **36 用例 / 433 断言 / 78 截图**。新进程读档 / 鉴赏持久进度 **1/14/2**，公开 v1.0.1 写档 **1/12/2**、新 EXE 读取旧档 / 已读记录 **2/24/3**（用例 / 断言 / 截图）。五个完整进程退出 0、未超时，异常计数全为 0；两遍实际前缀另各 **6/88/25** 通过。

Windows 审计完整解码并核对 **163 张原始 PNG** 的尺寸 / SHA-256；复核 **52 个关键视图**，其中 8 个实际查看全分辨率 JPEG 副本、44 个原始 PNG 哈希与已有直接观察完全相同。副本绑定原图哈希并保留 JPEG 查看限制；85 包内资产、ZIP CRC、版本、玩家说明、许可与录音证据通过，玩家包无测试注入或模型。

全分支 15,065 字符，单路线 11,303–11,666。真人试听、Normal / True 阅读计时、普通电脑 / 中文路径 / DPI、最终创作定案与冻结继续由用户统一操作。Windows 使用 dummy 音频，自动执行耗时不等于阅读时长。真实旧档覆盖两个代表位置；不宣称逐一验证所有玩家存档或 Linux 原生 UI 通过。

## 开发与验证

当前游戏验收提交 `b1f4f180b7a315fcb9a195889389d5af5e7688d2`。完整机器与图像证据见 [本次验收](docs/RELEASE_ACCEPTANCE_V11.md)，发布进度见 [当前断点](docs/WORK_CHECKPOINT.md)。

Python 3.12、Pillow、SoundFile / NumPy 只用于开发。模型与推理依赖不进入玩家包。

```bash
python -m pip install -r requirements-dev.txt
python -m tools.preflight
python -m tools.validate
python -m tools.build.sdk
```

Windows 使用固定并校验 SHA-256 的 Ren’Py 8.5.3 SDK：

升级构建先从已发布的 v1.0.1 ZIP 校验并保留原语句名；CI 自动完成。手工构建也应在 lint 前运行 `python -m tools.build.seed_release_names --previous-zip <已下载的完整v1.0.1-ZIP>`。标准 [old-game 机制](https://www.renpy.org/doc/html/build.html#old-game) 不进入玩家包；真实旧档加载另行测试。

```powershell
$sdk = ".runtime/renpy-8.5.3-sdk"
& "$sdk/lib/py3-windows-x86_64/python.exe" "$sdk/renpy.py" . lint --error-code --all-problems
python -m tools.build.display
python -m tools.build.verify_package --source-sdk $sdk --timeout 2400
python -m tools.build.package --sdk $sdk
$version = (Get-Content VERSION -Raw).Trim()
python -m tools.build.verify_package --zip "dist/BeforeTheRainStops-$version-win.zip" --timeout 2400
python -m tools.build.verify_upgrade --previous-zip .runtime/compat/BeforeTheRainStops-1.0.1-win.zip --current-zip "dist/BeforeTheRainStops-$version-win.zip"
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

[正式 v1.1.0](https://github.com/AureliusWu/Test/releases/tag/v1.1.0) 已于 **2026-10-07T14:55:02Z** 发布，非草稿、非预发行，且为最新正式版。tag 指向 `f32c2de9b67aa3f46e9e32146239477407b9c450`，与验收提交仅有允许的文档差异；[发布 CI 37640637862](https://github.com/AureliusWu/Test/actions/runs/37640637862) 成功，公开 ZIP 下载回读 SHA-256 / CRC 与验收包一致。v1.0.1、v1.0.0 的标签及下载资产保持原样。实际身份见 [发布记录](docs/evidence/v11-publication.json)。

[发布授权](docs/review/V11_PUBLICATION_AUTHORIZATION.json) · [语音方案与来源](docs/VOICE_UPGRADE_V10.md)。

保留 [v1.0.1](https://github.com/AureliusWu/Test/releases/tag/v1.0.1) 及其 [证据](docs/evidence/v101-publication.json)，以及 [v1.0.0](https://github.com/AureliusWu/Test/releases/tag/v1.0.0) 及其 [证据](docs/evidence/v10-publication.json)。
