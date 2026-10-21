# 全量素材 Web 分包

新增六幅原生 PNG CG 后，官方 WASM 的 game.zip 超过既有 50 MB 单文件预算。保留原始运行 PNG 与总离线预算，采用 Ren’Py 官方 progressive_download.txt 的首匹配规则，将 CG 放在独立资源文件中。PWA 构建仍枚举、摘要并原子缓存全部文件，未完成全部缓存前不宣称离线就绪；游戏读取 CG 时由本应用缓存响应。

官方规则：https://renpy.org/doc/html/web.html#progressive-downloading 。实际网页、断网重开、完整哈希和下载结果仍须通过本次 CI，规则变更本身不代表验收通过。
