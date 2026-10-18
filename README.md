# vibe-knowledge-film

你一定见过这种视频。最近抖音上爆火的 Vibe 知识大赏，看完收获满满。

这种视频到底怎么做？我做了一个 skill，可以一键生成这种类型的视频。成片在下面。

原版有两种视觉世界：「夜曲」适合讲底层、难懂的知识；「寓言」把心理、行为逻辑直观演给观众看。本分支保留这两套设计，并增加按主题制定原创视觉方向的工作流。

用的时候，给 Agent 一个选题或文案。它先核对事实、比较视觉方案，再确定美术方向、分镜和关键画面，制作 30–45 秒样片，通过实际静帧、Motion Strip 和局部视频返工。音效随事件合成，BGM 可以自己加。用户已授权直接制作时，不需要逐阶段重复确认。

原理不复杂。用 Canvas 和 JavaScript 把每一帧画出来，驱动浏览器一帧一帧截图，压成视频，再混上声音。字体都是开源的。说白了，就是用代码做这样一条视频。

## 本次升级与可检查的作品

原创 36 秒《先换来速度》：为什么更长的摆线比直线更快？从实体实验、同一时刻的速度比较，过渡到生成曲线的几何模型。

[![先换来速度：成片关键帧](evidence/descent_studio/final/s_0030.00.png)](evidence/descent_studio/final.mp4)

- [升级版有声 MP4](evidence/descent_studio/final.mp4) · [原版流程有声 MP4](evidence/descent_baseline/final.mp4)
- [源代码与分镜](examples/descent_studio/) · [同题对照、返工证据与已知限制](docs/experiments/director-2026-10/README.md)
- [导演决策](references/directing.md)、[视觉实现配方](references/craft.md)、[按时间点返工](references/review.md)按需加载，主 Skill 保持简短。
- 渲染失败、非确定性和事件异常会返回失败；raw/clip 渲染成功后才替换对应视频。新增媒体诊断与回归测试，继续使用原来的 seek、sheet、motion、clip 和并行渲染。

这是两个独立创作臂的同会话模型、同题、同环境单次实验，不是盲测，也没有调用 DeepSeek。它展示可检查的设计变化，不宣称已证明某个轻量模型的普遍提升。用户提到的 Opus 参考片未提供，未作为已观看材料使用。

## 夜曲：《折叠》

题目是蛋白质折叠，2024 年诺贝尔化学奖。这里是开头 33 秒。

![折叠](examples/fold_C.gif)

## 寓言：《鸽子的迷信》

一只鸽子怎么变得迷信。这里是开头 33 秒。

![鸽子的迷信](examples/pigeon_B.gif)

## 安装

把这个目录放到 Agent 的 skill 目录，文件夹名保持 `vibe-knowledge-film`。Claude Code 的常见位置是 `~/.claude/skills/vibe-knowledge-film`。交给 Agent 的流程在 `SKILL.md`。

```bash
pip install -r requirements.txt
python -m playwright install chromium
python engine/get_fonts.py
```

还需要 ffmpeg 和 ffprobe。渲染器优先使用本机 Google Chrome，缺失时使用 Playwright Chromium；也可用环境变量 `VK_BROWSER` 指定浏览器路径。字体是 SIL Open Font License，不放进仓库，所以要先跑一次 `get_fonts.py`。完整 [Windows PowerShell 命令](docs/windows.md)。

在你自己的项目里建工程，不要建在这个 skill 目录里。

```bash
python scripts/new_film.py <工程目录> --world C
python engine/render.py <工程目录> --serve
```

`--world` 用 `C`（夜曲）、`B`（寓言）或 `custom`（无辉光/颗粒的中性起点，同时生成 direction.md）。原 B/C 工程无需迁移；已有 film.js 默认不会被覆盖，需要明确 `--force`。命令和写法见 [engine](references/engine.md)。

```bash
python -m unittest discover -s tests -v
python engine/render.py examples/descent_studio --det
python engine/render.py examples/descent_studio --jobs 3
python engine/render.py examples/descent_studio --events
python engine/audio.py examples/descent_studio
python scripts/check_media.py examples/descent_studio/renders/final.mp4 --duration 36
```

媒体诊断验证编码、时长和音轨，输出黑段/静音/切换候选；它不判断审美，也不能自动证明字幕无遮挡、事实正确。须结合实际画面审查。

## 许可

引擎、脚本和文档里的方法说明使用 MIT 许可，见 `LICENSE`。

`references/analysis.md`、`references/historical-prompts.md` 里按成片填好的 brief，以及 `examples/stim_B`、`info_C`，字幕和画面设计来自他人的短片，版权属于原作者。这两段是学习对照，不要当成自己的作品发布。

本次 descent 两部样片的代码、程序化画面和合成音轨为本任务原创，随仓库 MIT 许可提供。未复制调研项目的代码或视听素材；依赖与调研许可边界见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 联系

微信号 Yangdavee，备注来意。

## 友情链接

https://linux.do/
