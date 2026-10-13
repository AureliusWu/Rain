# Rain ↔ Circuit 制作交流 · 2026-10-13

本轮由《雨停之前》的离线配音流程进入《回路》v1.2.0《回访》，再将多人物配音请求和声音演出的检查方法回传 Rain。两仓入口互相链接，具体实现各自适配原有引擎。

- [Rain 交流入口](https://github.com/AureliusWu/Rain/blob/main/docs/production/RAIN-CIRCUIT-BRIDGE.md)
- [Circuit 交流入口](https://github.com/AureliusWu/Circuit/blob/main/docs/production/RAIN-CIRCUIT-BRIDGE.md)
- 参考基线：Rain `36504476c7cde3fcc0a8052db3c8fa67962d5a39`；Circuit 剧情修订基线 `b8ce7eb4791a87f009b48c9bb6676a19ef0e8990`。

## 已吸收的内容

| 来源 | 本轮落地 | 对应文件 |
| --- | --- | --- |
| Rain 的 Qwen3-TTS 1.7B 离线录音 | Circuit 为9名人物制作32段关键对白；固定模型 revision、角色预设、指令、seed、源码片段与请求指纹 | Circuit `docs/audio/voice-plan.json`、`voice-provider.json`、`voice-manifest.json` |
| Rain 的源录音与响度处理 | 原始WAV、-20 LUFS目标的两遍归一化WAV、游戏MP3分别保留；每份文件SHA-256登记 | Circuit `tools/audio/generate_voice.py`；Rain MIT署名保留在 Circuit `third_party/Rain-MIT-LICENSE.txt` |
| Rain 的当前/历史重听与自动等待 | Circuit 添加暂停、继续、当前重听、已访问历史重听；面板与隐藏页面暂停；换节点撤销旧回调；加载失败允许继续阅读 | Circuit `src/game/recordedAudio.ts`、`tests/recorded-audio.test.cjs`、`tests/voice-browser.py` |
| Rain 的独立语音复核 | Circuit 全量解码、源文件哈希及无正文提示的独立 large-v3 ASR；逐项标出需要复听的片段 | Circuit `tools/audio/validate_media.py`、`check_asr.py`、`docs/audio/` |

Qwen模型使用同一固定revision；Rain既有录音用Serena与CPU float32，本轮Circuit采用多个预设和CPU bfloat16。dtype、生成指令及文本都进入请求指纹，不能把不同配置的缓存视作同一次生成。MP3是Circuit网页/桌面的交付格式，Rain继续使用其原有OGG与Ren'Py voice通道。

## 回传 Rain 的可用配方

| 内容 | 如何吸收 | 本轮交付 |
| --- | --- | --- |
| 多角色请求 | 从一名女主扩展到多角色时，把角色、预设、指令与所有台词绑定纳入同一个录音请求；修改任一项必须失效缓存 | Rain `tools/audio_process/voice_request.py` 与独立反例测试；只用于作者工具 |
| 同一录音多处出现 | 保存多个稳定台词ID，校验每处正文都含实际录制片段；重用一个成品文件，避免重复生成造成波形差异 | Circuit `v01-arrived`用于到场与回声，`v01-confirm`用于车内与封存盒；Rain请求配方支持多个line_ids |
| 声音作为演出线索 | 让重复句、迟来的应答与物件声跟剧情中能观察到的现象对齐；对日常重逢故事，可用停顿、杯子落桌、翻纸、雨声变化 | Circuit11项原创音效与节点绑定；Rain保持原题材，自行选择适用的声音动作 |
| 异步播放反例 | 播放未就绪时换节点、迟到的ended、拒绝自动播放、缺文件、隐藏页面、手动暂停、历史重听 | Circuit6项通道单位测试与浏览器真实媒体检查；Rain可在原生测试里采用相同触发条件 |
| 离线素材验收 | 完整缓存后断网，再解码全部游戏音频，核对角色字幕与实际节点；增加人物素材时同步alpha、尺寸与手机触控 | Circuit浏览器全量43个音频、32幅插画的离线检查；Rain按WASM包与原生资源布局编写对应检查 |

Rain本轮新增的是作者请求配方、测试及交流记录。该配方可检查未来多角色任务，不会自动生成录音或改写游戏台词。现有Serena录音、女主形象、原生引擎、存档身份与发行候选继续按原验收链管理。

## 移植时的字段对照

| 概念 | Rain现有来源 | Circuit本轮来源 |
| --- | --- | --- |
| 剧情绑定 | story.json的line_id / voice_id | chapter + node + clip id |
| 音色 | voice_provider_qwen.json的Serena | voice-plan每条speaker与character |
| 源音频 | assets_source中的原WAV与处理结果 | assets_source/audio/v1.2.0 |
| 游戏音频 | game/audio/voice/*.ogg | public/audio/voice/*.mp3 |
| 运行时播放 | Ren'Py voice / 自动与历史逻辑 | HTMLAudioElement队列 / 独立音量 |
| 验证 | 原生测试、资产/台词/声音校验 | 节点图、指纹、完整解码、浏览器/PWA |

不修改Rain、NetLove、Healing三仓已登记的共享契约和REUSE-MANIFEST；本文件是单独的双仓适配记录。共享的对象是制作方法与明确授权的代码配方。角色形象、剧情、私人参考小说和角色录音留在各自项目；Circuit新增素材标注生成或原创来源，不额外赋予第三方素材包许可。

自动解码、ASR与浏览器媒体事件能够发现技术问题，角色演技、方言和名称读法仍需真人试听。桌面编译、浏览器实跑和实体设备验收分别记录。
