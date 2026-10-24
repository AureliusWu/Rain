# 原创纯音乐制作源

本批由作者编写旋律、和声、配器与 MIDI，以 GeneralUser GS 2.0.3 乐器库离线渲染；没有演唱、语音或合唱音色，也未调用 Runway。JSON/MIDI、作曲脚本、渲染器和母带脚本随本目录留存。两首属于当前作品，完整 48kHz/24bit 母带与试听另见已交付的《四作原创纯音乐完整制作包.zip》。

乐器库：S. Christian Collins / GeneralUser GS，仓库 https://github.com/mrbumpy409/GeneralUser-GS ，固定提交 684543d5e5efaef08d02be50dcda8d552478fa60；GeneralUser-GS.sf2 SHA-256 为 9575028c7a1f589f5770fccc8cff2734566af40cd26ed836944e9a5152688cfe。保留原许可，不将代码 MIT 许可证套用到乐器库。完整许可随玩家包分发。

复现：在本目录 npm ci；将该固定字节的 SF2 放到 generaluser/GeneralUser-GS.sf2，安装 requirements.txt 与 FFmpeg。对 output/scores 中各 JSON 执行 node render.cjs <score.json> <bank.sf2> loop <raw.f32>。循环按原速度渲染三个连续周期，取中间 32 小节，gridBeat 负责选择跨边界的人性化音符。master.py 的 prepare(raw, stem, True) 应用 EQ 和约 -21 LUFS 线性增益，encode() 写入 OGG Vorbis q5。中间文件位于 raw/，完成品位于 output/loops/。完整重新渲染可运行 python master.py。开发依赖不进入玩家运行环境。

循环为完整文件范围，无首尾静音。采样量化误差小于 1ms；解码帧数、峰值、响度与接缝测量见项目接入清单。听感审阅继续 pending。

Ren’Py 原生制作清单另留 48kHz 双声道 16bit PCM FLAC 循环参考。游戏 OGG 为原先验证过的相同字节；24bit 完整母带仍在已交付制作包。
