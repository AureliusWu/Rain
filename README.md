# 雨停之前 / Before the Rain Stops

<!-- project-badges:start -->
[![Version](https://img.shields.io/github/v/tag/AureliusWu/Rain?sort=semver&style=flat-square&label=version)](https://github.com/AureliusWu/Rain/tags) [![Build](https://github.com/AureliusWu/Rain/actions/workflows/release-v10.yml/badge.svg?branch=main)](https://github.com/AureliusWu/Rain/actions/workflows/release-v10.yml) [![Last commit](https://img.shields.io/github/last-commit/AureliusWu/Rain?style=flat-square)](https://github.com/AureliusWu/Rain/commits/main) [![License](https://img.shields.io/github/license/AureliusWu/Rain?style=flat-square)](LICENSE)
<!-- project-badges:end -->

当前正式版：`1.7.0`。Windows 离线版与 Web/PWA 使用同一剧情与存档身份。

雨夜旧车站，两位久未联系的旧友，和一封没有寄出的信。六章、四次选择、16 条路线，包含 Normal / True 两个结局。

[在线游玩](https://aureliuswu.github.io/Rain/) · [v1.7.0 Release](https://github.com/AureliusWu/Rain/releases/tag/v1.7.0)

## 当前内容

- 六章完整剧情、24 个叙事场景与 16 条完整路线。
- 306 条人物对白离线语音，旁白保留文字。
- 场景、CG、人物鉴赏、音乐与历史重听随阅读解锁。
- Windows 桌面端与可安装 PWA；首次完整缓存后支持离线游玩。
- 原生存档、手动存档与 Web/Windows 备份导入导出。

## 开发与验证

Ren’Py 8.5.3 / Python 3.12：

```bash
python -m tools.preflight
python -m tools.validate
```

剧情唯一来源为 `game/data/story.json`；修改后按仓库现有工具重新编译故事、测试和平台发行包。

## AI / 维护者入口

修改前先读 [AGENTS.md](AGENTS.md)。

- 项目与制作约束：`docs/PROJECT.md`、`docs/production/VN-WORKFLOW-R1.md`。
- 剧情事实源：`game/data/story.json`。
- 资产与语音清单：`game/data/asset_manifest.json`、`game/data/voice_manifest.json`。
- 当前发行与机器证据：GitHub Release 与 `docs/production/`。
- 创作方法：`docs/production/CREATIVE-PLAYBOOK.md`。

README 不保存逐版本验收数字、历史工作流 run、四作共存流水或人工审阅清单；这些继续留在 `docs/`、Release 与 Git 历史中。任何未实际执行的真人听感、实体设备或创作审读都不能写成已通过。

## License

许可与素材来源见 [LICENSE](LICENSE)、`CREDITS.md` 和 `licenses/`。