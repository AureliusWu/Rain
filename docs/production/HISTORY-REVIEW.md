# v1.2.2 清除筛选生命周期修复 · 2026-10-15

Windows 38662368205 与 PWA 38662368211 均在清除筛选后出现 `None.scope`。根因为 `Function` 把查询函数的 `True` 返回给 Ren’Py，结束了历史菜单交互。专用清除动作现返回 `None`，清空关键词和人物，并保留当前面板 token；查询桥接仍返回布尔确认。新增四项原生函数回归及真实点击后的面板／token／筛选断言，同步严格素材哈希。

上一轮固定依赖完整验证通过：152项Python（10.724秒）、16条路线、全部作者检查、10项Node、15份共用文件、90项／224文件素材及60项／151文件导出。上一轮Chromium153的5项真实浏览器控件检查通过，覆盖中文IME预编辑／提交、退格／Enter、面板开关及迟到查询；原生桥接为模拟夹具，不能替代实际WASM／语音运行。本次环境恢复后快速重验7项历史专项、10项Node、生成一致性及90项／224文件素材全部通过；没有重装SDK／浏览器或把上一轮结果写成新执行。上一轮官方SDK解释器在`--version`时SIGBUS，未进入新的原生lint／交互或WASM构建。现有PR分支推送此前被自动审批拒绝，远程CI／公开PWA未更新；未合并、部署或发布。

---

# Rain v1.2.2 · 回看检索制作记录

2026-10-14。基线提交见 [HISTORY-VALIDATION.json](HISTORY-VALIDATION.json)。

原生历史可按关键词与人物筛选，并沿原记录重播语音。浏览器以原生 HTML 输入接收中文，只更新当前历史面板查询。多个关键词以空格分开并同时匹配。清除恢复已读记录，关闭/重开不移动剧情或改变存档。原有剧情、美术、录音、路线和存档身份沿用。

## 当前 CI 修复 · 2026-10-14

[Windows CI 38579109574](https://github.com/AureliusWu/Rain/actions/runs/38579109574) 和 [PWA CI 38579109569](https://github.com/AureliusWu/Rain/actions/runs/38579109569) 均已通过 148 项 Python 与作者校验，随后在共用素材检查处退出：最终输入与字体修订后，`REUSABLE-ASSETS.json` 中 `tools/build/web.py` 的 SHA-256 未同步。遍历全部引用又发现 `client.js`、`history_search.rpy` 的相同问题，三处现在按实际文件字节同步。校验器和失败门禁保持原样。

已有 OFL 浏览器字体、许可和中文覆盖再次核对；921 个当前需要的汉字缺字为 0，字体二进制沿用。保留原生成指纹，另记录当前输入的覆盖检查；把既有字体生成器及该记录补入可导出配方。未重新绘图、录音或改动玩家运行代码。

本批本地实际完成 148 项 Python（11.214 秒）、16 条状态路线、全部作者校验、10 项 Node 测试、15 份共享文件及 90 项／224 文件素材校验；共用包导出为 60 项／151 文件。平台验收没有据此改为通过：此环境的 SDK 解释器在启动前以 SIGBUS 退出，未完成本批原生 lint／交互或官方 WASM 构建；新的 Windows、PWA、公开网页与真人试听继续待独立证据。机器记录见 [HISTORY-VALIDATION.json](HISTORY-VALIDATION.json) 的 `ciRepair`。

## 实际本地验证

以下为先前制作批次记录；本批结果和限制以上面的 CI 修复记录为准。

145 项 Python、16 条状态路线、素材/音频/生成一致性与 Ren’Py 8.5.3 lint 通过。官方 WASM 生产 PWA 14 项检查通过，含真实中文输入、检索清除、原位置、离线重开、原生存档导出/导入和缓存更新边界。生产 TypeScript/Vite 或官方 WASM 构建通过。浏览器使用 Chromium 140.0.7339.186；真实 Windows 与公开 PWA 的执行单独记录。

## 跨作品复用

[回看检索方法](READ-HISTORY.md) 在四仓保持同字节。NetLove、Healing、Circuit 的 history.ts、RecordSearch.tsx 与样式也保持同字节；三个制作契约仓库的素材目录纳入检索配方及许可。Rain 保留 Ren’Py 8.5.3 和原生 _history_list、语音与存档。

## 当前平台状态

本地机器验证完成。待当前提交的 GitHub CI、Windows 及公开 PWA 执行后归档对应运行网址；旧版平台成功证据不用于证明新版。真人试听、阅读计时、普通设备体验沿用用户统一后续安排。

## 输入修复检查点 · 2026-10-14

[Windows 首轮 CI](https://github.com/AureliusWu/Rain/actions/runs/38506767764) 的 7 个真实前缀用例中 6 个通过，历史检索用例在 `type "不存在的记录XYZ"` 处因物理 keysym 不认识“ 不 ”而退出。生成器改用 SDL TEXTINPUT 事件，事件进入实际聚焦的 Ren'Py Input；保留中文匹配与空结果，增加退格、Enter、ahls、80 字限制、原索引重播、筛选停声和旧面板迟到查询检查。

原生 InputValue 与 HTML 输入现在共用 `rain_set_history_query`，严格接收字符串和当前 UUID 面板 token；UUID 不消耗剧情随机数。Web 轮询记录发起时的空闲状态和最新已发送值，防止查询写入与旧轮询返回交错时丢字。官方 Web 输出先在独立临时目录完成，再核验 WASM、ZIP 中央目录与逐文件 CRC；失败保留此前完整输出并拒绝写入 built 成功报告。

修复检查点的 148 项 Python、16 状态路线、作者校验、生成一致性与 Ren'Py 8.5.3 Linux lint 通过。新版 Linux 原生前缀和官方 WASM 的输入/声音专项仍在执行；这批结果不代替 Windows 源码、独立 EXE、旧档升级与公开 PWA 验收。

2026-10-15 最终补验：恢复后的 production client.js 在 Chromium 153.0.8010.0 重新通过5项输入控件检查（真实中文IME、面板开关与迟到查询）。原生桥接仍使用模拟对象；此结果不替代真实WASM或Windows执行。
