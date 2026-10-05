# v0.8.0 回归 Beta 验收

2026-10-05。候选提交 `2356c7f5ba9764f213286fd9d0e83a52f8a4e06b`；[Windows CI 37281855516](https://github.com/AureliusWu/Test/actions/runs/37281855516) 成功。技术验收完成，真人事项由用户后续统一操作，不把它们作为工程暂停条件。公开 Release 仍为 v0.6.0，本批交付候选包。

| 检查 | 实际结果 |
|---|---|
| Python / 作者校验 | 79 项 Windows Python 通过（14.099 秒）；所有校验与 Ren'Py 8.5.3 lint 通过 |
| Windows 源码 | 30/30 用例、345/345 断言，461.155 秒；失败 / 跳过 / not run 均 0 |
| ZIP 独立 EXE | 同套 30/345，322.228 秒；失败 / 跳过 / not run 均 0 |
| 关闭后再开 EXE 读档 | 1/1 用例、10/10 断言，2.002 秒；读小店存档后可继续 True |
| 包进程 | 两进程均退出 0、未超时；主进程 324.328 秒，上限 900 秒 |
| 截图 | 源码 54、EXE 54、新进程 1，共 109 PNG 完整解码；窗口 922×518 |
| 显示审阅 | 15 个独立 EXE UI 视图；最终 5 张直接打开，其余通过与首轮图 SHA-256 相同复用审阅；最终 55 张 EXE 图与首轮字节相同 |

## 新增覆盖

CG 前后、第四章合流后的雨棚、第五章离场、同行、小店雨声停止前后和 Normal 正式道别段共 8 处原生存读档。保存后推进、清空背景为 black、改动三个状态及表情 / 音轨，再点读取；必须恢复实际章节、完整路径、状态、背景、表情及 music / ambient。预期值独立从剧情路线求出。

坦白回应原生回退后选择暂缓，随后落实联系和同行，必须进入 Normal、truth_known=false，坦白路径不残留。同进程 True 后新游戏清零，再进 Normal。自动模式开启 wait_voice，在 3.704 秒录音中等待 0.5 秒不得跳句；声音结束后实际推进，单调时钟要求至少 3.554 秒观察时长（容许 0.15 秒观察延迟），及时关闭自动。快进在全部四个选择停止。全部 16 条路线与旧八个交互用例保留。

## 失败与修复

首轮 [37278769927](https://github.com/AureliusWu/Test/actions/runs/37278769927) 已通过源码 / EXE 30/337 和新进程 1/10。加入背景清空后，[37280375775](https://github.com/AureliusWu/Test/actions/runs/37280375775) 暴露自动用例时序竞争：0.1 秒间隔下语音结束后可推进多个静音台词，“恰好一行”不成立。29/30 用例通过、344 个执行断言中 1 个失败；构建、包验证、候选上传均实际 skipped。

修复为及时关自动、核对录音时长 / 通道结束 / 实际推进，完整集合重新通过上述最终 CI。失败事实保留在 [v08-ci-failure.json](evidence/v08-ci-failure.json)。生成文件过期 / 缺失、原生摘要缺失、缺截图 / 截断截图的真实 CLI 均退出 1，正向生成和检查退出 0，见 [v08-negative-checks.json](evidence/v08-negative-checks.json)。79 项中另覆盖实际 Vorbis 截断、已有文字 / 语音缓存漂移、缺资产、版本不一致、图像损坏与 I/O 回滚。

main 和手动发布使用同一源码报告 / 包证据门槛；报告须匹配全部预期用例名与断言数，失败 / 跳过 / not run 非零即拒绝，全部预期截图必须完整解码。本批实际证明了失败阻止候选构建与上传；手动发布入口沿用相同检查和成功依赖关系。

## 包身份与下载

- 游戏 ZIP：`BeforeTheRainStops-0.8.0-win.zip`，**44,868,967 字节**。
- SHA-256：`e436d30a93e7a51671b4ffec60a43ff636a865299b67f237af1c8195e048ba9c`。两份 SHA256SUMS、ZIP CRC、0.8.0 build_info 已核验。
- Windows artifact：[11333430981](https://github.com/AureliusWu/Test/actions/runs/37281855516/artifacts/11333430981)，digest `d533e0de58b032603cbf5b7942ab3b5f316c328e750a8326bf1ad23081fe4c0e`。
- Evidence artifact：[11333196450](https://github.com/AureliusWu/Test/actions/runs/37281855516/artifacts/11333196450)，digest `c89c8a56bdf6e325b8fc58b9ca279ccbff14e35f9c7c7281f8010af8d7df7e00`。
- Actions 下载需登录，保留至 2027-01-03；同字节游戏 ZIP、校验和、实际预览与统一审阅包另作为交付文件保存。

包内没有作者数据、测试脚本、项目 rpy 源码、模型或存档；只有临时解压验收目录注入了测试。保留官方所需的 build_info.json、bytecode-312.rpyb 与 Ren'Py common 脚本，不把它们误删为开发缓存。逐图哈希、过程、身份与检查结果见 [v08-acceptance.json](evidence/v08-acceptance.json)。

## 后续与范围

逻辑画布仍为 1280×720；缩放窗口截图不能替代原生 1080p / DPI 验收。v0.9 继续 UI、阅读节奏和可审阅体验打磨。已知 P2：“关于”页沿用 Alpha 称呼，随 v0.9 文案整理修改；主菜单已改为可玩候选。另有 P2：原始 ZIP 内的开发 README 下载段沿用 v0.7 链接，当前交付说明与 main 已标明正确 v0.8 包；v0.9 生成专用玩家说明，避免包内引用自身构建哈希。本批机器验收未发现 P0 / P1。

真人阅读计时、17 句试听与混音、普通 Windows 离线试玩、显示 / 中文路径和最终创作定案集中在 [HUMAN_HANDOFF](HUMAN_HANDOFF.md)，由用户后续统一操作。正文、16 条路径与三种终态效果、17 句配音文字、所有图像 / 音频字节沿用已验收 v0.7；主题、人物、声音与重大结局仍为候选，未宣称正式冻结或 v1.0 完成。
