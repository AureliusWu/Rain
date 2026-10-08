# NetLove 能力交流 / 2026-10-08

NetLove 复用本项目的单一 JSON 剧情来源、源资产与 Prompt/许可/哈希绑定、全状态路线和 Windows 实际包验收方法。共用制作契约位于 [SHARED-VN.md](production/SHARED-VN.md)，同版本同哈希脚本同步到三个仓库。

本项目新增可选 Node 结构检查：`node scripts/vn-contract.mjs game/data/story.json`。它已验证 26 个结构节点、539 段节点正文、4 次选择、2 个结局；嵌入选项的 response 另检查 ID，条件分支的真实执行仍由 Python/Ren’Py 的 16 路线验证负责。它不改变 game/data/story.json、生成脚本、资产、玩家包或既有发行。

NetLove 回馈结构接口、JSON 字体覆盖修正与双端移植检查清单。原有 v1.1.1 的 Windows 与真人待办仍按 STATUS.md 继续，不把本次交流当作已完成原有验收。
