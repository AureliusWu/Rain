# 雨停之前 / Before the Rain Stops

**v1.6.0 玩家帮助与完整发行验收正式版：Windows 离线 EXE + 同引擎官方 WebAssembly PWA。**

[在线游玩](https://aureliuswu.github.io/Rain/) · [正式下载](https://github.com/AureliusWu/Rain/releases/tag/v1.6.0) · [Windows ZIP](https://github.com/AureliusWu/Rain/releases/download/v1.6.0/BeforeTheRainStops-1.6.0-win.zip) · [Web ZIP](https://github.com/AureliusWu/Rain/releases/download/v1.6.0/BeforeTheRainStops-1.6.0-web.zip) · [校验表](https://github.com/AureliusWu/Rain/releases/download/v1.6.0/SHA256SUMS.txt)

雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。六章、24 个叙事场景、四次选择、16 条路线与 Normal / True 两个结局；560 个台词 ID 与原有 v1 存档身份保持。

## v1.6.0 玩家帮助与正式验收

桌面、手机与 PWA 均可从主菜单或阅读菜单打开帮助，查看触屏 / 键鼠、保存与原生备份、回看重听、离线和更新说明。打开及返回沿用原生菜单，保留当前台词、历史和选择。

Windows 39913692426、官方 WASM / PWA 39913692408、原包发行 39919945671 全部成功，运行 / tag 固定于 `b820f868e4fe10a9d74d2a35769696a0b1550ef6`。源码和独立 EXE 各 39 用例 / 521 断言 / 91 截图，真实 v1.1.0 旧档升级、新进程恢复及 18 项 WASM 检查通过。四份公开下载、两个 ZIP、当前 Worker 和四作共同断网复验通过；[发布凭据](docs/production/PUBLISHED-v1.6.0.json) · [下载回读](docs/production/PUBLIC-READBACK-v1.6.0-20261023.json) · [四作闭环](docs/production/FOUR-GAMES-CLOSURE-20261023.md)。真人体验项继续集中待验。

## 当前声音与画面（v1.5.0 接入）

- 全分支 306 条人物对白绑定离线录音，包括选择回应；原 17 句录音保留原字节，旁白保留文字。
- 当前台词、已读历史和收藏支持原录音重听；自动阅读等待当前语音，独立语音音量继续使用原生设置。
- 新增玩家六表情的人物鉴赏与六幅按实际台词触发的事件 CG；玩家立绘用于鉴赏，正文保持原有第一人称表现。
- 十二幅剧情画面与四首音乐沿实际阅读解锁；场景、CG、立绘、录音和许可随两个客户端提供。
- 收藏可按关键词、人物与章节交叉检索；阅读、重听、删除和跨端导入保留真实剧情位置及删除记录。
- PWA 逐文件校验长度与 SHA-256，完整下载成功后才显示离线就绪；更新等所有旧窗口关闭后接管。

## Windows 与 PWA

完整解压 Windows ZIP 后双击 BeforeTheRainStops.exe，无需 Python、引擎或账号。左键 / 空格 / Enter 推进，右键 / Esc 开菜单，F 切换全屏；阅读层提供回退、历史、自动、快进、存读档与设置。

PWA 首次保持联网，等待完整离线下载成功后再断网。左上角支持原生存档 ZIP 导入 / 导出；浏览器与 Windows 各自保存本机进度。原生存档目录继续使用 AureliusWu-BeforeTheRainStops-v1，清理站点前可导出备份。

## v1.5.0 历史验收与正式发布

2026-10-22：[Windows 39715827353](https://github.com/AureliusWu/Rain/actions/runs/39715827353)、[官方 WASM / PWA 39715827275](https://github.com/AureliusWu/Rain/actions/runs/39715827275) 与 [同字节发行 39721240542](https://github.com/AureliusWu/Rain/actions/runs/39721240542) 均成功。运行 / tag 固定于 `e4856b5a5f44803e1c1b263534702f5d7d8c80dc`。

Windows 源码与独立 EXE 各 38 用例、509 断言、89 张截图通过；新进程读档、真实 v1.1.0 旧档升级、188 张原始截图和 388 项包内资产审计通过。官方 WASM 的 16 项浏览器检查及公开原生存读档、中文历史检索和断网续读通过。

四份公开下载、三条校验和、两个 ZIP 的 CRC 与当前线上 Worker 原字节再次回读通过。四作共存复验通过，共 1,248 条缓存及各自存档状态保留，页面错误为零。[发布凭据](docs/production/PUBLISHED-v1.5.0-full-media.json) · [独立下载回读](docs/production/PUBLIC-READBACK-v1.5.0-20261022.json) · [四作闭环](docs/production/FOUR-GAMES-CLOSURE-20261022.md)。

真人试听、阅读计时、普通电脑 / 中文路径 / DPI、物理设备与最终创作定案继续按实际体验登记。六幅恢复 CG 缺失的原生成请求如实保留来源缺口，未补写虚构记录。较早版本的验收数据按下文日期保留。

## v1.3.1 历史验收与发布

[原生 Windows 39197411208](https://github.com/AureliusWu/Rain/actions/runs/39197411208)、[官方 WASM / PWA 39197411207](https://github.com/AureliusWu/Rain/actions/runs/39197411207)、[同字节正式发布 39202170966](https://github.com/AureliusWu/Rain/actions/runs/39202170966) 均成功。

Windows 源码与独立 EXE 各 37 用例 / 494 断言 / 86 截图，两轮语音与收藏前缀各 7 / 149 / 33，真实旧档升级、182 PNG / 85 资产和 16 项官方 WASM 检查通过。直接提升该次原始 ZIP，四份公开下载及当前 Worker 已回读 SHA-256；冻结运行和 tag 为 `f1b521db0c7c954a9245411b58438f344b5717f7`。真人后续保持原真实状态，详见 [发布凭据](docs/production/PUBLISHED-v1.3.1.json)。

## v1.3.0 历史验收与发布

冻结运行提交：cf8e0b5ae61b90815eb0f3a16188493e89c1fd05。

| 范围 | 实际结果 |
| --- | --- |
| Windows源码 / 独立发行EXE | 各37用例、487断言、85截图 |
| 退出后新进程 | 1用例、17断言、3截图 |
| 真实v1.1.0旧档写入 / 新版读取 | 1/14/3 与 2/26/4 |
| 两次原生语音/收藏前缀 | 每次7用例、142断言、32截图 |
| 完整原始PNG / 资产审计 | 180张 / 85项 |
| 官方WASM与公开PWA | 16项实际浏览器检查及公开存读档、断网续读通过 |

[Windows 39107156547](https://github.com/AureliusWu/Rain/actions/runs/39107156547) 与 [PWA 39107156529](https://github.com/AureliusWu/Rain/actions/runs/39107156529) 使用同一冻结提交，均成功。正式发行直接提升这两次构建的原始ZIP；[发布任务39134956684](https://github.com/AureliusWu/Rain/actions/runs/39134956684) 完成公开下载字节回读。[原包在线提升39138941116](https://github.com/AureliusWu/Rain/actions/runs/39138941116) 再次确认公开worker逐字节一致，并完成真实存读档和断网续读。后续文档/发布支持调整不充当新的玩家运行验收。

真人试听、Normal/True阅读计时、普通电脑/中文路径/DPI、物理设备安装与最终创作定案仍待实际体验。自动执行耗时和PNG解码不能代替这些体验。详见[统一真人后续](docs/HUMAN_HANDOFF.md)、[本版发布凭据](docs/production/PUBLISHED-v1.3.0.json)。

## 开发

Ren’Py 8.5.3、Python 3.12。game/data/story.json是剧情唯一来源；改动后使用tools.compile_story和tools.compile_tests重建原生脚本与交互用例。运行python -m tools.preflight、python -m tools.validate及Python测试；平台发行继续执行原生Windows与官方WASM门禁。

新Windows构建先用tools.build.seed_release_names保留已发布v1.1.0语句身份，再执行Ren’Py lint、tools.build.verify_package和tools.build.verify_upgrade。跨编译ZIP不能替代Windows实际启动证明。

[项目约束](docs/PROJECT.md) · [架构与双端](docs/DUAL_PLATFORM_V12.md) · [三作制作契约](docs/production/SHARED-VN.md) · [创作方法](docs/production/CREATIVE-PLAYBOOK.md) · [素材复用](docs/production/REUSABLE-MATERIALS.md) · [声音来源](docs/VOICE_UPGRADE_V10.md)

## 来源与历史

原素材、Prompt、台词、许可证和摘要保留于assets_source、prompts、game/data、CREDITS.md及licenses。306 条人物对白使用固定 Qwen3-TTS 模型的离线录音，原 17 句保留原字节；模型及推理依赖不进入玩家包。

[本版说明](docs/RELEASE_NOTES_V150.md) · [v1.2.2历史发布](docs/production/PUBLISHED-v1.2.2.json) · [v1.1.1历史发布](docs/evidence/v111-publication.json) · [工作检查点](docs/WORK_CHECKPOINT.md)
