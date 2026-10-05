# Work checkpoint

2026-10-05，main。用户要求工程自主继续，真人后续统一由用户操作。

## 当前接续点

v0.9 原生 1080p 已完整提交 d6c68983768124594327aa886c0b5440c2dc5080；所有 GUI、60 图片 / 配方、玩家说明与显示回归已接入，81 Python / 作者检查和 Windows lint 通过。

首轮 Windows 37297516216 的原生 / 缩放界面与 560 句字体测量通过，但旧 15 秒 advance-until 上限使长剧情段超时：31 用例中 13 通过、18 失败；235 已执行断言均通过，包构建被正确阻止。保留失败证据 docs/evidence/v09-first-failure.json。按实际 1080p 软件渲染耗时把主集合单次等待改为 45 秒，包进程上限 2400 秒、CI 总上限 75 分钟；路线、断言、截图和失败规则不变。新菜单截图增加 0.3 秒等待以避开 dissolve，原生存档卡和空缩略图统一为蓝色。完整重验待执行。

读取取消后日志已定位二轮 37300201619：并非整个集合仍正常慢跑，而是在 21.711 秒报 FAILED；31 用例中 1 失败、30 not run，10 已执行断言均通过，560 句字体溢出列表为空。空存档缩略图误用了 gui.thumbnail_width / height（实际定义于 config），引发 AttributeError；后续 before / teardown 又触发 float > NoneType，使引擎未能退出。已更正为 config.thumbnail_width / height，保留原生蓝色空卡，并保留有界源码进程防止类似错误无限等待。源码 / EXE 各 2400 秒，新进程读档 120 秒、总作业 90 分钟；31/359、65 图与跨进程 1/10、1 图的完整门槛不变。失败 artifact 11344121426 的身份见 evidence/v09-source-overrun.json。完整 Windows 重验仍待完成。

## 下一步

核对 main 与工作区，不重置或 force push。等待修复候选的 Windows 完整源码 / 独立 ZIP EXE / 新进程读档结果；严格核验 31/359、1/10、131 PNG、1080p / 720p 物理尺寸与包哈希。失败即修复后重跑。成功后检查实际 EXE 画面，更新 DISPLAY_ACCEPTANCE_V09、STATUS、TEST_PLAN、CHANGELOG、HUMAN_HANDOFF 与本接续点，交付原始游戏 ZIP、66 画面 / 24 OGG-WAV / 两完整路线正文的审阅包及校验和。

后续从 V09-01 正文精修继续；真人计时、试听、普通电脑 / 中文路径 / DPI、创作定案统一待用户操作，不阻塞独立工程工作。内容未冻结、v1.0 未完成，公开 Release 仍 v0.6.0。
