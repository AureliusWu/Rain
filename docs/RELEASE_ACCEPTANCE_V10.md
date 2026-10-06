# v1.0 验收与发布

版本 1.0.0 已准备为验收候选。40 处正文精修已应用，560 个台词 ID、17 句录音文字、四次选择与 16 路线保留。全分支 15,065 字符、单路线 11,303–11,666。

## 机器验收

本次 Windows 源码、独立 EXE 与关闭后新进程读档正在重验；候选提交、run、artifact、原始游戏 ZIP 大小 / SHA-256 和实际画面将在完成后写入 `docs/evidence/v10-acceptance.json`。历史 v0.9 通过结果仅作基线。

## 统一人工验收

[HUMAN_HANDOFF](HUMAN_HANDOFF.md) 包含一次完成的操作范围。`docs/review/V10_HUMAN_ACCEPTANCE.json` 当前五组均 pending，没有自动填写通过、真人计时、试听或冻结。

结果需绑定实际试玩候选提交及 ZIP SHA-256。填写 reviewer、reviewed_at、五组 status / evidence，Normal 和 True 完整实测分钟，以及 unresolved_issues。正式发布要求所有组 passed、整体 approved、无遗留问题。若时长偏离 30–60 分钟，先根据阅读结果调整，或由用户明确修改范围；不使用估算代替测量。

## 后续发布操作

1. 用户统一完成普通 Windows、中文路径、DPI、试听、两结局计时和创作定案；工程侧整理真实结果并填写绑定记录。
2. 执行 `python -m tools.release_gate --version 1.0.0`。记录完整后通过，当前会阻止发布。
3. 从 main 手动运行 `Publish exact approved v1 Windows package`，输入 1.0.0。
4. workflow 验证成功 CI 的候选 SHA、artifact ID 与版本，下载既有 ZIP，再校验文件大小、SHA-256、CRC、元数据、许可及开发文件排除。
5. 没有现存同名 tag / Release 时才创建正式 v1.0.0；发布的 ZIP 不重新构建，并重新下载核验同字节。

如果 artifact 过期，先恢复已交付原始 ZIP 或重新建立完整候选验收，不绕过哈希或人工绑定。旧 release.yml 仅处理 v1 以前的候选。
