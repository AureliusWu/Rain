# Credits / 资产来源

- 项目创意与最终决策：AureliusWu。
- 编程、文稿和流程：AI 辅助制作，详见 Git 历史。
- 引擎与默认 GUI：Ren'Py 8.5.3，https://www.renpy.org/ ，详见 licenses/RENPY.txt。未使用 The Question 的角色、美术或音乐。
- 中文字体：SourceHanSansLite，Ren'Py SDK 随附；Adobe Source Han Sans，SIL OFL 1.1，详见 licenses/SourceHanSans-OFL.txt。
- v0.1 人物、背景、图标、对话框：项目内程序生成的临时资产。
- BGM、雨声及纸张／消息音效：项目内原创程序合成，AI 辅助谱曲与代码实现，未使用第三方录音或现成曲目；未冒称为音乐生成模型输出。
- 图片、音频及字体的逐文件出处、版本与哈希：game/data/asset_manifest.json。
- v0.2 背景、许澄基础立绘与旧信 CG：OpenAI 内置图像生成工具。工具未暴露具体模型标识；使用原创 Prompt 和本项目生成的参考图，没有引用第三方人物或现成作品。源图及 Prompt 保留在 assets_source 与 prompts。人物透明版由基础立绘编辑生成。
- v0.3 六张表情变体：同一 normal 基础图通过内置图像生成工具分别做面部编辑；未使用第三方角色参考。固定组件、精确请求、输入与输出哈希随仓库保留；正常、微笑、开心、难过、生气、惊讶、害羞共七种。
- v0.2 蓝色菜单、滑块与选择标记：原创程序生成图元，tools/image_process/create_ui.py；其他控件沿用 Ren'Py 默认 GUI。
- 关键语音：Kokoro-82M v1.1-zh，zf_001，speed 0.95；模型 Apache-2.0，许可证见 licenses/Kokoro-model-Apache-2.0.txt。[官方模型](https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh)；[ONNX 导出](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1)。开发工具 kokoro-onnx 使用 MIT，Misaki 中文前处理使用 Apache-2.0。模型和推理依赖不随游戏分发。
- 语音为项目台词的本地合成，未克隆现实人物。v0.6 共 17 句、58.048 秒，保留 v0.2 的六句录音。ONNX Runtime 在导入前设置 ORT_DISABLE_TELEMETRY=1，并关闭事件 API；游戏仅播放离线 OGG。
- 全部视觉和声音是本轮可试玩候选；最终美术与声音选择仍待用户审阅。MIT 适用于原创代码及程序图元，第三方许可保留；不对 AI 输出主张独占版权。

- v0.5 生产流程：版本化请求索引 prompts/registry.json；图片、语音与场景通过 ID、路径及 SHA-256 绑定。新增导入配方、像素元数据与复用/参考来源，原有图片和音频内容沿用前阶段。
- v0.6 程序音频的原创音符、参数与制作方向：prompts/audio/soundtrack_v1.json；渲染工具 tools/audio_process/render_soundtrack.py。新增配音请求：prompts/voice/heroine_v2.md；声音、语速、模型及前处理沿用原配置。信号检查由 SoundFile 0.14.0 完成，仅为开发依赖，不进入分发包。
- v0.7 三张场景背景：站外雨棚、雨停后的出口、街角小店，使用 OpenAI 内置 imagegen 和本项目生成的旧站背景作画风参考；模型标识未暴露。出口底图另做一次店招去字编辑，输入、完整请求、最终源 PNG 与导入配方保存在 assets_source/background 与 prompts/background。游戏使用 1280×720 输出；旧信 CG、七种角色表情与 17 句关键录音保留。全部仍为待最终选择的视觉候选，没有第三方参考图。

- v0.9 原生 1080p：由既有 1672×941 背景 / CG、1024×1536 透明立绘重建，保留原始 Prompt；背景 / CG 约 1.15 倍重采样。20 蓝色图元直接在目标尺寸重画，其他原始 GUI 按明确配方导入。60 图片均有可复现源、许可与哈希，见 docs/DISPLAY_V09.md。
