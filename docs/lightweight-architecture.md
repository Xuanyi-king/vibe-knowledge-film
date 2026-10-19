# 轻量执行重构：审计、设计与验证

基线：`121e984`（仓库 main，2026-10-19）。本次不制作新影片，不变更既有媒体、引擎画面 API 或授权范围。

## 审计结论

- `SKILL.md` 11,264 UTF-8 字节，README 11,199 字节，references 共 211,838 字节。核心虽声明按需阅读，十阶段表仍要求 facts/direction/storyboard/review 四份记录、每个关键概念至少两个候选、难镜头加两种景别；相同自主完成/短片不交付原则重复出现。
- `production.md`、`prompts.md`、`directing.md` 重复候选数量与完整分镜前置；`new_film.py` 的注释、错误信息和 direction 模板又强化同样要求。研究边界、可追溯来源、真实帧和动态审查本身有价值，保留；解除的是文件数量、候选数量和先规划完再试画的配额。
- 艺术与音乐文档虽然允许不采用，核心的“优先评估曜石鎏金/We Never”仍造成主题外的前置选择。改为主题驱动、需要时取用；候选与许可说明保留。
- `review.md` 的“每镜至少落定帧”、历史 `script.md` 的字数/表格/标题配额容易被当成硬规则。历史样本须标明非规范；检查以阅读、因果、动作和实际风险决定，发行仍审查全片。
- `produce.py` 每次启动 fonts→inspect→det→resume→events→sound→master→sync/visual→media→mobile。已有 resume 只省逐帧截图，仍校验分段/拼接并重做所有后续步骤。score/checks 已自动探测，不应要求 Agent 再手工决定。
- `render_cache.source_files` 保守哈希项目全部输入（含 Markdown）及引擎/字体/可选依赖，生成目录排除。这个边界不能盲目放松：旧测试用 `.md` 做真实输入。此次不以扩展名推断“无关文件”，创作记录应放 `review/`。
- 新工程不预设 world 的约束保留，显式 B/C 的 30 秒兼容占位保留；允许已有明确理解目标后先建可改时长骨架，不强制完整十列表先行。

## 文档依赖与读取边界

| 类别 | 入口及下一跳 | 读取时机 |
|---|---|---|
| 启动必需 | SKILL.md | 新主题仅需此页启动研究和概念草图；不递归读取所有链接 |
| 创作问题按需 | script / directing → story-cases、visualization、craft | 主张难核、叙事难组织或镜头表达卡住时，取相关段落 |
| 技术按需 | engine；choreography → action-checks / light-music；complex-scenes；cartography | 当前实现需要对应 API 时 |
| 风格/素材按需 | worlds、art-direction、music-direction | 已决定采用 B/C、暗金、外部音乐或音乐驱动时 |
| 正式生产 | production → mobile、review | 第一次全片生产和发行；旧任务复用已知规则 |
| 失败排查 | docs/windows、docs/media、engine 中恢复章节 | 平台、编码、缓存、依赖失败时 |
| 历史归档 | docs/archive、docs/experiments、evidence、analysis、historical-prompts | 查案例、许可、基线或实验；正常启动不读 |

真实链接图可由 `scripts/benchmark_workflow.py` 输出；链接的可达性不是必读依赖。README 是用户首页，不是 Agent 的第二份规范。

## 最小设计与实施计划

选择：轻量核心 + 现有参考模块 + produce 的三个内部策略。只改文档无法消除重复生产；逐镜依赖图/新编排框架会增加配置和错误面，均不采用。

1. 压缩核心到质量判断、连续执行、按需路由、交付边界；统一参考页和脚手架中的配额。README 原文归档保留链接。
2. `produce(..., mode='release')` 保持旧调用/默认完整检查；Draft 默认 sheet，可指定 stills/motion/clip，不触碰正式 final 和 production 报告；Standard 保留确定性、全片/事件、声音/母带、适用同步/动作及媒体检查；Release 在其上生成手机证据。
3. 在现有 review 下仅存一个生产复用记录，按构建与手机证据两组复用。绑定全部输入、生产脚本/依赖/浏览器后端/FFmpeg身份和产物字节。失败、缺失、损坏或任一身份变化重跑；不引入逐镜缓存猜测。事件、WAV、MP4、侧车、检查图及报告均参与校验。
4. 用现有 unittest 写实际 CLI/媒体回归，先失败再实现；完整跑已有套件。基准只渲不足一秒的技术 fixture 与现有复杂镜头，不生成多部新影片；文档量是静态代理指标，工具调用与模型 Token 不混算。
5. 记录 Linux 实测、兼容性边界，独立分支提交/PR，不合并 main。原生 Windows、硬件 GPU、主观听审、完整影片观看和目标模型能力需分别报告。

## 进度

- 完成基线仓库、调用链、规范与历史实验审计。
- 完成轻量核心、文档归档、策略与缓存实施，独立审查问题已修复；最终回归与效率数字见下方结果。

## 重复效率对照的方法

无需外部模型 API。创建冻结基线检出，准备相同字体与浏览器，再运行：

```bash
git worktree add --detach ../vk-baseline 121e984
python ../vk-baseline/engine/get_fonts.py
python scripts/benchmark_workflow.py --baseline-root ../vk-baseline --output ../vk-metrics.json
# 可测运行：同一 .4 秒、12 帧技术 fixture；--scene 另检查已有 governor_scene 的一帧
python scripts/benchmark_workflow.py --baseline-root ../vk-baseline --output ../vk-metrics.json --run --scene
```

`--scene` 会准备公共 Three 资产，并复制到基线的忽略目录以保持依赖一致；工程与生成媒体放临时目录，完成即清理。日志在输出 JSON 同级 `*-logs/`；不应提交临时媒体。

四类场景分别记录：仅主题启动的 UTF-8 核心字节；单镜头的 still/motion/clip；复杂实体的现有 3D 镜头单帧；完整技术链及 Standard→Release、重复 Release。每个路线的文件数量/字节是审计者指定的静态代理，不是对真实模型的观测。链接图保留所有直接依赖以便复查；不会把所有可达链接都当作必读。

实测时间含 CLI 启动；stage_subprocess_count 是入口实际执行的制作脚本数，不含它们内部 FFmpeg/浏览器请求，也不含入口的两次版本探测及一次浏览器检查。Agent 工具调用数/模型 Token 记为 unavailable：一条 produce 命令本来就可执行整条链，不能把子进程减少包装成模型工具调用下降。

这是可重复的路径与缓存成本验证，不证明长片渲染加速、艺术质量提高或普通模型能力提升。真实模型实验继续使用 [既有对照工具](model-probe.md)，本轮不调用付费 API。

## 审查中修正的边界

- 独立静态审查发现 Python Draft API 可透传 `--clip ... final` 或 `--events`，CLI 虽安全仍不足。新增失败回归后在函数入口限制预览操作、时间范围与固定 `draft` 输出名，参数错误在写报告/执行工具前拒绝。
- 原 B/C 警告中“必须先完成完整分镜”已与迭代工作流统一；骨架兼容默认、world 要求和拒绝覆盖行为不变。
- 基准分别测独立冷启动 Release 和 Standard 后补 Release，不混用两者的时间。
- 软件 GL 测试暴露 Chromium Canvas 首次读回转换：未改动基线中连续两次 `getImageData`、期间无操作，仍有 19 个通道差 1，第三次稳定。原 `test_roles_measure_real_text_and_reject_overflow_without_painting` 可复现失败。仅让测试在基准快照前初始化读回；保留三个拒绝和前后逐像素完全相同的原断言，不增加容差、不改变生产 Canvas 行为。

## 结果与适用范围

- 核心 Skill：11,264 → 6,538 UTF-8 字节，减少 41.96%；README：11,199 → 5,787 字节。没有把字节换算为 Token。
- 冻结基线 `121e984`，字体准备完成后：`VK_BROWSER=/usr/bin/chromium python -m unittest discover -s tests -v`，110 项中 97 通过、13 可选跳过，508.834 秒。耗时含同机其他验证负载，不作为执行加速对照。
- 最初测试与字体下载并行，出现一项字体 NetworkError，110 项/1 error/13 跳过，315.361 秒；已保留失败并用冻结基线重跑，不认为重跑证明浏览器所有间歇问题已修复。
- B/C 真实静帧：fold_C@24、pigeon_B@29 两版本的 PNG SHA256 各自完全一致；源码、已有媒体和引擎算法未改。
- 独立审查的 Draft API 问题有明确 RED→GREEN 回归；软件 GL 读回测试同样先复现基线失败，再保留原断言完成初始化修正。

完整回归与基准结果见以下各节。原生 Windows/GPU/真实音源 bank/完整影片观看和主观听音不由上述结果证明。完整软件 GL 尝试在诊断读回失败后中止；修正保留断言的测试初始化，并重新启动默认浏览器参数的完整套件，未将中止记录计为通过。

### 制作实测

同机、同输入、同字体/可选依赖、Chromium 154 + 软件 GL，单次顺序执行；同时有回归任务，因此不把冷启动差异归因于重构。均为 `.4s / 12帧` 技术 fixture，非新电影。完整机器结果及直接链接图见 [efficiency.json](../evidence/lightweight/efficiency.json)。

| 路径 | 制作子进程数 | 实测秒 |
|---|---:|---:|
| 旧入口冷 Release | 9 | 100.78 |
| 新入口冷 Release | 9 | 80.50 |
| 旧入口重复 Release | 9 | 60.19 |
| 新入口重复 Release | 1 | 3.81 |
| 新入口冷 Standard | 8 | 96.00 |
| 新入口重复 Standard | 1 | 14.04 |
| Standard 后补 Release | 2 | 12.14 |
| 新入口 Draft 静帧 / 动作条 / 片段 | 各 2 | 6.92 / 19.44 / 15.81 |
| 现有复杂机构单帧（前 / 后） | 各 1 次底层渲染命令 | 8.98 / 9.12 |

重复 Release 确实跳过八项制作脚本，仍做字体就绪、浏览器/运行时探测、输入与产物 SHA 校验和最终身份复验；不是跳过首次验收。新入口另有两次工具版本探测，不计入表中制作脚本数。冷启动步骤数不减，3D 没有测得算法加速；局部预览复用原渲染器，没有声称比旧 `render.py --stills/motion/clip` 更快。

示例阅读路线的参考页数量由脚本明确列出：主题启动规划 5→0、单镜头 4→1、复杂实体 5→3、完整生产发行 9→5。它们是可复查的文档路由代理，不是目标模型真实阅读/工具调用日志；核心启动字节才是无条件可直接比较的指标。Agent 自主调用数、Token、普通模型成功率与艺术质量提升仍未测得。

### 最终回归与限制

最终代码的 `VK_BROWSER=/usr/bin/chromium python -m unittest discover -s tests -v`：**115 项中 110 通过、5 跳过、0 失败/错误，677.993 秒，退出码 0**。已安装 Three 与 Geo；默认浏览器参数的全套包含可用复杂场景、地图、分轨音乐、外部音乐、输入身份、原子恢复、媒体/同步/手机及新增策略回归。测试在共享主机上运行，新增真实媒体回归与更多可选覆盖使测试时长不可与基线当作生产速度比较。

5 跳过为 torque 两项真实钢琴 bank 与 mirror 三项素材/bank 依赖，未删除原断言或新增跳过。初次软件 GL 读回失败、基线复现与修正后的单项通过另存记录；最终整套已重新完整执行，并非拼接单项结果。新增五项测试覆盖 Draft 隔离/参数拒绝、Python API、复用记录和 Standard→Release/产物篡改/源码变化。

[验证摘要与已验证文件 SHA256](../evidence/lightweight/validation.json)绑定此次实现；[B/C 同刻字节](../evidence/lightweight/legacy-frames.json)、[Canvas 读回诊断](../evidence/lightweight/canvas-readback.json)可追溯。未新制完整影片，未执行完整主观观看/听审，也未调用目标模型 API。

本机没有原生 Windows 或硬件 GPU；仓库保留原 Linux/Windows Actions 矩阵和 PowerShell 入口，可在 PR 检查中查看本次原生核心结果。即使这些 CI 通过，也不能外推为 Windows 完整长片、真实采样 bank、硬件 WebGL、实际抖音转码或主观质量已验收。源码变化仍保守整体失效，没有逐镜依赖图或自动 LRU；这是可审查的安全边界。
