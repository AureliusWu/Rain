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
