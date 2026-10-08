# v1.1.1 发行验收 — 2026-10-08

音乐鉴赏显示已解锁数量、当前曲名及播放 / 暂停 / 停止状态；暂停后显示“继续”，停止后提示选择已解锁音乐。状态分隔符改用现有字体支持的中文冒号，修复方框缺字。

游戏验收提交 `491e9859368a402960afcdf856be4f456b885ec5` / [Windows CI 37711912728](https://github.com/AureliusWu/Test/actions/runs/37711912728)；原始 ZIP **56,382,628 字节**，SHA-256 `7f57b4f4d3f2cc4071d7e4d59ff6a2e3c7db0531b78477abae18804c47d6d35b`。

Windows **118 项 Python**、全部作者校验及 Ren’Py 8.5.3.26051504 lint 通过；源码和独立 EXE 各 **36 用例 / 448 断言 / 82 截图**。新进程读档 / 鉴赏持久进度 **1/16/3**，公开 v1.1.0 写档 **1/14/3**、新 EXE 读取旧档 / 已读解锁 **2/26/4**（用例 / 断言 / 截图）。五个完整进程退出 0、未超时，异常计数全为 0；两遍真实前缀另各 **6/103/29** 通过。

Windows 审计完整解码并核对 **174 张原始 PNG** 的尺寸 / SHA-256；复核 **58 个关键视图**，其中 12 个直接查看当前全分辨率 JPEG 副本、46 个原始 PNG 与已有审阅哈希完全相同。副本绑定原图哈希，保留 JPEG 检查限制。85 包内资产、ZIP CRC、版本、署名及许可核验通过，原始玩家包无测试注入或模型。

保留六章正文、560 台词 ID、16 条真实状态路线、17 句 Qwen3-TTS / Serena 录音、85 资产及 v1 存档目录。剧情 JSON 相较已验收 v1.1.0 仅改变版本字段。

用户 2026-10-08 新增的共享制作文档与 Node 结构校验脚本已保留：26 节点、539 段节点正文、4 次选择、2 结局；三份共享文件 SHA-256 全部匹配清单。结构检查补充原生 16 路线检查。新增支持文件不进入已验收玩家包；发行逐一核对四个精确 Git blob，禁止放宽至整个 scripts 目录。

本批工程与画面验收已完成，尚待发行 CI 下载同一原始安装包、发布并回读验证。当前正式下载仍为 v1.1.0，不能将验收通过写成已发布。

真人试听、Normal / True 阅读计时、普通电脑 / 中文路径 / DPI、最终创作定案与冻结继续由用户统一操作，五组保持 pending。Windows 使用 dummy 音频，自动执行耗时不等于阅读时长；真实旧档覆盖两个代表位置，未宣称验证全部玩家旧档或 Linux 原生 UI。

| 证据 | 位置 |
|---|---|
| 机器、ZIP、原生进程、174 PNG | [v111-acceptance.json](evidence/v111-acceptance.json) |
| 58个逐图结论与原图 / JPEG 绑定 | [v111-visual-review.json](evidence/v111-visual-review.json) |
| 新增共享文件、精确 blob 与门禁验证 | [v111-support-review.json](evidence/v111-support-review.json) |
| 用户发布指令及精确候选 / ZIP | [V111_PUBLICATION_AUTHORIZATION.json](review/V111_PUBLICATION_AUTHORIZATION.json) |
| 五组真实待办 | [V111_HUMAN_ACCEPTANCE.json](review/V111_HUMAN_ACCEPTANCE.json) |

原始 Windows 导出封印 SHA-256 `0be81309b80b4b380bb5a20ae26a7e17f0df787764ae26bd1e75a230fbbc3ec8`，10,482,106 字节，1,748个连续分块。当前12个 JPEG 哈希及46条既有原图审阅链独立核对。原始 ZIP / PNG 字节审计在 Windows runner 执行；未宣称本地下载并重组原始大包。发行 CI 必须实际下载工件及公开 ZIP，通过相同 SHA-256 / CRC 门禁。
