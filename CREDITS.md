# Credits / 资产来源

- 项目创意与最终决策：AureliusWu。
- 编程、文稿和流程：AI 辅助制作，详见 Git 历史。
- 引擎与默认 GUI：Ren'Py 8.5.3，https://www.renpy.org/ ，详见 licenses/RENPY.txt。未使用 The Question 的角色、美术或音乐。
- 中文字体：SourceHanSansLite，Ren'Py SDK 随附；Adobe Source Han Sans，SIL OFL 1.1，详见 licenses/SourceHanSans-OFL.txt。
- v0.1 人物、背景、图标、对话框：项目内程序生成的临时资产。
- BGM 与雨声：项目内原创程序合成，未使用第三方录音或现成曲目。
- 图片、音频及字体的逐文件出处、版本与哈希：game/data/asset_manifest.json。
- v0.2 背景、许澄基础立绘与旧信 CG：OpenAI 内置图像生成工具。工具未暴露具体模型标识；使用原创 Prompt 和本项目生成的参考图，没有引用第三方人物或现成作品。源图及 Prompt 保留在 assets_source 与 prompts。人物透明版由基础立绘编辑生成。
- v0.2 蓝色菜单、滑块与选择标记：原创程序生成图元，tools/image_process/create_ui.py；其他控件沿用 Ren'Py 默认 GUI。
- 关键语音：Kokoro-82M v1.1-zh，zf_001，speed 0.95；模型 Apache-2.0，许可证见 licenses/Kokoro-model-Apache-2.0.txt。[官方模型](https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh)；[ONNX 导出](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1)。开发工具 kokoro-onnx 使用 MIT，Misaki 中文前处理使用 Apache-2.0。模型和推理依赖不随游戏分发。
- 语音为项目台词的本地合成，未克隆现实人物。6 句合计 19.759 秒。ONNX Runtime 在导入前设置 ORT_DISABLE_TELEMETRY=1，并关闭事件 API；游戏仅播放离线 OGG。
- 全部视觉和声音是本轮可试玩候选；最终美术与声音选择仍待用户审阅。MIT 适用于原创代码及程序图元，第三方许可保留；不对 AI 输出主张独占版权。
