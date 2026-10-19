# 许可与来源边界

可选Three.js 0.180.0为MIT，版权属于Three.js Authors；仅通过get_scene_assets.py下载两个固定模块及原LICENSE到忽略的engine/vendor/，逐文件校验SHA256。它不进入Python依赖或旧Canvas工作流。新增场景层与机构美术为本任务原创，没有复制外部模型/纹理。此前“本次没有引入Three.js”的调研判断仅适用于第一轮；第二轮六秒验证后按需引入。

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
尤其 Remotion 使用带主体条件的 Remotion License，不应将其当作一概 MIT。第一轮未安装这些运行时；本轮只增加经六秒镜头验证的可选Three.js，未引入Remotion或Manim。

requirements.txt 是兼容范围，不是跨平台逐字节复现锁文件；具体实验版本保存在实验记录中。跨操作系统字体栅格化和浏览器版本可能产生像素差异。

本轮指定视听项目的commit、实读路径、方法归因和许可逐项列于[能力融合记录](docs/capability-integration.md)。iart.ai两个视听Skill及WebGL Skill为MIT、video-shotcraft为Apache-2.0、motion-canvas为MIT；只借鉴方法，不复制代码/资产。remotion-dev/skills当前checkout缺少LICENSE，未复制其正文/代码。video-motion-craft中的派生参考追溯shotcraft。营销样片商业配乐及shotcraft音包未再分发。

resonance的几何、程序化微表面、模态激励/摩擦/气流声音、五音音乐与公共编排代码均为本任务原创、MIT；没有外部音频素材。合成材质不是录音或实测声学模型。`sound.license`是使用者的来源声明，不会自动授予素材权利。

## 完整地图作品的可选依赖

仅地图作品按需执行`get_geo_assets.py`；没有加入Python必需依赖或旧作品启动路径。逐文件URL、版本、数据commit和SHA256在该脚本中，原许可证随本地文件保留。

| 内容 | 来源与许可 | 实际使用 |
|---|---|---|
| d3-geo 3.1.1 | Mike Bostock，ISC；原LICENSE另含Charles Karney/GeographicLib的MIT许可 | 原版压缩分发构建，本地球面投影、裁剪和路径，不复制示例影片 |
| d3-array 3.2.4 | Mike Bostock，ISC | d3-geo的数值依赖，固定原版构建 |
| Natural Earth 110m land | nvkelso/natural-earth-vector commit ca96624a56bd078437bca8184e78163e5039ad19，public domain，原条款保留 | 地理陆地轮廓；不使用第三方照片、模型、音乐或政治边界 |

本地约208KB，包括许可证；`vk-geo.mjs`为原创轻量适配，数学解释由事实表与测试限定。此处是实际运行库/数据复用，因此此前“没有复制第三方代码/图片”的说法只指此前方法调研，不涵盖这些新声明的依赖。新string声源采用公开Karplus–Strong延迟反馈方法，以现有SciPy实现，无第三方音频/声库复制；合成器不是录音或声学测量保证。
