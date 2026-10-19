# 《另一种你》制作状态与保留证据

按用户最新要求停止原创作品开发，本轮以Skill优化收尾，不再新增镜头、重渲染、发行转码或继续艺术打磨。[源码、事实与112秒分镜](../../examples/mirror/README.md)保留，不将此工程记作完成主观验收的作品。

暂停前已生成完整技术导出：本地`examples/mirror/renders/final.mp4`，1920×1080、30fps、112秒、3360帧、H.264/AAC48kHz，22,823,874字节。新MP4和分轨留在工作区，未重复加入Git或宣称存在公开下载；复现命令见工程及Windows文档。[导出身份与范围](export-record.json)保存SHA256，原有公开影片不删除。

已完成：真实首版拼图/翻转与相机动作条检查；修复标签重叠、投影变化不显眼及镜框拉伸人像。首版[v1.jpg](v1.jpg)保留，属于早期画面，不是最终编码截图。独立审查只返回一项重要问题后中断，范围见[记录](../director-story/independent-review.md)。拉伸问题有实际Canvas调用的RED→GREEN回归。

技术报告分层保留：

- [生产汇总](production.json)：`technical_complete_needs_subjective_review`，不是电影质量通过。
- [编码音频同步](sync.json)：106个窗口无失败；源混音对最终AAC的对齐，不证明物体动作同步或听感。
- [声明视觉条件](visual-sync.json)：15项实际帧条件通过，涉及同图翻转、真实投影与条件控制；不覆盖未声明动作或通用语义。所引PNG留于本地`examples/mirror/review/visual`，没有冒充已随报告公开。
- [母带](mastering.json)及[媒体检查](media.json)：无媒体错误；实测−30.11 LUFS、−3.54 dBTP、LRA20.2。低响度与多段静音候选并不证明舒适音乐，尚需听审判断；未为收尾再调音乐。
- [本地测试](../director-story/tests-linux.log)：70项通过、282.208秒、无跳过；[原生Linux/Windows CI](../director-story/ci.json)明确可选跳过与首次Linux超时。

未完成：最终编码连续观看、手机尺寸可读性验收、完整主观听音、Windows完整本片导出及普通模型同条件创作实验。参考片音视频不复制进本片；素材来源与许可见工程assets。技术链运行不等于导演方法提升了普通模型创作能力。

## 本轮只读核查与长期保留

文件仍可读取，SHA256为`219bdcfc9fb7c6347190970ca2a7e0fa2de9d0fc10a16a41ba891051fc18f058`，与归档相同。只有当前工作区副本；Git不包含最终MP4、分轨或生成的音符bank，工作区也不能当作长期备份。没有上传Release/网盘，没有处理新第三方素材或覆盖原片。大文件持久化须用户另行指定位置并授权。

如自行长期保留，可在当前仓库根目录执行以下PowerShell命令；D盘位置由保管者选择，**此处提供方法，未代用户执行**：

```powershell
$archive = 'D:\VK-archive\mirror-7403640'
New-Item -ItemType Directory -ErrorAction Stop $archive | Out-Null # 选新目录，已存在则停止
# 原源码快照包含当时引擎与许可；不混用本轮更新后的引擎。
git archive --format=zip --output="$archive\source-7403640.zip" 74036406fc20e209722bc8076a81b907a1f76f7b
if ($LASTEXITCODE -ne 0) { throw 'source archive failed' }
# 含原视频、侧车、分轨、事件、报告及生成bank，均不修改源工程。
Copy-Item examples\mirror "$archive\project" -Recurse -ErrorAction Stop
$actual = (Get-FileHash "$archive\project\renders\final.mp4" -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne '219bdcfc9fb7c6347190970ca2a7e0fa2de9d0fc10a16a41ba891051fc18f058') { throw 'archive checksum mismatch' }
```

像素级复现还依赖原浏览器、字体和驱动；备份成片本身可确保原始可播放字节留存。本轮只增加渲染失败诊断，未改影片；但引擎内容指纹随之改变。上面的旧报告仍只证明7403640时的导出，不能直接认领为新输入版本的验收；需使用新引擎重新生产时再重建事件/媒体，不能手改侧车冒认。本轮不做该重渲。

## 轻音乐检测复核（未听审）

谱面80 BPM、每小节3秒；明确跳过第4/5、15/16、25小节（从0计数），并声明76–78秒静默。最终检测的候选应分别理解：

| 静默候选（秒） | 可以由源码核对的事实 | 仍需听审的部分 |
|---|---|---|
| 12.041–18.003 | 与12–18秒两小节休止基本对应 | 休止是否过长、余尾是否自然 |
| 44.779–45.831、45.833–51.008 | 跨越45–51秒两小节休止，阈值造成分段 | 44.779起的提前回落是否太弱 |
| 71.702–72.008 | 没有声明整轨静默 | 是自然音间空隙还是过弱，尚未判定 |
| 74.528–78.006 | 75–78秒无伴奏，76–78秒显式静默 | 74.528–76秒的提前衰减尚未验收 |
| 109.925–112 | 末乐句收束、轨增益在111.7秒归零 | 是否过早消失，不能仅凭结尾设计认定通过 |

读取原始未母带分轨（112秒/48kHz，未改字节）：music样本峰值−52.924 dBFS、全段RMS−73.922 dBFS；sfx峰值−37.225、RMS−72.922。音乐峰值比音效低约15.7 dB，但不同时间的峰值不是感知响度差。恒定增益母带优先保证真峰值余量，没有压缩动态以追求−18 LUFS；最终实测−30.11 LUFS，未达到目标。音乐可能过弱、音效相对突出及长静默都应列入试听，不拿“无削波”当舒适结论。按本轮范围不调音、不替换旧片；完整试听和动态观看仍待人工验收。
