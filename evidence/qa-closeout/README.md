# PR #2 最终收尾（基线 7a602af9）

本轮只修复手机QA重复解码与《力的远近》读数组显现；不更改正式编码质量、物理模型、摄影机、音乐或音效时间。旧证据和旧母版保留在 `evidence/torque/mobile/`。

## 实测性能

同一机器、同一输入、同一采样点，完整纯MP4 `review_video`（包含压力转码、音轨检查和320/390缩图）；不含浏览器布局采集和影片制作。单次测量，不是跨机器性能保证。资源为每20ms采样的进程树RSS总和，CPU含子进程。

|输入|目标帧数|原耗时→新版|提速|CPU秒 原→新|峰值RSS MiB 原→新|选择解码次数 原→新|
|---|---:|---:|---:|---:|---:|---:|
|14秒现有1080p短片|7|10.62→6.43秒|1.65×|14.76→9.34|252.61→247.31|14→2|
|72秒现有1080p作品|12|61.98→30.54秒|2.03×|89.21→46.57|255.58→255.69|24→2|
|180秒合成960×540/30fps|32|149.90→36.65秒|4.09×|204.65→54.60|153.65→152.80|64→2|

母版及压力副本的全部204张320/390缩图，前后RGB逐像素相同（每张hash见[记录](performance.json)）。改用一次顺序`select(n)`，不以近似时间seek提速。180秒不是1080p作品，不冒称已测同分辨率长片。

另用2348事件检查采样规划：原2087帧→32帧，8个接触点全部保留，1440个音乐音符不单独产生视觉检查点。**这只测规划，不把它当作2087帧整次QA的计时结果。** 必检条件、接触/揭晓/停留及明确指定时刻不受软预算截断；相邻可选点合并。超过32个必检点时仍全部保留，拼图每页最多24行，报告记录取舍。

## 复现（Linux性能采样）

`benchmark.py`仅测量脚本，`psutil`不是制作依赖。输出使用独立临时目录，不写母版。Windows核心功能由原生CI验证，性能数字来自Linux。

```bash
python -m pip install psutil
# 导出基线，不能从旧提交复制覆盖现有正式脚本
git show 7a602af9:scripts/check_mobile.py > /tmp/check_mobile_before.py
ffmpeg -v error -y -f lavfi -i testsrc2=s=960x540:r=30:d=180 -f lavfi -i sine=frequency=330:sample_rate=48000:duration=180 -c:v libx264 -preset ultrafast -crf 20 -g 60 -pix_fmt yuv420p -c:a aac -shortest /tmp/many-events.mp4
python evidence/qa-closeout/benchmark.py --baseline /tmp/check_mobile_before.py --candidate scripts/check_mobile.py --synthetic /tmp/many-events.mp4 --output /tmp/mobile-benchmark
```

## Windows字体故障边界

[Linux有限生命周期检查](server-audit.json)：8次独立服务器各12个并行字体读取，hash一致；关闭后端口均拒绝连接；3次实际浏览器启动均READY且字体加载完成。**未复现Windows偶发拒连，未证明根因，未改服务器或增加超时/自动重试。** 原生CI成功不等于已根治间歇性问题。已有资源失败诊断和明确失败行为保留。

## 验收边界

技术同步与画面阅读分开记录；未完成连续人工观看/听审、真实抖音上传转码、Windows完整真实乐器14秒生产，不能因测试通过改写为已验收。本轮按用户加速收尾要求冻结。17项针对性测试通过（见 `target-green.log`）；完整本地回归与14秒重渲尚未完成，新HEAD原生CI需以PR Checks为准。不能把上一HEAD的CI或旧成片身份认作本次通过。暂不建议无条件合并，待这些技术检查结束后再决定。

[320px同刻对照](intermediate-320.png)左列为旧完整编码MP4，右列来自新正式渲染器已完成的第一段缓存（不是新全片）。53/54/55帧不再孤立显示力矩标签、横杠和单位；96帧的2 N与0.70 N·m保持可读。尚不能据此认领完整动态与两档重压缩验收。旧完整有声MP4仍保留于[原目录](../torque/mobile/README.md)，不会以不完整新片替换。

继续未完成的本地技术验证可执行：

```powershell
python -m unittest discover -s tests -v
python scripts/produce.py examples/torque --assets scene --chunk 3.5 --jobs 2
python scripts/check_mobile.py examples/torque/renders/final.mp4 --project examples/torque --profile 540p-crf33 --output examples/torque/review/mobile-strong
```

持久缓存只复用通过源码指纹与有效片段校验的当前输入，不冒用旧缓存。
