# 验证与发布门槛

## Python

```bash
python -m unittest discover -s tests -v
python -m tools.route_validator --report reports/routes.json
python -m tools.story_lint
python -m tools.asset_validator
python -m tools.compile_story --check
python -m tools.compile_tests --check
```

路线校验遍历状态路径，检查缺失目标、死节点、不可达结局、循环和全部选择。负面测试使用损坏图验证检查器确实拒绝错误。资产验证 SHA-256、路径、来源、许可证、Prompt、表情、语音文本绑定。

## Ren'Py 实际运行

```bash
SDK/renpy.sh . lint --error-code --all-problems
SDK/renpy.sh . test global --report-detailed --overwrite_screenshots
SDK/renpy.sh launcher distribute . --package windows --destination dist
```

Linux 无桌面时使用 Xvfb 和软件渲染。测试实际点击开始、选择、保存槽位、读取槽位、确认、历史、设置和返回主菜单。每条完整路线都检查结局与变量，保存/读取必须恢复选择之前的状态，新游戏必须清零。

## Windows

GitHub Actions 在 Windows runner 上运行原生 Ren'Py，测试和构建后从 ZIP 解压的分发程序再次运行同一测试集合。开发 testcases 在分发包中排除；包测试时仅临时注入测试脚本，不改变发行版。

普通用户验收：解压 ZIP、双击 EXE、无需 Python/引擎安装；检查文字、语音、音乐、窗口/全屏、存读档、两种结局和重新开始。

## 报告原则

只记录已实际完成的检查；CI 配置存在不等于 CI 已通过；跨构建不等于 Windows 已启动；预计阅读时长不等于真人计时；候选美术不等于用户最终选定。
