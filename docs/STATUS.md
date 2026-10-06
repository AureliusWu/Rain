# v1.0.1 配音重听开发候选 — 2026-10-06

本批继续打磨已完成的免费配音：当前有录音的台词显示“重听语音”，历史中仅已读、有录音的条目显示“重播语音”。沿用正文、路线、语音文件和 v1 存档目录。旧正式版的真实语音行存档和后半段存档将由新 EXE 读取并检查状态与新重播入口。

本地 113 Python、全部作者校验及 Ren'Py 8.5.3 lint 通过；Linux 环境无显示服务，本批没有通过 Linux 原生 UI 测试。Windows 源码 / EXE / 新进程 / 真实 v1.0.0 升级测试待执行，不能沿用下方 v1.0.0 的结果作为新功能验收。

公开正式版仍为下方 v1.0.0；本批候选不覆盖既有 tag 或 ZIP。真人后续仍由用户统一操作。

---

# v1.0.0 正式发布 — 2026-10-06

[正式 Release](https://github.com/AureliusWu/Test/releases/tag/v1.0.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v1.0.0/BeforeTheRainStops-1.0.0-win.zip) · [发行回读记录](evidence/v10-publication.json)

17 句关键配音已替换为免费开源 Qwen3-TTS 1.7B CustomVoice / Serena，保存逐句表演指令并完成响度处理。全部信号 / 独立 ASR 检查通过；保留旧录音历史，玩家无需模型或网络。

游戏验收提交 `dff19a6ecf516fa674e24fcb3481413efc25b849`；发行 tag 指向 `b4f06f89eebb73ff0494cb18fc4cfc38192c84ce`，仅增加文档与发布工作流差异，游戏内容完全一致。原始 ZIP **56,359,988 字节**，SHA-256 `0d09a78a482e2ff0d34e14f51d49c89d5cc0d36b91506d44c6a3bcdcc678d3f1`。

Windows 113 项 Python、全部作者校验与 Ren’Py 8.5.3 lint 通过；源码和独立 EXE 各 31 用例 / 359 断言，退出后新进程读档 1 用例 / 10 断言通过。全部异常计数为 0，三个进程退出 0、未超时；131 PNG 完整解码、35 个 EXE 关键视图复核、85 包内资产与 ZIP CRC / 许可检查通过。

按用户“完成后发布正式版”发布，Release 为非 draft、非 prerelease。发布 workflow 下载既有验收 ZIP，公开资产再次下载校验通过，没有重新构建。真人试听、Normal / True 阅读计时、普通电脑 / 中文路径 / DPI、最终创作定案与冻结仍待用户统一操作。ASR、dummy 音频与自动测试耗时不代表这些项目通过。


---

# 以下为本次发布前的历史记录

# v1.0 免费语音升级进度（当前批次）

Qwen3-TTS 1.7B / Serena 制作管线已提交，17 句录音已集成到 main（21d5176）。生成任务 37436201390 与恢复核验 37438947888 的出处保留。作者侧 113 项 Python、全部校验与 Linux lint 已通过。新版录音合计 57.360 秒，large-v3 逐句复核通过：16 句归一化文字一致，1 句为“哪 / 哪儿”的儿化差异。下方为之前的 Kokoro 候选验收历史，新配音需要重新生成安装包并完成 Windows 全链路，尚未发布正式版。最新候选 dff19a6 / Windows CI 37440590549 已通过前置校验和 lint，正在执行实际交互。

用户新增指令为“完成后发布正式版”；独立发布授权将绑定新版提交、语音证据和安装包字节，同时保留真人统一操作项。实施说明见 VOICE_UPGRADE_V10.md。

---

# v1.0 候选更新 — 2026-10-06

候选 `7593a348bf28e196c2ee3a55fd1e14c837289ef3` / [Windows CI 37411258713](https://github.com/AureliusWu/Test/actions/runs/37411258713)；原始游戏 ZIP **56,354,657 字节**，SHA-256 `4ecba6cea822947b08bc8a877af2d5eed4ccbb3ffdd367c92032c236f5dac048`。

91 项 Windows Python、作者侧全部校验与 Ren’Py 8.5.3 lint 通过。源码和独立 EXE 各 **31/31 用例、359/359 断言**（1088.999 / 741.506 秒）；关闭首进程后重新启动 EXE，真实读档另 **1/1 用例、10/10 断言**（3.719 秒）。全部 failed / xfailed / xpassed / skipped / not run 为 0，三个进程退出 0、未超时。

131 张 PNG 完整解码；35 张实际 EXE 关键画面按当前原图或相同 SHA-256 的既有直接审阅记录复核，未发现遗留机器问题。85 个包内资产 SHA-256、原始 ZIP CRC、版本、玩家说明及许可文件已核验；未注入测试脚本。仅保留引擎启动必需的 build_info / bytecode 缓存。

Windows runner 使用 dummy 音频；真人试听、两结局阅读计时、普通电脑 / 中文路径 / 100% 与 150% DPI、创作定案及内容冻结继续待用户统一操作。正式发布 workflow 尚未执行，没有正式 v1.0 tag / Release。

40 处正文精修已应用；全分支 15,065 字符，单路线 11,303–11,666，560 台词 ID / 17 句录音 / 16 路线保留。版本与 v1 独立存档目录同步；81 份版本化 Prompt 可追踪。统一审阅提供 66 EXE PNG、24 OGG / WAV、两结局全文及其余 100 行分支，覆盖全部正文。

## 发布工具补检 — 已完成

Linux 97 项 Python、全部作者校验与引擎 lint 通过。新增 6 项发布反例；原生摘要与发布检查完整保留 / 验证 xfailed、xpassed，拒绝布尔值或错误类型计数、源码 / EXE 数量不一致、缺失记录和机器问题。三个原始 Windows 报告已重新解析，原游戏 ZIP / 预览校验通过，真实人验仍 pending。详见 [RELEASE_ENGINEERING_V10](RELEASE_ENGINEERING_V10.md)。

# 历史阶段记录（v0.9 及以前）

## v0.9 原生 1080p 技术验收完成 — 2026-10-06

候选 `d8c61e2b3b03498115ea26d89d029026a0191c40` / [Windows CI 37405577661](https://github.com/AureliusWu/Test/actions/runs/37405577661)；原始游戏 ZIP **56,354,895 字节**，SHA-256 `68b14936327a9c9df36c6aafc7238688676419594d2846598199aa7c4947f385`。

83 项 Windows Python、作者侧全部校验与 Ren'Py 8.5.3 lint 通过。源码和独立 EXE 各 **31/31 用例、359/359 断言**（1324.780 / 897.690 秒）；关闭首进程后重新启动 EXE，真实读档另 **1/1 用例、10/10 断言**（4.282 秒）。全部 failed / xfailed / xpassed / skipped / not run 为 0，三个原生进程退出 0、未超时。

源码 65、独立 EXE 65、新进程 1，共 **131 张 PNG** 全部完整解码并核对物理尺寸及 SHA-256；完成 35 个实际 EXE 视图的检查。新图直接查看；逐字节相同且此前已直接审阅的画面按 SHA-256 沿用结论，方法逐图记录。最终关于页长文在内容区内换行，稳定历史 / 设置 / 存读档不透出底层台词；七表情、CG、背景、结局及重开读档画面有记录。

60 图片 / 配方、85 资产、24 声音、69 请求有效；原始游戏 ZIP、66 画面 / 24 OGG-WAV / 两完整正文的统一审阅包、校验和与预览已整理交付。正文与录音保持当前候选；37 处精修草案已准备但未应用。

关于页裁切和缩放历史过渡截帧已修复并对新包重验；原始问题、旧失败与严格包身份见 [DISPLAY_ACCEPTANCE_V09](DISPLAY_ACCEPTANCE_V09.md)。下一批从 V09-01 草案的上下文 / 规模复核与精修继续。

Windows runner 使用 dummy 音频。普通电脑 / 中文路径 / 100% 与 150% DPI、两结局正常阅读计时、17 句配音与 7 个声音的听感及最终创作仍待用户统一操作。内容未冻结，v1.0 未完成；公开 Release 仍为 v0.6.0。

## v0.8 验收记录 — 2026-10-05

**v0.8.0 回归 Beta 技术验收完成。** [Windows CI 37281855516](https://github.com/AureliusWu/Test/actions/runs/37281855516) 对候选 `2356c7f5ba9764f213286fd9d0e83a52f8a4e06b` 全部通过：79 项 Python；源码与独立 EXE 各 30/30 用例、345/345 断言（461.155 / 322.228 秒），新进程读档另 1/10（2.002 秒）。全部失败 / 跳过 / not run 为 0，两个 EXE 进程退出 0、未超时。

新增后半段 8 处真实存读档与背景清空后恢复、回退改选、True 后新游戏进 Normal、完整语音时长自动衔接及全部选择的快进停止。源码和包验收严格核对实际摘要 / 用例名与全部截图。保留 16 路线及旧交互，正文与图像 / 音频字节沿用 v0.7；主菜单“可玩候选”、独立 Beta 存档目录与版本 0.8.0 已同步。

109 张 PNG 全部完整解码，15 个实际 EXE 视图已审阅；最终 55 张 EXE 截图与首轮 SHA-256 全同。候选 ZIP **44,868,967 字节**，SHA-256 `e436d30a93e7a51671b4ffec60a43ff636a865299b67f237af1c8195e048ba9c`；两个 artifact digest、两份 SHA256SUMS、CRC 和包内版本均核验。详情及失败 / 修复见 [BETA_ACCEPTANCE_V08](BETA_ACCEPTANCE_V08.md) 与机器证据清单。公开 Release 仍为 v0.6.0。

用户已要求真人后续统一操作，集中在 [HUMAN_HANDOFF](HUMAN_HANDOFF.md)。当前 GUI 1280×720，下一批为 v0.9 原生 1920×1080 适配、体验打磨和可审阅材料；计时、听感、普通电脑与最终创作定案继续待验收，工程可自主推进。已知 P2：游戏“关于”页仍沿用 Alpha 称呼，v0.9 文案整理时修改。本批机器范围未发现 P0 / P1。

## v0.7 Alpha 验收记录 — 2026-10-05

六章、24 个叙事场景与 2 个状态路由的完整短篇 Alpha 正文候选已完成；4 次选择、16 条路线、4 True / 12 Normal 保持原结构。全分支 **15,206** 字符，单路线 **11,404–11,744**，文字估算约 **32–47 分钟**。真人完整阅读时长尚未验收，不把估算算作通过。

已审阅第三章、第四章与第五章合流，补齐同行后进入 Normal 的离场、今晚酒店与次日到家、未拆信封及照片归属、号码已经保存、叫车只查看未下单、站外环境与换景立绘。保留全部 17 句配音文字；新增三个匹配地点的背景，源图、编辑输入、Prompt 与 33 个重建配方均可追踪。详情见 [剧情审阅](STORY_REVIEW_V07.md)、[路线统计](STORY_STATS_V07.md) 与 [美术审阅](ART_REVIEW_V07.md)。

本候选本地 **72 项 Python 测试**和全部作者检查通过；85 个资产、60 张 PNG、24 个 OGG、69 份 Prompt、33 个图片配方均校验 0 错误；Ren'Py 8.5.3 Linux lint 通过。完整候选提交 `96cdfa087583c63a0020bca138aec57384211fd3` 的 [Windows CI 37273842254](https://github.com/AureliusWu/Test/actions/runs/37273842254) 已 success：Windows 72 项 Python 通过；源码和 ZIP 独立 EXE 各 **24/24 用例、160/160 断言**（346.531 / 237.702 秒），失败和跳过均为 0。包进程退出 0、未超时。

已核验两个 artifact digest、两份 SHA256SUMS、ZIP CRC 和包内 0.7.0 元数据；82 张证据 PNG 完整解码，直接审阅 10 张独立 EXE 新场景及 UI 画面。游戏 ZIP 为 **44,861,562 字节**，SHA-256 `9e9cd77da3b2ff9507b5fec89fab68091e0eca2ce4376c8188c1412651dc0af1`。**v0.7 Alpha 技术验收完成，候选试玩包与预览已交付；公开 Release 仍为 v0.6.0。**具体证据及人工项见 [ALPHA_ACCEPTANCE_V07](ALPHA_ACCEPTANCE_V07.md)。

下一批工程工作已建立 [v0.8 回归覆盖表](REGRESSION_COVERAGE_V08.md)：优先补旧信 CG、雨棚、离场和小店前后存读档，再补回退改选与同一进程换结局。真人阅读计时、试听和创作审阅继续并行待办，不据估算把整个 v0.7 里程碑勾为完成。主菜单“可玩样片”称呼保留为 v0.9 待改 P2 文案。

第四章提交 `246217f4791b6e3e4aef3ea1874bfb9decaaf543` 的 [CI 37250452907](https://github.com/AureliusWu/Test/actions/runs/37250452907) 已通过：72 项 Python；Windows 源码 24/24 用例、151/151 断言（323.377 秒），独立 EXE 同为 24/151（219.247 秒），无失败或跳过。已下载证据匹配 digest `72bfdb8d84719a8c9bc4ffc55f71cf45ef762fbf0cd620998868d5ff6f75f768`，72 PNG 完整解码；旧包 SHA-256 为 `b1a89057e0d75fd5e917ec8abf10ce36352410f37722aaa99d60305d4a77e49a`，VERSION 为 0.6.0，不将它标为 v0.7 包。

本批 VERSION / 引擎 / 剧情已同步 **0.7.0**，使用独立 Alpha 存档目录；公开 Release 仍为 v0.6.0。main 只生成候选与证据，手动发布另行重验。当前接续位置见 [WORK_CHECKPOINT](WORK_CHECKPOINT.md)，候选证据与人工项见 [ALPHA_ACCEPTANCE_V07](ALPHA_ACCEPTANCE_V07.md)。

2026-10-05（北京时间）。仓库：[AureliusWu/Test](https://github.com/AureliusWu/Test)，仅 main。

## 当前进度

最新版本 [v0.6.0](https://github.com/AureliusWu/Test/releases/tag/v0.6.0) 已于 2026-10-05 07:31:53（北京时间）完成 Windows 验收并发布预发行版。

| 统计口径 | 当前结果 |
|---|---|
| 发布里程碑 | v0.1–v1.0 共 10 个节点；v0.1–v0.6 已发布，6/10 = **60%** |
| v0.6 工程收尾 | 音频、校验、Windows 源码与独立 EXE、Release 均完成 |
| 后续阶段 | v0.7 / v0.8 技术已验收；v0.9 原生 1080p 与体验打磨 → v1.0 普通电脑及正式发布 |

60% 只表示版本节点比例，不表示总工时或完整内容达到同一比例。真人计时、听感、创作定案与普通 Windows 电脑验收仍待后续完成。

## 规划记录

规划时以 `b519a051cd53ad0c8579ef7a34dfd89996c1d594` 为基线核对 GitHub：当时最新 Release 和 VERSION 为 v0.5.0，CI 37214804210 的结论为 success；之后的 v0.6 完成结果记录于下文。

新增 [v0.7–v1.0 执行计划](RELEASE_PLAN_V07_V10.md)，同步 [ROADMAP](../ROADMAP.md)、测试计划和 README。顺序为 v0.6 收尾 → v0.7 完整剧情 → v0.8 回归加固 → v0.9 文本、1080p 和声音打磨 → v1.0 普通电脑验收及正式发布。

核对出的缺口：当前原生 GUI 为 1280×720；完整字数与真人时长、最终创作定案、真实听感及普通 Windows 电脑验收仍待完成。既有 CI 在 main 验证通过后自动创建预发行 Release，后续需分离验证与发布并增加正式版验收记录。

此前规划提交仅修改文档，已核对 Markdown 本地链接、任务 ID、版本与变更范围，未重新运行游戏回归。随后恢复并完成 v0.6 音频收尾；v0.7–v1.0 仍保持待办。

## v0.1.0 — 已发布

起始仓库为空，已建立 Ren'Py 8.5.3 项目、中文 UI、临时人物、背景、音乐、雨声、一个选择与两个片段结局。SDK 固定版本并核验 SHA-256。

12 个 Python 用例通过；Linux 原生 Ren'Py 4 个交互用例 / 16 个断言通过；Windows 原生引擎以及 ZIP 解压后的独立 EXE 同样通过。保存、读取、选择、结局、历史、设置与新游戏清零已实际执行。

[成功 CI 37163489320](https://github.com/AureliusWu/Test/actions/runs/37163489320) · [v0.1.0 Release](https://github.com/AureliusWu/Test/releases/tag/v0.1.0)

发现并修复：SDK 解压共享库截断、错误截图开关、launcher 相对路径、错误平台包名，以及独立 EXE 测试未传 basedir。修复后重新通过验收。

## v0.2.0 — 已验收并发布

8 个场景、3 次选择、8 种完整路线、2 个片段结局；AI 站台背景、成年女主透明立绘、旧信 CG；6 句本地 AI 中文语音（19.759 秒）、原创 BGM 与雨声；统一蓝色原生 UI。

12 个 Python 用例通过；路线、文本、资产、Prompt 哈希、语音绑定和编译检查 0 错误；Ren'Py lint 通过。Linux 原生运行 12 个交互用例 / 51 个断言通过，包含存读档、重进路线、历史、语音播放、静音、全屏/窗口、自动播放和快进。已检查真实游戏截图并修正遮脸菜单、模板残留和字体分隔符。

本轮发现推理库默认启用遥测，自动审核阻止了相关动作。已使用官方 ORT_DISABLE_TELEMETRY=1 初始化前完整关闭机制与事件关闭 API，重新完成本地语音合成。发行包只包含离线音频。

Windows 最终 CI 已通过：Python 12 个用例；Windows 原生引擎 12 个交互用例 / 51 个断言（38.956 秒）；ZIP 解压后的独立 EXE 12 个用例 / 51 个断言（26.140 秒）。测试确认分发包没有开发数据、测试脚本或存档，临时注入测试仅用于验收；实际玩家运行不依赖 SDK 或系统 Python。

[成功 CI 37178555675](https://github.com/AureliusWu/Test/actions/runs/37178555675) · [v0.2.0 Release](https://github.com/AureliusWu/Test/releases/tag/v0.2.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v0.2.0/BeforeTheRainStops-0.2.0-win.zip)

发布提交：004edfdde53ff892df6d3d84e0844a7f50d65864。ZIP：37,693,318 字节。SHA-256：ad7873d2d4937afb83c48ef6bfac9961fef52a4e4f342934fd713f6757b2a2ba。Release 附 SHA256SUMS.txt；Actions 留存源码与独立 EXE 截图、日志和路线报告。

已下载 CI 验收证据并核验 SHA-256，直接检查独立 Windows EXE 的主菜单、对话与 CG 截图：中文字形、透明立绘、背景、CG 和 UI 均正常显示。

仓库只有 main；阶段版本使用 tag。源码、Prompt 和原始资产已提交，SDK、模型、缓存和中间报告保持在版本库之外。

## v0.3.0 — 已验收并发布

新增六种表情，与 normal 共七种透明立绘；每张分别编辑同一基础图，固定 Prompt 组件与精确请求均已保存。源图、参考图、组件和游戏文件可追踪；七种接入 20 处现有台词与选择回应，剧情文本、状态效果和八条路线与 v0.2 相同。

16 个 Python 用例通过；角色、路线、资产、文本、来源哈希及编译检查 0 错误；Ren'Py lint 通过。Linux 原生全集 13 个交互用例 / 62 个断言通过（30.859 秒），七种表情专项 1 个用例 / 8 个断言通过。保存后强制切换 angry，再读取 normal，表情与状态均恢复。

游戏图全部 540×700；六张新图与基础轮廓 IoU 0.993–0.998，包围盒偏差最多 1 像素。已人工查看七种生成结果与实际剧情画面；最终形象选择待用户审阅。审阅记录见 EXPRESSION_REVIEW.md。

本轮发现本地临时运行环境需要恢复，以及部分本地原生截图写入不完整。已从固定 SDK 恢复 Linux 运行库，增加独立 EXE 截图完整解码门槛。

最终 Windows CI 已通过：16 个 Python 用例；源码引擎 13 个交互用例 / 62 个断言（45.089 秒）；ZIP 解压后的独立 EXE 同为 13 个用例 / 62 个断言（31.223 秒）。全部七种表情截图通过完整解码；已下载验收证据、核验 SHA-256 并解码全部 42 张 PNG，直接看过 Windows 独立 EXE 的七种表情，中文、透明边缘、服装、位置与 UI 均正常。

[成功 CI 37180677754](https://github.com/AureliusWu/Test/actions/runs/37180677754) · [v0.3.0 Release](https://github.com/AureliusWu/Test/releases/tag/v0.3.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v0.3.0/BeforeTheRainStops-0.3.0-win.zip)

发布提交：c3d09d8e8c9c906f8de3ba5b2e1cae7249d2fc8e。ZIP：39,436,278 字节。SHA-256：f064f4407e6ed0a62b3356f153124cb716accc9bc1164d01b502d36bdd0c13d6。Release 附 SHA256SUMS.txt；Actions 保留源码引擎与独立 EXE 的日志、表情截图、路线和几何报告。仓库继续只维护 main，阶段使用 tag。

## v0.4.0 — 已验收并发布

六章、26 节点（含两个纯状态路由）、四次选择、16 条完整路线。17 个新叙事场景逐一起草与保存 Prompt；四条 True、十二条 Normal，早期回避可补救，最终分别始终 Normal。章节卡采用原生 centered；三个剧情状态不增加，访问路径与章节随原生存档恢复。

28 个 Python 用例通过；路线、资产、文本、Scene Prompt、版本一致性与编译检查 0 错误。Ren'Py lint 通过。Linux 首轮 21 用例 / 129 断言通过（85.434 秒）；修正标题分隔符缺字与截图停在过场问题后，路线 1 专项 1 用例 / 9 断言通过（8.508 秒），直接查看章节卡、实际 CG 与补充选择画面。

发现并修复：story.json 的旧版本字段、部分分支合流后物品或知识状态矛盾、章节标题缺字、过早截图。此后使用版本联合检查、逐场事实审阅、中文冒号与显示文字等待条件。最终 Windows CI 已通过，结果与独立 EXE 证据如下。

最终 Windows 验收：28 个 Python 用例；源码引擎 21 个交互用例 / 132 个断言（160.390 秒）；ZIP 解压后的独立 EXE 21 个用例 / 132 个断言（104.382 秒）。16 条真实选择路径逐项匹配访问记录，两个结局、章节与表情存读档、重新开始、历史、音频通道、全屏、快进和自动播放均通过。

已下载验收证据，SHA-256：703504cb236b7ec7829b03bf933b3d3b92a4ece8af8e585f5e274e5883976cf5；全部 68 张 PNG 完整解码。直接查看独立 EXE 的序章、第四章标题、两种信任分支、CG、补充选择、True 与 Normal 结局截图，中文字形、立绘、CG 与 UI 正常。独立 EXE 的必需截图通过完整解码门槛；发布 ZIP 不包含开发剧情数据、测试脚本或存档。

[成功 CI 37191065889](https://github.com/AureliusWu/Test/actions/runs/37191065889) · [v0.4.0 Release](https://github.com/AureliusWu/Test/releases/tag/v0.4.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v0.4.0/BeforeTheRainStops-0.4.0-win.zip)

发布提交：98d5d8e2bec642e8a94063dc5df9729842d22240。ZIP：39,469,538 字节。SHA-256：44cecf41f9146e5b244f43406d9e5424c214e6ebc371b2ca43a16e0148898fcd。Release 附 SHA256SUMS.txt，Actions 保留全部报告、日志与截图。仓库只维护 main，阶段使用 tag，最终创作选择继续由用户审阅。

## v0.5.0 — 已验收并发布

31 份 Prompt 登记稳定 ID、版本、文件与哈希；图片、语音和场景均绑定 Registry。66 个资产追踪补全，57 张 PNG 记录显示元数据并完整解码，30 个导入配方可从源图重建。主菜单复用站台背景、CG 原始参考、normal 清理参考与基础音频源 WAV 均可追踪。

45 个 Python 用例全部通过（17 个新增管线用例）；路线、Registry、元数据、语音与生成脚本检查 0 错误，30 个配方内存重建 0 错误。实际重复导入 heroine_smile 返回 changed=false；66 个既有游戏文件 SHA-256 未改变，剧情文本及 16 条路线沿用 v0.4。Ren'Py lint 通过，Linux 实际引擎全集 21 个交互用例 / 132 个断言通过（103.301 秒）。

发现并修复：UI 导入被统一放大、缺参考/组件时可能先覆盖游戏图片、输出归属与版本缺少保护、复用主菜单缺少来源哈希，以及匹配文件哈希仍不能证明 PNG 可解码。加入先预检后写入、原尺寸 UI、dry-run、版本与路径检查、Manifest 正常 I/O 失败回滚、重复导入与完整解码门槛。保留已有字体 ID 的大小写，不重命名已登记资产。

Windows 首轮 CI 37214662059 的两个回滚用例未注入预期错误：临时目录短路径别名与解析后的文件名被当作不同路径。已将测试根目录与故障注入目标统一解析；首轮在 Python 检查处停止，未执行引擎或发布。修正后全部 45 个 Windows Python 用例通过，固定 Pillow 11.3.0 下 Registry、资产、30 个配方重建与 Ren'Py lint 均通过。所有新管线工具均留在开发仓库。

最终 Windows 源码引擎 21 个交互用例 / 132 个断言通过（154.067 秒）；ZIP 解压后的独立 EXE 同为 21 个用例 / 132 个断言（96.154 秒），均无跳过。16 条路线、两个结局、章节及表情存读档、重新开始、历史、音频通道、全屏、快进和自动播放均通过。

已下载验收证据（24,099,325 字节），SHA-256：ebd955adbe101d950a07ea28828c5959f6af07b094526a673ba002614a7c56db；全部 68 张 PNG 完整解码。直接查看独立 EXE 的 v0.5.0 主菜单、首个选择、CG、设置、happy 表情与第四章标题，中文字形、透明立绘、CG 和 UI 正常。发布 ZIP 不包含开发剧情数据、测试脚本或存档。

[成功 CI 37214804210](https://github.com/AureliusWu/Test/actions/runs/37214804210) · [v0.5.0 Release](https://github.com/AureliusWu/Test/releases/tag/v0.5.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v0.5.0/BeforeTheRainStops-0.5.0-win.zip)

发布提交及 tag：8cf379d78c1f5ea82c97bdd31ed229ba1f133441。ZIP：39,470,025 字节。GitHub 发行资产 SHA-256：d304f11cb8cba794c8cd1a36a616b23299b241ac97c2a4d944e3302775c5c07c。Release 附 SHA256SUMS.txt；Actions 保留全部报告、日志与截图。仓库只维护 main，阶段使用 tag。

## v0.6.0 — 已验收并发布

新增 11 句固定音色关键台词，覆盖坦白回应、两种信任分支、界限、关系修复与两个结局；17 句合计 58.048 秒。新增两首原创程序 BGM、渐弱雨声、纸张与消息提示，音乐随已有剧情切换，雨声在进入小店和雨停台词处淡出。33 份 Prompt、82 个资产可追踪；原有 66 个游戏文件的 SHA-256、剧情文本与 16 条路线保持一致。

60 个 Python 用例通过（15 个新增音频用例）；24 个游戏 OGG 与对应源 WAV 完整解码，元数据、来源、格式、峰值和语音信号范围检查 0 错误。全部 OGG 最大峰值 .420157，语音 RMS -24.043～-22.833 dBFS。图片、Registry、角色、剧情及编译校验 0 错误，30 个图片配方重建通过。重复配音返回 0 changes，未初始化模型；重复程序音频导入保留五个配方文件。

Ren'Py lint 通过；Linux 原生全集 24 个交互用例 / 151 个断言通过（133.014 秒）。三个新增用例实际推进坦白及两个结局，核对音乐切换、纸张／消息音效、关键语音和雨声停止；旧存读档用例核对音轨恢复，全静音核对 music / sfx / voice。

发现并修复：旧语音缓存只比较文字和输出存在，可能误用改配置或损坏录音；OGG 头不能证明可播放；相同配置反复重启音乐；结尾雨声与文本不符。本轮增加请求指纹、全量解码、if_changed 和明确淡出节点。制作缓存中的模型及声音库已截断，在任何合成前校验拦截；从官方发行恢复到固定 SHA-256 后完成新增录音，没有更换模型或音色。

本轮恢复断点后，重新通过全部 60 个 Python 用例、24 个音频完整解码及所有数据 / 图片 / 生成一致性校验，确认 66 个既有游戏资产哈希未改变。同步新路线时保留了原有音频改动和规划文档。本轮本地 Linux 引擎进程退出 135，未把它记为重新通过；本段 133.014 秒的 Linux 结果为上一轮保留的执行记录。

最终 Windows CI：60 个 Python 用例通过（8.503 秒），所有校验与 Ren'Py lint 通过；源码引擎 24 个交互用例 / 151 个断言通过（183.479 秒），ZIP 解压后的独立 EXE 同为 24 个用例 / 151 个断言通过（120.472 秒），均无失败或跳过。三个新增用例覆盖音轨切换、坦白与两种结局语音、纸张和消息音效、雨声淡出，既有 16 条路线及核心交互全部保留。

已下载 Windows 验收证据（24,156,857 字节），SHA-256：`6df9a345e1ed534aecc9ebb7196e855894d21d64253c2caa265352798b42844e`；全部 72 张 PNG 完整解码。直接查看独立 EXE 的 v0.6.0 主菜单、音量设置与 True / Normal 结局语音画面，中文及控件正常。声音信号检查和 dummy 音频流程测试不等于真人试听。

[成功 CI 37243693967](https://github.com/AureliusWu/Test/actions/runs/37243693967) · [v0.6.0 Release](https://github.com/AureliusWu/Test/releases/tag/v0.6.0) · [Windows ZIP](https://github.com/AureliusWu/Test/releases/download/v0.6.0/BeforeTheRainStops-0.6.0-win.zip)

发布提交及 tag：`a6d919a6c09cd2a95df5f57504d80c7fd4e144cc`。ZIP：40,179,877 字节。GitHub 发行资产 SHA-256：`ff92da6659e1f6d5392c5a0ea20532aa39c344c1f2b51924de1d137d91f60c35`。Release 附 SHA256SUMS.txt，Actions 保留源码与包的报告、日志和截图；发布仍为预发行版。

已直接下载发行 ZIP，实测 SHA-256 与 GitHub 资产摘要及 SHA256SUMS.txt 完全一致；ZIP 全部条目完整性检查通过，包含独立启动 EXE，未含开发剧情数据目录、测试脚本或存档目录。Windows 实际运行结果来自上述 CI；本地下载校验未替代普通 Windows 电脑试玩。

## v0.6 发布时的遗留范围（历史）

主题《雨停之前》、许澄形象、声音与结局仍是可试玩候选。单路线约 5,050–5,350 字，预估 17–24 分钟，尚未真人计时；全分支约 7,000 字，仍未达到最终 15,000–30,000 字及 30–60 分钟目标。音频自动测试使用 dummy 输出，真人听感与普通 Windows 电脑双击体验需要试玩。七种表情沿用，更多背景 / CG 在后续资产阶段完善。

下一阶段 v0.7：补齐完整短篇剧情与对应场景资产，达到目标字数后进行真人计时和路线体验审阅。普通工程决策自行推进；重大剧情、角色关系和最终视觉由用户决定。
