> 远端接续：最终提交的 Web/PWA 与公开网站验证已通过；Windows 作者检查、lint、两轮原生前缀与 ZIP 构建通过；旧档升级中的测试范围已修正，Windows 完整验收重新接续。详见 [候选检查点](docs/production/CANDIDATE-v1.3.0.json)。

> 2026-10-18：**v1.3.0 阅读收藏与离线进度候选已实现，完整远端验收接续中。** [本轮实现与验证](docs/production/IMPLEMENTATION-20261018.md)。正式下载仍为 v1.2.2；当前候选不覆盖原发行资产。

> 2026-10-16：**v1.2.2 双平台正式版已发布。** [在线游玩](https://aureliuswu.github.io/Rain/) · [Windows / Web 下载](https://github.com/AureliusWu/Rain/releases/tag/v1.2.2) · [本次完整发布记录](docs/production/PUBLISHED-v1.2.2.json)。四个公开资产与成功 CI 原字节一致，当前公网 PWA 的 worker 也已逐字节核对。 本轮更新与推送的最终核验见 [闭环回执](docs/production/RELEASE-CLOSURE-20261017.md)。 下一版目标与四仓交流见 [更新规划](docs/production/FOUR-GAMES-NEXT-20261017.md)。

# 雨停之前 / Before the Rain Stops

离线中文 Ren’Py 视觉小说。雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。

**v1.2.2：Ren'Py 原生 Windows EXE + 同引擎 WebAssembly PWA。** 历史记录增加关键词搜索、人物筛选、结果数量和一键清除；筛选后可重听原台词，关闭重开会重置筛选。网页版支持中文输入，清除筛选后历史面板保持打开。六章、24 个叙事场景、四次选择、16 条路线和 Normal / True 两个结局，沿用 560 台词 ID、17 句录音与 v1 存档身份。见 [版本说明](docs/RELEASE_NOTES_V122.md)。

PWA 首次联网保存完整内容后可安装、离线重开和导入 / 导出 Ren'Py 原生存档。浏览器与 Windows 的本机保存位置独立；请使用浏览器左上角导出备份。新版本下载完成后等待旧窗口关闭再激活，正在阅读的窗口继续使用原版本。

三作品共用制作契约 v1.2.0、[精修方法与场景模板](docs/production/CREATIVE-PLAYBOOK.md) 和可导出的许可素材包：`node scripts/vn-materials.mjs verify`、`node scripts/vn-materials.mjs export .reuse-kit/v1.2.0`。保留角色、剧情、引擎和存档身份，移植入口见 [可复用素材](docs/production/REUSABLE-MATERIALS.md)。

与《回路》的离线人物语音、声音演出和多角色请求配方已双向整理，见 [双项目制作交流](docs/production/RAIN-CIRCUIT-BRIDGE.md)。v1.2.1 的 [43 段剧情精修与小店画面](docs/production/CREATIVE-REVIEW.md) 已包含在当前版本。

主菜单进入“鉴赏室”：五张已有背景 / CG、三首音乐随真实剧情解锁，退出后保留进度，未解锁内容隐藏图片和标题。音乐鉴赏显示已解锁数量、当前曲名及播放 / 暂停 / 停止状态；暂停后显示“继续”，停止后提示选择已解锁音乐。状态分隔符改用现有字体支持的中文冒号，修复方框缺字。

关键配音使用免费开源 **Qwen3-TTS 1.7B CustomVoice / Serena**，预生成OGG随包提供；当前台词可重听，已读历史可重播，自动模式等待重播结束。

## 下载与运行

[v1.2.2 Release](https://github.com/AureliusWu/Rain/releases/tag/v1.2.2) · [Windows ZIP](https://github.com/AureliusWu/Rain/releases/download/v1.2.2/BeforeTheRainStops-1.2.2-win.zip) · [Web ZIP](https://github.com/AureliusWu/Rain/releases/download/v1.2.2/BeforeTheRainStops-1.2.2-web.zip) · [SHA-256](https://github.com/AureliusWu/Rain/releases/download/v1.2.2/SHA256SUMS.txt) · [统一真人后续](docs/HUMAN_HANDOFF.md)

1. 完整解压 `BeforeTheRainStops-1.2.2-win.zip` 到可写目录。
2. 双击 `BeforeTheRainStops.exe`，无需Python、引擎、模型、账号或语音API，可离线游玩。
3. 左键 / 空格 / Enter推进，右键 / Esc开菜单，F切换全屏；下方有回退、历史、快进、自动、存读档与设置。
4. 主菜单进入鉴赏室，看过的图片与听过的音乐自动解锁。

原生1920×1080、默认1280×720；沿用 `AureliusWu-BeforeTheRainStops-v1` 存档目录，已用公开v1.1.0实际写入并验证两个代表存档和原生已读解锁。

游戏与 tag 同为 `15d87ef4455b95feb6069e044a1d3a6456f75e0c`。Windows ZIP **56,170,913 字节**，SHA-256 `f5a482cf5a36ec2dfda047d1d3d67610d4c221c37e62b6aaac318ae417a176f3`；Web ZIP **47,790,829 字节**，SHA-256 `b18718ca1df99975f55d1bdd8df3d6a3bc58e82bd9c595b4e958623e2c0e86fb`。

[Windows CI 38828604885](https://github.com/AureliusWu/Rain/actions/runs/38828604885) 的源码和独立 EXE 各 **37 用例 / 477 断言 / 84 截图**，新进程 **1/16/3**、真实 v1.1.0 写档 **1/14/3**、新版读取 **2/26/4**，两遍语音 / 历史前缀各 **7/132/31** 通过；178 张原始 PNG、85 资源、ZIP CRC 与许可完成审计。原生进程退出 0、未超时，异常与跳过计数均为 0。

[PWA CI 38828604848 attempt 2](https://github.com/AureliusWu/Rain/actions/runs/38828604848/attempts/2) 完成官方 WASM 的 14 项实际浏览器检查及公开站点存读档、中文检索、断网重开续读，页面错误为 0。公网 revision `dacc7624a60ede30f69edece`，当前 worker 与正式 Web ZIP 精确一致。正式发布后已独立匿名下载全部四个资产，核对完整 SHA-256、字节数、两个 ZIP CRC 和三条 checksum。

真人试听、Normal / True 阅读计时、普通电脑 / 中文路径 / DPI、物理设备安装、最终创作定案与冻结继续由用户统一操作，五组保持 pending。Windows 使用 dummy 音频；自动执行耗时不能代替阅读时长，178 PNG 的机器审计也不代表新增直接逐图审阅。真实旧档覆盖两个代表位置；不宣称已验证全部玩家旧档或 Linux 原生 UI。

## 开发与验证

当前游戏验收提交 `15d87ef4455b95feb6069e044a1d3a6456f75e0c`。完整工件、原生 / PWA 与发行身份见 [本次发布记录](docs/production/PUBLISHED-v1.2.2.json)，发布进度见 [当前断点](docs/WORK_CHECKPOINT.md)。

Python 3.12、Pillow、SoundFile / NumPy 只用于开发。模型与推理依赖不进入玩家包。

```bash
python -m pip install -r requirements-dev.txt
python -m tools.preflight
python -m tools.validate
python -m tools.build.sdk
```

Windows 使用固定并校验 SHA-256 的 Ren’Py 8.5.3 SDK：

本机验收可通过 `RENPY_ACCEPTANCE_WINDOWED=1`、`RENPY_HIGHDPI=1` 使用真正 1920×1080 窗口，无需改系统分辨率或 DPI；仍实际切换全屏并校验硬件尺寸，所有原生 / 缩放 PNG 门槛保持。源码验收与发行构建分别复制到临时工程，排除 `game/saves`，保护作者 / 玩家持久数据。

Web 构建与浏览器检查：

```powershell
python -m tools.build.sdk
python -m tools.build.web
npm ci
npx playwright install chromium
npm run test:pwa
```

生成 `dist/web/` 与版本化 `*-web.zip`，CI 使用相同官方 WASM、完整原子缓存和 `/Rain/` 子路径检查后部署 Pages。Windows 继续使用 Ren'Py 原生 ZIP，无新播放器框架。

升级构建先从已发布的 v1.1.0 ZIP 校验并保留原语句名；CI 自动完成。手工构建也应在 lint 前运行 `python -m tools.build.seed_release_names --previous-zip <已下载的完整v1.1.0-ZIP>`。标准 [old-game 机制](https://www.renpy.org/doc/html/build.html#old-game) 不进入玩家包；真实旧档加载另行测试。

```powershell
$sdk = ".runtime/renpy-8.5.3-sdk"
& "$sdk/lib/py3-windows-x86_64/python.exe" "$sdk/renpy.py" . lint --error-code --all-problems
python -m tools.build.display
python -m tools.build.verify_package --source-sdk $sdk --timeout 2400
python -m tools.build.package --sdk $sdk
$version = (Get-Content VERSION -Raw).Trim()
python -m tools.build.verify_package --zip "dist/BeforeTheRainStops-$version-win.zip" --timeout 2400
python -m tools.build.verify_upgrade --previous-zip .runtime/compat/BeforeTheRainStops-1.1.0-win.zip --current-zip "dist/BeforeTheRainStops-$version-win.zip"
```

可选共享结构检查：`node scripts/vn-contract.mjs game/data/story.json`。制作契约见 [SHARED-VN.md](docs/production/SHARED-VN.md)，不替代16条原生状态路线及Windows实际包验收。

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

[正式 v1.2.2](https://github.com/AureliusWu/Rain/releases/tag/v1.2.2) 于 **2026-10-16T06:34:32Z** 发布，非草稿、非预发行，GitHub latest 也指向该版。[发布 CI 38861929614](https://github.com/AureliusWu/Rain/actions/runs/38861929614) 成功，保留已验收的原始 tag 和四个资产，正式公开后逐一无凭证下载回读。原准备提交 `93c4714` 与完成提交 `a5f0fdf` 分别记录；后者仅修复草稿读取 / 恢复，不重建游戏。最后的文档归档也不改变已发布玩家包。

[发布授权](docs/review/V122_PUBLICATION_AUTHORIZATION.json) · [完整身份证据](docs/production/PUBLISHED-v1.2.2.json) · [语音方案与来源](docs/VOICE_UPGRADE_V10.md)。

历史 [v1.1.1 发布记录](docs/evidence/v111-publication.json)、[v1.1.0](https://github.com/AureliusWu/Test/releases/tag/v1.1.0)、[v1.0.1](https://github.com/AureliusWu/Test/releases/tag/v1.0.1) 和 [v1.0.0](https://github.com/AureliusWu/Test/releases/tag/v1.0.0) 保留原有下载；v1.2.1 的工程候选证据保留在 [精修记录](docs/production/PUBLISHED-v1.2.1.json)。
