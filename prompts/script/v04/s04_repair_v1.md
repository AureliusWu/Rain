# s04_repair — Scene Prompt v1

LLM assistant scene draft. Candidate, Agent reviewed; final direction remains user reviewable.

Input: docs/WORLD.md, docs/CHARACTERS.md, docs/STORY_OUTLINE_V04.md, existing v0.3 story.
Chapter: ch04. Location: old_station. Present time: 22:10.
Scene goal: 补充过去与现在的意思，修复一次早期回避。

Write only this scene in Chinese. Use narrator n, adult Xu Cheng h and first-person player p. Maintain the silver clip, standing pose, independent heroine and concrete restrained speech. No new character, supernatural rule or past secret. Do not change the already-authored route effects. Letter authorship is known to the player from the start; truth_known concerns the heroine. Avoid assuming a withheld fact was confessed. Keep each dialogue within 140 characters, natural pauses, and a clear transition to the next scene.

Context for this draft: q04_revisit 设置 truth_known=true，入口可能之前诚实也可能延迟；不能无条件说刚才撒谎。明确作者及当时想继续关系，表达今天愿意联系，不要求她答复。

Output is integrated into game/data/story.json; this Prompt does not become a second runtime source.
