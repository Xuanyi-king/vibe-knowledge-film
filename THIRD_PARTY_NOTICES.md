# 许可与来源边界

本项目保留上游 HeyChengC/vibe-knowledge-film 的 MIT LICENSE 与署名。本次变更不改变历史视听素材的权利归属。

| 内容 | 来源与许可 | 使用方式 |
|---|---|---|
| Python Playwright | Microsoft, Apache-2.0 | 浏览器驱动，依赖安装 |
| NumPy / SciPy | 各项目，BSD-3-Clause | 原有音频合成与数值验证 |
| Pillow | python-pillow，HPND | 原有拼图与帧比较 |
| Chrome / Chromium | 各自发行许可 | 系统安装或 Playwright 下载，未随仓库分发 |
| FFmpeg / ffprobe | FFmpeg，LGPL/GPL 依构建选项 | 外部命令，未随仓库分发；自行核查所用构建许可 |
| engine/fonts | get_fonts.py 中的 Google Fonts 来源，SIL OFL-1.1 | 下载到本地，字体二进制不提交；保留许可证文件 |
| historical-prompts / analysis / stim_B / info_C | 上游作者对他人影片的学习复现 | 不属于可自由发布的原创视听资产 |
| descent_baseline / descent_studio | 本次任务原创代码、画面与原引擎合成音 | 随仓库 MIT；数学事实来源列在各 facts.md |

外部六仓库的 commit、入口和采用/舍弃理由见 [调研记录](docs/experiments/director-2026-10/audit.md)。只借鉴创作机制与公开算法，没有复制第三方源码、视频、音效或图片。
尤其 Remotion 使用带主体条件的 Remotion License，不应将其当作一概 MIT。本次没有安装或引入 Remotion、Three.js、Manim 等运行时。

requirements.txt 是兼容范围，不是跨平台逐字节复现锁文件；具体实验版本保存在实验记录中。跨操作系统字体栅格化和浏览器版本可能产生像素差异。
