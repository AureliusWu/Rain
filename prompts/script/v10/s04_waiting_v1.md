# v0.7 Scene expansion request — s04_waiting

Purpose: 女主表达独立生活和对明确联系的需求。

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

This request is the v0.7 restoration/expansion pass for s04_waiting. Review character voice, timeline, item ownership and branch knowledge after writing.


## 合流修订 v2

保持既有关键配音文字、四次选择、16 路线、三个状态和结局条件不变。允许修改无配音旧句以修复以下事实或视角问题：登记只办一次；站内十点关门，21:55 已移动到门外雨棚；信封保持在玩家内袋、未拆；手机由椅面拿起，发消息前明确交换号码；叙述不提另一条分支的表现或数值高低。新增联系动作使用稳定 ID。

## v3 合流复核

核对当前已位于出口门外的事实：确认号码后的环境描写保持出口雨棚，不再把两人写回站台。


## v1.0 正文精修请求

继承以上角色、时间线、物品归属和分支条件。保留所有稳定台词 ID、17 句配音文字、四次选择和 16 路线。用动作、具体环境与自然口语收敛重复解释；不能把 AI 审阅记为用户创作批准。

- `s04_waiting_l010`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：她说得很平常。我却忽然松了一口气：她有自己的生活，也有自己保存东西的理由。
  - 修订：她说完抬起头。灯光落在她的银色发夹上，我的目光停了一下，才也笑了笑。
- `s04_waiting_l027`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：她把边界说得很具体，没有让我猜什么频率才算在意，也没有给自己安排一个必须随时等待的角色。
  - 修订：雨棚外有车开过去，轮胎带起一片水声。我等那声音落下，才接着她的话说下去。
- `s04_waiting_l034`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：我把刚打到一半的提醒删了。不是因为约定不重要，而是这件事不需要靠形式证明认真。
  - 修订：我把刚打到一半的提醒删了。她看着我关掉备忘录，嘴角又往上扬了一点。
- `s04_waiting_l035`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：她随后说起明天下午要给新到的书贴标签，晚上可能还要替同事半个班。那些琐碎安排让我第一次听见她现在生活的具体声音。
  - 修订：她随后说起明天下午要给新到的书贴标签，晚上可能还要替同事半个班。我听她把两段时间算了一遍，也想起自己的车票。
- `s04_waiting_l036`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：我也只说自己的明早：退房、坐车、回去处理积下来的工作。没有承诺很快搬回来，也没有把一次重逢夸成生活转折。
  - 修订：我也说了自己的明早：退房、坐车、回去处理积下来的工作。她问我行李多不多，我指了指脚边的纸箱。
- `s04_waiting_l038`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：她说完看向纸袋里的照片。我顺着她的视线看过去，下一段话终于可以从“现在”回到那张我们都记得、却记得不完全一样的旧照片。
  - 修订：她说完看向纸袋。我也看过去，照片的一角露在袋口，已经压得很平。
- `s04_waiting_l039`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：她把纸袋提起来试了试重量，又重新放下。今晚之后，这些照片会回到她的家，而不是继续留在旧站替谁保存过去。
  - 修订：她提起纸袋试了试重量，又重新放下，把折起的袋口压牢。薄纸在她手里轻轻响了一声。
- `s04_waiting_l042`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：我笑了一下，没有伸手。这个回答正好把下一段谈话的边界画出来：可以一起回忆，所有权仍属于她。
  - 修订：我笑了一下，继续扶着自己的箱子。许澄捏着袋口，也笑了笑。
- `s04_waiting_l026`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：我只是希望，如果你想继续联系，就别把“以后再说”当成默认设置。忙可以说忙，不想聊也可以说不想聊。
  - 修订：忙的时候说一声就好。哪天不想聊，也告诉我，我就去做自己的事。
- `s04_waiting_l029`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：两条就够。明天之后再看我们有没有想聊的。
  - 修订：嗯，先这样。后面的事，等有话想说再说。
- `s04_waiting_l033`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：那就删掉。记得做就行。
  - 修订：还用写下来？又不是盘点。
- `s04_waiting_l037`：用可见动作和自然对白替换重复解释；保留分支事实与双方主动性
  - 原句：这样就挺好。至少我们现在知道明天各自在做什么。
  - 修订：嗯。听起来都闲不了。
- `s04_waiting_l001`：补充离站位置、雨中动作或明确回应，使时间线和场景衔接可见
  - 原句：站台尽头的灯灭了一盏。我们把东西搬到出口门外连着的雨棚下，在长椅边停了下来。
  - 修订：站台尽头的灯灭了一盏。我们把东西搬到出口门外连着的雨棚下，在长椅边停了下来。门里有人卷起登记桌上的塑料布，门外的灯还亮着，照得见通向街角的那段路。
- `s04_waiting_l014`：补充离站位置、雨中动作或明确回应，使时间线和场景衔接可见
  - 原句：雨声从急促变得均匀。一阵风把告示的一角掀起来，露出下面旧时刻表的一小段。
  - 修订：雨声从急促变得均匀。一阵风把告示的一角掀起来，露出下面旧时刻表的一小段。我用箱子挡住飘来的水，许澄把鞋尖往椅子下面收了收。
