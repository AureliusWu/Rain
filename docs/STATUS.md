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

## 限制与下一阶段

主题《雨停之前》、许澄形象、声音与结局是可试玩的待审阅方案。单路线时长预估 6–9 分钟，尚未真人计时。音频自动测试使用 dummy 输出，真人听感与普通 Windows 电脑双击体验仍需试玩。仅一张基础立绘；多表情、更多背景/CG 和 30–60 分钟完整剧情尚未制作。

先发布并试玩 v0.2，确认创作方向后进入 v0.3 一致表情体系，不增加大型新系统。
