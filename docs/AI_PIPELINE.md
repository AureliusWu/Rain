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
