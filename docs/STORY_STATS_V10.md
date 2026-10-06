# v1.0.0 路线字数报告

剧情版本：`1.0.0`。剧情源 SHA-256：`8456fefa4ec8c504444bfafab017ceb882c7ba5e335a1541842a9526bca919f3`。

按台词 ID 去重，正文包含标点，单位为 Unicode 字符；各路线仅计算所选选项的回应。菜单选项单列，章节标题、Prompt 和纯路由节点不计入正文。

全分支正文 **15065** 字符；560 行；菜单 102 字符。共 24 个叙事场景、2 个纯路由节点、16 条路线。

单路线 **11303–11666** 字符。True 4 条，Normal 12 条。

阅读估算仅用每分钟 250–350 字符换算正文，不含选择停顿、画面停留、试听和离开游戏的暂停。它不能替代真人 30–60 分钟验收。

| 章节 | 全分支正文字符 | 叙事场景 |
|---|---:|---:|
| ch00 序章 ： 雨夜 | 2196 | 3 |
| ch01 第一章 ： 重逢 | 2967 | 4 |
| ch02 第二章 ： 旧信 | 3157 | 4 |
| ch03 第三章 ： 空白 | 2119 | 3 |
| ch04 第四章 ： 今天 | 2265 | 5 |
| ch05 第五章 ： 雨停之前 | 2361 | 5 |

| 路线 | 选择顺序 | 结局 | 正文字符 | 菜单字符 | 叙事场景 | 纯文本估算分钟 |
|---|---|---|---:|---:|---:|---:|
| R01 | q01_care → q02_honest → q04_revisit → q03_walk | true | 11666 | 102 | 18 | 33.33–46.66 |
| R02 | q01_care → q02_honest → q04_revisit → q03_leave | normal | 11506 | 102 | 18 | 32.87–46.02 |
| R03 | q01_care → q02_honest → q04_concrete → q03_walk | true | 11656 | 102 | 18 | 33.3–46.62 |
| R04 | q01_care → q02_honest → q04_concrete → q03_leave | normal | 11496 | 102 | 18 | 32.85–45.98 |
| R05 | q01_care → q02_defer → q04_revisit → q03_walk | true | 11499 | 102 | 18 | 32.85–46.0 |
| R06 | q01_care → q02_defer → q04_revisit → q03_leave | normal | 11339 | 102 | 18 | 32.4–45.36 |
| R07 | q01_care → q02_defer → q04_concrete → q03_walk | normal | 11305 | 102 | 18 | 32.3–45.22 |
| R08 | q01_care → q02_defer → q04_concrete → q03_leave | normal | 11329 | 102 | 18 | 32.37–45.32 |
| R09 | q01_business → q02_honest → q04_revisit → q03_walk | true | 11634 | 102 | 18 | 33.24–46.54 |
| R10 | q01_business → q02_honest → q04_revisit → q03_leave | normal | 11474 | 102 | 18 | 32.78–45.9 |
| R11 | q01_business → q02_honest → q04_concrete → q03_walk | normal | 11440 | 102 | 18 | 32.69–45.76 |
| R12 | q01_business → q02_honest → q04_concrete → q03_leave | normal | 11464 | 102 | 18 | 32.75–45.86 |
| R13 | q01_business → q02_defer → q04_revisit → q03_walk | normal | 11313 | 102 | 18 | 32.32–45.25 |
| R14 | q01_business → q02_defer → q04_revisit → q03_leave | normal | 11337 | 102 | 18 | 32.39–45.35 |
| R15 | q01_business → q02_defer → q04_concrete → q03_walk | normal | 11303 | 102 | 18 | 32.29–45.21 |
| R16 | q01_business → q02_defer → q04_concrete → q03_leave | normal | 11327 | 102 | 18 | 32.36–45.31 |

复现：`python -m tools.story_stats --report reports/story-stats.json --markdown reports/story-stats.md`。完整路径及三个终态保存在 JSON 报告中。
