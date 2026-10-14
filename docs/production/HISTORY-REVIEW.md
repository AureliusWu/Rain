# Rain v1.2.2 · 回看检索制作记录

2026-10-14。基线提交见 [HISTORY-VALIDATION.json](HISTORY-VALIDATION.json)。

原生历史可按关键词与人物筛选，并沿原记录重播语音。浏览器以原生 HTML 输入接收中文，只更新当前历史面板查询。多个关键词以空格分开并同时匹配。清除恢复已读记录，关闭/重开不移动剧情或改变存档。原有剧情、美术、录音、路线和存档身份沿用。

## 实际本地验证

145 项 Python、16 条状态路线、素材/音频/生成一致性与 Ren’Py 8.5.3 lint 通过。官方 WASM 生产 PWA 14 项检查通过，含真实中文输入、检索清除、原位置、离线重开、原生存档导出/导入和缓存更新边界。生产 TypeScript/Vite 或官方 WASM 构建通过。浏览器使用 Chromium 140.0.7339.186；真实 Windows 与公开 PWA 的执行单独记录。

## 跨作品复用

[回看检索方法](READ-HISTORY.md) 在四仓保持同字节。NetLove、Healing、Circuit 的 history.ts、RecordSearch.tsx 与样式也保持同字节；三个制作契约仓库的素材目录纳入检索配方及许可。Rain 保留 Ren’Py 8.5.3 和原生 _history_list、语音与存档。

## 当前平台状态

本地机器验证完成。待当前提交的 GitHub CI、Windows 及公开 PWA 执行后归档对应运行网址；旧版平台成功证据不用于证明新版。真人试听、阅读计时、普通设备体验沿用用户统一后续安排。
