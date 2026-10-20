# 轻量 Skill 与自适应生产验证

基线 `121e984`。本轮不制作新影片，不提交临时技术 fixture 的媒体。

- [架构审计、文档依赖与复现命令](../../docs/lightweight-architecture.md)
- [B/C 同刻 PNG 字节对照](legacy-frames.json)：系统 Chromium 154，同一字体与软件 GL 参数，fold_C@24、pigeon_B@29 前后完全相同。
- [基线 Canvas 连续无操作读回](canvas-readback.json)：首次→第二次有 19 通道差 1，第二次→第三次完全一致。测试仅在比较前初始化读回；不放宽原断言。

[效率结果与文档链接图](efficiency.json) · [最终回归摘要与文件指纹](validation.json)。115 项中 110 通过、5 可选跳过；原生 Windows 结果以 PR CI 为准。模型 API 未调用，模型工具调用数及 Token 不可得。普通模型能力、完整新片创作质量、实际播放/听音和平台转码不由这些技术测量证明。

## PR #3 收尾验证

上面的 JSON 保留前轮测量与代码指纹。本次 `python scripts/ci_tests.py`：122 项，117 通过、5 项原有可选资产跳过，482.443 秒，退出码 0；最终 `python -m unittest tests.test_draft_resources tests.test_setup -v` 另跑 7 项全部通过，8.929 秒。新增校验损坏下载缓存、三次重试上限、真实 FFmpeg 编码/探测/解码及中文/空格/引号工程路径；Draft 的静帧、Motion Strip、Clip 保持有效 final/侧车/正式报告/缓存/事件字节不变，后续 Release 仍复用两组结果。音乐锚点变更更新真实像素，动态 JSON 路径保守刷新，音源变更或缺必要画面资源明确失败。

只读采样现有 0.4 秒回归夹具的报告：热缓存 Release 1.4217 秒（仅 fonts，复用 standard + mobile_evidence），0–0.3 秒无声 Draft Clip 6.316 秒（fonts + preview）。这不是冷启动/新影片或严格前后性能对照；源码变化后的 Standard 重建样本为 30.5873 秒。核心仍为 6,538 字节，README 5,787 字节；原引擎/作品源码未改，不重复渲染历史影片。复现工具仍为 `scripts/benchmark_workflow.py`，不外推 Token/质量收益。

[旧 Windows 503/504 失败记录](https://github.com/Xuanyi-king/vibe-knowledge-film/actions/runs/39290048270)保留；改用固定、SHA256 校验的 FFmpeg 8.0.1 ZIP，实际执行两个工具后设置 PATH。最终提交的 Ubuntu/原生 Windows 核心、PowerShell 与软件 WebGL 日志链接记录在 [PR #3](https://github.com/Xuanyi-king/vibe-knowledge-film/pull/3) 检查及说明。硬件 GPU、Windows 完整可选 3D/真实乐器成片、主观审听与平台转码仍未验证。

首次修复提交 c780a98 的[原生运行](https://github.com/Xuanyi-king/vibe-knowledge-film/actions/runs/39344712143)：Ubuntu 核心 122 项/109 通过/13 可选跳过，组件 4 项通过；Windows 安装两个工具成功，核心发现 2 项失败（107 通过/13 跳过）：未规范化根路径使合法收据被拒绝，以及一次 Chromium 确定性截图 TargetClosedError。前者用 Linux 等价路径先复现失败，再统一规范化根路径，并保留越界拒绝断言；后者本地原测试重跑未复现（上述两项共 63.366 秒通过），没有修改渲染器、削弱断言或添加自动重试，根因未定。该失败记录保留；后续最终提交完整原生结果见 PR，不将这次失败冒充通过。

160e6e8 的[原生运行](https://github.com/Xuanyi-king/vibe-knowledge-film/actions/runs/39346196887)：Ubuntu 全部通过；Windows 路径收据及音乐生产通过，日志确认 RUNNER~1 别名，但三处真实字体请求发生 loopback ERR_CONNECTION_REFUSED（120 项、3 错误、13 跳过）。Python 3.12 默认监听队列 5 是有证据支持的候选原因：受控无 accept 突发连接实验旧队列第七个超时，64 队列十二个成功。因此仅扩大本地 HTTP 监听队列，保留错误检查，不加入重试；17 项渲染回归通过（14.475 秒），含真实并发字体与有界 TCP 突发验证。原生最终结果仍以 PR 为准，不把队列实验当 Windows 已验收。

HTTP 服务改动的 B/C 真实 PNG 前后完全一致：fold_C@24 SHA256 `26de4df2935bdf13e2377ce9056bbaab7231063a9700e8976e4883590a4bb5c8`；pigeon_B@29 `89106a6822c7635f487fcf81ded8d05b619db7276dd667542db149f8b2da643f`。仅捕获这两个原镜头的改动前后静帧，未重渲历史影片。
