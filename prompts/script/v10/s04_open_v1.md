# v0.7 Scene expansion request — s04_open

Purpose: 信任较高时主动问玩家现在能说清什么。

Expand the existing scene in Chinese without changing the route graph, state effects, chapter order, or existing line IDs.
Preserve all voice-bound lines exactly. Keep existing IDs; revise unvoiced lines only for the reviewed continuity issues. Add concrete actions, environment details, motives and consequences rather than abstract explanation.

Hard facts:
- Modern fictional Jiangcheng, old station closing on a rainy night.
- The player is a 25-year-old adult who returned to collect stored books; meeting Xu Cheng was not planned.
- Xu Cheng is a 23-year-old adult bookstore worker with her own home, work schedule and decisions.
- The player knows from the opening that he wrote the unsent letter. Xu Cheng only knows this after q02_honest or later q04_revisit.
- The envelope remains unopened and in the player's possession after the letter scene.
- Old photos belong to Xu Cheng and do not prove that she waited for the player.
- Do not turn nostalgia into a demand for romantic repayment.
- Keep the existing four choices, 16 routes, two endings, and affection/trust/truth_known state model.
- q04 repair may affect what happens next but may not erase earlier choices.

This request is the v0.7 restoration/expansion pass for s04_open. Review character voice, timeline, item ownership and branch knowledge after writing.


## 合流修订 v2

保持既有关键配音文字、四次选择、16 路线、三个状态和结局条件不变。允许修改无配音旧句以修复以下事实或视角问题：登记只办一次；站内十点关门，21:55 已移动到门外雨棚；信封保持在玩家内袋、未拆；手机由椅面拿起，发消息前明确交换号码；叙述不提另一条分支的表现或数值高低。新增联系动作使用稳定 ID。


## v1.0 正文精修请求

继承以上角色、时间线、物品归属和分支条件。保留所有稳定台词 ID、17 句配音文字、四次选择和 16 路线。用动作、具体环境与自然口语收敛重复解释；不能把 AI 审阅记为用户创作批准。

- `s04_open_l017`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：她没有追问是哪一件，只等我自己往下说。这个等待和三年前不同——不是无限期留在原地，而是现在愿意给我几分钟。
  - 修订：她把纸袋放稳，转过身来。我试了两次开头，终于迎上她的目光。
- `s04_open_l020`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：我应了一声。她把“愿意聊”和“要求留下”清楚分开，这让接下来的谈话有了一个不需要表演牺牲的起点。
  - 修订：我应了一声。她把被风吹起的袋口压住，等我接着说。
- `s04_open_l022`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：我点头。既然她愿意听，我就不能只说对自己有利的那半段。
  - 修订：我点头。先前只想说“没来得及”的那些事，这会儿得从头说了。
