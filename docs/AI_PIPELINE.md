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

## v0.4 已实际使用

章节目标 → 26 节点场景表 → 17 次独立 Scene Draft → 逐场审阅知识、物品与立绘姿态 → 保存逐场 Prompt、SHA-256 与候选审阅状态 → JSON 编译章节卡和原生路线 → 自动枚举 16 条状态路径 → 为每条生成实际选择交互与完整 visited_scenes 断言。

校验器新增章节与 HH:MM 顺序、状态边界、全局选择 ID、无效效果、独立后果场景、空稿、条件 fallback、Prompt 哈希和版本一致性。曾发现 story.json 版本停在旧版本，现与 VERSION/config.version 联合校验。机械时间检查只核验声明，内容矛盾仍需编辑审阅。

## v0.5 已实际使用

全部版本化请求 → Registry 固定 ID 与哈希 → 场景/语音/资产三类绑定 → 源图和参考图预检 → 内存变换与 dry-run → PNG 与 Manifest 替换及失败回滚 → 相同输入重复导入 → 30 个图片配方内存复现 → 完整 PNG 解码、像素哈希和类型校验 → 现有原生交互及独立 EXE 验收。

UI 导入按原尺寸，背景式菜单需要显式配方。基础音频补齐源 WAV，主菜单复用和 CG 两个输入参考可追踪。现有 66 个游戏文件 SHA-256 未改变。不同 PNG 压缩器可能产生不同文件字节，相同显示像素时保持已经发布的文件。工具不保证重新生成相同 AI 输出，只复现固定源资产的导入。CLI 操作、元数据结构与能力边界见 ASSET_PIPELINE_V05.md。

## v0.6 已实际使用

逐场选择关键台词 → 固定声音／语速与版本化请求 → 模型缓存 SHA-256 预检 → 11 句离线 TTS → 源 WAV 与游戏 OGG 完整解码 → 请求指纹与信号元数据 → 保留六句旧录音 → 原生 voice 接入。原创音符、声音参数与固定种子 → 五个程序音频 → 已有剧情换曲／音效／雨声淡出 → 原生交互回归。

普通 CI 只用 SoundFile 解码和验证，模型不进入 CI 或玩家包；检测声音完整性、信号和配置缓存，发音、演绎与音乐审美仍需用户试听。制作工具重复执行验证既有文件并返回零变更，实际使用与边界见 AUDIO_V06.md。
