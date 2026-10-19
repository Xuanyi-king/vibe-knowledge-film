# PR #1 最终验收：按证据层级区分结论

本轮继续feat/director-evidence-workflow，不合并main。既有两部36秒影片、6秒机构、8秒音画作品及有效证据保留；没有重新做九仓库全面调研。

## 当前增量

- 主Skill明确只有主题也自主研究、编剧、定艺术/声音/时长、制作、返工和交付完整有声MP4。短试片是内部验证，通过后自动继续，不让用户逐阶段批准。入口produce.py执行技术链，不冒充自动创意算法。
- 事件表封装全输入SHA256和导出内容SHA；raw/final有媒体字节与时间区间侧车，final还绑定事件和参考混音。改film/score但保持END/FPS、手改JSON、复用旧raw、改参考WAV/MP4均不能通过。
- 无版本旧导出须重新渲染/导事件/合音，不提供“忽略指纹”绿灯开关。旧B/C源码API不变；保守追踪包括Markdown、字体和全部本地资产。生成目录不可当输入。
- VK_CHECKS在实际编码帧网格seek并截图后读场景状态。可声明接触前/当刻/后几何间隙、到达/比例/文字边界等，不实现通用语义图像识别。END不在编码帧集合，需end偏移一个帧周期。
- camera省略fov时固定首次基准，乱序seek不再累积。共享score/contact/impulse/track/camera与音效/音乐自动化接口已有最小调用例，不让作品重复实现调度和合音。
- 新可选D3地理适配复用球面裁剪、投影与海岸线；本地固定构建/数据、逐文件SHA、完整许可。新增确定性Karplus–Strong拨弦复用SciPy，无额外Python依赖。

## 验收必须分层

| 层 | 能证明什么 | 不能证明什么 |
|---|---|---|
| 输入/媒体版本 | 当前画面、事件、参考混音和最终媒体字节属于同一次输入版本 | 知识和美术正确、抗恶意签名 |
| 编码音频同步 | 源混音与最终AAC解码的相关性、局部编码延迟 | 物体真的碰到、音色好听、单个声部在重叠音乐中必然可辨 |
| 声明视觉条件 | 实际帧上的作者声明数值条件，附截图与事件锚点 | 未声明动作、通用图像语义、摄影/审美评分 |
| 实际画面审查 | 已看关键帧/动作条/编码抽帧的具体问题与返工 | 没有完整播放时的全部动态体验 |
| 人工完整听审 | 音色、声像、混音舒适度、音乐叙事与整体节奏 | 当前执行环境未完成，不能拿LUFS或相关度替代 |
| 普通模型创作效果 | 需要相同提示/模型/预算的真实多题材产物与审查 | 本轮Agent开发上下文实践和旧简报不一致案例均未证明 |

## 完整作品

《地图是一种选择》输入只有“地图为什么一定会失真？”，当前Agent自主制作完整72秒叙事。[有声MP4](../evidence/atlas/final.mp4)、[源码与知识来源](../examples/atlas/README.md)、[返工与真实画面](../evidence/atlas/review.md)。这是端到端实践，不是隔离模型能力实验。地理/数学解释限定球面、赤道标准纬线、局部微分尺度；没有把局部四倍套成任意国家面积。

最终Linux本地完整**60项通过，340.028秒**；包含已安装的可选Three与Geo。此前56项通过后追加收尾审查与WindowsMIME回归，旧计数不是最终计数。具体最终结果列下方；未运行不等于通过。

## 自动验证与平台

首次原生Windows Actions实际运行，暴露.mjs被系统映射为text/plain，导致模块加载失败（56项中1失败、11错误、4可选跳过）。服务器已改显式JavaScript MIME，真实HTTP模拟错误映射已RED→GREEN；最终Windows重跑结果待录入。最终完整日志见[evidence/final-round/tests-linux.log](../evidence/final-round/tests-linux.log)。Linux本地安装可选Three与Geo；GitHub Actions核心矩阵不强制这些可选资产，会明确跳过对应测试。手动webgl任务执行现有8秒作品的完整渲染/混音/两层同步与媒体检查。Windows原生结果以真实Actions日志为准，本地无Windows主机。

完整Linux命令：

```bash
VK_BROWSER=/usr/bin/chromium python -m unittest discover -s tests -v
VK_BROWSER=/usr/bin/chromium python scripts/produce.py examples/atlas --assets geo --chunk 4 --jobs 1
```

[Windows安装/维护](windows.md) · [事件与动作声明](../references/action-checks.md) · [迁移与完整生产](../references/production.md)。没有声称实现真实多体求解、自动乐句审美、专业DAW、通用图像动作识别或弱模型能力提升保证。
