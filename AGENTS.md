# AI Galgame execution rules

- Follow `docs/PROJECT.md` and the user's AI Galgame execution document v1.0.
- Use Ren'Py 8.5.3; never implement a custom VN runtime.
- Work on `main`; preserve user edits and history. No force push.
- Keep story source in `game/data/story.json`; regenerate standard DSL with `python -m tools.compile_story` and runtime tests with `python -m tools.compile_tests`.
- Keep source assets separate from game-ready assets; preserve prompt, source, license and checksum metadata.
- Characters are adults. Maintain Character Bible and story timeline.
- No new servers, accounts, real-time LLM, Live2D or large frameworks during Vertical Slice.
- Do not claim semantic character/timeline checks are fully automated.
- Run Python tests, all validators, Ren'Py lint and actual interaction tests before a release.
- User decides final theme, heroine, art style, major plot and ending. Proposed defaults remain reviewable drafts until chosen.
- Update `CHANGELOG.md`, `docs/STATUS.md` and `docs/TEST_PLAN.md` with evidence and limitations.
- Report platform-specific execution separately: a cross-built ZIP is not proof of Windows execution.

跨项目复用另读 [三项目制作契约](docs/production/SHARED-VN.md)。本仓库原有引擎、剧情、存档和发行约束继续生效；共用结构检查不能替代原生状态路线与平台验收。

剧情、美术精修另读 [协作方法](docs/production/CREATIVE-PLAYBOOK.md)。保留原段落、路线与录音句，检查点与实际平台证据分别留档。

项目类型和完成标准另读 [本作验收](docs/production/PROJECT-ACCEPTANCE.md)，以用户 2026-10-25 四作要求为准。按各作实际玩法验收，不强制统一 Galgame 模板；资源必须实际触发并验证效果，才能标记完成。
