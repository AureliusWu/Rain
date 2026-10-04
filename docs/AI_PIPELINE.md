# 小型 AI 生产流程

1. 固定世界、角色 Bible 与本场景目标。
2. 一次起草一个场景；审阅对白后进入结构化 JSON。
3. Prompt 保存在 prompts，固定身份和画风，仅改变必要场景或表情。
4. AI 图像生成后保留源图；人工/Agent 视觉检查后做确定性导入。
5. 使用 `tools/image_process/import_asset.py` 做尺寸、格式、元数据与 SHA-256 更新。
6. 关键语音以稳定台词 ID 生成，文本变化后必须重新生成；不按顺序号码绑定。
7. `python -m tools.compile_story` 输出引擎标准脚本，`python -m tools.compile_tests` 输出实际路线交互测试。
8. 先校验剧情、资产和文本，再做 Ren'Py lint、交互测试、Windows 构建。

## 数据边界

JSON 只保存数据；工具不执行来自 JSON 的任意 Python 表达式。条件仅允许固定变量的 eq/gte；数值效果是 delta，bool 是赋值。

`asset_manifest.json`：id/type/file/source/license/version/prompt/sha256/status。`voice_manifest.json`：voice_id/line_id/character/text/emotion/model/voice/file。

## 人与 AI

AI 辅助起草、编程、图像与音频生产。工程校验保证结构和文件完整。最终审美、重大剧情和角色方向由用户决定；自动化不能保证角色动机或视觉质量。

## v0.2 已实际使用

逐场景剧情起草与审阅 → 8 场景 JSON → 生成标准 Ren'Py 脚本；固定角色 Prompt → 基础立绘 → 同图透明编辑 → Pillow 尺寸导入；站台背景 → 参考角色与地点生成 CG；文字绑定 → Kokoro 本地关键语音 → FFmpeg OGG；图元生成 → 原生 GUI；路线遍历 → 真实鼠标交互测试 → Windows EXE 打包与启动 → Release。

本轮发现并修复：模型透明素材的 alpha 最大值为 254，不能机械要求恰好 255；界面模板含无关游戏署名；截图库必须等场景实际渲染；配音推理库默认启用遥测，必须在初始化前显式关闭。Prompt、源图、声音配置和最终文件均随 Git 追踪。

## v0.3 已实际使用

同一基础图 + 版本化固定组件 + 单一表情方向 → 六次独立内置 imagegen 面部编辑 → 视觉检查 → 保留源图 → 确定性导入 → 记录原始参考图、组件、精确 Prompt 和文件哈希 → 20 处台词绑定 → 七种表情几何检查 → 实际剧情截图与表情存读档测试。没有接入新的 Agent 框架或运行时模型。

重做某张表情时保留旧版本，并使用同一基准图；导入示例：

```bash
python -m tools.image_process.import_asset --source assets_source/character/heroine_smile_v1.png --id heroine_smile --type sprite --output characters/heroine_smile_v1.png --prompt prompts/character/heroine_smile_v1.md --expression smile --version 1 --reference-source assets_source/character/heroine_clean_v2.png --prompt-components prompts/character/heroine_expressions_v1.json
python -m tools.character_validator --report reports/characters.json
```

修改已追踪文件后重新更新 Manifest 哈希、编译剧情并完整验证。几何指标可以发现位置和轮廓漂移，无法证明面部身份或剧情情绪正确。
