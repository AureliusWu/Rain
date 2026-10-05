# v0.7 路线字数报告

剧情版本：`0.7.0`（开发中）。剧情源 SHA-256：`c9d4bd6ec954c0eca8e5273c5e2e9b9f058aff3be93268b295ec407f4a975681`。

按台词 ID 去重，正文包含标点，单位为 Unicode 字符；各路线仅计算所选选项的回应。菜单选项单列，章节标题、Prompt 和纯路由节点不计入正文。

全分支正文 **15206** 字符；560 行；菜单 102 字符。共 24 个叙事场景、2 个纯路由节点、16 条路线。

单路线 **11404–11744** 字符。True 4 条，Normal 12 条。

阅读估算仅用每分钟 250–350 字符换算正文，不含选择停顿、画面停留、试听和离开游戏的暂停。它不能替代真人 30–60 分钟验收。

| 章节 | 全分支正文字符 | 叙事场景 |
|---|---:|---:|
| ch00 序章 ： 雨夜 | 2196 | 3 |
| ch01 第一章 ： 重逢 | 2967 | 4 |
| ch02 第二章 ： 旧信 | 3157 | 4 |
| ch03 第三章 ： 空白 | 2247 | 3 |
| ch04 第四章 ： 今天 | 2281 | 5 |
| ch05 第五章 ： 雨停之前 | 2358 | 5 |

| 路线 | 选择顺序 | 结局 | 正文字符 | 菜单字符 | 叙事场景 | 纯文本估算分钟 |
|---|---|---|---:|---:|---:|---:|
| R01 | q01_care → q02_honest → q04_revisit → q03_walk | true | 11744 | 102 | 18 | 33.55–46.98 |
| R02 | q01_care → q02_honest → q04_revisit → q03_leave | normal | 11625 | 102 | 18 | 33.21–46.5 |
| R03 | q01_care → q02_honest → q04_concrete → q03_walk | true | 11733 | 102 | 18 | 33.52–46.93 |
| R04 | q01_care → q02_honest → q04_concrete → q03_leave | normal | 11614 | 102 | 18 | 33.18–46.46 |
| R05 | q01_care → q02_defer → q04_revisit → q03_walk | true | 11560 | 102 | 18 | 33.03–46.24 |
| R06 | q01_care → q02_defer → q04_revisit → q03_leave | normal | 11441 | 102 | 18 | 32.69–45.76 |
| R07 | q01_care → q02_defer → q04_concrete → q03_walk | normal | 11406 | 102 | 18 | 32.59–45.62 |
| R08 | q01_care → q02_defer → q04_concrete → q03_leave | normal | 11430 | 102 | 18 | 32.66–45.72 |
| R09 | q01_business → q02_honest → q04_revisit → q03_walk | true | 11695 | 102 | 18 | 33.41–46.78 |
| R10 | q01_business → q02_honest → q04_revisit → q03_leave | normal | 11576 | 102 | 18 | 33.07–46.3 |
| R11 | q01_business → q02_honest → q04_concrete → q03_walk | normal | 11541 | 102 | 18 | 32.97–46.16 |
| R12 | q01_business → q02_honest → q04_concrete → q03_leave | normal | 11565 | 102 | 18 | 33.04–46.26 |
| R13 | q01_business → q02_defer → q04_revisit → q03_walk | normal | 11415 | 102 | 18 | 32.61–45.66 |
| R14 | q01_business → q02_defer → q04_revisit → q03_leave | normal | 11439 | 102 | 18 | 32.68–45.76 |
| R15 | q01_business → q02_defer → q04_concrete → q03_walk | normal | 11404 | 102 | 18 | 32.58–45.62 |
| R16 | q01_business → q02_defer → q04_concrete → q03_leave | normal | 11428 | 102 | 18 | 32.65–45.71 |

复现：`python -m tools.story_stats --report reports/story-stats.json --markdown docs/STORY_STATS_V07.md`。完整路径及三个终态保存在 JSON 报告中。
