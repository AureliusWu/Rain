# v0.7 场景候选审阅

更新时间：2026-10-05（北京时间）。本次增加三张背景，旧站台、旧信 CG 和七种透明表情保留；没有为凑资产数量新增 CG。当前原生 GUI 1280×720，1080p 适配留在 v0.9。

| 背景 | 对应场景 | 已查看的图像事实 |
|---|---|---|
| station_exit_covered | 第三章 waiting、第四章、第五章 departure | 镜头在站外；玻璃门、连着建筑的雨棚、长椅与干地可辨，左侧为潮湿街道；无人物和可读文字 |
| station_exit_after_rain | shared / separate、Normal | 同类旧站出口在右侧、街角小店在左侧；夜色、湿地和檐下等车位置成立；编辑后店招无可读字 |
| nearby_cafe | True 小店尾声 | 普通木桌、两杯水、饼干与纸巾；窗外夜街与站外背景一致；右侧有立绘位置；没有信或照片烘焙进背景 |

已直接查看三个 1280×720 游戏 PNG，按剧情地点和时间审核布局、人物预留区域和无文字约束；这不代替实际游戏截图。后续 Windows 原生截图名称为 bg-exit-covered、bg-exit-after-rain、bg-nearby-cafe、bg-s05_shared_path、bg-s05_separate_path，全部作为独立包必需证据。

源图为四个 PNG（三张最终源图及一次去店招编辑的输入）。精确生成与编辑请求保存在 prompts/background；Manifest 保存源、参考、Prompt、源文件及像素哈希、许可与配方。图片处理只做既有 fit_1280x720_v1 导入；33 个配方必须可复现，60 个游戏 PNG 必须完整解码。

素材的 approved=true 仅表示 Agent 允许接入候选，status=candidate_user_review 与 approval_scope 明确最终选择仍由用户决定。未把工具输出标成用户定案；模型标识未暴露。

完整候选 CI 37273842254 已通过；源码与独立包共 82 张 PNG 完整解码。已直接查看五张新背景 / 两条离场首句截图，以及菜单、选择、设置和两个结局，共 10 张独立包画面：人物位置与透明边缘正常，中文可读，Normal 正式分别后无人物，True 小店显示 smile。截图窗口为 922×518，逻辑 GUI 仍为 1280×720。

实际截图审阅、哈希与完整证据见 [ALPHA_ACCEPTANCE_V07](ALPHA_ACCEPTANCE_V07.md)。真人视觉选择、1080p 构图与普通电脑 DPI 检查尚待后续。主菜单“可玩样片”称呼列为 v0.9 P2 文案，不据此改动已经验收的候选 ZIP。
