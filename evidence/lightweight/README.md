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
