# 冻结影片交接

## 当前完成状态（2026-10-18 07:47:53 UTC）

持久分段恢复已全部完成。成片：`evidence/descent_studio/final.mp4`（与工程`renders/final.mp4` SHA-256一致）。视频H.264/yuv420p、1920×1080、30fps、36.000s、1080帧；AAC音频48kHz、35.997s。全片音视频解码检查无错误，黑场候选为空；采样峰值−1.504506dBFS、RMS−20.501376dBFS。35.574–35.997s静音候选对应结尾有意静默。峰值是解码采样峰值，不是真峰值或LUFS。

实际查看了从最终编码MP4抽出的16帧contact（`final_contact.jpg`），覆盖开场、条件、赛跑、到达、回看/定格、生成圆、结尾。样本中未见编码新增的裁切或字幕碰撞。没有通过工具实时播放整片或完整听音，因此不宣称完成主观全片视听验收；这些限制不影响已通过的规格与全解码检查。

恢复脚本墙钟672.093s；其中后续9段渲染合计645.740s，全部成功操作合计657.540s。父任务渲染的0–2s段未计时，记录unavailable。此前中断留下11,534,480字节不可播放临时数据；精确浪费运行时间和所有worker完成帧数不可恢复，未估造数值。完整逐段记录见`recovery_state.json`与`timing_and_cost.json`。

冻结源码与`final/`备份hash一致。原来的“未完成”章节仅描述此前环境中断的历史状态，当前恢复渲染、拼接、事件导出、音画合成、全解码及contact均已完成。

## 以下为恢复前的历史交接记录

源目录：`examples/descent_studio/`。冻结源码备份：`evidence/descent_studio/final/`。父任务已接管编码恢复，本子代理不再启动渲染进程。

已完成：facts/direction/storyboard/review；film.js+physics.js+index.html；v1和v2源/静帧；final同刻静帧；8.8–13.2 Motion Strip；同刻对照图；真实浏览器字体测量；乱序det通过；音效事件表；36秒score.wav。

恢复前未完成：可播放全片MP4与局部MP4、最终编码规格报告；现均已完成。主观完整视频播放/听音仍未完成。失败render临时MP4均缺moov atom，不可复用。现场没有运行中的渲染，原session41256失效。

历史恢复使用以下分段方案。新克隆只有成片证据，没有忽略的renders短段；如需重算本样片，可先生成脚本要求的0–2秒首段，再运行脚本。不要把首段改成0–4秒，脚本会检查其必须为60帧。

```bash
python engine/render.py examples/descent_studio --clip 0 2 seg00
python examples/descent_studio/recover_render.py
```

常规重新生成仍可直接用`engine/render.py --jobs`；恢复脚本只用于本样片冻结源码，不是通用创作命令。它保留源码字节hash，换行或源码改变会拒绝复用旧片段；修改作品后请使用常规渲染命令。

物理值：θ=3.2339751452171397，a=.3006410009354001m；Tc=.5661431779960597s，Ts=.6797892979713827s；Lc=1.2580921822198052m，Ls=1.16619037896906m。竞赛片时8.8+6t；起步回看片时15.2+6t，并在t=.300s（片时17.0s）明确“定格比较”。

模型ID unknown，token/cost unavailable。原brief已逐字保存在brief.md，且明确指出升级臂得到的艺术方向提示构成prompt差异，不能将差异全归因于技能。两次图像主导返工后未继续美术修改。没有读取控制片源码/画面，无DeepSeek效果主张。

## 持久分段恢复已启动

父任务完成`seg00.mp4`（0–2s，60帧）后，样片专用脚本`examples/descent_studio/recover_render.py`已开始串行恢复。再次重启后可直接重新执行该脚本；只复用经ffprobe确认帧数、1920×1080、30fps、H.264/yuv420p正确的段。

```bash
python examples/descent_studio/recover_render.py > evidence/descent_studio/recovery_driver.log 2>&1
```

其余片段为2–6、6–10、10–14、14–18、18–22、22–26、26–30、30–34、34–36s，合计1080帧。脚本校验冻结源码hash，逐段记录实际耗时，拼接后导出事件并合成声音，完整解码检查，最后从编码MP4抽16帧生成contact。`recovery_state.json`是运行状态与每段计时的权威记录。先前失败渲染的精确耗时无法恢复，明确记为unknown，不估造“浪费分钟数”。
