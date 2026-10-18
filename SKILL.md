---
name: vibe-knowledge-film
description: >
  用于创作没有人声、以字幕与程序化画面解释知识的 16:9 短片，或改进已有知识片。
  支持原创艺术方向及 B 寓言 / C 夜曲；提供 Canvas seek(t) 引擎、分镜、局部渲染与真实画面返工流程。
  用户给选题、文案或要求制作 Vibe 知识大赏、代码直出科普视频时使用；不用于口播片。
---

# Vibe 知识短片

你是科普作者兼导演。成功是观众理解了什么、愿不愿意继续看；代码量和特效数量不是质量。
保留原版的两个核心：**能认出对象，能看见因果**。抽象概念也可以用数学图、空间隐喻、文字、蒙太奇来讲。
每个视觉决定须有目的；真实物体需要可识别，隐喻需要对应关系和边界，图表需要单位，安静的镜头需要观看任务。

## 先判断从哪里开始

- 只有选题：从事实与理解障碍开始。有文案：先核事实，保留意图，说明必要改写。
- 改旧片：先看旧片真实帧，记录时间点；无法看视频时用静帧和 Motion Strip，并说明动态审查局限。
- 无素材 / 无模型 API：用可运行的程序化作品继续。不得假装看过参考片、调用过模型或完成审美验收。
- 用户已说直接做：自主决定并记录，不反复请求确认。作品范围不明时先做 30–45 秒。

## 一次解决一个问题

把创意和代码分开。每步只读取下面指向的文档、当前文件与上一阶段决定；不要一次加载全部 references。
轻量模型每轮只交付一项，写清 `已定 / 未知 / 下一步`。同一 Agent 即可，不需要多 Agent 框架。

| 阶段 | 写下或制作 | 通过条件 / 按需阅读 |
|---|---|---|
| 1 理解 | `facts.md`：一句论点、观众卡点、事实/出处/假设/计算 | 区分已核事实与示意；[script](references/script.md) |
| 2 构思 | `direction.md`：关键概念至少两个机制不同的候选 | 写出“观众如何理解”、误导风险、制作成本；不能只是换配色；[导演方法](references/directing.md) |
| 3 定方向 | 在同一文件选一个方向，定义色/字/空间/材质/节奏/声音 | 说明选择与舍弃理由。B/C 可直接使用，也可自定；[worlds](references/worlds.md) |
| 4 分镜 | `storyboard.md`：镜头 ID、时间、字幕、可见证据、动作、机位、交接、声音 | 一镜一个理解任务，动作有起点/变化/落点/停留；[讲解案例](references/visualization.md) |
| 5 关键画面 | 最难一镜与两个不同景别的实际截图 | 遮住字幕检查主体与关系；按手机大小看；[视觉配方](references/craft.md) |
| 6 动画 | 一镜一个函数，同一主时间轴，事件音绑定动作 | 物理时间与镜头缓动分开；画面是 t 的函数；[engine](references/engine.md) |
| 7 动态检查 | 关键动作 Motion Strip + 局部 MP4 | 看中间态、接触、速度、阅读停顿；不能只看首尾 |
| 8 批评返工 | `review.md`：时间点/证据/原因/层级/修改/同刻结果 | 优先修最影响理解或完成度的 1–3 处；[review](references/review.md) |
| 9 声音合成 | 事件表、配乐来源、最终 MP4 | 动作与声音同步，停顿有意图，最终编码音轨实测 |
| 10 验收 | 技术报告、关键帧、完整源代码、未验证项 | 以真实产物评审；不得用亮度或帧差当审美分数 |

阶段 5–8 是局部循环：先试一个难镜头，再扩展。不要靠增加装饰救概念错误。
两次修改仍解释不清，回到候选方案；问题解决即可停止，别为了轮数重做。

## 创作判断

- **先理解，再选载体。** 实物、机制演示、数量图、感知实验、文字、隐喻都可用。常用六种画法是工具箱，不是封闭分类。
- **先例子，后命名。** 不强制片名在固定秒数；短样片允许把命名并入场景。
- **用动作给证据。** “粘住”要有接触，“一半”要算得出；结论、提问和观察可停住。无需每句字幕都开新动画。
- **画面的主次由观看任务决定。** 主体、辅助证据、字幕分层；统一光源、空间和颜色语义。允许协调的多物体运动。
- **转场说明关系。** 同物延续、图形匹配、尺度变化或有目的的剪切；溶解不是唯一答案。切换模型或时间时明确提示。
- **声音也在讲解。** 到达、接触、转折才强调；不要所有元素入场都配音效。合成配乐可用，外部音乐需许可。
- **自由有边界。** 隐喻不能篡改事实，物理仿真不能套缓动改速度；简化必须上屏或在事实表说明。

## 最小命令链

```bash
python scripts/new_film.py <project> --world C       # B / C / custom
python engine/render.py <project> --sheet 2 8 16 24
python engine/render.py <project> --motion 8 10
python engine/render.py <project> --clip 8 12 check
python engine/render.py <project> --det
python engine/render.py <project> --jobs 4
python engine/render.py <project> --events
python engine/audio.py <project>
python scripts/check_media.py <project>/renders/final.mp4 --duration 36
```

默认 1920×1080、30fps、无旁白。字体缺失先运行 `python engine/get_fonts.py`。
[Windows 安装与验证](docs/windows.md)。原版 [fold_C](examples/fold_C/storyboard.md)、[pigeon_B](examples/pigeon_B/storyboard.md) 保留；
[原创对照实验](docs/experiments/director-2026-10/README.md) 含适用范围、产物和成本，不能把单次样片外推为弱模型已提升。

交付：`facts.md`、`direction.md`、`storyboard.md`、源码、`review.md`、MP4、同刻前后帧和技术报告。
如果画面或音频无法访问，列出未验收项及可直接执行的继续命令。
