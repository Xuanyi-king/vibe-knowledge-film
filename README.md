# vibe-knowledge-film

基于 [HeyChengC/vibe-knowledge-film](https://github.com/HeyChengC/vibe-knowledge-film) 优化。给 Agent 一个知识主题，制作无旁白、暗金深沉、以字幕与程序动画把道理演出来的16:9知识电影。保留原版先找形象、写字幕与分镜、看实际画面返工的方法；优化制作稳定性，不把它改成任意风格的动画生成框架。

## 看真实作品

- **《盲区》——邓宁—克鲁格效应**：130秒完整视觉源码、字幕与分镜。[制作实例](examples/dunning_kruger/README.md)。暗金器具与一笔画类比贯穿首尾，保留研究争议；本地配乐版已制作，商业参考录音及含其音频的MP4不随仓库分发。
- **《地图是一种选择》**：72 秒完整作品，解释纬圈、面积与地图投影的取舍。[有声 MP4](https://raw.githubusercontent.com/Xuanyi-king/vibe-knowledge-film/feat/director-evidence-workflow/evidence/atlas/final.mp4) · [源码和知识来源](examples/atlas/README.md) · [实际画面与验收边界](evidence/atlas/review.md)
- **《先换来速度》**：36 秒原创，解释摆线为何更快。[有声 MP4](https://raw.githubusercontent.com/Xuanyi-king/vibe-knowledge-film/8c93e14809b839586ab4652cf1e89b2a03876717/evidence/descent_studio/final.mp4) · [源码](examples/descent_studio/) · [同题对照与局限](docs/experiments/director-2026-10/README.md)
- **夜曲《折叠》 / 寓言《鸽子的迷信》**：保留的 B/C 原版开头，各 33 秒。[折叠预览](examples/fold_C.gif) · [鸽子预览](examples/pigeon_B.gif) · [示例目录](examples/)
- 组件镜头：[复杂机构](examples/governor_scene/README.md)、[共享视听事件](examples/resonance/README.md)、[力矩与手机对照](evidence/torque/mobile/README.md)。这些是局部验证，不作为多分钟影片或模型能力提升证明。

## 安装

将仓库放到 Agent 的 Skill 目录，文件夹名保持 `vibe-knowledge-film`，例如 Claude Code 的 `~/.claude/skills/vibe-knowledge-film`，Codex 的 `~/.agents/skills/vibe-knowledge-film`。其他支持通用 Skill 规范的 Agent 按其目录约定安装；入口为 [SKILL.md](SKILL.md)。

```bash
git clone https://github.com/Xuanyi-king/vibe-knowledge-film.git
cd vibe-knowledge-film
pip install -r requirements.txt
python -m playwright install chromium
python engine/get_fonts.py
```

需要 Python 3.10+、FFmpeg 与 ffprobe；字体约 45 MB，首次需要联网。渲染器优先本机 Google Chrome，否则使用 Playwright Chromium，可通过 `VK_BROWSER` 指定浏览器路径。[Windows PowerShell 安装与验证](docs/windows.md)。

## 给一个主题直接开始

对 Agent 说：

> 用 vibe-knowledge-film 制作“地图为什么一定会失真？”。保持《运气的形状》的暗金深沉气质，自主研究、写出完整字幕稿和逐镜分镜，把原因在画面里演出来，完成整部MP4，并说明知识来源和实际审片范围。

无需逐项选择技术参数。默认保持暗金外观，创作自由用于对象、故事与讲解；用户明确选择B/C时保留其原貌。完整中英字幕与分镜先写出，工程建在Skill目录外；默认先展示3–5张实际关键帧给用户看，再根据反馈铺全片。用户明确要求自主完成时，内部验证后连续推进。`custom`是自绘实现入口，不表示可任意换颜色与美术。

新系列真实录音为音乐主体，拟音做减法，Music/SFX/Ambience保留独立轨。原片、纯音乐母版与公开授权的状态按当前素材实际核查；明确授权的本地参考混音审看如实标记，不冒充正式母版或Release，不换歌或仿作。缺素材仍继续可完成的画面；接入和严格发行边界见[音乐导演](references/music-direction.md)。旧作品接口保持兼容。

调整旧片时说：

> 修改这个工程 12–16 秒的镜头，让接触动作和力臂关系更清楚。先看原片，局部预览，完成后重新验收成片。

## 制作能力与执行成本

Canvas 确定性动画、可选 Three.js/PBR 与地理组件、解析运动和相机、共享 `VK_SCORE`、原创音乐与音效、合法外部音乐、分轨混音、母带、断点恢复、媒体/同步/动作条件和手机证据均保留。

Agent 内部用 Draft 调画面、Standard 制作全片、Release 做交付技术验收；它们是执行策略。旧命令默认 Release，用户只给主题最终仍应收到完整作品。

```bash
python scripts/produce.py <工程> --mode draft --motion 8.2 10.6
python scripts/produce.py <工程> --mode standard
python scripts/produce.py <工程>  # 正式交付前；自动复用身份相同且字节校验通过的结果
```

[生产与缓存](references/production.md) · [绘图/字幕/底层命令](references/engine.md) · [可修改交付与清理](references/handoff.md)。不新增 Python 依赖；3D/地图按需下载本地依赖。自动缓存对源码变化保守失效；有明确范围证明时，可保留原片段身份做显式局部剪辑，不能伪造缓存命中。交付后保留可编辑源码、分轨、完整画面底稿和版本记录，再清理重复生成物。

DeepSeek等支持文件与执行工具的模型可使用同一入口：先读SKILL，只按当前任务打开参考页，实际写出字幕与分镜，参考完整实例验证一镜后继续全片。模型中立的交付物和恢复步骤已经明确；尚未执行DeepSeek独立实测，不保证不同模型的成片质量相同。

技术报告能证明当前产物身份与具体检查；事实准确、电影表现、手机阅读和听感仍需真实审查。不能播放或试听时必须说明未验收范围。未做实际平台上传，就不能声称通过抖音转码；Linux 测试也不代表 Windows/GPU 全片生产已验证。

## 高级资料与历史

- [按需模块入口](SKILL.md) · [视听组件](references/choreography.md) · [复杂场景](references/complex-scenes.md) · [音乐导演与授权](references/music-direction.md)
- [本次架构审计、依赖关系与效率结果](docs/lightweight-architecture.md) · [轻量基准工具](scripts/benchmark_workflow.py)
- [重构前首页完整归档](docs/archive/README-before-lightweight.md)：保留所有升级记录、作品说明与原有媒体/证据入口。
- [历史实验](docs/experiments/) · [历史验收记录](docs/final-acceptance.md) · [已有模型对照方法](docs/model-probe.md) · [证据目录](evidence/)

开发验证：`python -m unittest discover -s tests -v`。可选资产未安装的测试会明确跳过；本轮结果与未验证项见架构审计页。

## 许可

引擎、脚本和方法文档使用 [MIT](LICENSE)。`references/analysis.md`、`references/historical-prompts.md` 的成片 brief 及 `examples/stim_B`、`info_C` 的字幕/画面来自他人作品，版权属于原作者，仅供学习对照，不可当作自己的作品发布。

原创 descent、governor_scene、resonance、atlas 的代码、程序画面和合成音轨随仓库 MIT 许可提供。D3、Three、Natural Earth、字体和采样资产各有独立许可，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。商业音乐不随仓库分发；We Never 已取消候选地位，既有讨论仅作历史记录。《运气的形状》的音乐需另行核实素材身份与使用、剪辑和发布权利，仓库许可不授予第三方录音权利。
