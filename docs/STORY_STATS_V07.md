# v0.7 路线字数报告

剧情版本：`0.6.0`（开发中）。剧情源 SHA-256：`407bba5ef89fdba73d04690a024fde0e9da8c0412f9c547bce42c8e1a9717a6d`。

按台词 ID 去重，正文包含标点，单位为 Unicode 字符；各路线仅计算所选选项的回应。菜单选项单列，章节标题、Prompt 和纯路由节点不计入正文。

全分支正文 **14283** 字符；528 行；菜单 102 字符。共 24 个叙事场景、2 个纯路由节点、16 条路线。

单路线 **10884–11208** 字符。True 4 条，Normal 12 条。

阅读估算仅用每分钟 250–350 字符换算正文，不含选择停顿、画面停留、试听和离开游戏的暂停。它不能替代真人 30–60 分钟验收。

| 章节 | 全分支正文字符 | 叙事场景 |
|---|---:|---:|
| ch00 序章 ： 雨夜 | 2176 | 3 |
| ch01 第一章 ： 重逢 | 2967 | 4 |
| ch02 第二章 ： 旧信 | 3157 | 4 |
| ch03 第三章 ： 空白 | 2244 | 3 |
| ch04 第四章 ： 今天 | 2278 | 5 |
| ch05 第五章 ： 雨停之前 | 1461 | 5 |

| 路线 | 选择顺序 | 结局 | 正文字符 | 菜单字符 | 叙事场景 | 纯文本估算分钟 |
|---|---|---|---:|---:|---:|---:|
| R01 | q01_care → q02_honest → q04_revisit → q03_walk | true | 11208 | 102 | 18 | 32.02–44.83 |
| R02 | q01_care → q02_honest → q04_revisit → q03_leave | normal | 11093 | 102 | 18 | 31.69–44.37 |
| R03 | q01_care → q02_honest → q04_concrete → q03_walk | true | 11200 | 102 | 18 | 32.0–44.8 |
| R04 | q01_care → q02_honest → q04_concrete → q03_leave | normal | 11085 | 102 | 18 | 31.67–44.34 |
| R05 | q01_care → q02_defer → q04_revisit → q03_walk | true | 11024 | 102 | 18 | 31.5–44.1 |
| R06 | q01_care → q02_defer → q04_revisit → q03_leave | normal | 10909 | 102 | 18 | 31.17–43.64 |
| R07 | q01_care → q02_defer → q04_concrete → q03_walk | normal | 10886 | 102 | 18 | 31.1–43.54 |
| R08 | q01_care → q02_defer → q04_concrete → q03_leave | normal | 10901 | 102 | 18 | 31.15–43.6 |
| R09 | q01_business → q02_honest → q04_revisit → q03_walk | true | 11159 | 102 | 18 | 31.88–44.64 |
| R10 | q01_business → q02_honest → q04_revisit → q03_leave | normal | 11044 | 102 | 18 | 31.55–44.18 |
| R11 | q01_business → q02_honest → q04_concrete → q03_walk | normal | 11021 | 102 | 18 | 31.49–44.08 |
| R12 | q01_business → q02_honest → q04_concrete → q03_leave | normal | 11036 | 102 | 18 | 31.53–44.14 |
| R13 | q01_business → q02_defer → q04_revisit → q03_walk | normal | 10892 | 102 | 18 | 31.12–43.57 |
| R14 | q01_business → q02_defer → q04_revisit → q03_leave | normal | 10907 | 102 | 18 | 31.16–43.63 |
| R15 | q01_business → q02_defer → q04_concrete → q03_walk | normal | 10884 | 102 | 18 | 31.1–43.54 |
| R16 | q01_business → q02_defer → q04_concrete → q03_leave | normal | 10899 | 102 | 18 | 31.14–43.6 |

复现：`python -m tools.story_stats --report reports/story-stats.json --markdown docs/STORY_STATS_V07.md`。完整路径及三个终态保存在 JSON 报告中。
