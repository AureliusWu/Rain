# 雨停之前 / Before the Rain Stops

离线中文 Ren’Py 视觉小说。雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。

main 已进入 **v1.0.0 验收候选**：六章、24 个叙事场景、4 次选择、16 条路线与 Normal / True 两个完整结局。40 处正文精修已经应用；七种表情、四背景、旧信 CG、17 句关键语音、三首原创程序音乐及环境音效保留。

正文全分支 **15,065** 字符，单路线 **11,303–11,666**。每分钟 250–350 字符的纯文字估算约 32–47 分钟；真人计时、试听、普通电脑 / DPI 和最终创作定案由用户统一完成，尚未记为通过。

## 下载与运行

v1.0 Windows 全量回归已通过，见 [v1.0 验收记录](docs/RELEASE_ACCEPTANCE_V10.md)。[统一真人清单](docs/HUMAN_HANDOFF.md) · [公开发行版本](https://github.com/AureliusWu/Test/releases)。历史 v0.9 技术证据保留在 [1080p 验收](docs/DISPLAY_ACCEPTANCE_V09.md)，不能代替新正文的运行结果。

1. 完整解压 `BeforeTheRainStops-1.0.0-win.zip` 到可写目录。
2. 双击 `BeforeTheRainStops.exe`。无需 Python、引擎、模型或网络。
3. 左键 / 空格 / Enter 推进，右键 / Esc 开菜单；下方提供回退、历史、快进、自动、存读档及设置。F 切换全屏。

原生 1920×1080、默认 1280×720 缩放窗口。v1 使用独立存档目录 `AureliusWu-BeforeTheRainStops-v1`，旧阶段存档保留，不跨阶段加载。

候选 `7593a348bf28e196c2ee3a55fd1e14c837289ef3` / [Windows CI 37411258713](https://github.com/AureliusWu/Test/actions/runs/37411258713)；原始游戏 ZIP **56,354,657 字节**，SHA-256 `4ecba6cea822947b08bc8a877af2d5eed4ccbb3ffdd367c92032c236f5dac048`。

91 项 Windows Python、作者侧全部校验与 Ren’Py 8.5.3 lint 通过。源码和独立 EXE 各 **31/31 用例、359/359 断言**（1088.999 / 741.506 秒）；关闭首进程后重新启动 EXE，真实读档另 **1/1 用例、10/10 断言**（3.719 秒）。全部 failed / xfailed / xpassed / skipped / not run 为 0，三个进程退出 0、未超时。

[Windows 候选下载](https://github.com/AureliusWu/Test/actions/runs/37411258713/artifacts/11390201913)（登录 GitHub，保留至 2027-01-04T03:55:25Z）。原始 ZIP 与统一审阅材料已另行交付；正式 Release 等待人工验收。

## 开发与验证

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
python -m tools.build.verify_package --zip dist/BeforeTheRainStops-1.0.0-win.zip --timeout 2400
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

## 正式发布

main 的 CI 生成候选游戏和证据。v1 正式发布入口为 `release-v10.yml`：要求机器验收、普通 Windows / DPI、24 个声音试听、两结局真人计时、创作定案与冻结记录全部绑定同一候选提交及 ZIP SHA-256。该入口下载已验收 artifact，校验后直接发布同字节 ZIP，再下载发行资产核对；不会重新构建另一份包。

当前人工记录为 pending，不创建正式 v1.0 tag。后续操作见 [发布步骤](docs/RELEASE_ACCEPTANCE_V10.md)。历史公开 Release 与当前 main 候选分开保留。

发布工具已完成 [工程补检](docs/RELEASE_ENGINEERING_V10.md)：Linux 97 项测试通过，补齐原报告异常计数，拒绝错误类型 / 缺失记录和机器问题。试玩候选及 Windows 证据继续绑定上方同一身份。
