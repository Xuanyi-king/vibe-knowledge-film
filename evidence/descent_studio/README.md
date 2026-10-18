# 升级工作流实验臂证据

## 当前完成状态（2026-10-18 07:47:53 UTC）

持久分段恢复已全部完成。成片：`evidence/descent_studio/final.mp4`（与工程`renders/final.mp4` SHA-256一致）。视频H.264/yuv420p、1920×1080、30fps、36.000s、1080帧；AAC音频48kHz、35.997s。全片音视频解码检查无错误，黑场候选为空；采样峰值−1.504506dBFS、RMS−20.501376dBFS。35.574–35.997s静音候选对应结尾有意静默。峰值是解码采样峰值，不是真峰值或LUFS。

实际查看了从最终编码MP4抽出的16帧contact（`final_contact.jpg`），覆盖开场、条件、赛跑、到达、回看/定格、生成圆、结尾。样本中未见编码新增的裁切或字幕碰撞。没有通过工具实时播放整片或完整听音，因此不宣称完成主观全片视听验收；这些限制不影响已通过的规格与全解码检查。

恢复脚本墙钟672.093s；其中后续9段渲染合计645.740s，全部成功操作合计657.540s。父任务渲染的0–2s段未计时，记录unavailable。此前中断留下11,534,480字节不可播放临时数据；精确浪费运行时间和所有worker完成帧数不可恢复，未估造数值。完整逐段记录见`recovery_state.json`与`timing_and_cost.json`。

冻结源码与`final/`备份hash一致。原来的“未完成”章节仅描述此前环境中断的历史状态，当前恢复渲染、拼接、事件导出、音画合成、全解码及contact均已完成。


- `v1/`：首版源码与真实首轮静帧（冻结，未覆盖）。
- `v2/`：第一次图像返工后源码与静帧。
- `final/`：第二次返工后源码、同刻静帧与真实Motion Strip。
- 原始影片和有声影片位于 `../../examples/descent_studio/renders/`。
- 审查记录位于 `../../examples/descent_studio/review.md`。
- `interrupted_full_render.log`保留失败并行渲染；实际完成耗时见`recovery_state.json`、`timing_and_cost.json`，编码检查见`final_media_report.json`。

这些是同一模型同题的一次独立创作案例，不支持模型家族总体能力或DeepSeek效果的结论。源码和关键帧保存在未被review/忽略规则覆盖的evidence目录，供父任务独立审查。

**历史状态：全片编码曾遭环境二次重启中断；现已恢复并交付raw/final MP4。** 已保留失败日志及临时文件ffprobe结果，见`interrupted_render_status.json`。父任务安排持久分段恢复，步骤与仍未主观验收项见`RECOVERY.md`。`full_render_time.json`未生成，不能引用其为完成耗时。
