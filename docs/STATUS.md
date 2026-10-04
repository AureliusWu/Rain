# 当前状态

2026-10-04。仓库：[AureliusWu/Test](https://github.com/AureliusWu/Test)，仅 main。

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

## 限制与下一阶段

主题《雨停之前》、许澄形象、声音与结局仍是可试玩候选。单路线约 5,050–5,350 字，预估 17–24 分钟，尚未真人计时；全分支约 7,000 字，仍未达到最终 15,000–30,000 字及 30–60 分钟目标。音频自动测试使用 dummy 输出，真人听感与普通 Windows 电脑双击体验需要试玩。七种表情沿用，更多背景 / CG 在后续资产阶段完善。

下一阶段 v0.5：完善现有 AI Asset Pipeline 的导入、Prompt Registry、Manifest 与图片校验。普通工程决策自行推进；重大剧情、角色关系和最终视觉由用户决定。
