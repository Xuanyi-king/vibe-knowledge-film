# PR #1 最终验收：按证据层级区分结论

本轮继续feat/director-evidence-workflow，不合并main。既有两部36秒影片、6秒机构、8秒音画作品及有效证据保留；没有重新做九仓库全面调研。

## 本轮Skill收尾（2026-10-19）

用户最新要求停止原创作品开发，以优化Skill收尾。已停止新增镜头、艺术打磨和发行转码，保留既有源码、公开影片和本地技术导出；不以未完成主观验收的镜像工程作为电影质量成功证据。下面历史64项及地图作品记录仍保留，本轮测试以本节70项为准。

本轮完成：主Skill的观众认知变化与自主完成契约；研究证据/个人体验/理论类比分层；带认知进入、事件、证据与认知离开的分镜；Shot Intent到场景/空间/状态/相机/声音/渲染的实现路径；两题候选与生活回扣；按需轻音乐指导、授权采样bank和共享拍点乐句；图像保比例公共实现与真实拉伸负例回归。没有再次研究九个仓库或新增Python依赖。

上传《运气的形状》已实际读取：130秒、1280×720/30fps，与描述的1080p不同；全长抽样、局部动作条、音频分析均有[记录](../evidence/director-story/reference-study.md)。不是连续播放或主观听审，不复制参考媒体。方法应用探针不满足同题/同预算公平对照，见[范围](../evidence/director-story/method-check.md)。

验证绑定代码`74036406fc20e209722bc8076a81b907a1f76f7b`，最后收尾提交仅改文档/证据：

| 环境 | 实际结果 | 限制 |
|---|---|---|
| Linux本地 | 70通过，282.208秒，无跳过 | 安装Three/Geo/本片bank |
| ubuntu-latest CI首次 | 62通过、1失败、7可选跳过，167.698秒 | production首帧截图超时，根因未确认 |
| ubuntu-latest同代码重跑 | 63通过、7可选跳过，124.351秒 | 只重跑失败任务；不能据此声称间歇问题已修复 |
| windows-latest CI | 63通过、7可选跳过，230.982秒 | 原生Windows，不是本地模拟；可选3D/Geo/镜像测试跳过 |
| Windows PowerShell | verify.ps1 -SkipTests成功 | 字体与fold_C@24静帧，不等于整片WebGL通过 |

[CI运行39204006908](https://github.com/Xuanyi-king/vibe-knowledge-film/actions/runs/39204006908)及[身份/失败与日志](../evidence/director-story/ci.json)。未触发可选WebGL手动任务。

《另一种你》在暂停前已完成112秒技术导出，仍留于本地，不新增22.8MB视频到Git。[保留状态与报告](../evidence/mirror/README.md)：106个编码音频窗口无失败、15项声明视觉条件通过、媒体无错误。−30.11 LUFS、−3.54 dBTP及静音候选只是测量，不是舒服或感人的结论。最终连续观看、手机可读性、人工听音、完整独立审查、Windows整片生产均未通过验收；独立审查仅完成一项拉伸问题的反馈与修复。普通模型创作效果提升仍未证明。

## 前轮保留增量

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

最终Linux本地完整**64项通过，204.234秒**；包含已安装的可选Three与Geo。此前56项通过后追加收尾审查与WindowsMIME回归，旧计数不是最终计数。实际成片又触发AAC超峰值，追加母带/失败恢复/旧BGM保护负例后得到64项。具体最终结果列下方；未运行不等于通过。

## 自动验证与平台

代码提交`0fead6a8`的[原生Actions运行39183691582](https://github.com/Xuanyi-king/vibe-knowledge-film/actions/runs/39183691582)已完成：

| 环境 | 实际结果 | 范围 |
|---|---|---|
| Linux本地 | 64项通过，204.234秒 | 安装可选Three与Geo，无跳过 |
| ubuntu-latest CI | 64项中60通过、4可选跳过，127.998秒 | 核心回归，固定Playwright Chromium |
| windows-latest CI | 64项中60通过、4可选跳过，213.146秒 | 核心回归，原生Windows/Python3.12/Playwright Chromium |
| Windows PowerShell | `verify.ps1 -SkipTests`成功 | 字体检查与fold_C@24真实静帧；测试已由上一CI步骤执行 |
| 可选WebGL手动任务 | 本轮未触发 | 不能把核心CI成功外推为Windows完整WebGL导出通过 |

[本地日志](../evidence/final-round/tests-linux.log)、[Windows测试与PowerShell摘录](../evidence/final-round/tests-windows-ci.log)、[CI身份与范围](../evidence/final-round/ci.json)。可选Three/Geo在核心CI明确跳过，本地已实际运行。Linux本地无Windows主机，原生验证来自Actions；本机Google Chrome频道、Windows完整72秒生产与可选WebGL仍未实测。最后的文档/证据提交不改已验证代码，使用`[skip ci]`避免重复相同矩阵；验收绑定上述代码提交。

完整Linux命令：

```bash
VK_BROWSER=/usr/bin/chromium python -m unittest discover -s tests -v
VK_BROWSER=/usr/bin/chromium python scripts/produce.py examples/atlas --assets geo --chunk 4 --jobs 1
```

[Windows安装/维护](windows.md) · [事件与动作声明](../references/action-checks.md) · [迁移与完整生产](../references/production.md)。没有声称实现真实多体求解、自动乐句审美、专业DAW、通用图像动作识别或弱模型能力提升保证。

## 真实成片终检与声音返工

72秒完整影片：2160帧1920×1080p30，H.264/yuv420p、AAC48kHz。78个编码窗口无失败、量测编码延迟0；15项声明条件通过，输入/事件/final字节绑定一致。终检曾拒绝单遍loudnorm输出的+2.90dBTP，未将其记为完成；新母带从原始混音重编码并两次测量，最终-24.71LUFS、真峰值-1.95dBTP、样本峰值-2.67dBFS，无解码错误或黑段候选。源FLAC与独听轨在evidence/atlas；不是分别拉满的试听母带。

新增master_audio.py采用已测共同恒定增益，AAC未达峰值线自动降增益，最多三次；无lookahead时移，不把LUFS达标当专业听感。母带失败保留旧片；produce的后续失败恢复旧final与侧车，硬中断查备份位置。旧--bgm外混不在score.wav，独立母带默认拒绝无score工程，明确无外混时才可--legacy-source-only。

8秒修正版保留在evidence/resonance/current.mp4，原final.mp4及报告未覆盖。实际射线间隙探针及新编码抽帧归档为current-*；原名义尺寸检查漏掉的绕序问题已明示。旧fold_C24s、pigeon_B29s当前截图SHA仍与原始基线相同，见final-round/legacy-regression.json。

Windows首次真实运行56项中1失败、11错误、4可选跳过，确认系统把.mjs映射为text/plain。显式JavaScript MIME修复有真实HTTP错误映射的RED→GREEN回归。第二轮60项中54通过、2错误、4可选跳过，错误为本地字体加载NetworkError；保留失败记录，没有证据确认其根因。最终64项带请求失败诊断的运行通过，不能由单次通过宣称此前间歇网络问题已永久解决。两次历史失败链接及最终成功均见ci.json。

## 发行文件与母带

公共final.mp4采用H.264 CRF20、1080p30/72秒发行编码（10,800,291字节），音频包复制；高码率CRF14母带21,216,326字节留于工程renders/final.mp4，由produce生成。发行版经过独立check_av/check_visual/check_media，生产聚合报告引用原master-production与delivery转换记录。最终编码截图来自发行文件本身；有损视频重编码不是无损复制。

Git命令写入通道出现503，21MB单对象通过仓库接口也发送失败；发行编码已由接口接收并核对Git blob SHA。全部50个变更对象及完整文件树核对后，以预期旧HEAD保护前移PR分支，未强推或改写已发布历史。5个新公开媒体已从固定提交地址实际下载，均HTTP200且大小/SHA256匹配，见[下载核验](../evidence/final-round/downloads.json)。仓库内证据约33MB；高码率母带仍在本地工程可复现，不再重复提交逐帧PNG、无效缓存或临时恢复日志。未创建Release或公网部署。
