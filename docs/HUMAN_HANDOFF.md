# 真人后续统一操作清单

依据用户指示：“你专心做好你能做的部分，所有需要真人操作的后续我会统一操作。”

当前对象 **v1.2.2 双平台正式版**，沿用 17 句 Qwen / Serena 录音与 v1 存档身份，新增历史关键词 / 人物筛选与中文输入。

游戏与 tag `15d87ef4455b95feb6069e044a1d3a6456f75e0c`；[Windows CI 38828604885](https://github.com/AureliusWu/Rain/actions/runs/38828604885) 与 [PWA CI attempt 2](https://github.com/AureliusWu/Rain/actions/runs/38828604848/attempts/2) 完整通过。Windows ZIP **56,170,913 字节**，SHA-256 `f5a482cf5a36ec2dfda047d1d3d67610d4c221c37e62b6aaac318ae417a176f3`。

[正式 Windows 下载](https://github.com/AureliusWu/Rain/releases/download/v1.2.2/BeforeTheRainStops-1.2.2-win.zip) · [在线 PWA](https://aureliuswu.github.io/Rain/) · [正式发行](https://github.com/AureliusWu/Rain/releases/tag/v1.2.2)。v1.2.2 已于 **2026-10-16T06:34:32Z** 正式公开；[发布 CI 38861929614](https://github.com/AureliusWu/Rain/actions/runs/38861929614) 成功，四个公开资产的实际匿名下载、完整 SHA-256 / 字节数、ZIP CRC 和当前 PWA worker 字节均已回读核对。[完整证据](production/PUBLISHED-v1.2.2.json) 明确分开原生 / 浏览器机器验证与下面的真人待验。

所有真人项保持 pending；包或哈希变化时重新绑定。

| 真人事项 | 操作与记录 | 状态 |
|---|---|---|
| 普通 Windows 离线试玩 | 完整解压原始 ZIP 到可写目录，断网双击 EXE；检查两结局、保存退出再读、回退改选、历史关键词 / 人物筛选 / 清除 / 重开、筛选后语音重播、当前台词重听、鉴赏解锁计数 / 当前曲名及状态 / 全图查看 / 音乐播放、暂停、继续与停止与离页停止、快进、自动、音量及全屏 | 待用户统一操作 |
| 显示与中文路径 | 记录系统、显卡、分辨率与 100% / 150% 缩放；中文目录下检查菜单、对白、选择、历史、存读档、结局和鉴赏页无裁切 | 待用户统一操作 |
| 关键配音与混音试听 | 逐句听 17 句新语音，检查错读 / 缺字 / 断句 / 情绪 / 音量；同时检查三首音乐、两种雨声、两种音效及循环淡入淡出 | 待用户统一操作 |
| 最终创作定案与冻结 | 审阅主题、成年女主许澄、七表情、背景 / CG、音色、重大剧情和两个结局；记录保留 / 修改项及冻结日期 | 待用户统一操作 |
| 两结局阅读计时 | Normal / True 各正常读一次，记录四次选择、文字 / 语音 / 自动设置、开始结束与离开暂停；目标有效阅读 30–60 分钟 | 待用户统一操作 |

统一回报：版本 / commit / ZIP SHA-256；系统与显示 / 声音设备；路线与选择；有效阅读分钟；各项通过或具体问题；对应台词 / 场景 / 操作和截图 / 录音；创作保留或修改意见。可直接用自然语言回报，无需自行修改 JSON。

`review/V111_HUMAN_ACCEPTANCE.json` 保留五组 pending、证据空白及计时 null。工程侧收到真实结果后修复缺陷、补齐记录与内容冻结；不会将 ASR 或 Windows runner 的 dummy 音频称为真人试听通过。正式发布已按既有用户授权完成并回读核验，未将 pending 人验表改为通过。现有 `review/V111_HUMAN_ACCEPTANCE.json` 继续保留其历史版本身份；v1.2.2 的五组待验以本清单、发布授权与最终发布记录明确绑定，不把旧表结果移作新版通过证据。物理设备 / PWA 安装、系统锁屏与真实声音设备体验也未由浏览器自动化代替。
