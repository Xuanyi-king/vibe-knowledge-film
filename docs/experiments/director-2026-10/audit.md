# 能力审计与取舍 · 2026-10-17

原版：fork 与 upstream 均为 `62d51508aad00003dc6209afa80c4b5dc540de59`。完整阅读 SKILL、七份 references、两个 JS 引擎、render/audio/get_fonts/new_film、全部五个示例源码与分镜及 fold 的布局生成。原版无自动化测试。

## 已有能力，继续复用

| 能力 | 实际实现 | 判断 |
|---|---|---|
| 任意时间与确定性 | `VK.film/seek`, 固定种子 | 不换时间轴；同环境乱序回放可核验 |
| 静帧、sheet、motion、clip、并行 | `render.py` | 不重写渲染框架，只补失败处理 |
| 实体与光分层 | `look.under`, `layer`, bloom/post | 足以做有体积的物体；原版 fold 已证明 |
| 三维与曲线 | `VKit.M3/die/track`, SVG Path2D, poly | 简单投影可做；poly 进度按点序、track 可超调，文档需说明 |
| 字体/动态字/数 | `layout/chars/measure`, odometer | 已有高价值 API；实际字体测量胜过字符数 |
| 事件音与音乐 | `sfx/events`, audio 合成与 BGM | 不新增音频框架；检查真实编码音轨 |
| 两套美学 | B / C，以及内部 gilt | 保留；“仅两套可选”的文档限制并非引擎限制 |

Canvas 的边界：没有通用深度缓冲、物理光照、折射、遮挡排序、景深或时间多采样运动模糊。复杂三维可评估 WebGL；本次轨道实验用投影、侧壁、球体渐变与接触影即可。引入 Three/Remotion 会增加依赖、浏览器/GPU和 Windows 调试成本，没有先验证的收益，不采用。

## 限制视觉上限的关键因素

1. “先找到第一个日常实物就停止”“图形不得当主体”“只有 B/C”将案例归纳误当普遍规则，限制抽象主题与艺术方向。
2. 缺少可比较的创意候选和视觉方向契约；弱模型易从名词直接跳到特效。
3. 原版自查已有用，但主要列症状，缺少“实现→运动→构图→概念→剧本”的返工分层和同刻证据记录。
4. 三份流程文档重复且互相冲突（必须每句运动 vs 停住、永远微动 vs 安静）；上下文负担高。
5. 工程失败可被误认为成功，破坏真实反馈。新测试重现了确定性失败不抛错、事件异常被吞、编码器失败返回成功、空/负 clip、并行首个失败后不等待后续进程、短 BGM 负淡出起点。

## 实际看过的材料

- `fold_old_vs_new.jpg`：旧版主体小、无环境参照、变色缺少中介机制；新版有珠串局部、细胞结果及纤维结构。
- 原版 fold_C/pigeon_B 在同一 Chromium/字体环境生成新 sheet，并通过新版 `--det`；证据 `evidence/original/`。
- 仓库原始 GIF 可抽帧检查动作；本任务原版回归 clip 另行保存。静帧观察与动态采样不等同完整观看。
- 实际抽看fold GIF22–26秒与pigeon GIF27–31秒：前者从黏点接触到成串，后者将转圈、计时器归零与投食连接。保留动作条在evidence/original，不只从源码推测动作。
- 用户提及 Opus 视频没有附在工作区；未声称看过。历史 `analysis.md` 是上游作者的观察，不是本次独立测量。

## 六个外部仓库的具体结论

精确 commit 见 research-commits.md，研究目录为只读，不改他人仓库。不复制第三方源码或视听素材。

| 项目 / 许可 | 阅读入口及机制 | 本次判断 |
|---|---|---|
| xiazhuo123456789/vibe-knowledge-video / MIT | `SKILL.md`, `scripts/qa_check.py`：ffprobe、帧差、OCR、音频峰值 | 复用技术诊断思路，独立实现 ffmpeg 检查；拒绝用深色占比/静帧率判断美学，也不强制 110–175s |
| Vincentwei1021/video-shotcraft / Apache-2.0 | `SKILL.md`, `workbench/src/time.ts`, `remotion/zodFromCard.ts`，镜头卡 frontmatter | 镜头意图与参数范围有用；改为轻量 Markdown 契约，不搬产品卡片、工作台或音效资产 |
| Liamrjohnston/remotion-motion-graphics-skill / MIT | cinematic-camera 的共享世界坐标/焦点/zoom 代码与 hold-move-hold；motion-graphics 研究/参考门禁 | 采纳运动服务因果、真实参考观察；不引入每次授权门禁、禁止所有辉光或固定 Instagram 表面 |
| haidrrrry/claude-remotion-skill / MIT | `examples/src/components/Motion.tsx`, `references/design-rules.md`：spring、字词 reveal、统一主题 | 采纳字阶和快慢对比；“所有入场叠 2–3 属性”“每90帧新元素”“zero linear easing”不适用于真实物理演示 |
| vumichien/manim-skill / Apache-2.0 | `scripts/validate-storyboard.py`、schema 与 render contract：引用、时长和分阶段文件 | 采纳阶段产物与契约交叉核对；不引入四代理、默认旁白、LaTeX/Manim 依赖 |
| remotion-dev/remotion / Remotion License | `core/src/spring/spring-utils.ts` 解析弹簧与缓存、路径插值源码、example Spring | 绝对时间与可重放运动值得保留，本项目已具备；不复制有条件许可的运行时代码，不引入框架 |

Remotion 主仓库不是一概 MIT；依使用主体有免费/商业条件。各组件许可可不同。本次没有新增这些依赖。

还对claude-remotion-skill公开的5.056秒demo.mp4执行ffprobe与2fps抽帧，实际看到品牌标记、字标、下划线、细副题依次落定，安静背景保留主体对比。它支持“少元素依序建立层级”的方法，不证明该框架更适合本项目的空间物体。抽帧仅保存在调研缓存，未复制外部demo或品牌资产进作品。

## 未实现的自动判定

对象越界、字幕遮挡、视觉语义、事实引用真实性、分镜一致性仍需真实画面/事实表与计算测试审查。媒体检测的黑段、静音、场景变化仅是候选，不能冒充审美评分。
