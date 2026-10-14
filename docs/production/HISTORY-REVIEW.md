# Rain v1.2.2 · 回看检索制作记录

2026-10-14。基线提交见 [HISTORY-VALIDATION.json](HISTORY-VALIDATION.json)。

原生历史可按关键词与人物筛选，并沿原记录重播语音。浏览器以原生 HTML 输入接收中文，只更新当前历史面板查询。多个关键词以空格分开并同时匹配。清除恢复已读记录，关闭/重开不移动剧情或改变存档。原有剧情、美术、录音、路线和存档身份沿用。

## 实际本地验证

145 项 Python、16 条状态路线、素材/音频/生成一致性与 Ren’Py 8.5.3 lint 通过。官方 WASM 生产 PWA 14 项检查通过，含真实中文输入、检索清除、原位置、离线重开、原生存档导出/导入和缓存更新边界。生产 TypeScript/Vite 或官方 WASM 构建通过。浏览器使用 Chromium 140.0.7339.186；真实 Windows 与公开 PWA 的执行单独记录。

## 跨作品复用

[回看检索方法](READ-HISTORY.md) 在四仓保持同字节。NetLove、Healing、Circuit 的 history.ts、RecordSearch.tsx 与样式也保持同字节；三个制作契约仓库的素材目录纳入检索配方及许可。Rain 保留 Ren’Py 8.5.3 和原生 _history_list、语音与存档。

## 当前平台状态

本地机器验证完成。待当前提交的 GitHub CI、Windows 及公开 PWA 执行后归档对应运行网址；旧版平台成功证据不用于证明新版。真人试听、阅读计时、普通设备体验沿用用户统一后续安排。

## 输入修复检查点 · 2026-10-14

[Windows 首轮 CI](https://github.com/AureliusWu/Rain/actions/runs/38506767764) 的 7 个真实前缀用例中 6 个通过，历史检索用例在 `type "不存在的记录XYZ"` 处因物理 keysym 不认识“ 不 ”而退出。生成器改用 SDL TEXTINPUT 事件，事件进入实际聚焦的 Ren'Py Input；保留中文匹配与空结果，增加退格、Enter、ahls、80 字限制、原索引重播、筛选停声和旧面板迟到查询检查。

原生 InputValue 与 HTML 输入现在共用 `rain_set_history_query`，严格接收字符串和当前 UUID 面板 token；UUID 不消耗剧情随机数。Web 轮询记录发起时的空闲状态和最新已发送值，防止查询写入与旧轮询返回交错时丢字。官方 Web 输出先在独立临时目录完成，再核验 WASM、ZIP 中央目录与逐文件 CRC；失败保留此前完整输出并拒绝写入 built 成功报告。

修复检查点的 148 项 Python、16 状态路线、作者校验、生成一致性与 Ren'Py 8.5.3 Linux lint 通过。新版 Linux 原生前缀和官方 WASM 的输入/声音专项仍在执行；这批结果不代替 Windows 源码、独立 EXE、旧档升级与公开 PWA 验收。
