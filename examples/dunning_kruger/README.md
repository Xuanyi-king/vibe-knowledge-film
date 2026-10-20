# 《盲区》——邓宁—克鲁格效应

130秒，1920×1080，30fps，无旁白。这是完整电影的可编辑视觉源码，供Agent学习文件组织、可见推理和首尾回场；不是通用画面模板。新主题要重新选择合适对象。

![实际成片画面](frame.jpg)

先读[字幕稿](script.md)、[逐镜分镜](storyboard.md)与[科学依据及类比边界](sources.md)，再看`film.js`。`objects.mjs`用现有Three/PBR绘制器具，`canvas.mjs`负责纸张、数轴和二维图形。`SUBS`、`SHOTS`、绝对时间和共享VK_SCORE在同一影片中管理，绘制代码不另造引擎。

观众的理解变化：从凭直觉判断一笔画，学会检查路口配对规则，再回到同一张图验证新判断。该图只是教学类比，不是心理学原实验。原研究12/62是百分位，不是答对率；2020与2023年的研究结果与范围分别交代，未使用流行山谷曲线。结尾直接给出“先做一次验证，再用反馈修正判断”的学习落点。

## 本地试画

先按仓库说明准备已有环境；复制到Skill之外的影片工作区。例如PowerShell：

```powershell
New-Item -ItemType Directory -Path ../films -Force
Copy-Item -LiteralPath ./examples/dunning_kruger -Destination ../films/dunning-kruger -Recurse
python scripts/produce.py ../films/dunning-kruger --mode draft --assets scene --visual-only --stills 3 36 75 120.5
python scripts/produce.py ../films/dunning-kruger --mode draft --visual-only --motion 108 118
```

`--assets scene`准备本例使用的可选Three依赖，已经存在时复用；不是安装另一套引擎。当前`music.json`如实保留缺母版状态。视觉Draft不导入缺失音乐计划；Standard/Release仍会拒绝认证。正式使用需按[音乐导演](../../references/music-direction.md)接入真实指定母版及适用权限。不能以修改状态或换歌取得通过。

本地成片使用用户提供的《运气的形状》参考混合录音；原视频、录音、WAV及含其音频的MP4均不随仓库分发。源码中的显式本地混音分支不授予录音权利，普通视觉Draft不会启用该分支。

## 修改与检查

实际制作曾把30–32秒的纸张/数轴重影修正，并把12/62的含义移入主要字幕。结尾只改两句，实际复用前116秒画面，重绘末14秒；编码包核对证明前116秒与全部AAC保持一致。局部复用采用保留旧源身份的新剪辑清单，不修改旧缓存记录。

主字幕在320px下折算约13.33px，仍有字号风险；小注释偏小，不能宣称手机全绿。全片解码、采样和数值检查不等于连续主观观看/试听。不要把本例或本机成功写成DeepSeek已测通过。

后续制作保留成片、画面底稿、源码/资产与分轨；见[修改、交接与清理](../../references/handoff.md)。本例不含机器路径固定的临时剪辑脚本，使用仓库现有入口。

原片需求为简体中文，因此当前画面保留中文主字幕；`subtitles/zh.srt`与`en.srt`提供26条同轴独立字幕，译文和时间源在`source.json`。英文尚未烧录进本例画面；新片按Skill默认设计中英双行，不能把字幕文件存在说成英文画面已验收。
