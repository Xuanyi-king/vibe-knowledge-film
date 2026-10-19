# 制作与实验条件记录

- 原仓库：`/workspace/vkf-baseline`，提交 `62d51508aad00003dc6209afa80c4b5dc540de59`。
- 条件：独立上下文子代理，以该提交原版 SKILL.md 为工作流。读了原版 visualization/worlds/engine/script 参考、new_film.py、引擎API/模板、fold_C 分镜及 look 图。没有读取升级版仓库的任何指导。
- 模型：same session model inherited；精确 API 模型名未知。不是 DeepSeek 实验，也不是模型间对照。
- 工具：本地 Python/SciPy、Canvas、原始 VK 引擎、Playwright/Chromium、ffmpeg。唯一适配是调用父任务提供的 `/workspace/baseline_render.py` 以使用本机 Chromium；未编辑引擎。
- 来源：任务提供的两个 MathWorld HTML 缓存；没有外部 AI 调用、没有图片生成调用。无法取得本会话 token/货币账单，不能报告总美元成本。
- 工作范围：仅写入本工程目录，没有提交或推送。

## 实际步骤与两轮图像修改

1. 阅读原版流程；计算给定端点的摆线；先写 `storyboard.md`、`facts.md`，再用 `new_film.py --world C` 创建工程。首个明确记录的 UTC 时刻为 **2026-10-17 15:29:22**（此时已完成前期文档阅读）；没有伪造更早的精确起点。
2. 初稿：直接比赛→片名→同一条件→同一时刻速度和落差→复赛→命名→文献。画出实体金属滑轨、实验架、有光泽的质点标记。位置使用解析式，不使用逐帧积累积分。
3. 第一轮看图：检查10帧拼图与15.3–22.5秒12帧运动条；同时看原版 `look_fold_C.jpg` 作外观参照。发现共同终点遮住蓝质点、复赛复位突变、落差尺小字靠近计时器、放大后支架底部太高。修改：双色重叠位置外圈、两个“已到达”状态、可见回放复位、尺字放另一侧、降低平台、放大片名。保存 `review/iteration0_sheet.jpg`。
4. 第二轮看图：重截相同10帧及21.2–22.6秒运动条。新增落差读数在运动中可能压住蓝轨，最终改为停格附近淡入、位于装置左侧并带引线；注明原因段“慢放×12”、复位“回到起点”。查看20秒原尺寸帧确认文字和轨道分离。保存 `review/iteration1_sheet.jpg`、`iteration1_motion.jpg`；最终图像在 `review/sheet.jpg` 与相应 motion/stills。
5. 原版工作流前30秒预览：`--clip 0 30 head`；完整输出和最终验收见下文；首次前30秒文件因中断没有完成，未将其误报为通过。

实际命令（工作目录 `/workspace/vkf-baseline`，P为`examples/descent_baseline`）：

```bash
python scripts/new_film.py examples/descent_baseline --world C
python /workspace/baseline_render.py examples/descent_baseline --sheet 2 4.4 6.5 9 13 18 20 24.5 28.8 34
python /workspace/baseline_render.py examples/descent_baseline --motion 15.3 22.5
python /workspace/baseline_render.py examples/descent_baseline --motion 21.2 22.6
python /workspace/baseline_render.py examples/descent_baseline --stills 20
python /workspace/baseline_render.py examples/descent_baseline --det
python /workspace/baseline_render.py examples/descent_baseline --clip 0 30 head
```

上述拼图/静帧命令随两轮修改重复执行；日志没有逐字保留所有shell调用，不声称这是完整原始转录。图像输出通过 view_image 实际查看。

## 实际限制

- 36秒短片压缩了原工作流通常2–5分钟的章节结构，片名卡约4秒，未使用完整12–14秒粒子片名卡。
- 主体是数学实验装置，不是场景写实；保留C夜曲配色和双语字幕。虽有轻推拉，主要仍为同一实验台机位。
- 起点、终点的两枚质点重合，用双色外圈及独立计时器说明；这不是两个分开的真实小球。
- 只比较直线和摆线，最优性依文献结论；未给出变分法证明。所有模型条件在事实表和片尾写明。
- 摆线本例末端略回升1.28mm，按真实比例呈现，不额外放大，因此肉眼不易看出。
- 未把源码描述等同于观众理解测验；没有外部盲评和真实观众测试。

## 中断与恢复（非创意迭代）

源码最终修改时间：2026-10-17 **15:34:30.650 UTC**。此后没有改动画面源码。
初次 `head` 渲染始于约15:34，尾段于15:39:36完成。任务经历用量中断后，于 **23:56:17 UTC** 恢复核验：tail.mp4完整（6秒，180帧），head.mp4缺少moov索引，最后写入15:43:00。该异常是中断造成的未完成文件，不算可交付影片。

按父任务指示先尝试一次快速无损恢复：`recover_head.py`使用完整尾段的AVC参数集提取前段NAL；结果789包但仅787可读帧，缺失时间戳，未用作最终视频。恢复尝试约一分钟。随后使用原版渲染器独立渲染0–10、10–20、20–30秒，保留完整30–36尾段，按帧顺序无损拼接。没有追加创意迭代。

```bash
python examples/descent_baseline/recover_head.py
ffmpeg -v warning -y -r 30 -i examples/descent_baseline/renders/head-recovered.h264 -c:v copy -movflags +faststart examples/descent_baseline/renders/head-recovered.mp4
python /workspace/baseline_render.py examples/descent_baseline --clip 0 10 head0
python /workspace/baseline_render.py examples/descent_baseline --clip 10 20 head1
python /workspace/baseline_render.py examples/descent_baseline --clip 20 30 head2
python /workspace/baseline_render.py examples/descent_baseline --clip 30 36 tail
python /workspace/baseline_render.py examples/descent_baseline --events
python engine/audio.py examples/descent_baseline --wav-only
```

`tail`命令是在中断前执行的，恢复时没有重跑。最终静帧/拼图/运动条重新导出仅为冻结源码的验证和交付，不是第三轮设计。

时间口径：已知的文档后创作区间15:29:22–15:34:30约5分9秒，前期阅读时间未精确记录；初次后台渲染约8分30秒直到中断，浪费的头段不算成功结果。15:43:00–23:56:17约8小时13分17秒的非运行中断不计入主动制作成本。恢复后的操作、渲染时间以下再按完成时间列出。总模型token和费用不可得，不能把外部AI调用为零等同于整个任务成本为零。


## 最终完成与可核验时间

三段恢复渲染已在再次重启前完整落盘：

| 片段 | 本地文件开始时间（UTC） | 完整文件最后修改（UTC） | 完整解码帧数 |
|---|---|---|---|
| 0–10秒 head0 | 2026-10-17 23:57:16 | 2026-10-18 00:07:41.980 | 300 |
| 10–20秒 head1 | 2026-10-17 23:57:18 | 2026-10-18 00:07:43.463 | 300 |
| 20–30秒 head2 | 2026-10-17 23:57:19 | 2026-10-18 00:07:35.953 | 300 |
| 30–36秒 tail（首次渲染复用） | 2026-10-17约15:37 | 2026-10-17 15:39:36.200 | 180 |

三路恢复渲染并行约10分27秒。再次恢复后于2026-10-18 **07:34:20 UTC**逐一核验，三段均有完整索引、300可读帧，尾段180可读帧；不需要再渲染。00:07:43–07:34:20约7小时26分37秒的非主动制作间隔也单独排除。

最终运行：

```bash
python examples/descent_baseline/finalize.py
```

该本地辅助脚本先用ffprobe检查300+300+300+180帧，再以ffmpeg concat demuxer、`-c copy -movflags +faststart`无损拼接，调用**原版**`engine/audio.py`重新生成配乐并合成final.mp4；随后全片解码到null，并从成片每秒取一帧生成6×6接触表。该脚本不改变引擎和任何画面，不进行新的Canvas渲染。

最终MP4完成时间：**2026-10-18 07:35:03.692 UTC**；全片接触表完成时间07:35:14.927；最终图像查看及哈希记录于07:35:29。首个明确记录15:29:22到最终检查的日历跨度约16小时6分7秒；减去两个已列非主动间隔，剩余约**26分13秒的工作/渲染窗口**，不含未精确记录的最初阅读。该数包括因中断浪费的初次前段渲染及恢复重算，不是纯人工思考耗时，不适合作为严格性能基准。两个创意迭代在15:34:30已结束，后续仅验证、恢复和封装。

## 验收证据与交付清单

- `renders/final.mp4`：**36.000秒、1920×1080、30fps、1080/1080可读视频帧**；H.264视频，48kHz立体声AAC音轨（35.997秒）；20,698,356字节。没有人声，音轨是原引擎合成的11个事件和低音铺底。
- `verification.json`：实际ffprobe完整输出。`ffmpeg -v error -i final.mp4 -f null -`执行成功，无解码错误。
- 最终源码的`--det`实际输出`deterministic`。画面源码自15:34:30冻结，SHA256：`c34f5e3bf497759629c6abdc7b1e414787976719cf9aaed8c03bba473252870b`。
- 成片SHA256：`7146585e837d4e11a2ffae5f09cdb82b1c2ec9bb7e07de5eb6c5f629226ac990`。
- 源文件：`film.js`、`index.html`、`storyboard.md`、`facts.md`、`brief.md`、本记录。
- 设计过程证据：`review/iteration0_sheet.jpg`、`iteration1_sheet.jpg`、`iteration1_motion.jpg`；最终`review/sheet.jpg`、`motion_21.2-22.6.jpg`、`s_0020.00.png`。
- 全片输出证据：`review/final-video-contact.jpg`（从最终MP4解码得到的每秒一帧，共36帧，已实际查看）。20秒原尺寸图是最终速度镜头，可直接用来比较。
- 音频证据：`audio/events.json`、`audio/score.wav`。可选保留`renders/raw.mp4`作无声版本。
- 不应作为交付成片的文件：`head-interrupted.mp4`、`head-recovered.mp4`、`head-recovered.h264`。它们是中断和恢复诊断遗留。`recover_head.py`、`finalize.py`是本次恢复辅助脚本，不属于影片依赖。

已看关键帧、原尺寸速度镜头、转场条以及最终MP4的36帧接触表；已逐句检查字幕和事实，并完成整片技术解码。**没有声称连续完整播放观看或人工听完音轨**；没有观众理解测试。未提交、未推送，原仓库仅本工程目录为新增。

交付副本说明：复制到功能分支后仅清理film.js空白行末的一个空格，以通过diff whitespace检查；原控制工作树的冻结源码未改，画面逻辑与常量未改。上文冻结SHA指原控制工作树，不是清理空白后的交付副本字节哈希。
