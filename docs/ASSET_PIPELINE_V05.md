# v0.5 资产流程与复现

现有 66 个资产、31 份版本化 Prompt、57 张 PNG 和 30 个图片导入配方。制作工具离线运行，游戏只播放已导入文件。场景、语音和图片记录都通过稳定 Prompt ID 绑定到 `prompts/registry.json`。

## 固定输入与审阅

1. 图像工具按 Character Bible、固定身份/服装/姿态/画风和本场方向生成或编辑。
2. 源图保存在 `assets_source`，精确请求保存在 `prompts` 的 `_vN.md`；共享组件可使用 `_vN.json`。保留旧版本。
3. 审阅脸部、表情、衣纹与透明边缘，再明确登记新的 Prompt 文件：

```bash
python -m tools.prompt_registry --write
python -m tools.prompt_registry --check
```

Registry 包含 id、version、kind、file、SHA-256 和精确请求声明的共享 components。`--check` 拒绝遗漏、删除、改动、重复 ID/文件、版本不符和缺组件；CI 只检查，不自动接受变更。Prompt 改动时使用新版本文件，已发布资产继续引用原来的请求。

图片、语音和场景分别记录 prompt_id；资产同时保留路径与哈希，三者必须匹配 Registry。Manifest 是游戏文件和出处的事实来源，Registry 是生成请求的索引，不复制剧情或推理模型。

## 新图片导入

先检查，再写入。所有 CLI 路径相对仓库根目录。

```bash
python -m tools.image_process.import_asset --source assets_source/character/heroine_smile_v2.png --id heroine_smile --type sprite --output characters/heroine_smile_v2.png --prompt prompts/character/heroine_smile_v2.md --expression smile --version 2 --reference-source assets_source/character/heroine_clean_v2.png --prompt-components prompts/character/heroine_expressions_v1.json --source-label "Built-in imagegen; model identifier not exposed by tool" --license "AI-generated output; see CREDITS.md" --dry-run
```

审阅 dry-run 的输出和版本后，移除 `--dry-run` 执行同一命令。示例 v2 文件代表未来制作流程，当前仓库只有已发布的 v1 表情，不声称示例新图已经生成。

新资产必须明确 source-label 与 license；旧 ID 重建沿用已经记录的来源。`approved` 只表示工程整合审阅，approval_scope/status 明确保留用户最终选择待定。

| 类型 | 导入策略 |
|---|---|
| sprite | 已有真实透明通道，透明四角且可见主体；全画布等比缩小、底部居中到 540×700 |
| background / cg | 保持比例中心裁切为 1280×720 RGB PNG |
| ui | 默认按 PNG 原尺寸复制，保留 alpha；全屏菜单背景可显式使用 fit_1280x720_v1 |

导入前校验全部路径、源文件、Prompt、参考图、组件、透明度、版本和输出所有权。禁止覆盖其他 ID 或未登记的文件；同版本不能改变像素、源文件、Prompt 或参考来源，降版本也会拒绝。UI 不再一律被放大成背景尺寸。

PNG 与 Manifest 分别写入同目录临时文件后替换。普通 I/O 异常发生在 Manifest 替换时，会恢复原图，首次导入则移除半成品；临时文件清理有测试。一次执行一个导入进程；多文件更新的断电恢复依靠 Git，不声称两个文件具备跨进程事务。

## 重建现有资产

```bash
python -m tools.image_process.import_asset --rebuild heroine_smile --dry-run
python -m tools.image_process.import_asset --rebuild heroine_smile
python -m tools.image_process.import_asset --check
```

30 个配方覆盖背景、CG、七种立绘、复用主菜单和 20 个程序 UI 图元。`--check` 从登记源图重建到内存，核对像素与元数据，不修改游戏文件。相同输入重复执行不会重排记录或改写文件。已实际重建 heroine_smile，返回 changed=false。

SHA-256 校验文件字节；image.pixel_sha256 以尺寸和 RGBA 像素为输入，检测显示内容。不同 Pillow/PNG 编码器可能输出不同压缩字节；显示像素一致时保留原发行 PNG。开发依赖固定 Pillow 11.3.0，最终 Windows CI 已通过全部 30 个重建检查。

所有图片记录 width/height/mode/format/has_alpha 与 pixel_sha256，并必须完整解码。主菜单记录 reused_from=station；normal 的清理参考与 CG 的两个原始参考也保留哈希。基础 BGM/雨声补齐源 WAV；6 句语音继续核对台词、来源、Prompt ID、文本哈希、采样率和源 WAV 时长。OGG 检查头部与运行时播放，完整编码分析在音频阶段完善。

## 验收

```bash
python -m tools.asset_validator --report reports/assets.json
python -m tools.character_validator --report reports/characters.json
python -m tools.compile_story
python -m tools.compile_tests
python -m tools.validate
```

17 个管线测试使用隔离临时目录，覆盖重复导入、原生 UI 尺寸、缺输入/改 Prompt、透明度、版本、输出冲突、Manifest 失败回滚、首次失败清理、路径与解析后的软链接、损坏 PNG、错误资产类型及 Registry 绑定。检查不能证明脸部身份、情绪含义或语音自然度；这些仍由看图、试听与用户选择完成。

本轮 66 个游戏资产文件的 SHA-256 与 v0.4 一致，剧情文本和状态效果沿用原版本。v0.5 交付改进的生产工具、元数据和验收链路。最终平台执行结果见 STATUS.md。
