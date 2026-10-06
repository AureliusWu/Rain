# v1.0 验收与发布

版本 1.0.0 已准备为验收候选。40 处正文精修已应用，560 个台词 ID、17 句录音文字、四次选择与 16 路线保留。全分支 15,065 字符、单路线 11,303–11,666。

## 机器验收

候选 `7593a348bf28e196c2ee3a55fd1e14c837289ef3` / [Windows CI 37411258713](https://github.com/AureliusWu/Test/actions/runs/37411258713)；原始游戏 ZIP **56,354,657 字节**，SHA-256 `4ecba6cea822947b08bc8a877af2d5eed4ccbb3ffdd367c92032c236f5dac048`。

91 项 Windows Python、作者侧全部校验与 Ren’Py 8.5.3 lint 通过。源码和独立 EXE 各 **31/31 用例、359/359 断言**（1088.999 / 741.506 秒）；关闭首进程后重新启动 EXE，真实读档另 **1/1 用例、10/10 断言**（3.719 秒）。全部 failed / xfailed / xpassed / skipped / not run 为 0，三个进程退出 0、未超时。

131 张 PNG 完整解码；35 张实际 EXE 关键画面按当前原图或相同 SHA-256 的既有直接审阅记录复核，未发现遗留机器问题。85 个包内资产 SHA-256、原始 ZIP CRC、版本、玩家说明及许可文件已核验；未注入测试脚本。仅保留引擎启动必需的 build_info / bytecode 缓存。

Windows runner 使用 dummy 音频；真人试听、两结局阅读计时、普通电脑 / 中文路径 / 100% 与 150% DPI、创作定案及内容冻结继续待用户统一操作。正式发布 workflow 尚未执行，没有正式 v1.0 tag / Release。

发布工具补检见 [RELEASE_ENGINEERING_V10](RELEASE_ENGINEERING_V10.md)：本轮 Linux 97 项测试及全部作者校验 / lint 通过；原 Windows 输出已重新解析并补齐 xfailed / xpassed，原 ZIP / 预览校验通过。正式检查继续按同一候选和真实 pending 人验表阻止发布。

## 统一人工验收

[HUMAN_HANDOFF](HUMAN_HANDOFF.md) 包含一次完成的操作范围。`docs/review/V10_HUMAN_ACCEPTANCE.json` 当前五组均 pending，没有自动填写通过、真人计时、试听或冻结。

结果需绑定实际试玩候选提交及 ZIP SHA-256。填写 reviewer、reviewed_at、五组 status / evidence，Normal 和 True 完整实测分钟，以及 unresolved_issues。正式发布要求所有组 passed、整体 approved、无遗留问题。若时长偏离 30–60 分钟，先根据阅读结果调整，或由用户明确修改范围；不使用估算代替测量。

## 后续发布操作

1. 用户统一完成普通 Windows、中文路径、DPI、试听、两结局计时和创作定案；工程侧整理真实结果，填写绑定记录和冻结日期，并按结果同步 README / RELEASE_NOTES 的验收状态。
2. 执行 `python -m tools.release_gate --version 1.0.0`。记录完整后通过，当前会阻止发布。
3. 从 main 手动运行 `Publish exact approved v1 Windows package`，输入 1.0.0。
4. workflow 验证成功 CI 的候选 SHA、artifact ID 与版本，下载既有 ZIP，再校验文件大小、SHA-256、CRC、元数据、许可及开发文件排除。
5. 没有现存同名 tag / Release 时才创建正式 v1.0.0；发布的 ZIP 不重新构建，并重新下载核验同字节。

如果 artifact 过期，先恢复已交付原始 ZIP 或重新建立完整候选验收，不绕过哈希或人工绑定。旧 release.yml 仅处理 v1 以前的候选。

## 下载入口与范围

[Windows 候选 artifact](https://github.com/AureliusWu/Test/actions/runs/37411258713/artifacts/11390201913)，需 GitHub 登录，保留至 2027-01-04T03:55:25Z。同字节游戏 ZIP、统一审阅 ZIP、校验和及实际 EXE 预览另已交付。公开 Release 仍为 v0.6.0。

审阅材料含 66 张原始 EXE PNG、24 OGG / 24 解码 WAV、两结局完整原文与其余 100 行分支文本，覆盖全部 560 台词 ID。统一回报模板保留 pending，不预填通过。
