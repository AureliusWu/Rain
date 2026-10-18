# 雨停之前 / Before the Rain Stops

**v1.3.0 正式版：Windows 离线 EXE + 同引擎官方 WebAssembly PWA。**

[在线游玩](https://aureliuswu.github.io/Rain/) · [正式下载](https://github.com/AureliusWu/Rain/releases/tag/v1.3.0) · [Windows ZIP](https://github.com/AureliusWu/Rain/releases/download/v1.3.0/BeforeTheRainStops-1.3.0-win.zip) · [Web ZIP](https://github.com/AureliusWu/Rain/releases/download/v1.3.0/BeforeTheRainStops-1.3.0-web.zip) · [校验表](https://github.com/AureliusWu/Rain/releases/download/v1.3.0/SHA256SUMS.txt)

雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。六章、24个叙事场景、四次选择、16条路线与Normal / True两个结局；沿用560个台词ID、17句离线录音及原有v1存档身份。

## v1.3.0 阅读与离线体验

- 历史记录保留关键词、人物筛选，增加章节筛选和已读台词收藏。
- 独立收藏列表可查看、删除及重听原录音；查阅和重听保持当前剧情位置。
- 收藏按新增/删除时间合并，跨设备导入不会让删除的旧收藏重新出现；旧档没有收藏时正常初始化。
- PWA按已核对的文件与字节显示完整下载进度，失败可重试。完整内容通过摘要校验后才能离线。
- 新包下载完成后等待所有旧窗口关闭，保留阅读中的完整版本。
- 五张画面、三首音乐沿真实阅读解锁；17句Qwen3-TTS / Serena关键录音随包提供，无运行时模型或语音服务。

## Windows 与 PWA

完整解压Windows ZIP后双击BeforeTheRainStops.exe，无需Python、引擎或账号。左键/空格/Enter推进，右键/Esc开菜单，F切换全屏；阅读层提供回退、历史、自动、快进、存读档与设置。

PWA首次保持联网，等待完整离线下载成功后再断网。左上角支持原生存档ZIP导入/导出；浏览器与Windows各自保存本机进度。原生存档目录继续使用AureliusWu-BeforeTheRainStops-v1。关闭或清理站点前可导出备份。

## 本版验收与发布

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

原素材、Prompt、台词、许可证和摘要保留于assets_source、prompts、game/data、CREDITS.md及licenses。17句当前录音由固定Qwen3-TTS模型离线生成，模型及推理依赖不进入玩家包。

[本版说明](docs/RELEASE_NOTES_V130.md) · [v1.2.2历史发布](docs/production/PUBLISHED-v1.2.2.json) · [v1.1.1历史发布](docs/evidence/v111-publication.json) · [工作检查点](docs/WORK_CHECKPOINT.md)
