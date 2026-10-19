# 轻量 Skill 与自适应生产验证

基线 `121e984`。本轮不制作新影片，不提交临时技术 fixture 的媒体。

- [架构审计、文档依赖与复现命令](../../docs/lightweight-architecture.md)
- [B/C 同刻 PNG 字节对照](legacy-frames.json)：系统 Chromium 154，同一字体与软件 GL 参数，fold_C@24、pigeon_B@29 前后完全相同。
- [基线 Canvas 连续无操作读回](canvas-readback.json)：首次→第二次有 19 通道差 1，第二次→第三次完全一致。测试仅在比较前初始化读回；不放宽原断言。

[效率结果与文档链接图](efficiency.json) · [最终回归摘要与文件指纹](validation.json)。115 项中 110 通过、5 可选跳过；原生 Windows 结果以 PR CI 为准。模型 API 未调用，模型工具调用数及 Token 不可得。普通模型能力、完整新片创作质量、实际播放/听音和平台转码不由这些技术测量证明。
