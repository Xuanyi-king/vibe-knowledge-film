# 《地图是一种选择》：完整主题到成片实践

输入只有[一句主题](brief.txt)“地图为什么一定会失真？”。当前Agent自主确定72秒范围、资料、叙事、美术、镜头、音乐和技术路线。影片解释球面纬圈、Mercator局部尺度和等面积投影的取舍，有完整开头、推理、比较和结尾，不是开头试片。

[完整有声MP4](../../evidence/atlas/final.mp4) · [关键帧与返工](../../evidence/atlas/review.md) · [事实和来源](facts.md) · [导演方向](direction.md) · [完整分镜](storyboard.md)

## 实际复用的公共能力

- `vk-geo.mjs`调用固定版本D3球面裁剪/投影/自适应路径和Natural Earth海岸线，不手画世界轮廓。真实地图形变服务局部尺度推导。
- `vk-motion.mjs`共享score/tempo；`score_audio.py`的确定性string拨弦、纸面摩擦和落点声、分轨自动化与有意静音。80BPM、24小节原创编排，不使用外部音乐素材。
- `vk-checks.mjs`读取实际传入绘制的尺寸、圆半径和文字测量，验证关键知识状态。它不代替图像语义识别或审美。
- 正式生产入口复用确定性、持久分段、事件指纹、失败保护、分轨、编码同步、声明条件与媒体检查。

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/produce.py examples/atlas --assets geo --chunk 4 --jobs 1
Start-Process examples/atlas/renders/final.mp4
# 独听，分别判断音乐和触感，不用相关度代替听音：
Start-Process examples/atlas/audio/music.wav
Start-Process examples/atlas/audio/sfx.wav
```

前提是Python、FFmpeg/ffprobe位于PATH。首次下载字体与地理资产，之后渲染不访问CDN；源码或资产修改后自动失效重算。可删除engine/vendor/geo卸载可选资产，旧作品不依赖它。Windows原生执行结果见[最终验收记录](../../docs/final-acceptance.md)，不以Linux通过冒充。

## 作品与结论的边界

当前Agent在项目开发上下文中完成，不是外部普通模型的独立盲测；没有证明换用Skill后所有模型创作质量提高。知识计算限于球面模型、赤道真尺度、无穷小局部；不把微分面积系数套到任意大国家。影片用两种柱面投影说明取舍，不声称完整证明高斯曲率定理。

实际看过的关键帧、动态条和编码抽帧逐项记录；完整动态播放、音色/混音听审以及观众理解仍需人工判断。技术报告通过不是电影品质证书。现有两部36秒对照、6秒机构和8秒音画样例均保留。

原创绘制/脚本/配乐方法为本项目MIT；D3与Natural Earth的独立许可在[第三方说明](../../THIRD_PARTY_NOTICES.md)和本地安装目录保留。
