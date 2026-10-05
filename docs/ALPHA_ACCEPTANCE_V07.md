# v0.7 Alpha 候选验收

更新时间：2026-10-05（北京时间）。本文件绑定完整候选内容与实际验收，人工项分别记录。

## 当前内容

- VERSION / 引擎 / JSON：0.7.0；存档目录：AureliusWu-BeforeTheRainStops-alpha-v07。
- 剧情原始文件 SHA-256：`c9d4bd6ec954c0eca8e5273c5e2e9b9f058aff3be93268b295ec407f4a975681`。
- 六章、24 叙事场景 + 2 路由、16 路线、4 True / 12 Normal；正文 15,206，单路线 11,404–11,744 字符。
- 17 句关键语音、七种表情、旧信 CG 与三个新增背景；没有新增状态或重大结局方向。

## 作者侧证据

- 本地 72 个 Python 用例通过；全部校验和 Ren'Py 8.5.3 Linux lint 通过。
- 69 Prompt、85 资产、60 PNG、24 OGG、33 图片配方无校验错误。
- 与第四章 main 246217f 比较，16 条路径 / 状态 / 结局、17 句配音文字不变。
- 24 个原生用例、160 条生成断言；五张新图为包验收必需证据。生成数量不是执行结果。
- 剧情及美术逐项审阅见 STORY_REVIEW_V07.md、ART_REVIEW_V07.md。

## Windows 候选证据

候选提交：`96cdfa087583c63a0020bca138aec57384211fd3`，tree：`50379e0e38f7cec780ff47f0dc6086fdaa3deee0`。[Windows CI 37273842254](https://github.com/AureliusWu/Test/actions/runs/37273842254) 结论 success；源码与独立 EXE 使用同一套测试。此前第四章的 0.6.0 包只保留为历史证据。

| 检查 | 实际结果 |
|---|---|
| Windows Python / 作者校验 / lint | 72 项 Python 通过（10.136 秒）；全部作者检查和 Ren'Py lint 通过 |
| Windows 源码交互 | 24/24 用例、160/160 断言，346.531 秒，失败 / 跳过均为 0 |
| ZIP 解压后的独立 EXE | 24/24 用例、160/160 断言，237.702 秒，失败 / 跳过均为 0 |
| 包进程 | returncode=0、timed_out=false，进程耗时 239.531 秒；上限 900 秒 |
| 下载证据完整性 | evidence / windows 两个 artifact 的 SHA-256 均匹配 GitHub digest；两个 ZIP CRC 完整 |
| PNG 证据 | 源码 41 张 + 独立包 41 张，共 82 张完整解码；五张新背景 / 离场截图全部存在 |
| ZIP 内容 | 1621 个条目；无剧情 JSON、项目 RPY 源码、测试脚本、存档、源资产、模型或 SDK |
| 版本 | ci-context、ZIP 名称与包内 Ren'Py build_info.json 均为 0.7.0 |

Windows ZIP：`BeforeTheRainStops-0.7.0-win.zip`，**44,861,562 字节**。SHA-256：`9e9cd77da3b2ff9507b5fec89fab68091e0eca2ce4376c8188c1412651dc0af1`。候选包 [artifact 11329379772](https://github.com/AureliusWu/Test/actions/runs/37273842254/artifacts/11329379772)，证据 [artifact 11329589324](https://github.com/AureliusWu/Test/actions/runs/37273842254/artifacts/11329589324)；Actions 保留至 2027-01-03，试玩 ZIP 与预览另已交付为可下载文件。本候选没有创建公开 Release，最新 Release 仍为 v0.6.0。

证据 artifact SHA-256：`88e793ea13593940ad6ea718f815f92e4c152fdc1533f42756136466a95900e7`；Windows artifact 外层 SHA-256：`122f3f5f74c892c00ac6e580d733a4091d29aaf0fadb4a1fa1472058a8d148c0`。两份 SHA256SUMS 均匹配内层实际游戏 ZIP。完整绑定、包信息与逐张截图哈希见 [证据清单](evidence/v07-acceptance.json)。

已直接查看独立 EXE 的主菜单、雨棚、两条离场首句、True 小店、Normal 分别后场景、首次选择、设置和两个结局，共 10 张。中文、角色透明边缘与位置、选择栏和设置均可读；换景后的两个离场首句显示 normal，正式分别后的 Normal 无人物，小店显示 smile。所有截图为测试窗口的 922×518 像素；逻辑 GUI 仍为 1280×720，1080p 与 DPI 验收留在 v0.9。

包中 `game/cache/build_info.json` 与 `game/cache/bytecode-312.rpyb` 是 Ren'Py 8.5.3 自动加入的发布元数据和运行字节码，分别核对版本及限定文件名；不能把它们当作开发缓存删除。Ren'Py 自身的 common RPY 是引擎运行文件，项目 `game/` 下没有 RPY 源码。

当前发现一项 P2 文案：主菜单仍称“可玩样片”。完整 Alpha 内容与版本无误，此称呼列入 v0.9 文本 / UI 打磨；没有据此改动已验收 ZIP。Normal / True 真人阅读时长、真实听感、普通电脑与最终创作继续按下表待办。

## 人工项（未完成）

| 项目 | 记录要求 | 状态 |
|---|---|---|
| True 正常阅读 | ZIP 哈希、R01 / 其他实际路线、开始结束时间、文字速度、语音设置、离开游戏的暂停时间 | 未计时 |
| Normal 正常阅读 | 同上；包括选择与正常画面停留，不使用快进 | 未计时 |
| 真实声音 | 17 句关键语音、BGM / 雨声 / 音效的发音、断句、循环与混音 | 待试听 |
| 普通 Windows 电脑 | 无 SDK / Python，完整解压、双击、两结局、存读档、历史、快进、自动、音量与全屏 | 待试玩 |
| 最终创作 | 主题、许澄形象、美术、音色、重大剧情与结局 | 用户审阅候选 |

文字估算约 32–47 分钟，仅为制作估计。CI 使用 dummy 音频；不能把播放通道通过写成听感通过。新包测试通过后可交付 Alpha 候选，v0.7 时长门槛与 v1.0 普通电脑门槛继续保持待办。
