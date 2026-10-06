# v0.7 Scene expansion request — s04_reserved

Purpose: 信任较低时先明确不猜、不替对方决定。

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

This request is the v0.7 restoration/expansion pass for s04_reserved. Review character voice, timeline, item ownership and branch knowledge after writing.


## 合流修订 v2

保持既有关键配音文字、四次选择、16 路线、三个状态和结局条件不变。允许修改无配音旧句以修复以下事实或视角问题：登记只办一次；站内十点关门，21:55 已移动到门外雨棚；信封保持在玩家内袋、未拆；手机由椅面拿起，发消息前明确交换号码；叙述不提另一条分支的表现或数值高低。新增联系动作使用稳定 ID。


## v1.0 正文精修请求

继承以上角色、时间线、物品归属和分支条件。保留所有稳定台词 ID、17 句配音文字、四次选择和 16 路线。用动作、具体环境与自然口语收敛重复解释；不能把 AI 审阅记为用户创作批准。

- `s04_reserved_l009`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：这不是她替我把话接下去。她只是留出了一个位置，要不要走进去，还得由我自己决定。
  - 修订：她说完便安静下来。我看着她，慢慢把下一句话组织好。
- `s04_reserved_l013`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：“碰巧”把这次重逢放回它真实的位置。不是命运替我们修好什么，也不是谁偷偷守了三年。
  - 修订：她把“碰巧”说得很轻。我看着她手里的书店纸袋，想起自己来时只带了一只空布袋。
- `s04_reserved_l020`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：这句话暂时没有换来笑。她只是往长椅另一端挪了一点，给我们留出能继续说话、也能随时停下来的距离。
  - 修订：她听完，往长椅另一端挪了一点。纸袋碰着她的膝盖，她把它扶稳，才重新看向我。
- `s04_reserved_l022`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：她把暂停的规则也说清楚。我终于有一个开口、停下都不必让她猜的办法。
  - 修订：我点头，慢慢吐了一口气。雨声填上了那一小段停顿，她仍坐在原处。
