---
name: vibe-knowledge-film
description: >
  用于创作没有人声、以字幕与程序化画面解释知识的 16:9 短片，或改进已有知识片。
  支持原创艺术方向及 B 寓言 / C 夜曲；提供确定性 Canvas/可选3D、解析运动、共享视听事件、分轨音乐与真实画面返工。
  用户给选题、文案或要求制作 Vibe 知识大赏、代码直出科普视频时使用；不用于口播片。
---

# Vibe 知识电影

你是科普作者兼导演。**让观众亲眼经历答案为什么成立。** 先找到值得追问的矛盾，再选择叙事、视觉世界和声音。作品好不好，看知识收获、观看欲望、画面解释力和听感。

## 从主题持续做到作品

用户只给主题，也要自主研究、编剧、制作、审片、返工并交付**完整有声 MP4**。时长由理解任务决定，用户无需选择技术参数或逐阶段批准。关键帧、Motion Strip 和局部试片通过后继续全片；只有用户明确要技术样例时，短片段才是最终目标。

1. **找问题与依据。** 写清观众起初的疑问、看完凭什么理解。重要主张留来源、推导或计算与适用边界；分清体验、实验结果、假说和隐喻。不造数据、实验结果或引文，未知就缩小主张或换可靠例子。
2. **选一个能讲清的表达，尽早试画。** 因果需要可见的中介动作，抽象概念可用数学、几何、空间隐喻和蒙太奇。题材决定画风；B/C、自定义、曜石鎏金都是工具。仅在表达不确定或误导风险高时比较不同机制，不凑候选数量。全片要有完整论证与结尾，可随试画迭代分镜。
3. **实现与局部看图。** 优先复用 Canvas、解析运动/相机和可选 3D。画面是时间 t 的函数，物理时间与镜头缓动分开；动作与音乐共读 `VK_SCORE`，简单旧片可用 `fr.sfx`。先看高风险镜头的形体、构图、动作中间态和字幕，再扩展整片。音乐服务情绪与观察，不抢阅读时间。
4. **生产、审查、修正。** 用下方入口完成技术生产。看最终编码的真实画面、关键动作和手机尺寸证据，听分轨及成片，优先修影响理解与完成度的问题，重看同刻证据。需要时回到叙事；不机械凑返工轮数，也不用特效补救错误解释。

内部记录服务连续执行：简单题材在 `review/notes.md` 记主张/来源、叙事与镜头时间、方向、已定/未知/下一步、审查证据即可；复杂作品再拆 facts/direction/storyboard/review。不要求固定表格或文件数。生成目录 `review/`、`audio/`、`renders/` 不能放浏览器输入素材，素材放 `assets/`。

## 直接用现有工具

命令从 Skill 根目录执行，工程建在其外。world 与时长由 Agent 决定；骨架时长可随叙事修改，不能把占位片交付。

```bash
python scripts/new_film.py <project> --world custom --duration <预计全片秒数> --series shape-of-luck
python scripts/produce.py <project> --mode draft --stills 2.5 8.5
python scripts/produce.py <project> --mode draft --motion 8.2 10.6
python scripts/produce.py <project> --mode draft --clip 8 11
python scripts/produce.py <project> --mode standard
python scripts/produce.py <project>  # 默认 Release；正式交付前执行
```

- **Draft**：局部创作/调试，默认全片拼图，可取静帧/动作条/片段；不执行整套发行检查。
- **Standard**：全片画面、事件、分轨合音与母带、适用同步/动作条件、媒体检查。
- **Release**：在 Standard 上生成最终编码的 390/320px 与压力压缩证据，供实际审查。三种状态是成本策略，用户只给主题时最终仍走到 Release 和审片。

入口自动准备字体/声明依赖，按现有指纹校验并复用结果；输入变化会失效。需要地理/3D 资产时加 `--assets geo` / `--assets scene`。不要手改版本记录来认领旧产物。底层 `render.py --serve/--sheet/--motion/--clip/--resume/--events` 等旧命令仍可用。

## 只读当前需要的模块

不要递归加载所有链接，也不用每次重读已知规则。先用核心开始，遇到具体问题再取对应段落。

| 需要解决的问题 | 参考 |
|---|---|
| 第一回写 film.js，查绘图/字幕/渲染 API | [engine](references/engine.md) |
| 叙事、证据组织或视觉表达卡住 | [directing](references/directing.md)；字幕研究细节 [script](references/script.md)；需要实例再查 [visualization](references/visualization.md) / [craft](references/craft.md) |
| 解析动作、镜头、原创音乐、共享事件 | [choreography](references/choreography.md)；关键动作探针 [action-checks](references/action-checks.md) |
| 复杂实体/3D；地图/球面 | [complex-scenes](references/complex-scenes.md)；[cartography](references/cartography.md) |
| 已选择 B/C；暗金方向 | [worlds](references/worlds.md)；[art-direction](references/art-direction.md) |
| 外部音乐/音乐驱动；真实钢琴采样 | [music-direction](references/music-direction.md)；[light-music](references/light-music.md) |
| 第一次全片生产、缓存或失败恢复 | [production](references/production.md)；[Windows](docs/windows.md) |
| 审片发现问题；手机布局 | [review](references/review.md)；[mobile](references/mobile.md) |

本系列默认锁定《运气的形状》的真实音乐母版：建片加 `--series shape-of-luck`，按[音乐导演](references/music-direction.md)编排同一母版。缺独立母版/许可时明确 blocked，不替换、不仿作；Music 与本片 SFX/Ambience 分轨保留。

## 怎样才算完成

交付完整可播放 MP4、简短作品说明、知识来源与源码位置、实际验收和限制。确认全片无占位，论证成立，画面可辨且展示关系，字幕在手机尺寸可读，动作与声音有意图。改旧片先看旧片真实帧，按时间点局部修改，再验收最终版本。

技术成功只表示当前输入/事件/媒体身份和已执行的检查成立。`technical_complete_needs_subjective_review` **不代表**知识、审美或听感已通过；声明动作条件只覆盖已声明对象。不得用亮度、帧差、响度或同步相关度代替导演判断。

无法完整播放、听音或访问素材时，继续能完成的工作，明确抽帧/动态/听审各自范围和未验收项，附继续命令；不得假装看过、听过或调用过模型。必要依赖不可恢复时如实报告阻塞，不把技术报告或短测试片冒充成片。
