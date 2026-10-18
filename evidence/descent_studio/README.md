# 原有升级片证据索引

两部36秒影片未重新制作。成片已迁到[PR媒体预发布](https://github.com/Xuanyi-king/vibe-knowledge-film/releases/tag/pr-1-media)，各文件SHA256和下载地址在[assets.json](../assets.json)。

- v1：首版源码与17秒、5.5秒问题帧。
- v2：第一次返工源码与同刻17秒帧。
- final：最终17秒PNG、代表性最终JPEG及比赛Motion Strip。最终源码以examples/descent_studio为准，不重复复制。
- same_time_before_after.jpg / final_contact.jpg：同刻返工对照及最终编码抽帧。
- final_media_report.json / timing_and_cost.json：原成片技术报告与精简逐项耗时，包含中断导致的未知成本，不制造节省。
- brief.md：原始输入，明确额外美术提示。此案例不能隔离证明Skill效果。

重复全尺寸帧、逐进程日志、失效临时路径和重复源码副本从当前树清理；需要历史全文时查看commit8c93e14。创作审查的唯一正文在examples/descent_studio/review.md。

专用恢复脚本已变为正式`engine/render.py --resume`的兼容入口，不再依赖这份证据目录或等待某个父进程片段。
